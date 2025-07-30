"""
Database configuration for Azure Cosmos DB and Gremlin.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfiguration:
    """
    Database configuration for Azure Cosmos DB and Gremlin.

    This configuration class provides settings for both document and graph database access.
    """

    # Cosmos DB document endpoint configuration
    document_endpoint: str = ""
    document_key: str = ""
    database_name: str = "apexnova"

    # Gremlin graph endpoint configuration
    gremlin_endpoint: str = ""
    gremlin_key: str = ""
    gremlin_port: int = 443
    gremlin_collection: str = "apexnova-db-graph-main"
    gremlin_enable_ssl: bool = True
    gremlin_serializer: str = "GRAPHSON_V3"

    # Connection settings
    preferred_regions: List[str] = field(default_factory=lambda: ["West US"])
    consistency_level: str = (
        "Session"  # Strong, BoundedStaleness, Session, ConsistentPrefix, Eventual
    )

    # Connection pool settings
    max_connections: int = 50
    connection_timeout_seconds: int = 30
    request_timeout_seconds: int = 30

    # Retry settings
    enable_retry: bool = True
    max_retry_attempts: int = 5
    max_retry_wait_time_seconds: int = 30

    @property
    def cosmos_connection_config(self) -> Dict[str, Any]:
        """Get Cosmos DB connection configuration."""
        return {
            "endpoint": self.document_endpoint,
            "key": self.document_key,
            "database_name": self.database_name,
            "preferred_regions": self.preferred_regions,
            "consistency_level": self.consistency_level,
            "connection_config": {
                "max_connections": self.max_connections,
                "connection_timeout": self.connection_timeout_seconds,
                "request_timeout": self.request_timeout_seconds,
            },
            "retry_config": {
                "enable": self.enable_retry,
                "max_attempts": self.max_retry_attempts,
                "max_wait_time": self.max_retry_wait_time_seconds,
            },
        }

    @property
    def gremlin_connection_config(self) -> Dict[str, Any]:
        """Get Gremlin connection configuration."""
        return {
            "endpoint": self.gremlin_endpoint,
            "key": self.gremlin_key,
            "port": self.gremlin_port,
            "database": self.database_name,
            "collection": self.gremlin_collection,
            "enable_ssl": self.gremlin_enable_ssl,
            "serializer": self.gremlin_serializer,
            "credentials": f"/dbs/{self.database_name}/colls/{self.gremlin_collection}",
        }

    def validate(self) -> List[str]:
        """Validate database configuration."""
        errors = []

        # Check if at least one endpoint is configured
        if not self.document_endpoint and not self.gremlin_endpoint:
            errors.append(
                "At least one database endpoint (document or gremlin) must be configured"
            )

        # Validate document database settings
        if self.document_endpoint:
            if not self.document_key:
                errors.append(
                    "Document database key is required when endpoint is configured"
                )
            if not self.database_name:
                errors.append("Database name is required")

        # Validate gremlin settings
        if self.gremlin_endpoint:
            if not self.gremlin_key:
                errors.append("Gremlin key is required when endpoint is configured")
            if self.gremlin_port < 1 or self.gremlin_port > 65535:
                errors.append(f"Invalid Gremlin port: {self.gremlin_port}")
            if self.gremlin_serializer not in [
                "GRAPHSON_V1",
                "GRAPHSON_V2",
                "GRAPHSON_V3",
            ]:
                errors.append(f"Invalid Gremlin serializer: {self.gremlin_serializer}")

        # Validate consistency level
        valid_consistency_levels = [
            "Strong",
            "BoundedStaleness",
            "Session",
            "ConsistentPrefix",
            "Eventual",
        ]
        if self.consistency_level not in valid_consistency_levels:
            errors.append(
                f"Invalid consistency level: {self.consistency_level}. Must be one of {valid_consistency_levels}"
            )

        # Validate connection settings
        if self.max_connections < 1:
            errors.append("Max connections must be at least 1")
        if self.connection_timeout_seconds < 1:
            errors.append("Connection timeout must be at least 1 second")
        if self.request_timeout_seconds < 1:
            errors.append("Request timeout must be at least 1 second")

        # Validate retry settings
        if self.enable_retry:
            if self.max_retry_attempts < 0:
                errors.append("Max retry attempts cannot be negative")
            if self.max_retry_wait_time_seconds < 1:
                errors.append("Max retry wait time must be at least 1 second")

        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DatabaseConfiguration":
        """Create configuration from dictionary."""
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "document_endpoint": self.document_endpoint,
            "document_key": self.document_key,
            "database_name": self.database_name,
            "gremlin_endpoint": self.gremlin_endpoint,
            "gremlin_key": self.gremlin_key,
            "gremlin_port": self.gremlin_port,
            "gremlin_collection": self.gremlin_collection,
            "gremlin_enable_ssl": self.gremlin_enable_ssl,
            "gremlin_serializer": self.gremlin_serializer,
            "preferred_regions": self.preferred_regions,
            "consistency_level": self.consistency_level,
            "max_connections": self.max_connections,
            "connection_timeout_seconds": self.connection_timeout_seconds,
            "request_timeout_seconds": self.request_timeout_seconds,
            "enable_retry": self.enable_retry,
            "max_retry_attempts": self.max_retry_attempts,
            "max_retry_wait_time_seconds": self.max_retry_wait_time_seconds,
        }

    def mask_sensitive_data(self) -> Dict[str, Any]:
        """Get configuration with masked sensitive data for logging."""
        config = self.to_dict()

        # Mask sensitive fields
        if config.get("document_key"):
            config["document_key"] = "***masked***"
        if config.get("gremlin_key"):
            config["gremlin_key"] = "***masked***"

        return config

    def log_configuration(self) -> None:
        """Log configuration (with sensitive data masked)."""
        masked_config = self.mask_sensitive_data()
        logger.info(f"Database configuration: {masked_config}")

        # Log validation status
        errors = self.validate()
        if errors:
            logger.error(f"Database configuration validation errors: {errors}")
        else:
            logger.info("Database configuration validation: PASSED")
