"""
Result type for error handling without exceptions.

This module provides a Result type that represents either success or failure,
similar to Rust's Result type or Kotlin's Result type.
"""

from typing import TypeVar, Generic, Union, Callable, Optional, Any
from dataclasses import dataclass

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound=Exception)


@dataclass(frozen=True)
class Result(Generic[T]):
    """
    A type that represents either success or failure.

    This provides better error handling compared to throwing exceptions,
    allowing for more functional programming patterns.
    """

    @dataclass(frozen=True)
    class Success(Generic[T]):
        """Represents a successful result with a value."""

        value: T

        def __bool__(self) -> bool:
            return True

    @dataclass(frozen=True)
    class Failure:
        """Represents a failed result with an exception and optional message."""

        exception: Exception
        message: Optional[str] = None

        def __bool__(self) -> bool:
            return False

    def __init__(self, result: Union[Success[T], Failure]):
        """Initialize with either Success or Failure."""
        object.__setattr__(self, "_result", result)

    @property
    def _result(self) -> Union[Success[T], Failure]:
        """Internal result storage."""
        return object.__getattribute__(self, "_result")

    def is_success(self) -> bool:
        """Check if result is successful."""
        return isinstance(self._result, Result.Success)

    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return isinstance(self._result, Result.Failure)

    def map(self, transform: Callable[[T], U]) -> "Result[U]":
        """Transform the success value if present."""
        if self.is_success():
            try:
                return Result.success(transform(self._result.value))
            except Exception as e:
                return Result.failure(e)
        else:
            return Result(self._result)

    def flat_map(self, transform: Callable[[T], "Result[U]"]) -> "Result[U]":
        """Transform the success value and flatten the result."""
        if self.is_success():
            try:
                return transform(self._result.value)
            except Exception as e:
                return Result.failure(e)
        else:
            return Result(self._result)

    def on_success(self, action: Callable[[T], None]) -> "Result[T]":
        """Execute action on success value."""
        if self.is_success():
            try:
                action(self._result.value)
            except Exception:
                pass  # Ignore exceptions in side effects
        return self

    def on_failure(self, action: Callable[[Exception], None]) -> "Result[T]":
        """Execute action on failure exception."""
        if self.is_failure():
            try:
                action(self._result.exception)
            except Exception:
                pass  # Ignore exceptions in side effects
        return self

    def get_or_none(self) -> Optional[T]:
        """Get the value if success, None if failure."""
        if self.is_success():
            return self._result.value
        return None

    def get_or_throw(self) -> T:
        """Get the value if success, raise exception if failure."""
        if self.is_success():
            return self._result.value
        else:
            raise self._result.exception

    def get_or_else(self, default_value: T) -> T:
        """Get the value if success, default value if failure."""
        if self.is_success():
            return self._result.value
        return default_value

    def get_or_else_lazy(self, default_supplier: Callable[[], T]) -> T:
        """Get the value if success, computed default if failure."""
        if self.is_success():
            return self._result.value
        return default_supplier()

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        """Create a successful result."""
        return cls(cls.Success(value))

    @classmethod
    def failure(
        cls, exception: Exception, message: Optional[str] = None
    ) -> "Result[Any]":
        """Create a failed result."""
        return cls(cls.Failure(exception, message))

    @classmethod
    def run_catching(cls, action: Callable[[], T]) -> "Result[T]":
        """Execute action and catch any exceptions."""
        try:
            return cls.success(action())
        except Exception as e:
            return cls.failure(e)

    @classmethod
    def of_nullable(
        cls, value: Optional[T], error_message: str = "Value is None"
    ) -> "Result[T]":
        """Create result from nullable value."""
        if value is not None:
            return cls.success(value)
        else:
            return cls.failure(ValueError(error_message))

    def __bool__(self) -> bool:
        """Result is truthy if successful."""
        return self.is_success()

    def __str__(self) -> str:
        """String representation of result."""
        if self.is_success():
            return f"Success({self._result.value})"
        else:
            return f"Failure({self._result.exception})"

    def __repr__(self) -> str:
        """Detailed representation of result."""
        return self.__str__()


# Convenience functions for common patterns
def success(value: T) -> Result[T]:
    """Create a successful result."""
    return Result.success(value)


def failure(exception: Exception, message: Optional[str] = None) -> Result[Any]:
    """Create a failed result."""
    return Result.failure(exception, message)


def run_catching(action: Callable[[], T]) -> Result[T]:
    """Execute action and catch any exceptions."""
    return Result.run_catching(action)


def of_nullable(value: Optional[T], error_message: str = "Value is None") -> Result[T]:
    """Create result from nullable value."""
    return Result.of_nullable(value, error_message)
