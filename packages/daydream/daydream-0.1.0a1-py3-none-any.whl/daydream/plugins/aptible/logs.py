import asyncio
import gzip
import json
import os
import re
import secrets
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

from pydantic import AwareDatetime, BaseModel
from sh import Command, ErrorReturnCode

from daydream.lib.log_anomalies import LogLine
from daydream.plugins.aptible.nodes.aptible_aws_instance import AptibleAwsInstance
from daydream.plugins.aptible.nodes.base import AptibleNode
from daydream.utils import print

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from daydream.plugins.aptible.nodes.aptible_container import AptibleContainer


LOGS_DIR = Path.home() / ".daydream" / "logs"
LOG_FILENAME_PATTERN = re.compile(r"^.*\.archived\.gz$")
LOG_FILENAME_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
MAX_CONTAINER_LOG_CHECKS = 2

LogResourceType = Literal["service", "container"]

random = secrets.SystemRandom()


class LogBucketConfig(BaseModel):
    bucket_name: str
    region: str
    decryption_keys: str


async def get_logs_for_time_range(
    stack: str,
    node: AptibleNode,
    containers: list["AptibleContainer"],
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> list[LogLine]:
    start_date = start_dt.date()
    end_date = end_dt.date()

    log_dir = LOGS_DIR / f"{stack}-{node.raw_data['_type']}-{node.node_id}-{start_date}-{end_date}"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filenames = log_files_in_dir(log_dir, start_dt, end_dt)

    if not log_filenames:
        print(
            f"Downloading logs for {stack} {node.raw_data['_type']} {node.node_id} {start_date} {end_date}"
        )

        if len(containers) > MAX_CONTAINER_LOG_CHECKS:
            print(f"Sampling {len(containers)} containers to {MAX_CONTAINER_LOG_CHECKS}")
            containers = random.sample(containers, MAX_CONTAINER_LOG_CHECKS)

        bucket_config = await get_log_bucket_config(stack)
        await asyncio.gather(
            download_container_logs(stack, containers, start_dt, end_dt, log_dir),
            download_s3_logs(stack, containers, start_date, end_date, bucket_config, log_dir),
        )

        log_filenames = log_files_in_dir(log_dir, start_dt, end_dt)
    else:
        print(
            f"Using cached logs for {stack} {node.raw_data['_type']} {node.node_id} {start_date} {end_date}"
        )

    return await get_log_lines(log_filenames, start_dt, end_dt)


async def get_log_lines(
    log_filenames: list[Path], start_dt: datetime, end_dt: datetime
) -> list[LogLine]:
    log_lines: list[LogLine] = []
    print(f"Getting log lines for {len(log_filenames)} files")

    if len(log_filenames) == 0:
        return log_lines

    # Ensure input datetimes are timezone-aware
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=UTC)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=UTC)

    # Get filesize of all log files
    log_file_size = sum([f.stat().st_size for f in log_filenames])
    print(f"Total log file size: {log_file_size}")

    if log_file_size == 0:
        return log_lines

    # Calculate sampling ratio based on a target filesize
    target_filesize = 100 * 1024 * 1024  # 100MB
    sampling_ratio = min(1.0, target_filesize / log_file_size)
    print(f"Sampling ratio: {sampling_ratio}")

    for log_filename in log_filenames:
        with gzip.open(log_filename, "rt") as f:
            for line in f:
                if random.random() < sampling_ratio:
                    try:
                        json_line = json.loads(line)
                        dt = parse_log_line_timestamp(json_line["time"])
                        if start_dt <= dt <= end_dt:
                            log_lines.append((dt, json_line["log"].strip()))
                    except (json.JSONDecodeError, ValueError):
                        pass

    return log_lines


