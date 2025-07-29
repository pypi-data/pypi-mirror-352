from __future__ import annotations

import traceback
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Protocol, TypeGuard, TypeVar, cast

# Optional pydantic integration
try:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema, core_schema

    _PYDANTIC_AVAILABLE = True
except ImportError:
    _PYDANTIC_AVAILABLE = False

# Type stubs for when pydantic is not available
if TYPE_CHECKING and not _PYDANTIC_AVAILABLE:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema

T = TypeVar("T")
U = TypeVar("U")

type Extra = dict[str, Any] | None


class Result[T]:
    """
    A container representing either a successful result or an error.
    Use `Result.ok()` or `Result.err()` to create instances.

    The optional `extra` field allows attaching arbitrary additional data:
    - HTTP response details, status codes, headers
    - Performance metrics like response times
    - Infrastructure info like proxy servers used
    - Retry attempts, circuit breaker states
    - User context, request metadata
    - Any other information relevant to your use case
    """

    value: T | None  # Success value, if any
    error: str | None  # Error message, if any
    extra: Extra  # Optional additional data for any purpose

    def __init__(self) -> None:
        raise RuntimeError("Result is not intended to be instantiated directly. Use the static methods instead.")

    def is_ok(self) -> bool:
        """
        Returns True if the result represents success.
        """
        return self.error is None

    def is_err(self) -> bool:
        """
        Returns True if the result represents an error.
        """
        return self.error is not None

    def unwrap(self, message_prefix: str | None = None, include_error: bool = True) -> T:
        """
        Returns the success value if the Result is Ok, otherwise raises a RuntimeError.

        Args:
            message_prefix: Optional custom prefix for the error message if the Result is an error.
                            If not provided, a default message will be used.
            include_error: If True, appends the internal error message from the Result to the final exception message.

        Raises:
            RuntimeError: If the Result is an error.

        Returns:
            The success value of type T.
        """
        if not self.is_ok():
            # Use the provided message or a default fallback
            error_message = message_prefix or "Called unwrap() on a failure value"
            # Optionally append the error detail
            if include_error:
                error_message = f"{error_message}: {self.error}"
            # Raise with the final constructed message
            raise RuntimeError(error_message)
        # Return the success value if present
        return cast(T, self.value)

    def unwrap_or(self, default: T) -> T:
        """
        Returns the success value if available, otherwise returns the given default.
        """
        if not self.is_ok():
            return default
        return cast(T, self.value)

    def expect_error(self) -> str:
        """
        Returns the error message.
        Raises RuntimeError if the result is a success.
        """
        if self.is_ok():
            raise RuntimeError("Called expect_error() on a success value")
        return cast(str, self.error)

    def value_or_error(self) -> T | str:
        """
        Returns the success value if available, otherwise returns the error message.
        """
        if self.is_ok():
            return self.unwrap()
        return self.expect_error()

    def to_dict(self) -> dict[str, object]:
        """
        Returns a dictionary representation of the result.
        Note: the error is converted to a string if present.
        """
        return {
            "value": self.value,
            "error": self.error,
            "extra": self.extra,
        }

    def with_value(self, value: U) -> Result[U]:
        """
        Returns a copy of this Result with the success value replaced by `value`.
        The `extra` metadata is preserved.
        """
        return Result.ok(value, self.extra)

    def with_error(self, error: str | Exception | tuple[str, Exception]) -> Result[T]:
        """
        Returns a copy of this Result as an Err with the given `error`.
        Preserves existing `extra` metadata.
        """
        return Result.err(error, self.extra)

    def map(self, fn: Callable[[T], U]) -> Result[U]:
        if self.is_ok():
            try:
                new_value = fn(cast(T, self.value))
                return Result.ok(new_value, extra=self.extra)
            except Exception as e:
                return Result.err(("map_exception", e), extra=self.extra)
        return cast(Result[U], self)

    async def map_async(self, fn: Callable[[T], Awaitable[U]]) -> Result[U]:
        if self.is_ok():
            try:
                new_value = await fn(cast(T, self.value))
                return Result.ok(new_value, extra=self.extra)
            except Exception as e:
                return Result.err(("map_exception", e), extra=self.extra)
        return cast(Result[U], self)

    def and_then(self, fn: Callable[[T], Result[U]]) -> Result[U]:
        if self.is_ok():
            try:
                return fn(cast(T, self.value))
            except Exception as e:
                return Result.err(("and_then_exception", e), extra=self.extra)
        return cast(Result[U], self)

    async def and_then_async(self, fn: Callable[[T], Awaitable[Result[U]]]) -> Result[U]:
        if self.is_ok():
            try:
                return await fn(cast(T, self.value))
            except Exception as e:
                return Result.err(("and_then_exception", e), extra=self.extra)
        return cast(Result[U], self)

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.is_ok():
            parts.append(f"value={self.value!r}")
        if self.error is not None:
            parts.append(f"error={self.error!r}")
        if self.extra is not None:
            parts.append(f"extra={self.extra!r}")
        return f"Result({', '.join(parts)})"

    def __hash__(self) -> int:
        return hash(
            (
                self.value,
                self.error,
                frozenset(self.extra.items()) if self.extra else None,
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False
        return self.value == other.value and self.error == other.error and self.extra == other.extra

    def __bool__(self) -> bool:
        """
        Returns True if the Result is Ok, False if it's an error.
        This allows using Result in boolean contexts: `if result:` is equivalent to `if result.is_ok():`
        """
        return self.is_ok()

    @classmethod
    def _create(cls, value: T | None, error: str | None, extra: Extra) -> Result[T]:
        obj = object.__new__(cls)
        obj.value = value
        obj.error = error
        obj.extra = extra
        return obj

    @staticmethod
    def ok(value: T, extra: Extra = None) -> Result[T]:
        """
        Creates a successful Result instance.

        Args:
            value: The success value to store in the Result.
            extra: Optional additional data for any purpose. Examples:
                   {"response_time_ms": 150, "status_code": 200, "proxy": "proxy1.com"}
                   {"attempt": 3, "cache_hit": True}
                   {"user_id": "123", "request_id": "abc-def"}

        Returns:
            A Result instance representing success with the provided value.
        """
        return Result._create(value=value, error=None, extra=extra)

    @staticmethod
    def err(error: str | Exception | tuple[str, Exception], extra: Extra = None) -> Result[T]:
        """
        Creates a Result instance representing a failure.

        Args:
            error: The error information, which can be:
                - A string error message
                - An Exception object (stored as error message + in extra["exception"])
                - A tuple containing (error_message, exception)
            extra: Optional additional data for any purpose. Examples:
                   {"response_time_ms": 5000, "status_code": 500, "retry_count": 3}
                   {"proxy": "proxy2.com", "timeout_ms": 30000}
                   {"circuit_breaker": "open", "last_success": "2024-01-01T10:00:00Z"}

        Returns:
            A Result instance representing failure with the provided error information.
        """
        final_extra = extra.copy() if extra else {}

        if isinstance(error, tuple):
            error_msg, exception = error
            # Only add exception if user didn't provide one
            if "exception" not in final_extra:
                final_extra["exception"] = exception
            # Add traceback if available
            if "traceback" not in final_extra and hasattr(exception, "__traceback__") and exception.__traceback__:
                final_extra["traceback"] = "".join(traceback.format_tb(exception.__traceback__))
        elif isinstance(error, Exception):
            error_msg = f"{type(error).__name__}: {error}"
            # Only add exception if user didn't provide one
            if "exception" not in final_extra:
                final_extra["exception"] = error
            # Add traceback if available
            if "traceback" not in final_extra and hasattr(error, "__traceback__") and error.__traceback__:
                final_extra["traceback"] = "".join(traceback.format_tb(error.__traceback__))
        else:
            error_msg = error

        return Result._create(value=None, error=error_msg, extra=final_extra or None)

    if _PYDANTIC_AVAILABLE:

        @classmethod
        def __get_pydantic_core_schema__(cls, _source_type: type[Any], _handler: GetCoreSchemaHandler) -> CoreSchema:
            return core_schema.no_info_after_validator_function(
                cls._validate,
                core_schema.any_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.to_dict()),
            )

        @classmethod
        def _validate(cls, value: object) -> Result[Any]:
            if isinstance(value, cls):
                return value
            if isinstance(value, dict):
                return cls._create(
                    value=value.get("value"),
                    error=value.get("error"),
                    extra=value.get("extra"),
                )
            raise TypeError(f"Invalid value for Result: {value}")


class OkResult(Protocol[T]):
    value: T
    error: None


class ErrResult(Protocol[T]):  # type: ignore[misc]
    value: None
    error: str


def is_ok(res: Result[T]) -> TypeGuard[OkResult[T]]:
    return res.is_ok()


def is_err(res: Result[T]) -> TypeGuard[ErrResult[T]]:
    return res.is_err()
