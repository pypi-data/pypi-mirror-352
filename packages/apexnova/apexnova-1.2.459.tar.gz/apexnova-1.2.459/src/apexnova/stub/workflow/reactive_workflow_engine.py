"""
Reactive Workflow Engine with State Machine support

This module provides a comprehensive workflow engine including:
- State machine patterns for workflow orchestration
- Reactive execution with async/await patterns
- Workflow step types (Action, Decision, Parallel, Wait)
- Retry logic with exponential backoff
- Workflow metrics and monitoring
- DSL builder pattern for workflow definition
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Generic,
    Protocol,
    runtime_checkable,
    Union,
    Callable,
    Awaitable,
    Set,
)
from uuid import uuid4, UUID
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from apexnova.stub.core.result import Result


logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")
R = TypeVar("R")

# ===== Step Results =====


@dataclass(frozen=True)
class BaseStepResult:
    """Base class for step execution results."""

    pass


@dataclass(frozen=True)
class StepSuccess(BaseStepResult):
    """Step executed successfully."""

    result: Any = None


@dataclass(frozen=True)
class StepFailure(BaseStepResult):
    """Step execution failed."""

    error: Exception
    retry: bool = True


@dataclass(frozen=True)
class StepConditional(BaseStepResult):
    """Step result with conditional next step."""

    next_step: str
    condition_result: bool


@dataclass(frozen=True)
class StepSkip(BaseStepResult):
    """Step was skipped."""

    reason: str = ""


# Convenience class with static methods for easy access
class StepResult:
    """Factory class for creating step results."""

    @staticmethod
    def success(result: Any = None) -> StepSuccess:
        return StepSuccess(result)

    @staticmethod
    def failure(error: Exception, retry: bool = True) -> StepFailure:
        return StepFailure(error, retry)

    @staticmethod
    def conditional(next_step: str, condition_result: bool = True) -> StepConditional:
        return StepConditional(next_step, condition_result)

    @staticmethod
    def skip(reason: str = "") -> StepSkip:
        return StepSkip(reason)

    # Class attributes for easy access
    Success = StepSuccess()
    Skip = StepSkip()


# ===== Workflow Execution States =====


class WorkflowExecutionState(Enum):
    """Workflow execution states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    WAITING = "WAITING"


# ===== Events and State Machine =====


@runtime_checkable
class Event(Protocol):
    """Base protocol for state machine events."""

    event_type: str
    data: Dict[str, Any]


@runtime_checkable
class State(Protocol):
    """Base protocol for state machine states."""

    state_name: str

    def can_transition_to(self, target_state: "State", event: Event) -> bool:
        """Check if transition to target state is allowed."""
        ...

    async def on_enter(self, context: "WorkflowContext") -> None:
        """Called when entering this state."""
        ...

    async def on_exit(self, context: "WorkflowContext") -> None:
        """Called when exiting this state."""
        ...


@dataclass(frozen=True)
class WorkflowEvent:
    """Concrete workflow event implementation."""

    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    workflow_id: str = ""


@dataclass
class WorkflowState:
    """Concrete workflow state implementation."""

    state_name: str
    allowed_transitions: List[str] = field(default_factory=list)

    def can_transition_to(self, target_state: State, event: Event) -> bool:
        """Check if transition to target state is allowed."""
        return target_state.state_name in self.allowed_transitions

    async def on_enter(self, context: "WorkflowContext") -> None:
        """Called when entering this state."""
        logger.debug(f"Entering state: {self.state_name}")

    async def on_exit(self, context: "WorkflowContext") -> None:
        """Called when exiting this state."""
        logger.debug(f"Exiting state: {self.state_name}")


@dataclass
class Transition:
    """State machine transition."""

    from_state: str
    to_state: str
    event_type: str
    condition: Optional[Callable[[Event, "WorkflowContext"], bool]] = None
    action: Optional[Callable[[Event, "WorkflowContext"], Awaitable[None]]] = None


