"""Tests for conditional execution functionality."""

import asyncio
from typing import Any

import pytest

from zuma import ZumaActionStep, ZumaConditionalStep, ZumaExecutionStatus, ZumaRunner, ZumaWorkflow


class ValueStep(ZumaActionStep):
    """A step that sets a specific value in the context."""

    def __init__(self, name: str, value: Any):
        super().__init__(name=name)
        self.value = value

    async def execute(self, context: dict[str, Any], **kwargs) -> dict[str, Any]:
        await asyncio.sleep(0.1)
        return {"value": self.value, "step": self.name}


@pytest.mark.asyncio
async def test_basic_conditional() -> None:
    """Test basic conditional execution."""

    def check_value(context: dict[str, Any]) -> bool:
        return context.get("value", 0) > 5

    conditional = ZumaConditionalStep(
        "Value Check",
        condition=check_value,
        true_component=ValueStep("High Value", 10),
        false_component=ValueStep("Low Value", 1),
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[conditional])
    runner = ZumaRunner()

    # Test true path
    result = await runner.run_workflow(workflow, context={"value": 7})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.children[0].children[-1].name == "High Value"
    assert result.context_snapshot["value"] == 10

    # Test false path
    result = await runner.run_workflow(workflow, context={"value": 3})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.children[0].children[-1].name == "Low Value"
    assert result.context_snapshot["value"] == 1


@pytest.mark.asyncio
async def test_conditional_without_false_branch() -> None:
    """Test conditional execution without a false branch."""

    def check_value(context: dict[str, Any]) -> bool:
        return context.get("value", 0) > 5

    conditional = ZumaConditionalStep(
        "Value Check",
        condition=check_value,
        true_component=ValueStep("High Value", 10),
        false_component=None,
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[conditional])
    runner = ZumaRunner()

    # Test true path
    result = await runner.run_workflow(workflow, context={"value": 7})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.children[0].children[-1].name == "High Value"

    # Test false path (should skip execution)
    result = await runner.run_workflow(workflow, context={"value": 3})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert len(result.children[0].children) == 1  # Only the condition check
    assert result.context_snapshot == {"value": 3}  # Context unchanged


@pytest.mark.asyncio
async def test_nested_conditionals() -> None:
    """Test nested conditional execution."""

    def check_value(context: dict[str, Any]) -> bool:
        return context.get("value", 0) > 5

    def check_even(context: dict[str, Any]) -> bool:
        return context.get("value", 0) % 2 == 0

    inner_conditional = ZumaConditionalStep(
        "Even Check",
        condition=check_even,
        true_component=ValueStep("Even Value", 100),
        false_component=ValueStep("Odd Value", 99),
    )

    outer_conditional = ZumaConditionalStep(
        "Value Check",
        condition=check_value,
        true_component=inner_conditional,
        false_component=ValueStep("Low Value", 1),
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[outer_conditional])
    runner = ZumaRunner()

    # Test high even path
    result = await runner.run_workflow(workflow, context={"value": 8})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.context_snapshot["value"] == 100

    # Test high odd path
    result = await runner.run_workflow(workflow, context={"value": 7})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.context_snapshot["value"] == 99

    # Test low path
    result = await runner.run_workflow(workflow, context={"value": 3})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.context_snapshot["value"] == 1


@pytest.mark.asyncio
async def test_conditional_context_handling() -> None:
    """Test context handling in conditional execution."""

    def check_value(context: dict[str, Any]) -> bool:
        # Modify context during condition check
        context["checked"] = True
        return context.get("value", 0) > 5

    conditional = ZumaConditionalStep(
        "Value Check",
        condition=check_value,
        true_component=ValueStep("High Value", 10),
        false_component=ValueStep("Low Value", 1),
    )

    workflow = ZumaWorkflow("Test Workflow", steps=[conditional])
    runner = ZumaRunner()

    result = await runner.run_workflow(workflow, context={"value": 7})
    assert result.status == ZumaExecutionStatus.SUCCESS
    assert result.context_snapshot["checked"] is True  # Condition check modification preserved
    assert result.context_snapshot["value"] == 10  # Step execution modification preserved
