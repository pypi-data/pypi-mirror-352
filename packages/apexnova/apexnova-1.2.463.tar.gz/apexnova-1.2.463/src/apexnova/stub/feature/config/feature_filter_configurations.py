"""
Feature filter configurations for feature flag management.
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class FilterType(Enum):
    """Feature filter types."""

    PERCENTAGE = "Microsoft.Percentage"
    TIME_WINDOW = "Microsoft.TimeWindow"
    TARGETING = "Microsoft.Targeting"
    CUSTOM = "Custom"


@dataclass
class FeatureFilterContext:
    """Context for feature filter evaluation."""

    feature_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    groups: Set[str] = field(default_factory=set)

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get parameter value."""
        return self.parameters.get(name, default)


class FeatureFilter(ABC):
    """Base class for feature filters."""

    @abstractmethod
    def evaluate(self, context: FeatureFilterContext) -> bool:
        """Evaluate if feature should be enabled."""
        pass

    @property
    @abstractmethod
    def filter_type(self) -> FilterType:
        """Get filter type."""
        pass


class PercentageFilter(FeatureFilter):
    """
    Percentage filter for feature flags.

    Enables feature for a specified percentage of users.
    """

    @property
    def filter_type(self) -> FilterType:
        return FilterType.PERCENTAGE

    def evaluate(self, context: FeatureFilterContext) -> bool:
        """
        Evaluate percentage filter.

        Args:
            context: Filter context with parameters containing 'Value' (percentage)

        Returns:
            True if feature should be enabled for this context
        """
        percentage = context.get_parameter("Value", 0)

        if (
            not isinstance(percentage, (int, float))
            or percentage < 0
            or percentage > 100
        ):
            return False

        # Use consistent hash based on feature name and user ID (if available)
        seed_value = context.feature_name
        if context.user_id:
            seed_value += context.user_id

        # Generate deterministic value between 0-100
        hash_value = hash(seed_value) % 10000
        normalized_value = hash_value / 100.0  # Convert to 0-100 range

        return normalized_value < percentage


@dataclass
class TimeWindow:
    """Time window configuration."""

    start: Optional[datetime] = None
    end: Optional[datetime] = None

    def is_within_window(self, current_time: Optional[datetime] = None) -> bool:
        """Check if current time is within the window."""
        if current_time is None:
            current_time = datetime.now()

        if self.start and current_time < self.start:
            return False

        if self.end and current_time > self.end:
            return False

        return True


class TimeWindowFilter(FeatureFilter):
    """
    Time window filter for feature flags.

    Enables feature within specified time windows.
    """

    @property
    def filter_type(self) -> FilterType:
        return FilterType.TIME_WINDOW

    def evaluate(self, context: FeatureFilterContext) -> bool:
        """
        Evaluate time window filter.

        Args:
            context: Filter context with parameters containing 'Start' and/or 'End'

        Returns:
            True if current time is within the specified window
        """
        start_str = context.get_parameter("Start")
        end_str = context.get_parameter("End")

        start_time = None
        end_time = None

        try:
            if start_str:
                start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            if end_str:
                end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False

        window = TimeWindow(start=start_time, end=end_time)
        return window.is_within_window()


@dataclass
class TargetingRule:
    """Targeting rule configuration."""

    name: str
    audience: Dict[str, Any] = field(default_factory=dict)

    def matches(self, context: FeatureFilterContext) -> bool:
        """Check if context matches this targeting rule."""
        # Check user targeting
        users = self.audience.get("Users", [])
        if context.user_id and context.user_id in users:
            return True

        # Check group targeting
        groups = set(self.audience.get("Groups", []))
        if groups and context.groups.intersection(groups):
            return True

        # Check default rollout percentage
        default_rollout = self.audience.get("DefaultRolloutPercentage", 0)
        if default_rollout > 0:
            # Use percentage logic similar to PercentageFilter
            seed_value = context.feature_name
            if context.user_id:
                seed_value += context.user_id

            hash_value = hash(seed_value) % 10000
            normalized_value = hash_value / 100.0

            return normalized_value < default_rollout

        return False


