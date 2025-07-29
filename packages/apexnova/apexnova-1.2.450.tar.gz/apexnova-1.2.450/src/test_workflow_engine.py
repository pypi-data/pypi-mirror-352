"""
Test script for the ReactiveWorkflowEngine implementation.

This script tests various workflow scenarios including:
- Simple sequential workflows
- Decision-based branching
- Parallel execution
- Error handling and retries
- Workflow metrics and monitoring
"""

import asyncio
import time
import uuid
from datetime import timedelta
from typing import Any, Dict

from apexnova.stub.workflow import (
    ReactiveWorkflowEngine,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowExecutionState,
    WorkflowEngineConfig,
    WorkflowRetryConfig,
    WorkflowTimeoutConfig,
    StepResult,
    create_workflow_engine,
    create_workflow_builder,
)


async def test_simple_workflow():
    """Test a simple sequential workflow."""
    print("=== Testing Simple Sequential Workflow ===")

    # Create workflow builder
    builder = create_workflow_builder("test_simple_workflow")

    # Add steps
    builder.add_action_step(
        "step1",
        "Initialize",
        action=lambda ctx: ctx.set_variable("counter", 0) or StepResult.Success,
    ).add_action_step(
        "step2",
        "Increment",
        action=lambda ctx: (
            ctx.set_variable("counter", ctx.get_variable("counter", 0) + 1),
            print(f"Counter: {ctx.get_variable('counter')}"),
            StepResult.Success,
        )[-1],
    ).add_action_step(
        "step3",
        "Finalize",
        action=lambda ctx: (
            ctx.set_step_result(
                "step3", f"Final counter: {ctx.get_variable('counter')}"
            ),
            print(f"Workflow completed with counter: {ctx.get_variable('counter')}"),
            StepResult.Success,
        )[-1],
    )

    # Build workflow definition
    definition = builder.build()

    # Create engine and execute
    engine = create_workflow_engine()
    instance = await engine.start_workflow(definition, {})

    # Wait for completion
    await engine.wait_for_completion(
        instance.instance_id, timeout=timedelta(seconds=10)
    )

    # Get final state
    final_instance = engine.get_workflow_instance(instance.instance_id)
    print(f"Final state: {final_instance.state}")
    print(f"Final context variables: {final_instance.context.variables}")

    assert final_instance.state == WorkflowExecutionState.COMPLETED
    assert final_instance.context.get_variable("counter") == 1
    print("✅ Simple workflow test passed\n")


async def test_decision_workflow():
    """Test workflow with decision branching."""
    print("=== Testing Decision-Based Workflow ===")

    builder = create_workflow_builder("test_decision_workflow")

    # Add steps with decision logic
    builder.add_action_step(
        "setup",
        "Setup",
        action=lambda ctx: (ctx.set_variable("value", 42), StepResult.Success)[-1],
    ).add_decision_step(
        "check_value",
        "Check Value",
        condition=lambda ctx: ctx.get_variable("value", 0) > 30,
        true_step="high_value",
        false_step="low_value",
    ).add_action_step(
        "high_value",
        "High Value Processing",
        action=lambda ctx: (
            ctx.set_variable("result", "HIGH"),
            print("Processing high value"),
            StepResult.Success,
        )[-1],
    ).add_action_step(
        "low_value",
        "Low Value Processing",
        action=lambda ctx: (
            ctx.set_variable("result", "LOW"),
            print("Processing low value"),
            StepResult.Success,
        )[-1],
    )

    definition = builder.build()

    # Test with high value
    engine = create_workflow_engine()
    instance = await engine.start_workflow(definition, {"value": 42})
    await engine.wait_for_completion(
        instance.instance_id, timeout=timedelta(seconds=10)
    )

    final_instance = engine.get_workflow_instance(instance.instance_id)
    print(f"Decision result: {final_instance.context.get_variable('result')}")

    assert final_instance.state == WorkflowExecutionState.COMPLETED
    assert final_instance.context.get_variable("result") == "HIGH"
    print("✅ Decision workflow test passed\n")


async def test_retry_workflow():
    """Test workflow with retry logic."""
    print("=== Testing Retry Logic ===")

    # Create a step that fails a few times then succeeds
    attempt_count = 0

    def flaky_action(ctx: WorkflowContext) -> StepResult:
        nonlocal attempt_count
        attempt_count += 1
        print(f"Attempt {attempt_count}")

        if attempt_count < 3:
            return StepResult.Failure(
                Exception(f"Simulated failure on attempt {attempt_count}"), retry=True
            )
        else:
            ctx.set_variable("success", True)
            return StepResult.Success

    builder = create_workflow_builder("test_retry_workflow")
    builder.add_action_step(
        "flaky_step",
        "Flaky Step",
        action=flaky_action,
        retry_config=WorkflowRetryConfig(
            max_attempts=5,
            initial_delay=timedelta(milliseconds=100),
            max_delay=timedelta(seconds=1),
            backoff_multiplier=2.0,
        ),
    )

    definition = builder.build()
    engine = create_workflow_engine()
    instance = await engine.start_workflow(definition, {})

    await engine.wait_for_completion(
        instance.instance_id, timeout=timedelta(seconds=10)
    )

    final_instance = engine.get_workflow_instance(instance.instance_id)
    print(f"Final state after retries: {final_instance.state}")

    assert final_instance.state == WorkflowExecutionState.COMPLETED
    assert final_instance.context.get_variable("success") is True
    assert attempt_count == 3
    print("✅ Retry workflow test passed\n")


