"""
Enhanced application properties with comprehensive configuration management.
"""

import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RetryMode(Enum):
    """Retry mode for database operations."""

    EXPONENTIAL = "EXPONENTIAL"
    LINEAR = "LINEAR"
    FIXED = "FIXED"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    # Cosmos DB settings
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_database: str = "apexnova"
    cosmos_container: str = "entities"
    cosmos_consistency_level: str = "Session"
    cosmos_max_retry_attempts: int = 5
    cosmos_max_retry_wait_time: timedelta = field(
        default_factory=lambda: timedelta(seconds=30)
    )

    # Gremlin settings
    gremlin_endpoint: str = ""
    gremlin_key: str = ""
    gremlin_database: str = "apexnova"
    gremlin_collection: str = "graph"
    gremlin_port: int = 443
    gremlin_enable_ssl: bool = True
    gremlin_serializer: str = "GRAPHSON_V3"

    # Connection pool settings
    connection_pool_size: int = 10
    connection_pool_timeout: timedelta = field(
        default_factory=lambda: timedelta(seconds=30)
    )
    connection_idle_timeout: timedelta = field(
        default_factory=lambda: timedelta(minutes=5)
    )

    # Retry policy
    retry_mode: RetryMode = RetryMode.EXPONENTIAL
    retry_base_delay: timedelta = field(
        default_factory=lambda: timedelta(milliseconds=100)
    )
    retry_max_delay: timedelta = field(default_factory=lambda: timedelta(seconds=10))
    retry_jitter: bool = True

    def validate(self) -> List[str]:
        """Validate database configuration."""
        errors = []

        if not self.cosmos_endpoint and not self.gremlin_endpoint:
            errors.append("At least one database endpoint must be configured")

        if self.cosmos_endpoint and not self.cosmos_key:
            errors.append("Cosmos DB key is required when endpoint is configured")

        if self.gremlin_endpoint and not self.gremlin_key:
            errors.append("Gremlin key is required when endpoint is configured")

        if self.connection_pool_size < 1:
            errors.append("Connection pool size must be at least 1")

        if self.cosmos_max_retry_attempts < 0:
            errors.append("Max retry attempts cannot be negative")

        return errors


@dataclass
class AuthorizationConfig:
    """Authorization configuration settings."""

    # Cache settings
    cache_enabled: bool = True
    cache_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    cache_max_size: int = 10000
    cache_eviction_policy: str = "LRU"

    # Metrics settings
    metrics_enabled: bool = True
    metrics_collection_interval: timedelta = field(
        default_factory=lambda: timedelta(minutes=1)
    )
    metrics_percentiles: List[float] = field(default_factory=lambda: [0.5, 0.95, 0.99])

    # Batch processing
    batch_max_size: int = 100
    batch_max_concurrency: int = 10
    batch_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=30))

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 10
    circuit_breaker_timeout: timedelta = field(
        default_factory=lambda: timedelta(minutes=1)
    )
    circuit_breaker_success_threshold: int = 3

    def validate(self) -> List[str]:
        """Validate authorization configuration."""
        errors = []

        if self.cache_max_size < 1:
            errors.append("Cache max size must be at least 1")

        if self.cache_eviction_policy not in ["LRU", "LFU", "FIFO"]:
            errors.append(
                f"Invalid cache eviction policy: {self.cache_eviction_policy}"
            )

        if self.batch_max_size < 1:
            errors.append("Batch max size must be at least 1")

        if self.batch_max_concurrency < 1:
            errors.append("Batch max concurrency must be at least 1")

        if self.circuit_breaker_failure_threshold < 1:
            errors.append("Circuit breaker failure threshold must be at least 1")

        return errors


