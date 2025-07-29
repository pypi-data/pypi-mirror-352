"""Tests for parallel execution functionality."""

import asyncio
from datetime import datetime
from typing import Any

import pytest

from zuma import (
    ZumaActionStep,
    ZumaExecutionError,
    ZumaExecutionStatus,
    ZumaParallelAction,
    ZumaRunner,
    ZumaWorkflow,
)


class CountingStep(ZumaActionStep):
    """A step that increments a counter in the context."""

    async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
        await asyncio.sleep(0.1)
        counter = context.get("counter", 0)
        return {"counter": counter + 1, "step": self.name}


class SlowStep(ZumaActionStep):
    """A step that takes a specified amount of time."""

    def __init__(self, name: str, duration: float):
        super().__init__(name)
        self.duration = duration

    async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
        await asyncio.sleep(self.duration)
        return {"duration": self.duration, "step": self.name}


class FailingStep(ZumaActionStep):
    """A step that always fails."""

    async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
        raise ZumaExecutionError(f"Step {self.name} failed")


@pytest.mark.asyncio
async def test_parallel_execution() -> None:
    """Test basic parallel execution."""
    parallel = ZumaParallelAction(
        "Parallel Steps",
        steps=[
            CountingStep("Step 1"),
            CountingStep("Step 2"),
            CountingStep("Step 3"),
        ],
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[parallel])
    runner = ZumaRunner()

    result = await runner.run_workflow(workflow, context={"counter": 0})

    assert result.status == ZumaExecutionStatus.SUCCESS
    assert len(result.children) == 1
    parallel_result = result.children[0]
    assert len(parallel_result.children) == 3
    assert all(child.status == ZumaExecutionStatus.SUCCESS for child in parallel_result.children)


@pytest.mark.asyncio
async def test_parallel_concurrency_limit() -> None:
    """Test parallel execution with concurrency limits."""
    steps = [SlowStep(f"Step {i}", 0.2) for i in range(5)]
    parallel = ZumaParallelAction("Limited Parallel", steps=steps, max_concurrency=2)

    workflow = ZumaWorkflow("Test Workflow", steps=[parallel])
    runner = ZumaRunner()

    start_time = datetime.now()
    result = await runner.run_workflow(workflow)
    duration = (datetime.now() - start_time).total_seconds()

    # With 5 steps taking 0.2s each and max_concurrency=2,
    # it should take at least 0.6s (3 batches)
    assert duration >= 0.6
    assert result.status == ZumaExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_parallel_error_handling() -> None:
    """Test error handling in parallel execution."""
    parallel = ZumaParallelAction(
        "Failing Parallel",
        steps=[
            CountingStep("Success 1"),
            FailingStep("Fail 1"),
            CountingStep("Success 2"),
            FailingStep("Fail 2"),
        ],
        fail_fast=True,
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[parallel])
    runner = ZumaRunner()

    result = await runner.run_workflow(workflow)
    assert result.status == ZumaExecutionStatus.FAILED

    # With fail_fast=True, some steps might not have started
    failed_steps = [
        child for child in result.children[0].children if child.status == ZumaExecutionStatus.FAILED
    ]
    assert len(failed_steps) >= 1


@pytest.mark.asyncio
async def test_parallel_continue_on_failure() -> None:
    """Test parallel execution with continue_on_failure."""
    parallel = ZumaParallelAction(
        "Resilient Parallel",
        steps=[
            CountingStep("Success 1"),
            FailingStep("Fail 1"),
            CountingStep("Success 2"),
        ],
        fail_fast=False,
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[parallel], continue_on_failure=True)
    runner = ZumaRunner()

    result = await runner.run_workflow(workflow)

    # Overall workflow should be marked as failed
    assert result.status == ZumaExecutionStatus.FAILED

    # But all steps should have executed
    parallel_result = result.children[0]
    assert len(parallel_result.children) == 3

    # Check specific step statuses
    success_steps = [
        child for child in parallel_result.children if child.status == ZumaExecutionStatus.SUCCESS
    ]
    failed_steps = [
        child for child in parallel_result.children if child.status == ZumaExecutionStatus.FAILED
    ]

    assert len(success_steps) == 2
    assert len(failed_steps) == 1


@pytest.mark.asyncio
async def test_parallel_context_isolation() -> None:
    """Test that parallel steps maintain context isolation."""
    parallel = ZumaParallelAction(
        "Isolated Parallel",
        steps=[
            CountingStep("Counter 1"),
            CountingStep("Counter 2"),
            CountingStep("Counter 3"),
        ],
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[parallel])
    runner = ZumaRunner()

    result = await runner.run_workflow(workflow, context={"counter": 0})

    # Each step should have incremented its own copy of the counter
    parallel_result = result.children[0]
    step_results = [child.context_snapshot.get("counter", 0) for child in parallel_result.children]

    # Each step should have counter = 1
    assert all(counter == 1 for counter in step_results)
