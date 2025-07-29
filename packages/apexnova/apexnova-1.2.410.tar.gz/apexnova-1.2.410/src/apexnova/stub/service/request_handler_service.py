"""Request handler service for gRPC operations."""

from __future__ import annotations

import time
from typing import TypeVar, Callable, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext
    from apexnova.stub.response_pb2 import ResponseStatus

from .application_insights_service import ApplicationInsightsService
from ..feature.context.feature_targeting_context import FeatureTargetingContext

T = TypeVar("T")
R = TypeVar("R")


class RequestHandlerService:
    """Service for handling gRPC requests with telemetry and feature context."""

    def __init__(
        self,
        application_insights_service: ApplicationInsightsService,
        feature_targeting_context_accessor: Optional[Any] = None,
    ):
        """
        Initialize the request handler service.

        Args:
            application_insights_service: Service for tracking telemetry
            feature_targeting_context_accessor: Accessor for feature targeting context
        """
        self.application_insights_service = application_insights_service
        self.feature_targeting_context_accessor = feature_targeting_context_accessor

    def handle_request_with_context(
        self,
        authorization_context: "AuthorizationContext",
        service_call: Callable[[T, Any], None],
        request: T,
        response_observer: Any,
    ) -> None:
        """
        Handle a gRPC request with authorization context and telemetry.

        Args:
            authorization_context: The authorization context
            service_call: The service method to call
            request: The request object
            response_observer: The response observer
        """
        start_time = time.time()

        try:
            # Set the targeting context for this thread/request
            if self.feature_targeting_context_accessor:
                targeting_context = FeatureTargetingContext(authorization_context)
                self.feature_targeting_context_accessor.set_local_context(
                    targeting_context
                )

            # Call the service method
            service_call(request, response_observer)

            # Track successful request
            duration_ms = int((time.time() - start_time) * 1000)
            request_name = type(request).__name__ if request else "UnknownRequest"

            self.application_insights_service.track_request(
                request_name=request_name,
                duration_millis=duration_ms,
                response_code="200",
                success=True,
                authorization_context=authorization_context,
            )

        except Exception as exception:
            # Track failed request
            duration_ms = int((time.time() - start_time) * 1000)
            request_name = type(request).__name__ if request else "UnknownRequest"

            self.application_insights_service.track_request(
                request_name=request_name,
                duration_millis=duration_ms,
                response_code="500",
                success=False,
                authorization_context=authorization_context,
            )

            # Handle the exception
            self.handle_exception(exception, request_name, authorization_context)

        finally:
            # Clear the targeting context
            if self.feature_targeting_context_accessor:
                self.feature_targeting_context_accessor.clear_targeting_context()

            # Complete the response
            if hasattr(response_observer, "on_completed"):
                response_observer.on_completed()

    def handle_exception(
        self,
        exception: Exception,
        operation: str,
        authorization_context: Optional["AuthorizationContext"] = None,
    ) -> Optional["ResponseStatus"]:
        """
        Handle an exception by logging it and returning appropriate response status.

        Args:
            exception: The exception that occurred
            operation: The operation name where the exception occurred
            authorization_context: Optional authorization context

        Returns:
            ResponseStatus corresponding to the exception type
        """
        # Track the exception with additional properties
        exception_type = type(exception).__name__
        properties = {"operation": operation, "typeName": exception_type}

        # Send the exception to Application Insights
        self.application_insights_service.track_exception(
            exception=exception,
            authorization_context=authorization_context,
            properties=properties,
        )

        # Return appropriate response status
        return self.get_response_status(exception)

    def get_response_status(self, exception: Exception) -> Optional["ResponseStatus"]:
        """
        Get the appropriate response status for an exception.

        Args:
            exception: The exception to map to a response status

        Returns:
            ResponseStatus corresponding to the exception type
        """
        # Note: ResponseStatus enum usage would need runtime import handling
        # For now, returning None as placeholder
        if isinstance(exception, PermissionError):
            return None  # ResponseStatus.RESPONSE_STATUS_PERMISSION_DENIED
        elif isinstance(exception, ValueError):
            return None  # ResponseStatus.RESPONSE_STATUS_INVALID_ARGUMENT
        elif isinstance(exception, AttributeError):
            return None  # ResponseStatus.RESPONSE_STATUS_BAD_REQUEST
        elif isinstance(exception, KeyError) or isinstance(exception, LookupError):
            return None  # ResponseStatus.RESPONSE_STATUS_NOT_FOUND
        elif isinstance(exception, RuntimeError):
            return None  # ResponseStatus.RESPONSE_STATUS_INTERNAL_ERROR
        else:
            return None  # ResponseStatus.RESPONSE_STATUS_UNKNOWN
