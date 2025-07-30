"""Azure Application Insights service for telemetry tracking."""

from __future__ import annotations

import asyncio
from typing import Dict, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

# Optional Azure dependencies - handle gracefully if not available
try:
    from azure.monitor.opentelemetry import configure_azure_monitor  # type: ignore

    azure_monitor_available = True
except ImportError:
    azure_monitor_available = False
    configure_azure_monitor = None  # type: ignore

try:
    from opentelemetry import trace, metrics  # type: ignore
    from opentelemetry.trace import Status, StatusCode  # type: ignore

    opentelemetry_available = True
except ImportError:
    opentelemetry_available = False
    trace = None  # type: ignore
    metrics = None  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore


class ApplicationInsightsService:
    """Service for tracking telemetry with Azure Application Insights."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        feature_manager: Optional[Any] = None,
    ):
        """
        Initialize the Application Insights service.

        Args:
            connection_string: Azure Application Insights connection string
            feature_manager: Feature manager for feature flags (optional)
        """
        self.service_identifier = "unknownService"
        self.feature_manager = feature_manager
        self.enabled = False
        self.tracer: Optional[Any] = None
        self.meter: Optional[Any] = None

        if connection_string and azure_monitor_available and opentelemetry_available:
            try:
                configure_azure_monitor(connection_string=connection_string)  # type: ignore
                self.tracer = trace.get_tracer(__name__)  # type: ignore
                self.meter = metrics.get_meter(__name__)  # type: ignore
                self.enabled = True
            except Exception:
                # Failed to configure, fall back to disabled state
                self.enabled = False

        # Always create a tracer for consistency, even if disabled
        if not self.tracer and opentelemetry_available:
            try:
                self.tracer = trace.get_tracer(__name__)  # type: ignore
            except Exception:
                pass

    def set_service(self, service_name: str) -> None:
        """Set the service identifier."""
        self.service_identifier = service_name

    def _extract_authorization_context(
        self, authorization_context: Optional[AuthorizationContext]
    ) -> Dict[str, str]:
        """Extract all properties from AuthorizationContext into a map."""
        if not authorization_context:
            return {}

        return {
            "service": self.service_identifier,
            "userId": authorization_context.id,
            "requestTime": str(authorization_context.request_time),
            "ipAddress": authorization_context.ip_address,
            "clientRequestId": authorization_context.client_request_id,
            "accountId": authorization_context.account_id,
            # Note: Protobuf enum .name attributes would need runtime import handling
            # "roles": ",".join([role.name for role in authorization_context.roles]),
            # "actor": authorization_context.actor.name,
            # "device": authorization_context.device.name,
            # "location": authorization_context.location.name,
            # "userAgent": authorization_context.user_agent.name,
            # "tier": authorization_context.tier.name,
        }

    async def _fetch_feature_flags(self) -> Dict[str, str]:
        """Fetch feature flags asynchronously."""
        if not self.feature_manager:
            return {}

        try:
            # Simulate async feature flag fetching
            # In real implementation, this would use the actual feature manager
            await asyncio.sleep(0)  # Placeholder for async operation
            return {}  # Return empty dict for now
        except Exception:
            return {}

    def _merge_properties(
        self,
        authorization_context: Optional[AuthorizationContext],
        properties: Optional[Dict[str, str]],
    ) -> Dict[str, str]:
        """Merge properties and AuthorizationContext details, and add feature flags."""
        context_properties = self._extract_authorization_context(authorization_context)

        # For now, skip async feature flags in sync context
        # In a real implementation, you might want to make this async or cache flags
        feature_flags: Dict[str, str] = {}

        combined_properties: Dict[str, str] = {**context_properties, **feature_flags}
        if properties:
            combined_properties.update(properties)

        return combined_properties

    def track_event(
        self,
        event_name: str,
        authorization_context: Optional[AuthorizationContext] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track a custom event."""
        if not self.enabled or not self.tracer or not opentelemetry_available:
            return

        merged_properties = self._merge_properties(authorization_context, properties)

        with self.tracer.start_span(event_name) as span:
            for key, value in merged_properties.items():
                span.set_attribute(key, value)
            span.set_status(Status(StatusCode.OK))  # type: ignore

    def track_exception(
        self,
        exception: Exception,
        authorization_context: Optional[AuthorizationContext] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track an exception."""
        if not self.enabled or not self.tracer or not opentelemetry_available:
            return

        merged_properties = self._merge_properties(authorization_context, properties)

        with self.tracer.start_span("exception") as span:
            span.set_attribute("exception.type", type(exception).__name__)
            span.set_attribute("exception.message", str(exception))
            for key, value in merged_properties.items():
                span.set_attribute(key, value)
            span.set_status(Status(StatusCode.ERROR))  # type: ignore

    def track_trace(
        self,
        message: str,
        severity_level: str = "INFO",
        authorization_context: Optional[AuthorizationContext] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track a trace message."""
        if not self.enabled or not self.tracer or not opentelemetry_available:
            return

        merged_properties = self._merge_properties(authorization_context, properties)

        with self.tracer.start_span("trace") as span:
            span.set_attribute("message", message)
            span.set_attribute("severity", severity_level)
            for key, value in merged_properties.items():
                span.set_attribute(key, value)
            span.set_status(Status(StatusCode.OK))  # type: ignore

    def track_request(
        self,
        request_name: str,
        duration_millis: int,
        response_code: str,
        success: bool,
        authorization_context: Optional[AuthorizationContext] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track a request."""
        if not self.enabled or not self.tracer or not opentelemetry_available:
            return

        merged_properties = self._merge_properties(authorization_context, properties)

        with self.tracer.start_span(request_name) as span:
            span.set_attribute(
                "http.url",
                f"https://{self.service_identifier}.apexnova.vc/{request_name}",
            )
            span.set_attribute("http.status_code", response_code)
            span.set_attribute("duration_ms", duration_millis)
            span.set_attribute("success", success)

            for key, value in merged_properties.items():
                span.set_attribute(key, value)

            status = Status(StatusCode.OK) if success else Status(StatusCode.ERROR)  # type: ignore
            span.set_status(status)
