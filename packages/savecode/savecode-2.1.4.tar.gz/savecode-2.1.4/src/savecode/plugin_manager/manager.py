"""
savecode/plugin_manager/manager.py - Plugin Manager for savecode.

Encapsulates plugin registration, execution, and management of plugin ordering and isolation.
"""

import logging
from typing import Any, Dict, List, Tuple, Type, Callable, TypeVar

# Define a TypeVar for plugins
T = TypeVar("T")

logger = logging.getLogger(__name__)


class PluginManager:
    """Encapsulates the registry and execution of plugins."""

    def __init__(self) -> None:
        self.registry: List[Tuple[int, Type[Any]]] = []

    def register_plugin(self, plugin_class: Type[T], order: int = 100) -> Type[T]:
        """Register a plugin class with an optional execution order.

        Args:
            plugin_class (Type[T]): The plugin class to register.
            order (int, optional): The execution order; lower values run earlier. Defaults to 100.

        Returns:
            Type[T]: The registered plugin class.
        """
        self.registry.append((order, plugin_class))
        return plugin_class

    def run_plugins(self, context: Dict[str, Any]) -> None:
        """Instantiate and run all registered plugins in sequence.

        Args:
            context (Dict[str, Any]): Dictionary containing the shared context and data.

        Returns:
            None
        """
        # Auto-import built-in plugins if nobody did so yet
        if not self.registry:
            try:
                import savecode.plugins  # noqa: F401  (side-effect registration)
            except ImportError:  # pragma: no cover
                pass

        sorted_plugins = sorted(self.registry, key=lambda item: item[0])
        for _, plugin_class in sorted_plugins:
            plugin_instance = plugin_class()  # Delayed instantiation.
            try:
                plugin_instance.run(context)
            except Exception as e:
                logger.error(
                    "Error running plugin %s: %s",
                    plugin_class.__name__,
                    e,
                    exc_info=True,
                )

    def list_plugins(self) -> List[str]:
        """List the names of all registered plugin classes in order of execution.

        Returns:
            List[str]: A list of plugin class names.
        """
        sorted_plugins = sorted(self.registry, key=lambda item: item[0])
        return [cls.__name__ for _, cls in sorted_plugins]

    def clear_registry(self) -> None:
        """Clear the plugin registry to ensure test isolation.

        Returns:
            None
        """
        self.registry.clear()


# Create a global instance of PluginManager.
plugin_manager = PluginManager()


def register_plugin(*args: Any, order: int = 100) -> Callable[[Type[T]], Type[T]]:
    """Decorator to register a plugin class with an optional execution order.

    Can be used as:
        @register_plugin
        class MyPlugin:
            ...
    or:
        @register_plugin(order=10)
        class MyPlugin:
            ...

    Args:
        order (int, optional): Execution order; lower values run earlier. Defaults to 100.

    Returns:
        Callable[[Type[T]], Type[T]]: A decorator that registers the plugin class.
    """
    if args and len(args) == 1 and callable(args[0]):
        cls = args[0]
        return plugin_manager.register_plugin(cls, order=order)

    def decorator(cls: Type[T]) -> Type[T]:
        return plugin_manager.register_plugin(cls, order=order)

    return decorator


def run_plugins(context: Dict[str, Any]) -> None:
    """Run all registered plugins using the global PluginManager instance.

    Args:
        context (Dict[str, Any]): Shared context dictionary.

    Returns:
        None
    """
    plugin_manager.run_plugins(context)


def list_plugins() -> List[str]:
    """List the names of all registered plugin classes in execution order.

    Returns:
        List[str]: List of plugin class names.
    """
    return plugin_manager.list_plugins()


def clear_registry() -> None:
    """Clear the global plugin registry to ensure test isolation.

    Returns:
        None
    """
    plugin_manager.clear_registry()
