"""
Dynamic Workflow Example

This example demonstrates:
1. Creating workflows with dynamic steps
2. Adding steps based on conditions
3. Runtime workflow modification
4. Context-based workflow decisions
"""

import asyncio
import random
from typing import Any, Dict, List

from zuma import ZumaActionStep, ZumaRunner, ZumaWorkflow


class DataAnalysisStep(ZumaActionStep):
    """Analyzes data and determines required processing steps"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        print(f"[{self.name}] Analyzing {len(data)} records...")
        await asyncio.sleep(0.3)  # Simulate analysis

        # Determine required processing based on data
        needs_cleaning = any(x is None for x in data)
        has_outliers = any(x > 100 or x < -100 for x in data if x is not None)
        requires_normalization = max(abs(x) for x in data if x is not None) > 1000

        return {
            "analysis_complete": True,
            "needs_cleaning": needs_cleaning,
            "has_outliers": has_outliers,
            "requires_normalization": requires_normalization,
        }


class DataCleaningStep(ZumaActionStep):
    """Cleans data by removing None values"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        print(f"[{self.name}] Cleaning data...")
        await asyncio.sleep(0.2)

        cleaned_data = [x for x in data if x is not None]
        return {"data": cleaned_data, "removed_values": len(data) - len(cleaned_data)}


class OutlierRemovalStep(ZumaActionStep):
    """Removes outliers from the dataset"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        print(f"[{self.name}] Removing outliers...")
        await asyncio.sleep(0.2)

        filtered_data = [x for x in data if -100 <= x <= 100]
        return {"data": filtered_data, "removed_outliers": len(data) - len(filtered_data)}


class DataNormalizationStep(ZumaActionStep):
    """Normalizes data to a -1 to 1 range"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        print(f"[{self.name}] Normalizing data...")
        await asyncio.sleep(0.2)

        max_abs = max(abs(x) for x in data)
        normalized_data = [x / max_abs for x in data]
        return {"data": normalized_data, "normalization_factor": max_abs}


def build_dynamic_workflow(initial_data: List[float]) -> ZumaWorkflow:
    """Builds a workflow based on initial data characteristics"""
    steps = [DataAnalysisStep("Analyze Data")]

    # We'll add more steps based on the analysis results
    workflow = ZumaWorkflow(
        "Dynamic Data Processing",
        steps=steps,
        description="A workflow that adapts to data characteristics",
    )

    return workflow


async def run_dynamic_workflow():
    """Run the dynamic workflow example"""
    # Generate sample data with some characteristics that will trigger different steps
    data = [random.uniform(-1000, 1000) if random.random() > 0.1 else None for _ in range(100)]

    # Create initial workflow
    workflow = build_dynamic_workflow(data)
    runner = ZumaRunner()

    # First run to analyze data
    context = {"data": data}
    result = await runner.run_workflow(workflow, context, diagram_output="dynamic_workflow")

    # Based on analysis results, add necessary steps
    if result.context_snapshot.get("needs_cleaning"):
        workflow.steps.append(DataCleaningStep("Clean Data"))

    if result.context_snapshot.get("has_outliers"):
        workflow.steps.append(OutlierRemovalStep("Remove Outliers"))

    if result.context_snapshot.get("requires_normalization"):
        workflow.steps.append(DataNormalizationStep("Normalize Data"))

    # Run the complete workflow
    print("\n[ZUMA] Running complete workflow with dynamic steps...")
    final_result = await runner.run_workflow(workflow, context, diagram_output="dynamic_workflow")
    runner.print_execution_summary(final_result)
    return final_result


if __name__ == "__main__":
    asyncio.run(run_dynamic_workflow())
