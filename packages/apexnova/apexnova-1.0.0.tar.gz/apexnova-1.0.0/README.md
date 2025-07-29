# ApexNova Python Stub Library

A comprehensive Python gRPC stub library with built-in authorization and Azure Application Insights telemetry support for the ApexNova platform.

## Migration Guide

### From Legacy Protobuf Setup to Modern Package

If you're migrating from a legacy protobuf setup, follow these steps:

1. **Remove old protobuf generated files**:

   ```bash
   rm -rf old_proto_generated/
   ```

2. **Uninstall old packages**:

   ```bash
   pip uninstall old-grpc-package
   ```

3. **Install the new package**:

   ```bash
   pip install apexnova
   ```

4. **Update your imports**:

   ```python
   # Old imports
   from old_proto_generated import authorization_pb2
   
   # New imports
   from apexnova.stub.authorization_context_pb2 import AuthorizationContext
   ```

5. **Update your configuration**:

   ```python
   # Old configuration
   channel = grpc.insecure_channel('localhost:50051')
   
   # New configuration with Application Insights
   from apexnova.stub.service.application_insights_service import ApplicationInsightsService
   
   insights = ApplicationInsightsService(
       connection_string="your-azure-connection-string"
   )
   ```

## Features

- **🚀 gRPC Support**: Complete protobuf stub generation with type hints
- **🔐 Authorization Context**: Built-in user, role, and device authorization models
- **📊 Azure Application Insights**: Automatic telemetry tracking and performance monitoring
- **🗃️ Graph Database**: Gremlin-based repository patterns for graph operations
- **⚡ High Performance**: Async/await support throughout
- **🛡️ Type Safety**: Full Python type hints with mypy compatibility
- **🔧 Flexible Dependencies**: Optional extras for different deployment scenarios

## Quick Start

### Installation

**Full installation (recommended for most users):**

```bash
pip install apexnova
```

**Minimal installation (core gRPC only):**

```bash
pip install apexnova[minimal]
```

**Specific feature installations:**

```bash
pip install apexnova[azure]    # Azure Application Insights only
pip install apexnova[graph]    # Graph database support only
pip install apexnova[all]      # All optional features
```

### Basic Usage

```python
from apexnova.stub.authorization_context_pb2 import AuthorizationContext, Actor, Role
from apexnova.stub.service.application_insights_service import ApplicationInsightsService

# Create authorization context
context = AuthorizationContext()
context.user_id = "user123"
context.actor = Actor.ACTOR_USER
context.role = Role.ROLE_USER

# Initialize telemetry service (optional)
insights = ApplicationInsightsService(
    connection_string="your-azure-connection-string"
)

# Use in your application
insights.track_event("user_action", {"user_id": context.user_id})
```

### Advanced Usage with Feature Targeting

```python
from apexnova.stub.feature.context.feature_targeting_context import FeatureTargetingContext

# Create feature targeting context from authorization
targeting_context = FeatureTargetingContext(authorization_context)

# Access feature targeting properties
user_groups = targeting_context.groups
device_info = targeting_context.device
location = targeting_context.location
```

## Authorization Models

The library provides comprehensive authorization support through protobuf-generated models:

### Core Enums

- **Actor**: `ACTOR_USER`, `ACTOR_SERVICE`, `ACTOR_SYSTEM`
- **Role**: `ROLE_ADMIN`, `ROLE_USER`, `ROLE_READONLY`, `ROLE_SERVICE`
- **Device**: `DEVICE_WEB`, `DEVICE_MOBILE`, `DEVICE_API`, `DEVICE_IOT`
- **Location**: Geographic and network location context
- **UserAgent**: Browser and client identification
- **Tier**: Service tier and subscription level

### Repository Patterns

```python
from apexnova.stub.repository.base_authorization_cosmos_repository import BaseAuthorizationCosmosRepository
from apexnova.stub.repository.base_gremlin_authorization_repository import BaseGremlinAuthorizationRepository

# Cosmos DB with authorization
class UserRepository(BaseAuthorizationCosmosRepository[MyAuthModel, User, str]):
    def save(self, entity: User) -> User:
        # Implementation with built-in authorization checks
        pass

# Graph database with authorization
class RelationshipRepository(BaseGremlinAuthorizationRepository[MyAuthModel, Relationship, str]):
    def find_by_id(self, id: str) -> Optional[Relationship]:
        # Implementation with graph traversal and authorization
        pass
```

## Azure Application Insights Integration

### Automatic Telemetry

The library automatically tracks:

- Request performance and timing
- User actions and authentication events
- Error rates and exception details
- Custom business metrics

### Configuration

```python
from apexnova.stub.service.application_insights_service import ApplicationInsightsService

# Basic configuration
insights = ApplicationInsightsService(
    connection_string="InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/"
)

# Advanced configuration with feature flags
insights = ApplicationInsightsService(
    connection_string="your-connection-string",
    feature_manager=your_feature_manager
)

# Track custom events
insights.track_event("purchase_completed", {
    "user_id": context.user_id,
    "amount": 99.99,
    "currency": "USD"
})

# Track performance metrics
insights.track_metric("response_time_ms", 150)

# Track exceptions with context
try:
    risky_operation()
except Exception as e:
    insights.track_exception(e, authorization_context)
```

## Graph Database Support

### Gremlin Repository Pattern

```python
from apexnova.stub.repository.base_gremlin_authorization_repository import BaseGremlinAuthorizationRepository

class UserGraphRepository(BaseGremlinAuthorizationRepository[AuthModel, User, str]):
    def find_friends(self, user_id: str, context: AuthorizationContext) -> List[User]:
        """Find user's friends with authorization checks."""
        if not self.authorization_model.can_read(context, user_id):
            raise PermissionError("Insufficient permissions")
        
        # Gremlin traversal query
        query = f"g.V('{user_id}').out('friend').hasLabel('user')"
        return self.execute_query(query)
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/apexnova/proto.git
cd proto/stub/python

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

### Building from Source

```bash
# Build the package
python -m build

# Install locally
pip install dist/apexnova-*.whl
```

## Type Safety

The library is fully typed and includes:

- Complete type hints for all public APIs
- mypy configuration for strict type checking
- py.typed marker for downstream type checking

```python
# Type hints work seamlessly
from apexnova.stub.authorization_context_pb2 import AuthorizationContext

def process_request(context: AuthorizationContext) -> bool:
    # Full IDE autocomplete and type checking
    user_id: str = context.user_id
    actor: Actor = context.actor
    return True
```

## Error Handling

The library provides robust error handling:

```python
from apexnova.stub.authorization.authorization_status import AuthorizationStatus

# Authorization results
status = authorization_rule.evaluate(context, entity)
if status == AuthorizationStatus.PASS:
    # Proceed with operation
    pass
elif status == AuthorizationStatus.FAIL:
    # Handle authorization failure
    raise PermissionError("Access denied")
else:  # AuthorizationStatus.NEXT
    # Continue to next rule in chain
    pass
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

### Azure Functions

```python
import azure.functions as func
from apexnova.stub.service.application_insights_service import ApplicationInsightsService

def main(req: func.HttpRequest) -> func.HttpResponse:
    insights = ApplicationInsightsService()
    
    with insights.start_span("function_execution") as span:
        # Your function logic
        return func.HttpResponse("Success")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: [GitHub Repository](https://github.com/apexnova/proto)
- **Issues**: [Bug Tracker](https://github.com/apexnova/proto/issues)
- **Email**: <team@apexnova.com>
