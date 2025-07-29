"""Common test fixtures and configuration."""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import pytest

from zuma import (
    ZumaActionStep,
    ZumaResult,
    ZumaRunner,
    ZumaWorkflow,
)


@dataclass
class TestContext:
    """Test context with common attributes."""

    workflow: ZumaWorkflow
    runner: ZumaRunner
    initial_context: dict[str, Any]


@pytest.fixture
async def runner() -> ZumaRunner:
    """Provide a ZumaRunner instance."""
    return ZumaRunner()


@pytest.fixture
async def basic_workflow(runner: ZumaRunner) -> AsyncIterator[TestContext]:
    """Provide a basic workflow with simple steps."""

    class SimpleStep(ZumaActionStep):
        async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
            await asyncio.sleep(0.1)  # Simulate work
            return {"counter": context.get("counter", 0) + 1}

    workflow = ZumaWorkflow(
        "Basic Workflow",
        steps=[
            SimpleStep("Step 1"),
            SimpleStep("Step 2"),
            SimpleStep("Step 3"),
        ],
    )

    context = TestContext(workflow=workflow, runner=runner, initial_context={"counter": 0})

    yield context


@pytest.fixture
async def error_workflow(runner: ZumaRunner) -> AsyncIterator[TestContext]:
    """Provide a workflow that includes error scenarios."""

    class ErrorStep(ZumaActionStep):
        async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
            raise ValueError("Simulated error")

    workflow = ZumaWorkflow(
        "Error Workflow", steps=[ErrorStep("Error Step")], continue_on_failure=True
    )

    context = TestContext(workflow=workflow, runner=runner, initial_context={})

    yield context
