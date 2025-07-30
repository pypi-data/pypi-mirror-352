"""Authorization rules."""

from apexnova.stub.authorization.rule.always_pass_rule import AlwaysPassRule
from apexnova.stub.authorization.rule.fail_if_not_logged_in_rule import (
    FailIfNotLoggedInRule,
)
from apexnova.stub.authorization.rule.fail_if_not_owner_rule import FailIfNotOwnerRule
from apexnova.stub.authorization.rule.pass_if_admin_rule import PassIfAdminRule
from apexnova.stub.authorization.rule.pass_if_is_service_rule import PassIfIsServiceRule
from apexnova.stub.authorization.rule.pass_if_is_vertex_owner_rule import (
    PassIfIsVertexOwnerRule,
)

__all__ = [
    "AlwaysPassRule",
    "FailIfNotLoggedInRule",
    "FailIfNotOwnerRule",
    "PassIfAdminRule",
    "PassIfIsServiceRule",
    "PassIfIsVertexOwnerRule",
]