async def test_timeout_workflow():
    """Test workflow timeout handling."""
    print("=== Testing Timeout Handling ===")

    def slow_action(ctx: WorkflowContext) -> StepResult:
        print("Starting slow operation...")
        time.sleep(2)  # This will timeout
        return StepResult.Success

    builder = create_workflow_builder("test_timeout_workflow")
    builder.add_action_step(
        "slow_step",
        "Slow Step",
        action=slow_action,
        timeout=timedelta(milliseconds=500),
    )

    definition = builder.build()
    engine = create_workflow_engine()
    instance = await engine.start_workflow(definition, {})

    await engine.wait_for_completion(instance.instance_id, timeout=timedelta(seconds=5))

    final_instance = engine.get_workflow_instance(instance.instance_id)
    print(f"Final state after timeout: {final_instance.state}")

    assert final_instance.state == WorkflowExecutionState.FAILED
    print("✅ Timeout workflow test passed\n")


async def test_parallel_workflow():
    """Test parallel step execution."""
    print("=== Testing Parallel Execution ===")

    results = []

    def parallel_action(name: str):
        def action(ctx: WorkflowContext) -> StepResult:
            print(f"Executing {name}")
            time.sleep(0.1)  # Simulate work
            results.append(name)
            ctx.set_variable(f"{name}_done", True)
            return StepResult.Success

        return action

    builder = create_workflow_builder("test_parallel_workflow")
    builder.add_parallel_step(
        "parallel_work",
        "Parallel Work",
        steps=["task1", "task2", "task3"],
        wait_for_all=True,
    ).add_action_step(
        "task1", "Task 1", action=parallel_action("task1")
    ).add_action_step(
        "task2", "Task 2", action=parallel_action("task2")
    ).add_action_step(
        "task3", "Task 3", action=parallel_action("task3")
    )

    definition = builder.build()
    engine = create_workflow_engine()
    instance = await engine.start_workflow(definition, {})

    await engine.wait_for_completion(
        instance.instance_id, timeout=timedelta(seconds=10)
    )

    final_instance = engine.get_workflow_instance(instance.instance_id)
    print(f"Parallel execution results: {results}")

    assert final_instance.state == WorkflowExecutionState.COMPLETED
    assert len(results) == 3
    print("✅ Parallel workflow test passed\n")


async def test_workflow_metrics():
    """Test workflow metrics and monitoring."""
    print("=== Testing Workflow Metrics ===")

    builder = create_workflow_builder("test_metrics_workflow")
    builder.add_action_step(
        "step1", "Step 1", action=lambda ctx: StepResult.Success
    ).add_action_step("step2", "Step 2", action=lambda ctx: StepResult.Success)

    definition = builder.build()

    # Create engine with custom config
    config = WorkflowEngineConfig(
        max_concurrent_workflows=10,
        default_timeout=WorkflowTimeoutConfig(workflow_timeout=timedelta(minutes=5)),
        enable_metrics=True,
    )
    engine = create_workflow_engine(config)

    # Run multiple workflows
    instances = []
    for i in range(3):
        instance = await engine.start_workflow(definition, {"run": i})
        instances.append(instance)

    # Wait for all to complete
    for instance in instances:
        await engine.wait_for_completion(
            instance.instance_id, timeout=timedelta(seconds=10)
        )

    # Check metrics
    metrics = engine.get_metrics()
    print(f"Workflows started: {metrics.workflows_started}")
    print(f"Workflows completed: {metrics.workflows_completed}")
    print(f"Active workflows: {metrics.active_workflows}")

    assert metrics.workflows_started >= 3
    assert metrics.workflows_completed >= 3
    print("✅ Workflow metrics test passed\n")


async def test_event_monitoring():
    """Test workflow event monitoring."""
    print("=== Testing Event Monitoring ===")

    events = []

    def event_handler(event):
        events.append(event)
        print(f"Event: {event}")

    builder = create_workflow_builder("test_events_workflow")
    builder.add_action_step("step1", "Step 1", action=lambda ctx: StepResult.Success)

    definition = builder.build()
    engine = create_workflow_engine()

    # Subscribe to events
    async def monitor_events():
        async for event in engine.get_workflow_events():
            event_handler(event)

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor_events())

    # Run workflow
    instance = await engine.start_workflow(definition, {})
    await engine.wait_for_completion(
        instance.instance_id, timeout=timedelta(seconds=10)
    )

    # Give events time to process
    await asyncio.sleep(0.1)
    monitor_task.cancel()

    print(f"Total events captured: {len(events)}")
    assert len(events) >= 2  # At least started and completed events
    print("✅ Event monitoring test passed\n")


async def run_all_tests():
    """Run all workflow engine tests."""
    print("🚀 Starting ReactiveWorkflowEngine Tests\n")

    try:
        await test_simple_workflow()
        await test_decision_workflow()
        await test_retry_workflow()
        await test_timeout_workflow()
        await test_parallel_workflow()
        await test_workflow_metrics()
        await test_event_monitoring()

        print("🎉 All tests passed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