class TargetingFilter(FeatureFilter):
    """
    Targeting filter for feature flags.

    Enables feature for specific users, groups, or percentages.
    """

    def __init__(self, ignore_case: bool = True):
        """
        Initialize targeting filter.

        Args:
            ignore_case: Whether to ignore case in user/group comparisons
        """
        self.ignore_case = ignore_case

    @property
    def filter_type(self) -> FilterType:
        return FilterType.TARGETING

    def evaluate(self, context: FeatureFilterContext) -> bool:
        """
        Evaluate targeting filter.

        Args:
            context: Filter context with targeting configuration

        Returns:
            True if feature should be enabled for this context
        """
        audience = context.get_parameter("Audience", {})

        # Normalize case if needed
        if self.ignore_case and context.user_id:
            context.user_id = context.user_id.lower()

        if self.ignore_case:
            context.groups = {group.lower() for group in context.groups}

        # Check direct user targeting
        users = audience.get("Users", [])
        if self.ignore_case:
            users = [user.lower() for user in users]

        if context.user_id and context.user_id in users:
            return True

        # Check group targeting
        groups = set(audience.get("Groups", []))
        if self.ignore_case:
            groups = {group.lower() for group in groups}

        if groups and context.groups.intersection(groups):
            return True

        # Check exclusion
        exclusion = audience.get("Exclusion", {})
        excluded_users = exclusion.get("Users", [])
        excluded_groups = set(exclusion.get("Groups", []))

        if self.ignore_case:
            excluded_users = [user.lower() for user in excluded_users]
            excluded_groups = {group.lower() for group in excluded_groups}

        if context.user_id and context.user_id in excluded_users:
            return False

        if excluded_groups and context.groups.intersection(excluded_groups):
            return False

        # Check default rollout percentage
        default_rollout = audience.get("DefaultRolloutPercentage", 0)
        if default_rollout > 0:
            # Use consistent hash-based percentage
            seed_value = context.feature_name
            if context.user_id:
                seed_value += context.user_id

            hash_value = hash(seed_value) % 10000
            normalized_value = hash_value / 100.0

            return normalized_value < default_rollout

        return False


class CustomFilter(FeatureFilter):
    """
    Custom feature filter for application-specific logic.
    """

    def __init__(self, name: str, evaluation_func: callable):
        """
        Initialize custom filter.

        Args:
            name: Filter name
            evaluation_func: Function that takes context and returns bool
        """
        self.name = name
        self.evaluation_func = evaluation_func

    @property
    def filter_type(self) -> FilterType:
        return FilterType.CUSTOM

    def evaluate(self, context: FeatureFilterContext) -> bool:
        """Evaluate custom filter."""
        try:
            return bool(self.evaluation_func(context))
        except Exception:
            return False


class FeatureFilterConfigurations:
    """
    Feature filter configurations and factory.

    Provides pre-configured feature filters for common scenarios.
    """

    def __init__(self):
        """Initialize feature filter configurations."""
        self._filters: Dict[str, FeatureFilter] = {}
        self._register_default_filters()

    def _register_default_filters(self):
        """Register default feature filters."""
        self._filters["Microsoft.Percentage"] = PercentageFilter()
        self._filters["Microsoft.TimeWindow"] = TimeWindowFilter()
        self._filters["Microsoft.Targeting"] = TargetingFilter(ignore_case=True)

    def get_percentage_filter(self) -> PercentageFilter:
        """Get percentage filter instance."""
        return PercentageFilter()

    def get_time_window_filter(self) -> TimeWindowFilter:
        """Get time window filter instance."""
        return TimeWindowFilter()

    def get_targeting_filter(self, ignore_case: bool = True) -> TargetingFilter:
        """Get targeting filter instance."""
        return TargetingFilter(ignore_case=ignore_case)

    def register_custom_filter(self, name: str, filter_instance: FeatureFilter):
        """Register a custom filter."""
        self._filters[name] = filter_instance

    def get_filter(self, filter_name: str) -> Optional[FeatureFilter]:
        """Get filter by name."""
        return self._filters.get(filter_name)

    def get_all_filters(self) -> Dict[str, FeatureFilter]:
        """Get all registered filters."""
        return self._filters.copy()

    def create_custom_filter(
        self, name: str, evaluation_func: callable
    ) -> CustomFilter:
        """Create and register a custom filter."""
        custom_filter = CustomFilter(name, evaluation_func)
        self.register_custom_filter(name, custom_filter)
        return custom_filter


# Global instance for easy access
_default_configurations = FeatureFilterConfigurations()


def get_percentage_filter() -> PercentageFilter:
    """Get default percentage filter."""
    return _default_configurations.get_percentage_filter()


def get_time_window_filter() -> TimeWindowFilter:
    """Get default time window filter."""
    return _default_configurations.get_time_window_filter()


def get_targeting_filter(ignore_case: bool = True) -> TargetingFilter:
    """Get default targeting filter."""
    return _default_configurations.get_targeting_filter(ignore_case)


def get_filter(filter_name: str) -> Optional[FeatureFilter]:
    """Get filter by name from default configurations."""
    return _default_configurations.get_filter(filter_name)


def register_custom_filter(name: str, filter_instance: FeatureFilter):
    """Register custom filter in default configurations."""
    _default_configurations.register_custom_filter(name, filter_instance)


def create_custom_filter(name: str, evaluation_func: callable) -> CustomFilter:
    """Create custom filter in default configurations."""
    return _default_configurations.create_custom_filter(name, evaluation_func)