class StateMachine:
    """State machine for workflow orchestration."""

    def __init__(self):
        self._states: Dict[str, State] = {}
        self._transitions: List[Transition] = []
        self._current_state: Optional[State] = None

    def add_state(self, state: State) -> None:
        """Add a state to the state machine."""
        self._states[state.state_name] = state

    def add_transition(self, transition: Transition) -> None:
        """Add a transition to the state machine."""
        self._transitions.append(transition)

    def set_initial_state(self, state_name: str) -> None:
        """Set the initial state."""
        if state_name in self._states:
            self._current_state = self._states[state_name]

    async def handle_event(self, event: Event, context: "WorkflowContext") -> bool:
        """Handle an event and potentially transition states."""
        if not self._current_state:
            return False

        for transition in self._transitions:
            if (
                transition.from_state == self._current_state.state_name
                and transition.event_type == event.event_type
            ):

                # Check condition if present
                if transition.condition and not transition.condition(event, context):
                    continue

                # Execute transition
                target_state = self._states.get(transition.to_state)
                if target_state and self._current_state.can_transition_to(
                    target_state, event
                ):
                    await self._current_state.on_exit(context)

                    if transition.action:
                        await transition.action(event, context)

                    self._current_state = target_state
                    await self._current_state.on_enter(context)

                    return True

        return False

    @property
    def current_state(self) -> Optional[State]:
        """Get the current state."""
        return self._current_state


# ===== Workflow Context =====


