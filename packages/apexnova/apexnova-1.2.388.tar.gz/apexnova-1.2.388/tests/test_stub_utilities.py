"""Basic tests for ApexNova stub utilities."""

import pytest
from datetime import datetime

from apexnova.authorization_context_pb2 import AuthorizationContext
from apexnova.stub.role_pb2 import Role

from apexnova.stub.authorization.authorization_status import AuthorizationStatus
from apexnova.stub.authorization.rule.always_pass_rule import AlwaysPassRule
from apexnova.stub.authorization.rule.fail_if_not_logged_in_rule import (
    FailIfNotLoggedInRule,
)


class MockEntity:
    """Mock entity for testing."""

    def __init__(self, id: str):
        self.id = id


def test_authorization_status():
    """Test authorization status enumeration."""
    assert AuthorizationStatus.PASS.value == "PASS"
    assert AuthorizationStatus.FAIL.value == "FAIL"
    assert AuthorizationStatus.NEXT.value == "NEXT"


def test_always_pass_rule():
    """Test AlwaysPassRule."""
    rule = AlwaysPassRule()
    context = AuthorizationContext()
    entity = MockEntity("test")

    result = rule.evaluate(context, entity)
    assert result == AuthorizationStatus.PASS


def test_fail_if_not_logged_in_rule():
    """Test FailIfNotLoggedInRule."""
    rule = FailIfNotLoggedInRule()
    entity = MockEntity("test")

    # Test with empty account_id (not logged in)
    context_not_logged_in = AuthorizationContext()
    context_not_logged_in.account_id = ""

    result = rule.evaluate(context_not_logged_in, entity)
    assert result == AuthorizationStatus.FAIL

    # Test with account_id (logged in)
    context_logged_in = AuthorizationContext()
    context_logged_in.account_id = "user123"

    result = rule.evaluate(context_logged_in, entity)
    assert result == AuthorizationStatus.PASS


def test_application_insights_service_import():
    """Test that ApplicationInsightsService can be imported."""
    from apexnova.stub.service.application_insights_service import (
        ApplicationInsightsService,
    )

    service = ApplicationInsightsService()
    service.set_service("test-service")

    # Should not raise an exception
    assert service.service_identifier == "test-service"


if __name__ == "__main__":
    pytest.main([__file__])
