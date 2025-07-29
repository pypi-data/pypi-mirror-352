"""Tests for the Zuma workflow functionality."""

import asyncio
from dataclasses import dataclass
from typing import Any, TypeAlias, TypeVar, override

import pytest

from zuma import (
    ZumaActionStep,
    ZumaConditionalStep,
    ZumaExecutionError,
    ZumaParallelAction,
    ZumaRunner,
    ZumaWorkflow,
)

# Type definitions
Context: TypeAlias = dict[str, Any]
T = TypeVar("T")


@dataclass
class StepResult:
    """Represents the result of a workflow step."""

    value: int
    metadata: dict[str, Any]


class SimpleStep(ZumaActionStep):
    """A simple step that adds a number to the context."""

    @override
    async def execute(self, context: Context, **kwargs) -> Context:
        await asyncio.sleep(0.1)  # Simulate work
        current = context.get("value", 0)
        return {"value": current + 1, "metadata": {"step": self.name}}


class FailingStep(ZumaActionStep):
    """A step that always fails."""

    @override
    async def execute(self, context: Context, **kwargs) -> Context:
        raise ZumaExecutionError("Step failed as expected")


@pytest.mark.asyncio
async def test_simple_workflow() -> None:
    """Test a simple sequential workflow."""
    workflow = ZumaWorkflow(
        "Simple Workflow",
        steps=[
            SimpleStep("Step 1"),
            SimpleStep("Step 2"),
            SimpleStep("Step 3"),
        ],
    )

    runner = ZumaRunner()
    result = await runner.run_workflow(workflow)

    assert result.status == "SUCCESS"
    assert len(result.children) == 3
    assert all(child.status == "SUCCESS" for child in result.children)


@pytest.mark.asyncio
async def test_parallel_workflow() -> None:
    """Test parallel execution of steps."""
    parallel = ZumaParallelAction(
        "Parallel Steps",
        steps=[
            SimpleStep("Parallel 1"),
            SimpleStep("Parallel 2"),
            SimpleStep("Parallel 3"),
        ],
        max_concurrency=2,
    )

    workflow = ZumaWorkflow("Parallel Workflow", steps=[parallel])

    runner = ZumaRunner()
    result = await runner.run_workflow(workflow)

    assert result.status == "SUCCESS"
    assert len(result.children) == 1  # The parallel action
    parallel_result = result.children[0]
    assert len(parallel_result.children) == 3  # The parallel steps
    assert all(child.status == "SUCCESS" for child in parallel_result.children)


@pytest.mark.asyncio
async def test_conditional_workflow() -> None:
    """Test conditional branching in workflow."""

    def check_value(context: Context) -> bool:
        return context.get("value", 0) > 5

    conditional = ZumaConditionalStep(
        "Value Check",
        condition=check_value,
        true_component=SimpleStep("High Value"),
        false_component=SimpleStep("Low Value"),
    )

    workflow = ZumaWorkflow("Conditional Workflow", steps=[conditional])

    # Test false path
    runner = ZumaRunner()
    result = await runner.run_workflow(workflow, context={"value": 3})
    assert result.status == "SUCCESS"
    assert result.children[0].children[-1].name == "Low Value"

    # Test true path
    result = await runner.run_workflow(workflow, context={"value": 7})
    assert result.status == "SUCCESS"
    assert result.children[0].children[-1].name == "High Value"


@pytest.mark.asyncio
async def test_error_handling() -> None:
    """Test workflow error handling."""
    workflow = ZumaWorkflow(
        "Error Workflow",
        steps=[
            SimpleStep("Step 1"),
            FailingStep("Failing Step"),
            SimpleStep("Step 3"),
        ],
        continue_on_failure=True,
    )

    runner = ZumaRunner()
    result = await runner.run_workflow(workflow)

    assert result.status == "FAILED"
    assert result.children[0].status == "SUCCESS"
    assert result.children[1].status == "FAILED"
    assert result.children[2].status == "SKIPPED"


@pytest.mark.asyncio
async def test_exception_groups() -> None:
    """Test handling of multiple failures in parallel execution."""
    parallel = ZumaParallelAction(
        "Failing Parallel Steps",
        steps=[
            FailingStep("Fail 1"),
            FailingStep("Fail 2"),
            SimpleStep("Success 1"),
        ],
        fail_fast=False,
    )

    workflow = ZumaWorkflow("Exception Group Workflow", steps=[parallel])
    runner = ZumaRunner()

    try:
        await runner.run_workflow(workflow)
    except ExceptionGroup as eg:
        # Python 3.11+ exception group handling
        assert len(eg.exceptions) == 2
        assert all(isinstance(e, ZumaExecutionError) for e in eg.exceptions)
    else:
        pytest.fail("Expected ExceptionGroup was not raised")