def parse_log_line_timestamp(ts: str) -> datetime:
    ts_parts = ts.split(".")

    if len(ts_parts) == 2:
        base, nanos = ts_parts
        micros = (nanos[:-1] + "000000")[:6]  # Remove Z, pad/truncate to 6 digits
        ts_fixed = f"{base}.{micros}Z"
        dt = datetime.strptime(ts_fixed, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

    # Make the datetime timezone-aware by assuming UTC
    return dt.replace(tzinfo=UTC)


async def get_log_bucket_config(stack: str) -> LogBucketConfig:
    log_bucket = await get_pancake_setting(stack, "sweetness/nonsensitive/DOCKER_LOGS_BUCKET_NAME")
    bucket_region = log_bucket.replace("aptible-docker-logs-", "")
    log_encryption_keys = await get_pancake_setting(
        stack, "sweetness/sensitive/LOG_ENCRYPTION_KEYS"
    )
    return LogBucketConfig(
        bucket_name=log_bucket,
        region=bucket_region,
        decryption_keys=log_encryption_keys,
    )


async def download_s3_logs(
    stack: str,
    containers: list["AptibleContainer"],
    start_date: date,
    end_date: date,
    bucket_config: LogBucketConfig,
    download_dir: Path,
) -> None:
    for container in containers:
        print(f"Downloading s3 logs for {container.raw_data['docker_name']}")

        try:
            aptible_cli = Command("aptible")
            await aptible_cli.logs_from_archive(
                stack=stack,
                container_id=container.raw_data["docker_name"],
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                region=bucket_config.region,
                bucket=bucket_config.bucket_name,
                decryption_keys=bucket_config.decryption_keys,
                download_location=str(download_dir),
                _async=True,
            )
        except ErrorReturnCode as e:
            print(f"Error running command: {e}")


async def download_container_logs(
    stack: str,
    containers: list["AptibleContainer"],
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
    download_dir: Path,
) -> None:
    pancake = cast("Callable[..., Awaitable[str]]", Command(os.getenv("PANCAKE_PATH")))

    log_lines: list[LogLine] = []

    pancake_env = os.environ.copy()
    pancake_env["THOR_SILENCE_DEPRECATION"] = "1"

    for container in containers:
        if container.raw_data["deleted_at"]:
            continue

        try:
            aws_instance = await anext(container.iter_neighboring(AptibleAwsInstance))
        except StopAsyncIteration as e:
            raise ValueError("Container has no parent AWS instance") from e

        container_id = container.raw_data["docker_name"]
        instance_name = aws_instance.raw_data["runtime_data"]["hostname"]

        print(f"Downloading container logs for {instance_name} {container_id}")
        output_lines = []

        try:
            output = await pancake(
                "stack:ssh",
                stack,
                "--instance",
                instance_name,
                "sudo",
                "docker",
                "container",
                "logs",
                container_id,
                "--timestamps",
                "--since",
                start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "--until",
                end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                _async=True,
                _env=pancake_env,
            )
            output_lines = output.splitlines()
            print(f"Found {len(output_lines)} log lines for {container_id}")
        except ErrorReturnCode as e:
            print(f"Error running command: {e}")

        for line in output_lines:
            try:
                dt, msg = line.split(" ", maxsplit=1)
                dt = parse_log_line_timestamp(dt)
                log_lines.append((dt, msg))
            except ValueError:
                pass

    # If we found any log lines, write them to a gzipped jsonl file (same format
    # as s3 logs)
    if len(log_lines) > 0:
        with gzip.open(
            download_dir
            / f"?????????-json.log.{start_dt.strftime(LOG_FILENAME_DATETIME_FORMAT)}.{end_dt.strftime(LOG_FILENAME_DATETIME_FORMAT)}.archived.gz",
            "wt",
        ) as f:
            for dt, msg in log_lines:
                log_line_json = {
                    "time": dt.isoformat(),
                    "log": msg,
                }
                f.write(json.dumps(log_line_json) + "\n")


def log_files_in_dir(log_dir: Path, start_dt: datetime, end_dt: datetime) -> list[Path]:
    filenames = [
        f for f in log_dir.glob("**/*") if f.is_file() and LOG_FILENAME_PATTERN.match(f.name)
    ]
    matching_files = []
    for filename in filenames:
        dt_range = str(filename).split("json.log.")[1].replace(".archived.gz", "")
        dt_range = dt_range.removeprefix("1.")

        log_start, log_end = dt_range.split(".")
        log_start_dt = datetime.strptime(log_start, LOG_FILENAME_DATETIME_FORMAT)
        log_start_dt = log_start_dt.replace(tzinfo=UTC)
        log_end_dt = datetime.strptime(log_end, LOG_FILENAME_DATETIME_FORMAT)
        log_end_dt = log_end_dt.replace(tzinfo=UTC)

        # Check if the log file's time range overlaps with our target period
        if (
            (start_dt <= log_start_dt <= end_dt)
            or (start_dt <= log_end_dt <= end_dt)
            or (log_start_dt <= start_dt <= log_end_dt)
        ):
            print(f"{filename} {log_start_dt} {log_end_dt}")
            matching_files.append(filename)

    return matching_files


async def get_pancake_setting(stack: str, setting: str) -> str:
    pancake = cast("Callable[..., Awaitable[str]]", Command(os.getenv("PANCAKE_PATH")))

    try:
        result = await pancake(
            "stack:settings:view_single",
            stack,
            setting,
            _async=True,
        )
        return result.strip()
    except ErrorReturnCode as e:
        print(f"Error running command: {e}")

    return ""
