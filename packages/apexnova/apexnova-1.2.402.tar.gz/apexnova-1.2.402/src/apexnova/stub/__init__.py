"""ApexNova stub utilities for Python.

This package provides utility classes and services for working with ApexNova
protobuf definitions, including authorization, telemetry, and repository patterns.
"""

# Authorization components
from .authorization.authorization_status import AuthorizationStatus
from .authorization.authorization_rule import AuthorizationRule
from .authorization.model.base_authorization_model import BaseAuthorizationModel

# Services
from .service.application_insights_service import ApplicationInsightsService
from .service.request_handler_service import RequestHandlerService

# Models
from .model.base_model import IBaseModel
from .model.base_element import IBaseElement

# Feature management
from .feature.context.feature_targeting_context import FeatureTargetingContext

__version__ = "1.0.0"

__all__ = [
    # Authorization
    "AuthorizationStatus",
    "AuthorizationRule",
    "BaseAuthorizationModel",
    # Services
    "ApplicationInsightsService",
    "RequestHandlerService",
    # Models
    "IBaseModel",
    "IBaseElement",
    # Feature management
    "FeatureTargetingContext",
]
