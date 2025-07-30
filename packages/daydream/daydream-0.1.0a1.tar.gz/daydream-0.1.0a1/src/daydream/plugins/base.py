from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast

from daydream.config.utils import Config, PluginConfig, PluginSettings
from daydream.utils import classproperty

if TYPE_CHECKING:
    from daydream.mcp import Context

REGISTRY: dict[str, type["Plugin"]] = {}


class PluginProtocol(Protocol):
    """Protocol for the plugins interface."""

    context: "Context"

    @classproperty
    def name(cls) -> str:
        """Converts a SomePlugin class to a "some" string, which is the key used in the configuration file.

        For example, AwsPlugin becomes "aws".
        """
        return cast("type[PluginProtocol]", cls).__name__.removesuffix("Plugin").lower()


class Plugin(PluginProtocol):
    """Base class for all plugins."""

    def __init__(self, **settings: Any) -> None:
        self._settings = settings

    def __init_subclass__(cls, **kwargs: Any) -> None:
        REGISTRY[cls.name] = cls

    @classproperty
    def default_plugin_settings(cls) -> PluginSettings:
        return {}


class PluginCapability(PluginProtocol):
    """Protocol for capabilities that plugins can have."""


HasPluginCapability = TypeVar("HasPluginCapability", bound=PluginCapability)


class PluginManager:
    """A manager for plugins and their configuration."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._plugins = {}

    def get_plugin_class(self, name: str) -> type[Plugin]:
        """Return the plugin class for a given name."""
        return REGISTRY[name]

    def get_plugin(self, name: str) -> Plugin:
        """Return the configured plugin for a given name."""
        if name not in self._plugins:
            self._plugins[name] = self.get_plugin_class(name)(**self._config.plugins[name].settings)
        return self._plugins[name]

    def get_enabled_plugins(self) -> list[Plugin]:
        """Return a list of enabled plugins."""
        return [
            self.get_plugin(name) for name, config in self._config.plugins.items() if config.enabled
        ]

    def get_plugins_with_capability(
        self, capability: type[HasPluginCapability]
    ) -> list[HasPluginCapability]:
        """Return a list of plugins that have the given capability."""
        return [plugin for plugin in self.get_enabled_plugins() if isinstance(plugin, capability)]

    def __iter__(self) -> Iterator[Plugin]:
        """Iterate over all enabled plugins."""
        return iter(self.get_enabled_plugins())

    @classproperty
    def default_config(cls) -> Config:
        cfg = Config()
        for p, plugin_cls in REGISTRY.items():
            cfg.plugins[p] = PluginConfig(enabled=True, settings=plugin_cls.default_plugin_settings)
        return cfg