@dataclass
class TelemetryConfig:
    """Telemetry configuration settings."""

    # Application Insights
    app_insights_enabled: bool = True
    app_insights_connection_string: str = ""
    app_insights_instrumentation_key: str = ""

    # Telemetry settings
    telemetry_sampling_percentage: float = 100.0
    telemetry_batch_size: int = 100
    telemetry_batch_interval: timedelta = field(
        default_factory=lambda: timedelta(seconds=5)
    )
    telemetry_queue_capacity: int = 10000

    # Metrics
    metrics_enabled: bool = True
    metrics_export_interval: timedelta = field(
        default_factory=lambda: timedelta(seconds=60)
    )
    custom_dimensions: Dict[str, str] = field(default_factory=dict)

    # Feature flags
    feature_flag_cache_ttl: timedelta = field(
        default_factory=lambda: timedelta(minutes=5)
    )
    feature_flag_refresh_interval: timedelta = field(
        default_factory=lambda: timedelta(minutes=1)
    )

    def validate(self) -> List[str]:
        """Validate telemetry configuration."""
        errors = []

        if self.app_insights_enabled and not (
            self.app_insights_connection_string or self.app_insights_instrumentation_key
        ):
            errors.append(
                "Application Insights connection string or instrumentation key is required when enabled"
            )

        if not 0 <= self.telemetry_sampling_percentage <= 100:
            errors.append("Telemetry sampling percentage must be between 0 and 100")

        if self.telemetry_batch_size < 1:
            errors.append("Telemetry batch size must be at least 1")

        if self.telemetry_queue_capacity < 1:
            errors.append("Telemetry queue capacity must be at least 1")

        return errors


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""

    # Timeouts
    default_request_timeout: timedelta = field(
        default_factory=lambda: timedelta(seconds=30)
    )
    database_query_timeout: timedelta = field(
        default_factory=lambda: timedelta(seconds=10)
    )
    http_request_timeout: timedelta = field(
        default_factory=lambda: timedelta(seconds=30)
    )

    # Concurrency
    max_concurrent_requests: int = 100
    thread_pool_size: int = 50
    async_executor_queue_size: int = 1000

    # Circuit breaker defaults
    default_circuit_breaker_failure_threshold: int = 10
    default_circuit_breaker_timeout: timedelta = field(
        default_factory=lambda: timedelta(minutes=1)
    )
    default_circuit_breaker_success_threshold: int = 3

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_tokens_per_second: float = 100.0
    rate_limit_bucket_capacity: int = 200

    def validate(self) -> List[str]:
        """Validate performance configuration."""
        errors = []

        if self.max_concurrent_requests < 1:
            errors.append("Max concurrent requests must be at least 1")

        if self.thread_pool_size < 1:
            errors.append("Thread pool size must be at least 1")

        if self.async_executor_queue_size < 1:
            errors.append("Async executor queue size must be at least 1")

        if self.rate_limit_tokens_per_second <= 0:
            errors.append("Rate limit tokens per second must be positive")

        if self.rate_limit_bucket_capacity < 1:
            errors.append("Rate limit bucket capacity must be at least 1")

        return errors


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    # Key Vault
    key_vault_enabled: bool = False
    key_vault_url: str = ""
    key_vault_tenant_id: str = ""
    key_vault_client_id: str = ""
    key_vault_client_secret: str = ""

    # JWT settings
    jwt_validation_enabled: bool = True
    jwt_issuer: str = ""
    jwt_audience: str = ""
    jwt_signing_key: str = ""
    jwt_expiration_leeway: timedelta = field(
        default_factory=lambda: timedelta(minutes=5)
    )

    # Encryption
    encryption_algorithm: str = "AES256"
    encryption_key_rotation_interval: timedelta = field(
        default_factory=lambda: timedelta(days=90)
    )

    # API keys
    api_key_header_name: str = "X-API-Key"
    api_key_rotation_enabled: bool = True
    api_key_rotation_interval: timedelta = field(
        default_factory=lambda: timedelta(days=30)
    )

    def validate(self) -> List[str]:
        """Validate security configuration."""
        errors = []

        if self.key_vault_enabled:
            if not self.key_vault_url:
                errors.append("Key Vault URL is required when enabled")
            if not all(
                [
                    self.key_vault_tenant_id,
                    self.key_vault_client_id,
                    self.key_vault_client_secret,
                ]
            ):
                errors.append(
                    "Key Vault authentication credentials are required when enabled"
                )

        if self.jwt_validation_enabled:
            if not self.jwt_issuer:
                errors.append("JWT issuer is required when validation is enabled")
            if not self.jwt_audience:
                errors.append("JWT audience is required when validation is enabled")

        if self.encryption_algorithm not in ["AES256", "AES128", "RSA2048"]:
            errors.append(f"Invalid encryption algorithm: {self.encryption_algorithm}")

        return errors


