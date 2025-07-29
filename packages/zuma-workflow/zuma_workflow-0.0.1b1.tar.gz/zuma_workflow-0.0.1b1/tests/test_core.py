"""Tests for core workflow functionality."""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import pytest

from zuma import (
    ZumaActionStep,
    ZumaComponentType,
    ZumaExecutionStatus,
    ZumaRunner,
    ZumaWorkflow,
)

from .conftest import TestContext


class TimedStep(ZumaActionStep):
    """A step that takes a specified amount of time."""

    def __init__(self, name: str, duration: float = 0.1):
        super().__init__(name)
        self.duration = duration

    async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
        await asyncio.sleep(self.duration)
        return {"duration": self.duration}


@pytest.mark.asyncio
async def test_workflow_execution(basic_workflow: TestContext) -> None:
    """Test basic workflow execution."""
    result = await basic_workflow.runner.run_workflow(
        basic_workflow.workflow, context=basic_workflow.initial_context
    )

    assert result.status == ZumaExecutionStatus.SUCCESS
    assert len(result.children) == 3
    assert all(child.status == ZumaExecutionStatus.SUCCESS for child in result.children)
    assert result.type == ZumaComponentType.WORKFLOW


@pytest.mark.asyncio
async def test_workflow_context_propagation(basic_workflow: TestContext) -> None:
    """Test that context is properly propagated through steps."""
    result = await basic_workflow.runner.run_workflow(
        basic_workflow.workflow, context=basic_workflow.initial_context
    )

    # Check final context
    assert result.context_snapshot.get("counter") == 3


@pytest.mark.asyncio
async def test_workflow_timing() -> None:
    """Test workflow execution timing and duration calculation."""
    workflow = ZumaWorkflow(
        "Timed Workflow",
        steps=[
            TimedStep("Quick Step", 0.1),
            TimedStep("Slow Step", 0.2),
        ],
    )

    runner = ZumaRunner()
    start_time = datetime.now()
    result = await runner.run_workflow(workflow)
    end_time = datetime.now()

    # Check timing
    assert result.start_time is not None
    assert result.end_time is not None
    assert result.duration is not None
    assert timedelta(seconds=0.3) <= (end_time - start_time) <= timedelta(seconds=0.5)


@pytest.mark.asyncio
async def test_workflow_validation() -> None:
    """Test workflow validation."""
    # Test empty workflow
    empty_workflow = ZumaWorkflow("Empty", steps=[])
    assert len(empty_workflow.validate()) > 0

    # Test valid workflow
    valid_workflow = ZumaWorkflow("Valid", steps=[TimedStep("Step")])
    assert len(valid_workflow.validate()) == 0


@pytest.mark.asyncio
async def test_workflow_dry_run(basic_workflow: TestContext) -> None:
    """Test workflow dry run functionality."""
    result = await basic_workflow.runner.run_workflow(
        basic_workflow.workflow, context=basic_workflow.initial_context, dry_run=True
    )

    assert result.status == ZumaExecutionStatus.SUCCESS
    # In dry run, context should not be modified
    assert result.context_snapshot == basic_workflow.initial_context


@pytest.mark.asyncio
async def test_workflow_metadata() -> None:
    """Test workflow metadata handling."""
    metadata = {"owner": "test", "priority": "high"}
    workflow = ZumaWorkflow(
        "Metadata Workflow",
        steps=[TimedStep("Step")],
        description="Test workflow",
        metadata=metadata,
    )

    runner = ZumaRunner()
    result = await runner.run_workflow(workflow)

    assert result.metadata.get("owner") == "test"
    assert result.metadata.get("priority") == "high"


@pytest.mark.asyncio
async def test_workflow_error_handling(error_workflow: TestContext) -> None:
    """Test workflow error handling."""
    result = await error_workflow.runner.run_workflow(
        error_workflow.workflow, context=error_workflow.initial_context
    )

    assert result.status == ZumaExecutionStatus.FAILED
    assert result.error is not None
    assert "Simulated error" in result.error


@pytest.mark.asyncio
async def test_workflow_result_serialization(basic_workflow: TestContext) -> None:
    """Test workflow result serialization."""
    result = await basic_workflow.runner.run_workflow(
        basic_workflow.workflow, context=basic_workflow.initial_context
    )

    # Test JSON serialization
    json_str = result.to_json()
    assert "step_name" in json_str
    assert "status" in json_str
    assert "children" in json_str

    # Test dictionary conversion
    dict_result = result.to_dict()
    assert dict_result["step_name"] == "Basic Workflow"
    assert dict_result["status"] == "SUCCESS"
    assert len(dict_result["children"]) == 3
