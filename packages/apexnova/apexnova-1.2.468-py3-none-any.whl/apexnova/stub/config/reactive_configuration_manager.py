"""
Reactive configuration management with hot reloading and type safety.
"""

import asyncio
import os
import sys
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Generic,
    Callable,
    Union,
    Set,
    AsyncIterator,
    cast,
)
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigurationSource(ABC):
    """Abstract configuration source."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get configuration value by key."""
        pass

    @abstractmethod
    async def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get source priority (higher = more important)."""
        pass

    @abstractmethod
    async def reload(self) -> None:
        """Reload configuration from source."""
        pass


@dataclass
class ConfigurationProperty(Generic[T]):
    """
    Reactive configuration property that updates automatically.
    """

    key: str
    default_value: T
    converter: Callable[[str], T]
    validator: Optional[Callable[[T], bool]] = None
    description: str = ""
    _value: T = field(init=False, repr=False)
    _listeners: List[Callable[[T], None]] = field(
        default_factory=list, init=False, repr=False
    )
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def __post_init__(self):
        """Initialize value."""
        self._value = self.default_value

    @property
    def value(self) -> T:
        """Get current value."""
        with self._lock:
            return self._value

    def set_value(self, raw_value: Optional[str]) -> None:
        """Set value from raw string."""
        with self._lock:
            if raw_value is None:
                new_value = self.default_value
            else:
                try:
                    new_value = self.converter(raw_value)
                    if self.validator and not self.validator(new_value):
                        logger.warning(
                            f"Validation failed for {self.key}={raw_value}, using default"
                        )
                        new_value = self.default_value
                except Exception as e:
                    logger.error(
                        f"Error converting {self.key}={raw_value}: {e}, using default"
                    )
                    new_value = self.default_value

            if new_value != self._value:
                old_value = self._value
                self._value = new_value

                # Notify listeners
                for listener in self._listeners:
                    try:
                        listener(new_value)
                    except Exception as e:
                        logger.error(
                            f"Error in configuration listener for {self.key}: {e}"
                        )

    def add_listener(self, listener: Callable[[T], None]) -> None:
        """Add value change listener."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[T], None]) -> None:
        """Remove value change listener."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)


class ReactiveConfigurationManager:
    """
    Reactive configuration manager with hot reloading and type safety.
    """

    def __init__(
        self,
        sources: Optional[List[ConfigurationSource]] = None,
        refresh_interval: timedelta = timedelta(seconds=30),
    ):
        """
        Initialize configuration manager.

        Args:
            sources: List of configuration sources
            refresh_interval: Auto-refresh interval
        """
        self.sources = sorted(
            sources or [], key=lambda s: s.get_priority(), reverse=True
        )
        self.refresh_interval = refresh_interval
        self.properties: Dict[str, ConfigurationProperty] = {}
        self._converters: Dict[Type, Callable[[str], Any]] = self._default_converters()
        self._running = False
        self._refresh_task: Optional[asyncio.Task] = None
        self._change_listeners: List[Callable[[str, Any, Any], None]] = []
        self._lock = asyncio.Lock()

    def _default_converters(self) -> Dict[Type, Callable[[str], Any]]:
        """Get default type converters."""
        return {
            str: lambda x: x,
            int: int,
            float: float,
            bool: lambda x: x.lower() in ("true", "1", "yes", "on"),
            timedelta: lambda x: timedelta(seconds=float(x)),
            List[str]: lambda x: [s.strip() for s in x.split(",") if s.strip()],
            List[int]: lambda x: [int(s.strip()) for s in x.split(",") if s.strip()],
            Dict[str, str]: json.loads,
        }

    def register_converter(self, type_: Type[T], converter: Callable[[str], T]) -> None:
        """Register custom type converter."""
        self._converters[type_] = converter

    def get_converter(self, type_: Type[T]) -> Callable[[str], T]:
        """Get converter for type."""
        if type_ in self._converters:
            return self._converters[type_]

        # Check for enum types
        if isinstance(type_, type) and issubclass(type_, Enum):
            return lambda x: type_[x.upper()]

        # Default to string
        return lambda x: cast(T, x)

    def register_property(
        self,
        key: str,
        type_: Type[T],
        default_value: T,
        validator: Optional[Callable[[T], bool]] = None,
        description: str = "",
    ) -> ConfigurationProperty[T]:
        """
        Register a configuration property.

        Args:
            key: Property key
            type_: Property type
            default_value: Default value
            validator: Optional validator function
            description: Property description

        Returns:
            Configuration property
        """
        converter = self.get_converter(type_)
        prop = ConfigurationProperty(
            key=key,
            default_value=default_value,
            converter=converter,
            validator=validator,
            description=description,
        )

        self.properties[key] = prop
        return prop

    def get_property(self, key: str) -> Optional[ConfigurationProperty]:
        """Get configuration property by key."""
        return self.properties.get(key)

    async def get_raw(self, key: str) -> Optional[str]:
        """Get raw configuration value."""
        for source in self.sources:
            value = await source.get(key)
            if value is not None:
                return value
        return None

    async def get(self, key: str, type_: Type[T], default: T) -> T:
        """
        Get typed configuration value.

        Args:
            key: Configuration key
            type_: Expected type
            default: Default value

        Returns:
            Configuration value
        """
        raw_value = await self.get_raw(key)
        if raw_value is None:
            return default

        try:
            converter = self.get_converter(type_)
            return converter(raw_value)
        except Exception as e:
            logger.error(f"Error converting {key}={raw_value} to {type_}: {e}")
            return default

    async def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        result = {}

        # Merge from all sources (lower priority first)
        for source in reversed(self.sources):
            values = await source.get_all()
            result.update(values)

        return result

    async def reload(self) -> None:
        """Reload configuration from all sources."""
        async with self._lock:
            # Reload all sources
            for source in self.sources:
                try:
                    await source.reload()
                except Exception as e:
                    logger.error(
                        f"Error reloading source {source.__class__.__name__}: {e}"
                    )

            # Update all registered properties
            for key, prop in self.properties.items():
                raw_value = await self.get_raw(key)
                old_value = prop.value
                prop.set_value(raw_value)

                # Notify change listeners if value changed
                if prop.value != old_value:
                    for listener in self._change_listeners:
                        try:
                            listener(key, old_value, prop.value)
                        except Exception as e:
                            logger.error(f"Error in change listener: {e}")

    async def start(self) -> None:
        """Start auto-refresh."""
        if self._running:
            return

        self._running = True
        await self.reload()  # Initial load

        async def refresh_loop():
            while self._running:
                await asyncio.sleep(self.refresh_interval.total_seconds())
                if self._running:
                    await self.reload()

        self._refresh_task = asyncio.create_task(refresh_loop())

    async def stop(self) -> None:
        """Stop auto-refresh."""
        self._running = False
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass

    def add_change_listener(self, listener: Callable[[str, Any, Any], None]) -> None:
        """Add configuration change listener."""
        self._change_listeners.append(listener)

    def remove_change_listener(self, listener: Callable[[str, Any, Any], None]) -> None:
        """Remove configuration change listener."""
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)

    async def change_stream(self) -> AsyncIterator[tuple[str, Any, Any]]:
        """
        Stream configuration changes.

        Yields:
            Tuples of (key, old_value, new_value)
        """
        queue: asyncio.Queue[tuple[str, Any, Any]] = asyncio.Queue()

        def listener(key: str, old_value: Any, new_value: Any):
            asyncio.create_task(queue.put((key, old_value, new_value)))

        self.add_change_listener(listener)

        try:
            while True:
                yield await queue.get()
        finally:
            self.remove_change_listener(listener)


class InMemoryConfigurationSource(ConfigurationSource):
    """In-memory configuration source."""

    def __init__(self, values: Optional[Dict[str, str]] = None, priority: int = 0):
        """
        Initialize in-memory source.

        Args:
            values: Initial configuration values
            priority: Source priority
        """
        self.values = values or {}
        self.priority = priority
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        async with self._lock:
            return self.values.get(key)

    async def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        async with self._lock:
            return self.values.copy()

    def get_priority(self) -> int:
        """Get source priority."""
        return self.priority

    async def reload(self) -> None:
        """Reload configuration (no-op for in-memory)."""
        pass

    async def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        async with self._lock:
            self.values[key] = value

    async def update(self, values: Dict[str, str]) -> None:
        """Update multiple values."""
        async with self._lock:
            self.values.update(values)

    async def delete(self, key: str) -> None:
        """Delete configuration value."""
        async with self._lock:
            self.values.pop(key, None)


class EnvironmentConfigurationSource(ConfigurationSource):
    """Environment variables configuration source."""

    def __init__(self, prefix: str = "", priority: int = 100):
        """
        Initialize environment source.

        Args:
            prefix: Environment variable prefix
            priority: Source priority
        """
        self.prefix = prefix
        self.priority = priority
        self._cache: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        async with self._lock:
            env_key = f"{self.prefix}{key}".upper().replace(".", "_")
            return os.environ.get(env_key)

    async def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        async with self._lock:
            result = {}
            prefix_len = len(self.prefix)

            for env_key, value in os.environ.items():
                if env_key.startswith(self.prefix):
                    # Convert back to configuration key format
                    config_key = env_key[prefix_len:].lower().replace("_", ".")
                    result[config_key] = value

            return result

    def get_priority(self) -> int:
        """Get source priority."""
        return self.priority

    async def reload(self) -> None:
        """Reload configuration from environment."""
        async with self._lock:
            self._cache = await self.get_all()


class SystemPropertiesConfigurationSource(ConfigurationSource):
    """System properties configuration source (for Python, uses sys module)."""

    def __init__(self, priority: int = 50):
        """
        Initialize system properties source.

        Args:
            priority: Source priority
        """
        self.priority = priority
        self._properties: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        async with self._lock:
            # Check custom properties first
            if key in self._properties:
                return self._properties[key]

            # Check sys attributes
            attr_name = key.replace(".", "_")
            return getattr(sys, attr_name, None)

    async def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        async with self._lock:
            result = self._properties.copy()

            # Add relevant sys attributes
            for attr in dir(sys):
                if not attr.startswith("_") and isinstance(
                    getattr(sys, attr, None), str
                ):
                    key = attr.replace("_", ".")
                    result[key] = getattr(sys, attr)

            return result

    def get_priority(self) -> int:
        """Get source priority."""
        return self.priority

    async def reload(self) -> None:
        """Reload configuration."""
        pass

    async def set_property(self, key: str, value: str) -> None:
        """Set a system property."""
        async with self._lock:
            self._properties[key] = value


@dataclass
class ConfigProperty:
    """Configuration property annotation."""

    key: str
    default: Any = None
    type_: Optional[Type] = None
    validator: Optional[Callable[[Any], bool]] = None
    description: str = ""


class ConfigurationBuilder:
    """Builder for creating reactive configuration."""

    def __init__(self):
        """Initialize builder."""
        self.sources: List[ConfigurationSource] = []
        self.refresh_interval = timedelta(seconds=30)
        self.properties: List[tuple[str, Type, Any, Optional[Callable], str]] = []

    def with_source(self, source: ConfigurationSource) -> "ConfigurationBuilder":
        """Add configuration source."""
        self.sources.append(source)
        return self

    def with_environment(
        self, prefix: str = "", priority: int = 100
    ) -> "ConfigurationBuilder":
        """Add environment configuration source."""
        self.sources.append(EnvironmentConfigurationSource(prefix, priority))
        return self

    def with_system_properties(self, priority: int = 50) -> "ConfigurationBuilder":
        """Add system properties source."""
        self.sources.append(SystemPropertiesConfigurationSource(priority))
        return self

    def with_refresh_interval(self, interval: timedelta) -> "ConfigurationBuilder":
        """Set refresh interval."""
        self.refresh_interval = interval
        return self

    def with_property(
        self,
        key: str,
        type_: Type[T],
        default: T,
        validator: Optional[Callable[[T], bool]] = None,
        description: str = "",
    ) -> "ConfigurationBuilder":
        """Add configuration property."""
        self.properties.append((key, type_, default, validator, description))
        return self

    def build(self) -> ReactiveConfigurationManager:
        """Build configuration manager."""
        manager = ReactiveConfigurationManager(self.sources, self.refresh_interval)

        # Register all properties
        for key, type_, default, validator, description in self.properties:
            manager.register_property(key, type_, default, validator, description)

        return manager


# Configuration DSL example
def create_configuration() -> ReactiveConfigurationManager:
    """Create configuration with DSL."""
    return (
        ConfigurationBuilder()
        .with_environment("APEXNOVA_")
        .with_system_properties()
        .with_refresh_interval(timedelta(minutes=1))
        .with_property("database.host", str, "localhost", description="Database host")
        .with_property(
            "database.port", int, 5432, lambda x: 1 <= x <= 65535, "Database port"
        )
        .with_property("cache.enabled", bool, True, description="Enable caching")
        .with_property(
            "cache.ttl", timedelta, timedelta(minutes=5), description="Cache TTL"
        )
        .build()
    )
