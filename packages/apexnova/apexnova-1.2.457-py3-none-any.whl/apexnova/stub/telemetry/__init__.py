"""
Reactive Telemetry Module for ApexNova Stub

This module provides comprehensive telemetry, observability, and Application Insights
integration with reactive patterns, circuit breaker implementation, batch processing,
and advanced monitoring capabilities.

Key Components:
- ReactiveTelemetryCollector: Modern telemetry collection with reactive streams
- ReactiveObservabilityCollector: Distributed tracing and observability framework
- ReactiveApplicationInsightsService: Advanced Application Insights integration
- EnhancedTelemetryService: High-level telemetry service with operation tracking
- TelemetryConfig: Comprehensive configuration management with dynamic updates
"""

from .reactive_telemetry_collector import (
    ReactiveTelemetryCollector,
    TelemetryMetric,
    MetricType,
    TelemetryCounter,
    TelemetryGauge,
    TelemetryHistogram,
    TelemetryTimer,
    TelemetryEvent,
    TelemetryConfig as TelemetryCollectorConfig,
    MetricsRegistry,
    MetricAggregator,
)

from .reactive_observability_collector import (
    ReactiveObservabilityCollector,
    SpanContext,
    TraceContext,
    Span,
    SpanBuilder,
    TracingConfig,
    SpanProcessor,
    DistributedTracingManager,
    ObservabilityMetrics,
)

from .reactive_application_insights_service import (
    ReactiveApplicationInsightsService,
    TelemetryEventType,
    ApplicationInsightsTelemetryEvent,
    CircuitBreakerState,
    CircuitBreakerStats,
    HealthStatus,
    HealthInfo,
    ReactiveApplicationInsightsConfig,
    PerformanceTimer,
    BatchProcessor,
)

from .enhanced_telemetry_service import (
    EnhancedTelemetryService,
    MetricAggregator,
    AuthorizationContext,
    OperationMetrics,
    BatchOperationResult,
)

from .telemetry_config import (
    ReactiveTelemetryConfig,
    TelemetryConfigSnapshot,
    TelemetryHealthMonitor,
    TelemetryConfigMetrics,
    TelemetryPerformanceMetrics,
    ConfigUpdateResult,
    ValidationResult,
    TelemetryHealthInfo,
    HealthStatus as ConfigHealthStatus,
)

__all__ = [
    # Reactive Telemetry Collector
    "ReactiveTelemetryCollector",
    "TelemetryMetric",
    "MetricType",
    "TelemetryCounter",
    "TelemetryGauge",
    "TelemetryHistogram",
    "TelemetryTimer",
    "TelemetryEvent",
    "TelemetryCollectorConfig",
    "MetricsRegistry",
    "MetricAggregator",
    # Reactive Observability Collector
    "ReactiveObservabilityCollector",
    "SpanContext",
    "TraceContext",
    "Span",
    "SpanBuilder",
    "TracingConfig",
    "SpanProcessor",
    "DistributedTracingManager",
    "ObservabilityMetrics",
    # Reactive Application Insights Service
    "ReactiveApplicationInsightsService",
    "TelemetryEventType",
    "ApplicationInsightsTelemetryEvent",
    "CircuitBreakerState",
    "CircuitBreakerStats",
    "HealthStatus",
    "HealthInfo",
    "ReactiveApplicationInsightsConfig",
    "PerformanceTimer",
    "BatchProcessor",
    # Enhanced Telemetry Service
    "EnhancedTelemetryService",
    "MetricAggregator",
    "AuthorizationContext",
    "OperationMetrics",
    "BatchOperationResult",
    # Telemetry Configuration
    "ReactiveTelemetryConfig",
    "TelemetryConfigSnapshot",
    "TelemetryHealthMonitor",
    "TelemetryConfigMetrics",
    "TelemetryPerformanceMetrics",
    "ConfigUpdateResult",
    "ValidationResult",
    "TelemetryHealthInfo",
    "ConfigHealthStatus",
]
