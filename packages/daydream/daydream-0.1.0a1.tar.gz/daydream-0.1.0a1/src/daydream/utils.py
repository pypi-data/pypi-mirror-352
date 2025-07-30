import colorsys
import importlib
import json
import pkgutil
import re
from collections.abc import Awaitable, Callable, Iterable
from re import Pattern
from types import ModuleType
from typing import Any, Generic, TypeVar, cast

import anyio
from anyio import create_memory_object_stream
from anyio.abc import TaskGroup
from boltons.iterutils import remap
from pydantic import AnyUrl, ValidationError
from rich.console import Console

T = TypeVar("T")


stderr = Console(stderr=True)


def print(message: str, _indent: int | None = None, **kwargs: Any) -> None:
    stderr.print_json(json.dumps({"message": message, **kwargs}, default=str), indent=_indent)


def import_submodules(
    package: str | ModuleType,
    recursive: bool = True,
) -> dict[str, ModuleType]:
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results: dict[str, ModuleType] = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = f"{package.__name__}.{name}"
        try:
            results[full_name] = importlib.import_module(full_name)
        except ModuleNotFoundError:
            continue
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


class classproperty(Generic[T]):
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """

    def __init__(self, method: Callable[[Any], T]) -> None:
        self.fget = method

    def __get__(self, instance: object, cls: type | None = None) -> T:
        return self.fget(cls if cls else instance.__class__)

    def getter(self, method: Callable[[Any], T]) -> "classproperty[T]":
        self.fget = method
        return self


def as_completed(tg: TaskGroup, aws: Iterable[Awaitable[T]]) -> Iterable[Awaitable[T]]:
    send_stream, receive_stream = create_memory_object_stream[T | Exception]()

    # Convert the iterable to a list to get its length
    aws_list = list(aws)
    count = len(aws_list)
    completed = 0

    async def populate_result(a: Awaitable[T]) -> None:
        nonlocal completed
        try:
            result = await a
            await send_stream.send(result)
        except Exception as e:
            # Send the exception too, so it can be raised in the caller's context
            await send_stream.send(e)
        finally:
            completed += 1
            # Close the send stream when all tasks are done
            if completed >= count:
                await send_stream.aclose()

    async def wait_for_result() -> T:
        try:
            result = await receive_stream.receive()
            # If we received an exception, raise it
            if isinstance(result, Exception):
                raise result
            return result
        except anyio.EndOfStream as e:
            # This should only happen if all senders are done but we're still trying to receive
            raise StopIteration("No more results available") from e

    for a in aws_list:
        tg.start_soon(populate_result, a)

    return (wait_for_result() for _ in aws_list)


def generate_contrasting_colors(n: int) -> list[tuple[str, str]]:
    """
    Generate N visually distinct colors as (background, foreground) hex pairs.

    The background colors are chosen by evenly spacing hues around the HSL color wheel.
    The foreground color is either black or white, chosen for maximum contrast.

    Args:
        n (int): Number of color pairs to generate.

    Returns:
        List[Tuple[str, str]]: List of (background_hex, foreground_hex) tuples.
    """

    def luminance(r: float, g: float, b: float) -> float:
        # sRGB to linear RGB conversion
        def to_linear(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r_lin, g_lin, b_lin = map(to_linear, (r, g, b))
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    def get_foreground_color(r: float, g: float, b: float) -> str:
        return "#000000" if luminance(r, g, b) > 0.5 else "#ffffff"

    color_pairs: list[tuple[str, str]] = []
    for i in range(n):
        hue = i / n
        saturation = 0.65
        lightness = 0.5
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        fg_color = get_foreground_color(r, g, b)
        color_pairs.append((hex_color, fg_color))

    return color_pairs


def camel_to_snake(s: str) -> str:
    """Convert a camelCase string to a snake_case string."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def strip_secrets(data: dict[str, Any]) -> dict[str, Any]:
    """Strip secrets from a dictionary."""

    # Define a constant for redacted content
    REDACTED = "REDACTED"

    def _visit(_path: tuple[str, ...], key: str, value: Any) -> bool | tuple[str, Any]:  # noqa: ANN401
        if key in ("passphrase", "connection_url"):
            return False
        if key == "env" and isinstance(value, dict):
            value = cast("dict[str, Any]", value)
            clean_env: dict[str, Any] = {}
            for k, v in value.items():
                clean_env[k] = v

                # If it's a URL, redact the password
                try:
                    original_url = AnyUrl(v)
                except ValidationError:
                    pass
                else:
                    if not original_url.host:
                        clean_env[k] = str(original_url)
                        continue
                    else:
                        clean_env[k] = str(
                            AnyUrl.build(
                                scheme=original_url.scheme,
                                username=original_url.username,
                                password=REDACTED,
                                host=original_url.host,
                                port=original_url.port,
                                path=original_url.path,
                                query=original_url.query,
                                fragment=original_url.fragment,
                            )
                        )

                if any(
                    secret_indicator in k.upper()
                    for secret_indicator in (
                        "KEY",
                        "PASS",
                        "PASSPHRASE",
                        "PASSWORD",
                        "PSK",
                        "SECRET",
                        "TOKEN",
                    )
                ):
                    clean_env[k] = REDACTED
            return "env", clean_env
        return True

    return remap(data, _visit)


def compile_regex(pattern: str) -> Pattern[str]:
    """Compile a string into a regex pattern."""
    # Extract the pattern and flags from the string
    delimiter = pattern[0]
    if pattern.rfind(delimiter) == 0:
        raise ValueError("Invalid regex pattern: Missing closing delimiter")

    # Split the pattern and the flags
    parts = pattern.rsplit(delimiter, 1)
    raw_pattern = parts[0][1:]
    flags_str = parts[1] if len(parts) > 1 else ""

    # Map string flags to re module flags
    flag_map = {
        "g": 0,  # Global flag is not needed in Python regex
        "i": re.IGNORECASE,
        "m": re.MULTILINE,
        "s": re.DOTALL,
        "x": re.VERBOSE,
        "u": re.UNICODE,
    }

    # Calculate the combined flags
    flags = 0
    for char in flags_str:
        if char in flag_map:
            flags |= flag_map[char]
        else:
            raise ValueError(f"Unknown regex flag: {char}")

    # Compile the regex pattern with the calculated flags
    return re.compile(raw_pattern, flags)
