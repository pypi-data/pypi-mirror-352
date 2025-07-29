"""
Workflow Composition Example

This example demonstrates:
1. Creating reusable workflow components
2. Composing workflows together
3. Sharing context between workflows
4. Nested workflow execution
"""

import asyncio
import random
from typing import Any, Dict, List

from zuma import ZumaActionStep, ZumaExecutionError, ZumaRunner, ZumaWorkflow


class DataFetchStep(ZumaActionStep):
    """Fetches data from a simulated source"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Fetching data...")
        await asyncio.sleep(0.3)

        # Simulate fetching data
        data = [random.randint(1, 100) for _ in range(20)]
        return {"raw_data": data}


class DataValidationStep(ZumaActionStep):
    """Validates fetched data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("raw_data", [])
        print(f"[{self.name}] Validating {len(data)} records...")
        await asyncio.sleep(0.2)

        if not data:
            raise ZumaExecutionError("No data to validate")

        # Validate data range
        invalid_values = [x for x in data if x < 1 or x > 100]
        if invalid_values:
            raise ZumaExecutionError(f"Found {len(invalid_values)} invalid values")

        return {"validated_data": data, "validation_passed": True}


class DataTransformStep(ZumaActionStep):
    """Transforms validated data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("validated_data", [])
        print(f"[{self.name}] Transforming data...")
        await asyncio.sleep(0.2)

        # Simple transformation: normalize to 0-1 range
        max_val = max(data)
        transformed_data = [x / max_val for x in data]

        return {"transformed_data": transformed_data}


class DataAggregationStep(ZumaActionStep):
    """Aggregates transformed data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("transformed_data", [])
        print(f"[{self.name}] Aggregating data...")
        await asyncio.sleep(0.2)

        return {
            "aggregated_results": {
                "count": len(data),
                "mean": sum(data) / len(data),
                "max": max(data),
                "min": min(data),
            }
        }


class ReportGenerationStep(ZumaActionStep):
    """Generates a report from aggregated data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        results = context.get("aggregated_results", {})
        print(f"[{self.name}] Generating report...")
        await asyncio.sleep(0.3)

        report = {
            "title": "Data Processing Report",
            "timestamp": context.get("processing_start_time"),
            "metrics": results,
            "status": "SUCCESS",
        }

        return {"report": report}


def create_data_processing_workflow() -> ZumaWorkflow:
    """Creates a reusable data processing workflow"""
    return ZumaWorkflow(
        "Data Processing",
        steps=[
            DataFetchStep("Fetch Data"),
            DataValidationStep("Validate Data"),
            DataTransformStep("Transform Data"),
        ],
        description="Fetches and processes data",
    )


def create_reporting_workflow() -> ZumaWorkflow:
    """Creates a reusable reporting workflow"""
    return ZumaWorkflow(
        "Reporting",
        steps=[
            DataAggregationStep("Aggregate Data"),
            ReportGenerationStep("Generate Report"),
        ],
        description="Generates reports from processed data",
    )


class WorkflowCompositionStep(ZumaActionStep):
    """Step that composes and executes multiple workflows"""

    def __init__(self, name: str, workflows: List[ZumaWorkflow]):
        super().__init__(
            name=name,
            description="Composes multiple workflows",
        )
        self.workflows = workflows

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Starting composed workflow execution...")

        runner = ZumaRunner()
        final_context = context.copy()

        for workflow in self.workflows:
            print(f"[{self.name}] Executing workflow: {workflow.name}")
            result = await runner.run_workflow(workflow, final_context)

            if result.status == "FAILED":
                raise ZumaExecutionError(f"Workflow {workflow.name} failed: {result.error}")

            # Merge results into context for next workflow
            final_context.update(result.context)

        return final_context


async def run_composed_workflows():
    """Demonstrates workflow composition"""

    # Create component workflows
    data_workflow = create_data_processing_workflow()
    reporting_workflow = create_reporting_workflow()

    # Create main workflow that composes the others
    main_workflow = ZumaWorkflow(
        "Main Workflow",
        steps=[
            WorkflowCompositionStep(
                "Process and Report",
                workflows=[data_workflow, reporting_workflow],
            ),
        ],
        description="Main workflow that composes other workflows",
    )

    # Run the composed workflow
    runner = ZumaRunner()
    context = {"processing_start_time": "2024-03-14T12:00:00"}

    print("\n[ZUMA] Starting composed workflow execution...")
    result = await runner.run_workflow(
        main_workflow, context, diagram_output="workflow_composition"
    )
    runner.print_execution_summary(result)

    # Print the final report
    if result.status == "SUCCESS" and "report" in result.context:
        print("\n[ZUMA] Final Report:")
        for key, value in result.context["report"].items():
            print(f"  {key}: {value}")

    return result


if __name__ == "__main__":
    asyncio.run(run_composed_workflows())