@dataclass
class EnhancedApplicationProperties:
    """
    Enhanced application properties with all configuration sections.

    This class provides a comprehensive configuration structure for the ApexNova application
    with built-in validation and sensible defaults.
    """

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    authorization: AuthorizationConfig = field(default_factory=AuthorizationConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Application metadata
    application_name: str = "apexnova-stub"
    application_version: str = "1.0.0"
    environment: str = "development"

    @classmethod
    def from_environment(cls) -> "EnhancedApplicationProperties":
        """
        Create configuration from environment variables.

        Environment variables follow the pattern: APEXNOVA_<SECTION>_<PROPERTY>
        For example: APEXNOVA_DATABASE_COSMOS_ENDPOINT
        """
        config = cls()

        # Database configuration
        if cosmos_endpoint := os.getenv("APEXNOVA_DATABASE_COSMOS_ENDPOINT"):
            config.database.cosmos_endpoint = cosmos_endpoint
        if cosmos_key := os.getenv("APEXNOVA_DATABASE_COSMOS_KEY"):
            config.database.cosmos_key = cosmos_key
        if cosmos_database := os.getenv("APEXNOVA_DATABASE_COSMOS_DATABASE"):
            config.database.cosmos_database = cosmos_database

        # Telemetry configuration
        if app_insights_key := os.getenv(
            "APEXNOVA_TELEMETRY_APP_INSIGHTS_CONNECTION_STRING"
        ):
            config.telemetry.app_insights_connection_string = app_insights_key

        # Security configuration
        if key_vault_url := os.getenv("APEXNOVA_SECURITY_KEY_VAULT_URL"):
            config.security.key_vault_url = key_vault_url
            config.security.key_vault_enabled = True

        # Application metadata
        if app_name := os.getenv("APEXNOVA_APPLICATION_NAME"):
            config.application_name = app_name
        if app_version := os.getenv("APEXNOVA_APPLICATION_VERSION"):
            config.application_version = app_version
        if environment := os.getenv("APEXNOVA_ENVIRONMENT"):
            config.environment = environment

        return config

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedApplicationProperties":
        """Create configuration from dictionary."""
        config = cls()

        # Update sections if present
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        if "authorization" in data:
            config.authorization = AuthorizationConfig(**data["authorization"])
        if "telemetry" in data:
            config.telemetry = TelemetryConfig(**data["telemetry"])
        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])
        if "security" in data:
            config.security = SecurityConfig(**data["security"])

        # Update metadata
        config.application_name = data.get("application_name", config.application_name)
        config.application_version = data.get(
            "application_version", config.application_version
        )
        config.environment = data.get("environment", config.environment)

        return config

    def validate(self) -> Dict[str, List[str]]:
        """
        Validate all configuration sections.

        Returns:
            Dictionary mapping section names to lists of validation errors
        """
        errors = {}

        if database_errors := self.database.validate():
            errors["database"] = database_errors

        if auth_errors := self.authorization.validate():
            errors["authorization"] = auth_errors

        if telemetry_errors := self.telemetry.validate():
            errors["telemetry"] = telemetry_errors

        if perf_errors := self.performance.validate():
            errors["performance"] = perf_errors

        if security_errors := self.security.validate():
            errors["security"] = security_errors

        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return not self.validate()


class ConfigurationValidator:
    """Configuration validator with health check support."""

    def __init__(self, properties: EnhancedApplicationProperties):
        """
        Initialize validator.

        Args:
            properties: Application properties to validate
        """
        self.properties = properties

    def health_check(self) -> Dict[str, Any]:
        """
        Perform configuration health check.

        Returns:
            Health check result with status and details
        """
        validation_errors = self.properties.validate()

        if not validation_errors:
            return {
                "status": "UP",
                "details": {
                    "configuration": "valid",
                    "environment": self.properties.environment,
                    "version": self.properties.application_version,
                },
            }
        else:
            return {
                "status": "DOWN",
                "details": {
                    "configuration": "invalid",
                    "errors": validation_errors,
                    "environment": self.properties.environment,
                    "version": self.properties.application_version,
                },
            }

    def log_configuration(self) -> None:
        """Log configuration summary (excluding sensitive values)."""
        logger.info(
            f"Application: {self.properties.application_name} v{self.properties.application_version}"
        )
        logger.info(f"Environment: {self.properties.environment}")

        # Log non-sensitive configuration
        logger.info(
            f"Database: Cosmos={bool(self.properties.database.cosmos_endpoint)}, "
            f"Gremlin={bool(self.properties.database.gremlin_endpoint)}"
        )
        logger.info(
            f"Authorization: Cache={self.properties.authorization.cache_enabled}, "
            f"Metrics={self.properties.authorization.metrics_enabled}"
        )
        logger.info(
            f"Telemetry: AppInsights={self.properties.telemetry.app_insights_enabled}, "
            f"Sampling={self.properties.telemetry.telemetry_sampling_percentage}%"
        )
        logger.info(
            f"Security: KeyVault={self.properties.security.key_vault_enabled}, "
            f"JWT={self.properties.security.jwt_validation_enabled}"
        )

        # Log validation status
        if self.properties.is_valid():
            logger.info("Configuration validation: PASSED")
        else:
            errors = self.properties.validate()
            logger.error(f"Configuration validation: FAILED - {errors}")