@dataclass
class WorkflowContext:
    """Context for workflow execution."""

    workflow_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

    def set_variable(self, key: str, value: Any) -> None:
        """Set a workflow variable."""
        self.variables[key] = value
        self.last_modified = datetime.now()

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a workflow variable."""
        return self.variables.get(key, default)

    def set_result(self, step_id: str, result: Any) -> None:
        """Set a step result."""
        self.results[step_id] = result
        self.last_modified = datetime.now()

    def get_result(self, step_id: str, default: Any = None) -> Any:
        """Get a step result."""
        return self.results.get(step_id, default)


# ===== Workflow Steps =====


@runtime_checkable
class WorkflowStep(Protocol):
    """Base protocol for workflow steps."""

    step_id: str
    step_type: str

    async def execute(self, context: WorkflowContext) -> BaseStepResult:
        """Execute the workflow step."""
        ...

    def get_next_steps(self, context: WorkflowContext) -> List[str]:
        """Get the next steps to execute."""
        ...


@dataclass
class ActionStep:
    """Action step that executes a specific action."""

    step_id: str
    step_type: str = "action"
    action: Callable[[WorkflowContext], BaseStepResult] = None
    next_step: Optional[str] = None

    async def execute(self, context: WorkflowContext) -> BaseStepResult:
        """Execute the action step."""
        try:
            if self.action:
                if asyncio.iscoroutinefunction(self.action):
                    result = await self.action(context)
                else:
                    result = self.action(context)

                # Store result in context if it's a success
                if isinstance(result, StepSuccess):
                    context.set_result(self.step_id, result.result)

                return result
            else:
                return StepResult.success(None)
        except Exception as e:
            logger.error(f"Error executing action step {self.step_id}: {e}")
            return StepResult.failure(e)

    def get_next_steps(self, context: WorkflowContext) -> List[str]:
        """Get the next steps to execute."""
        return [self.next_step] if self.next_step else []


@dataclass
class DecisionStep:
    """Decision step that chooses the next step based on a condition."""

    step_id: str
    step_type: str = "decision"
    condition: Callable[[WorkflowContext], bool] = None
    true_step: Optional[str] = None
    false_step: Optional[str] = None

    async def execute(self, context: WorkflowContext) -> BaseStepResult:
        """Execute the decision step."""
        try:
            if self.condition:
                if asyncio.iscoroutinefunction(self.condition):
                    decision = await self.condition(context)
                else:
                    decision = self.condition(context)

                context.set_result(self.step_id, decision)
                next_step = self.true_step if decision else self.false_step

                if next_step:
                    return StepResult.conditional(next_step, decision)
                else:
                    return StepResult.success(decision)
            else:
                return StepResult.success(True)
        except Exception as e:
            logger.error(f"Error executing decision step {self.step_id}: {e}")
            return StepResult.failure(e)

    def get_next_steps(self, context: WorkflowContext) -> List[str]:
        """Get the next steps to execute."""
        result = context.get_result(self.step_id)
        if result:
            return [self.true_step] if self.true_step else []
        else:
            return [self.false_step] if self.false_step else []


@dataclass
class ParallelStep:
    """Parallel step that executes multiple steps concurrently."""

    step_id: str
    step_type: str = "parallel"
    parallel_steps: List[str] = field(default_factory=list)
    next_step: Optional[str] = None
    wait_for_all: bool = True

    async def execute(self, context: WorkflowContext) -> BaseStepResult:
        """Execute the parallel step."""
        # This step itself doesn't execute logic, just coordinates parallel execution
        context.set_result(self.step_id, "parallel_initiated")
        return StepResult.success("parallel_initiated")

    def get_next_steps(self, context: WorkflowContext) -> List[str]:
        """Get the next steps to execute."""
        return self.parallel_steps


@dataclass
class WaitStep:
    """Wait step that pauses execution for a specified duration."""

    step_id: str
    step_type: str = "wait"
    duration: timedelta = field(default_factory=lambda: timedelta(seconds=1))
    condition: Optional[Callable[[WorkflowContext], bool]] = None
    next_step: Optional[str] = None

    async def execute(self, context: WorkflowContext) -> BaseStepResult:
        """Execute the wait step."""
        try:
            if self.condition:
                # Wait for condition
                start_time = time.time()
                timeout = self.duration.total_seconds()

                while time.time() - start_time < timeout:
                    if asyncio.iscoroutinefunction(self.condition):
                        condition_met = await self.condition(context)
                    else:
                        condition_met = self.condition(context)

                    if condition_met:
                        context.set_result(self.step_id, "condition_met")
                        return StepResult.success("condition_met")
                    await asyncio.sleep(0.1)

                context.set_result(self.step_id, "timeout")
                return StepResult.failure(Exception("Wait condition timeout"))
            else:
                # Simple duration wait
                await asyncio.sleep(self.duration.total_seconds())
                context.set_result(self.step_id, "completed")
                return StepResult.success("completed")
        except Exception as e:
            logger.error(f"Error executing wait step {self.step_id}: {e}")
            return StepResult.failure(e)

    def get_next_steps(self, context: WorkflowContext) -> List[str]:
        """Get the next steps to execute."""
        return [self.next_step] if self.next_step else []


# ===== Configuration =====


@dataclass
class WorkflowRetryConfig:
    """Configuration for workflow retry behavior."""

    max_retries: int = 3
    initial_delay: timedelta = field(default_factory=lambda: timedelta(seconds=1))
    max_delay: timedelta = field(default_factory=lambda: timedelta(seconds=60))
    backoff_multiplier: float = 2.0
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=list)


@dataclass
class WorkflowTimeoutConfig:
    """Configuration for workflow timeouts."""

    execution_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    step_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    idle_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=10))


@dataclass
class WorkflowEngineConfig:
    """Configuration for the workflow engine."""

    max_concurrent_workflows: int = 100
    max_concurrent_steps: int = 10
    enable_metrics: bool = True
    enable_event_streaming: bool = True
    retry_config: WorkflowRetryConfig = field(default_factory=WorkflowRetryConfig)
    timeout_config: WorkflowTimeoutConfig = field(default_factory=WorkflowTimeoutConfig)
    persistence_enabled: bool = False


# ===== Metrics and Monitoring =====


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""

    total_workflows: int = 0
    running_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    cancelled_workflows: int = 0
    average_execution_time: float = 0.0
    step_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def record_workflow_start(self, workflow_id: str) -> None:
        """Record workflow start."""
        self.total_workflows += 1
        self.running_workflows += 1

    def record_workflow_completion(
        self, workflow_id: str, execution_time: float
    ) -> None:
        """Record workflow completion."""
        self.running_workflows -= 1
        self.completed_workflows += 1

        # Update average execution time
        total_completed = self.completed_workflows
        self.average_execution_time = (
            self.average_execution_time * (total_completed - 1) + execution_time
        ) / total_completed

    def record_workflow_failure(self, workflow_id: str) -> None:
        """Record workflow failure."""
        self.running_workflows -= 1
        self.failed_workflows += 1

    def record_workflow_cancellation(self, workflow_id: str) -> None:
        """Record workflow cancellation."""
        self.running_workflows -= 1
        self.cancelled_workflows += 1


# ===== Workflow Definition and Instance =====


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""

    workflow_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    initial_step: Optional[str] = None
    state_machine: Optional[StateMachine] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps[step.step_id] = step

        if not self.initial_step:
            self.initial_step = step.step_id

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        return self.steps.get(step_id)


@dataclass
class WorkflowInstance:
    """Instance of a workflow execution."""

    instance_id: str
    workflow_definition: WorkflowDefinition
    context: WorkflowContext
    state: WorkflowExecutionState = WorkflowExecutionState.PENDING
    current_step_id: Optional[str] = None
    active_steps: List[str] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_id: str
    instance_id: str
    state: WorkflowExecutionState
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None


# ===== Exception Types =====


class WorkflowException(Exception):
    """Base exception for workflow errors."""

    pass


class WorkflowTimeoutException(WorkflowException):
    """Exception raised when workflow times out."""

    pass


class WorkflowExecutionException(WorkflowException):
    """Exception raised during workflow execution."""

    pass


class InvalidWorkflowStateException(WorkflowException):
    """Exception raised for invalid workflow state transitions."""

    pass


# ===== Reactive Workflow Engine =====


class ReactiveWorkflowEngine:
    """Reactive workflow engine with state machine support."""

    def __init__(self, config: Optional[WorkflowEngineConfig] = None):
        self._config = config or WorkflowEngineConfig()
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._instances: Dict[str, WorkflowInstance] = {}
        self._metrics = WorkflowMetrics()
        self._running = False
        self._execution_semaphore = asyncio.Semaphore(
            self._config.max_concurrent_workflows
        )
        self._step_semaphore = asyncio.Semaphore(self._config.max_concurrent_steps)
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._background_tasks: List[asyncio.Task] = []

    async def start(self) -> None:
        """Start the workflow engine."""
        self._running = True

        # Start background tasks
        if self._config.enable_event_streaming:
            task = asyncio.create_task(self._process_events())
            self._background_tasks.append(task)

        logger.info("ReactiveWorkflowEngine started")

    async def stop(self) -> None:
        """Stop the workflow engine."""
        self._running = False

        # Cancel all background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._executor.shutdown(wait=True)
        logger.info("ReactiveWorkflowEngine stopped")

    def register_workflow(self, workflow_definition: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._workflows[workflow_definition.workflow_id] = workflow_definition
        logger.info(f"Registered workflow: {workflow_definition.workflow_id}")

    async def execute_workflow(
        self, workflow_id: str, initial_variables: Optional[Dict[str, Any]] = None
    ) -> Result[WorkflowResult]:
        """Execute a workflow."""
        workflow_definition = self._workflows.get(workflow_id)
        if not workflow_definition:
            return Result.failure(f"Workflow not found: {workflow_id}")

        instance_id = str(uuid4())
        context = WorkflowContext(
            workflow_id=instance_id, variables=initial_variables or {}
        )

        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_definition=workflow_definition,
            context=context,
            current_step_id=workflow_definition.initial_step,
        )

        self._instances[instance_id] = instance

        async with self._execution_semaphore:
            return await self._execute_workflow_instance(instance)

    async def _execute_workflow_instance(
        self, instance: WorkflowInstance
    ) -> Result[WorkflowResult]:
        """Execute a workflow instance."""
        instance.state = WorkflowExecutionState.RUNNING
        instance.start_time = datetime.now()

        self._metrics.record_workflow_start(instance.instance_id)

        try:
            # Initialize state machine if present
            if instance.workflow_definition.state_machine:
                initial_state = instance.workflow_definition.state_machine.current_state
                if initial_state:
                    await initial_state.on_enter(instance.context)

            # Execute workflow steps
            current_step_id = instance.current_step_id

            while current_step_id and instance.state == WorkflowExecutionState.RUNNING:
                step = instance.workflow_definition.get_step(current_step_id)
                if not step:
                    break

                # Execute step with retry logic
                step_result = await self._execute_step_with_retry(instance, step)

                if step_result.is_failure():
                    instance.state = WorkflowExecutionState.FAILED
                    instance.error = step_result.error
                    instance.failed_steps.append(current_step_id)
                    break

                instance.completed_steps.append(current_step_id)

                # Get next steps
                next_steps = step.get_next_steps(instance.context)

                if not next_steps:
                    # No more steps, workflow completed
                    break
                elif len(next_steps) == 1:
                    # Single next step
                    current_step_id = next_steps[0]
                    instance.current_step_id = current_step_id
                else:
                    # Multiple next steps (parallel execution)
                    await self._execute_parallel_steps(instance, next_steps)
                    break

            # Complete workflow
            instance.end_time = datetime.now()
            execution_time = (instance.end_time - instance.start_time).total_seconds()

            if instance.state == WorkflowExecutionState.RUNNING:
                instance.state = WorkflowExecutionState.COMPLETED
                self._metrics.record_workflow_completion(
                    instance.instance_id, execution_time
                )
            else:
                self._metrics.record_workflow_failure(instance.instance_id)

            # Create result
            result = WorkflowResult(
                workflow_id=instance.workflow_definition.workflow_id,
                instance_id=instance.instance_id,
                state=instance.state,
                results=instance.context.results,
                error=instance.error,
                execution_time=execution_time,
            )

            # Emit workflow event
            if self._config.enable_event_streaming:
                event = WorkflowEvent(
                    event_type="workflow_completed",
                    data={"result": result.__dict__},
                    workflow_id=instance.instance_id,
                )
                await self._event_queue.put(event)

            return Result.success(result)

        except Exception as e:
            instance.state = WorkflowExecutionState.FAILED
            instance.error = str(e)
            instance.end_time = datetime.now()

            self._metrics.record_workflow_failure(instance.instance_id)

            logger.error(f"Error executing workflow {instance.instance_id}: {e}")
            return Result.failure(str(e))

    async def _execute_step_with_retry(
        self, instance: WorkflowInstance, step: WorkflowStep
    ) -> BaseStepResult:
        """Execute a step with retry logic."""
        retry_config = self._config.retry_config
        attempt = 0
        delay = retry_config.initial_delay.total_seconds()

        while attempt <= retry_config.max_retries:
            try:
                async with self._step_semaphore:
                    result = await step.execute(instance.context)

                if isinstance(result, (StepSuccess, StepConditional, StepSkip)):
                    return result

                # Check if we should retry
                if (
                    isinstance(result, StepFailure)
                    and result.retry
                    and attempt < retry_config.max_retries
                ):
                    logger.warning(f"Step {step.step_id} failed, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    delay = min(
                        delay * retry_config.backoff_multiplier,
                        retry_config.max_delay.total_seconds(),
                    )
                    attempt += 1
                else:
                    return result

            except Exception as e:
                if attempt < retry_config.max_retries and any(
                    isinstance(e, exc_type)
                    for exc_type in retry_config.retry_on_exceptions
                ):
                    logger.warning(
                        f"Step {step.step_id} raised {type(e).__name__}, retrying in {delay}s"
                    )
                    await asyncio.sleep(delay)
                    delay = min(
                        delay * retry_config.backoff_multiplier,
                        retry_config.max_delay.total_seconds(),
                    )
                    attempt += 1
                else:
                    return StepResult.failure(e)

        return StepResult.failure(Exception("Max retries exceeded"))

    async def _execute_parallel_steps(
        self, instance: WorkflowInstance, step_ids: List[str]
    ) -> None:
        """Execute multiple steps in parallel."""
        tasks = []

        for step_id in step_ids:
            step = instance.workflow_definition.get_step(step_id)
            if step:
                task = asyncio.create_task(
                    self._execute_step_with_retry(instance, step)
                )
                tasks.append((step_id, task))

        # Wait for all tasks to complete
        for step_id, task in tasks:
            try:
                result = await task
                if result.is_failure():
                    instance.failed_steps.append(step_id)
                else:
                    instance.completed_steps.append(step_id)
            except Exception as e:
                instance.failed_steps.append(step_id)
                logger.error(f"Error executing parallel step {step_id}: {e}")

    async def _process_events(self) -> None:
        """Process workflow events in the background."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                logger.debug(f"Processing workflow event: {event.event_type}")
                # Process event (e.g., send to external systems, update metrics, etc.)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing workflow event: {e}")

    async def cancel_workflow(self, instance_id: str) -> Result[None]:
        """Cancel a running workflow."""
        instance = self._instances.get(instance_id)
        if not instance:
            return Result.failure(f"Workflow instance not found: {instance_id}")

        if instance.state != WorkflowExecutionState.RUNNING:
            return Result.failure(f"Workflow {instance_id} is not running")

        instance.state = WorkflowExecutionState.CANCELLED
        instance.end_time = datetime.now()

        self._metrics.record_workflow_cancellation(instance_id)

        logger.info(f"Cancelled workflow: {instance_id}")
        return Result.success(None)

    def get_workflow_status(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get the status of a workflow instance."""
        return self._instances.get(instance_id)

    def get_metrics(self) -> WorkflowMetrics:
        """Get workflow execution metrics."""
        return self._metrics

    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the workflow engine."""
        return {
            "status": "healthy" if self._running else "stopped",
            "running_workflows": self._metrics.running_workflows,
            "total_workflows": self._metrics.total_workflows,
            "completed_workflows": self._metrics.completed_workflows,
            "failed_workflows": self._metrics.failed_workflows,
            "average_execution_time": self._metrics.average_execution_time,
            "uptime": time.time(),
        }

    async def start_workflow(
        self, definition: WorkflowDefinition, variables: Dict[str, Any] = None
    ) -> WorkflowInstance:
        """Start a new workflow instance."""
        if variables is None:
            variables = {}

        instance_id = str(uuid4())
        context = WorkflowContext(instance_id, variables)

        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_definition=definition,
            context=context,
            state=WorkflowExecutionState.PENDING,
            created_time=datetime.now(),
        )

        self._instances[instance_id] = instance

        # Start execution in the background
        asyncio.create_task(self.execute_workflow(definition, context))

        return instance

    async def wait_for_completion(
        self, instance_id: str, timeout: timedelta = None
    ) -> None:
        """Wait for a workflow instance to complete."""
        start_time = time.time()
        timeout_seconds = timeout.total_seconds() if timeout else float("inf")

        while True:
            instance = self._instances.get(instance_id)
            if not instance:
                raise ValueError(f"Workflow instance not found: {instance_id}")

            if instance.state in [
                WorkflowExecutionState.COMPLETED,
                WorkflowExecutionState.FAILED,
                WorkflowExecutionState.CANCELLED,
            ]:
                break

            if time.time() - start_time > timeout_seconds:
                raise asyncio.TimeoutError(
                    f"Workflow {instance_id} did not complete within {timeout}"
                )

            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

    def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get a workflow instance by ID."""
        return self._instances.get(instance_id)


# ===== Workflow Builder =====


class WorkflowBuilder:
    """Builder for creating workflow definitions."""

    def __init__(self, workflow_id: str, name: str):
        self._definition = WorkflowDefinition(workflow_id=workflow_id, name=name)
        self._current_step_id: Optional[str] = None

    def add_action_step(
        self,
        step_id: str,
        name: str,
        action: Callable[[WorkflowContext], BaseStepResult],
    ) -> "WorkflowBuilder":
        """Add an action step to the workflow."""
        step = ActionStep(step_id=step_id, action=action)
        self._definition.add_step(step)

        # Link to previous step
        if self._current_step_id:
            prev_step = self._definition.get_step(self._current_step_id)
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        self._current_step_id = step_id
        return self

    def add_decision_step(
        self,
        step_id: str,
        name: str,
        condition: Callable[[WorkflowContext], bool],
        true_step: Optional[str] = None,
        false_step: Optional[str] = None,
    ) -> "WorkflowBuilder":
        """Add a decision step to the workflow."""
        step = DecisionStep(
            step_id=step_id,
            condition=condition,
            true_step=true_step,
            false_step=false_step,
        )
        self._definition.add_step(step)

        # Link to previous step
        if self._current_step_id:
            prev_step = self._definition.get_step(self._current_step_id)
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        self._current_step_id = step_id
        return self

    def add_parallel_step(
        self, step_id: str, parallel_steps: List[str]
    ) -> "WorkflowBuilder":
        """Add a parallel step to the workflow."""
        step = ParallelStep(step_id=step_id, parallel_steps=parallel_steps)
        self._definition.add_step(step)

        # Link to previous step
        if self._current_step_id:
            prev_step = self._definition.get_step(self._current_step_id)
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        self._current_step_id = step_id
        return self

    def add_wait_step(
        self,
        step_id: str,
        duration: timedelta,
        condition: Optional[Callable[[WorkflowContext], bool]] = None,
    ) -> "WorkflowBuilder":
        """Add a wait step to the workflow."""
        step = WaitStep(step_id=step_id, duration=duration, condition=condition)
        self._definition.add_step(step)

        # Link to previous step
        if self._current_step_id:
            prev_step = self._definition.get_step(self._current_step_id)
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        self._current_step_id = step_id
        return self

    def with_state_machine(self, state_machine: StateMachine) -> "WorkflowBuilder":
        """Add a state machine to the workflow."""
        self._definition.state_machine = state_machine
        return self

    def with_metadata(self, key: str, value: Any) -> "WorkflowBuilder":
        """Add metadata to the workflow."""
        self._definition.metadata[key] = value
        return self

    def build(self) -> WorkflowDefinition:
        """Build the workflow definition."""
        return self._definition


# ===== Modern Workflow Builder =====


class ModernWorkflowBuilder:
    """Modern workflow builder with method chaining and DSL syntax."""

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.name = workflow_id
        self.version = "1.0.0"
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_order: List[str] = []
        self.start_step: Optional[str] = None
        self.end_steps: Set[str] = set()
        self.metadata: Dict[str, Any] = {}

    def add_action_step(
        self,
        step_id: str,
        name: str,
        action: Callable[[WorkflowContext], BaseStepResult],
    ) -> "ModernWorkflowBuilder":
        """Add an action step to the workflow."""
        step = ActionStep(step_id=step_id, action=action, next_step=None)
        self.steps[step_id] = step
        self.step_order.append(step_id)

        if not self.start_step:
            self.start_step = step_id

        # Link from previous step
        if len(self.step_order) > 1:
            prev_step_id = self.step_order[-2]
            prev_step = self.steps[prev_step_id]
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        return self

    def add_decision_step(
        self,
        step_id: str,
        name: str,
        condition: Callable[[WorkflowContext], bool],
        true_step: str,
        false_step: str,
    ) -> "ModernWorkflowBuilder":
        """Add a decision step to the workflow."""
        step = DecisionStep(
            step_id=step_id,
            condition=condition,
            true_step=true_step,
            false_step=false_step,
        )
        self.steps[step_id] = step
        self.step_order.append(step_id)

        if not self.start_step:
            self.start_step = step_id

        # Link from previous step
        if len(self.step_order) > 1:
            prev_step_id = self.step_order[-2]
            prev_step = self.steps[prev_step_id]
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        return self

    def add_parallel_step(
        self, step_id: str, name: str, parallel_steps: List[str]
    ) -> "ModernWorkflowBuilder":
        """Add a parallel step to the workflow."""
        step = ParallelStep(step_id=step_id, parallel_steps=parallel_steps)
        self.steps[step_id] = step
        self.step_order.append(step_id)

        if not self.start_step:
            self.start_step = step_id

        return self

    def add_wait_step(
        self, step_id: str, name: str, duration: timedelta
    ) -> "ModernWorkflowBuilder":
        """Add a wait step to the workflow."""
        step = WaitStep(step_id=step_id, duration=duration)
        self.steps[step_id] = step
        self.step_order.append(step_id)

        if not self.start_step:
            self.start_step = step_id

        # Link from previous step
        if len(self.step_order) > 1:
            prev_step_id = self.step_order[-2]
            prev_step = self.steps[prev_step_id]
            if isinstance(prev_step, ActionStep):
                prev_step.next_step = step_id

        return self

    def build(self) -> WorkflowDefinition:
        """Build the workflow definition."""
        definition = WorkflowDefinition(
            workflow_id=self.workflow_id,
            name=self.name,
            version=self.version,
            metadata=self.metadata,
        )

        for step in self.steps.values():
            definition.add_step(step)

        definition.initial_step = self.start_step

        return definition


# ===== Factory Functions =====


def create_workflow_engine(
    config: Optional[WorkflowEngineConfig] = None,
) -> ReactiveWorkflowEngine:
    """Create a reactive workflow engine."""
    return ReactiveWorkflowEngine(config)


def create_workflow_builder(workflow_id: str) -> ModernWorkflowBuilder:
    """Create a modern workflow builder."""
    return ModernWorkflowBuilder(workflow_id)


@asynccontextmanager
async def workflow_engine_context(config: Optional[WorkflowEngineConfig] = None):
    """Context manager for workflow engine."""
    engine = create_workflow_engine(config)
    try:
        await engine.start()
        yield engine
    finally:
        await engine.stop()


# ===== Example Usage =====


async def example_usage():
    """Example usage of the reactive workflow engine."""
    async with workflow_engine_context() as engine:
        # Create a simple workflow
        builder = create_workflow_builder("example_workflow", "Example Workflow")

        async def step1_action(context: WorkflowContext) -> Result[str]:
            context.set_variable("step1_completed", True)
            return Result.success("Step 1 completed")

        async def step2_condition(context: WorkflowContext) -> bool:
            return context.get_variable("step1_completed", False)

        async def step3_action(context: WorkflowContext) -> Result[str]:
            return Result.success("Step 3 completed")

        async def step4_action(context: WorkflowContext) -> Result[str]:
            return Result.success("Step 4 completed")

        workflow = (
            builder.add_action_step("step1", step1_action)
            .add_decision_step("step2", step2_condition, "step3", "step4")
            .add_action_step("step3", step3_action)
            .add_action_step("step4", step4_action)
            .build()
        )

        # Register and execute workflow
        engine.register_workflow(workflow)

        result = await engine.execute_workflow("example_workflow")

        if result.is_success():
            workflow_result = result.value
            print(f"Workflow completed: {workflow_result.state}")
            print(f"Execution time: {workflow_result.execution_time}s")
            print(f"Results: {workflow_result.results}")
        else:
            print(f"Workflow failed: {result.error}")

        # Get metrics
        metrics = engine.get_metrics()
        print(f"Total workflows: {metrics.total_workflows}")
        print(f"Completed workflows: {metrics.completed_workflows}")


if __name__ == "__main__":
    asyncio.run(example_usage())
