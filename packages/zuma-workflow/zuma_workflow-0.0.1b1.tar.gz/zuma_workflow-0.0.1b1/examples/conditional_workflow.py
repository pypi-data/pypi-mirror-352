"""
Conditional Workflow Example

This example demonstrates:
1. Conditional branching in workflows
2. State management between steps
3. Dynamic decision making
4. Different processing paths
"""

import asyncio
from typing import Any, Dict

from zuma import (
    ZumaActionStep,
    ZumaConditionalStep,
    ZumaRunner,
    ZumaWorkflow,
)


class DataLoadStep(ZumaActionStep):
    """Loads and measures the size of input data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        # Simulate loading data
        data = context.get("input_data", list(range(2000)))
        print(f"[{self.name}] Loading {len(data)} items...")
        await asyncio.sleep(0.5)

        return {"data": data, "data_size": len(data)}


class BatchProcessingStep(ZumaActionStep):
    """Handles large dataset processing in batches"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        batch_size = 100

        print(f"[{self.name}] Processing {len(data)} items in batches...")
        processed = []

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            await asyncio.sleep(0.1)  # Simulate batch processing
            processed.extend([f"processed_{item}" for item in batch])

        return {
            "processed_items": len(processed),
            "processing_type": "batch",
            "results": processed,
        }


class SimpleProcessingStep(ZumaActionStep):
    """Handles small dataset processing"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data", [])
        print(f"[{self.name}] Processing {len(data)} items directly...")
        await asyncio.sleep(0.5)  # Simulate processing

        processed = [f"processed_{item}" for item in data]
        return {
            "processed_items": len(processed),
            "processing_type": "simple",
            "results": processed,
        }


class ResultSaveStep(ZumaActionStep):
    """Saves the processed results"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        processing_type = context.get("processing_type", "unknown")
        processed_items = context.get("processed_items", 0)

        print(
            f"[{self.name}] Saving results: {processed_items} items processed using {processing_type} method"
        )
        await asyncio.sleep(0.3)  # Simulate save operation

        return {
            "saved": True,
            "timestamp": "2024-03-14T12:00:00Z",
            "summary": {"items": processed_items, "method": processing_type},
        }


def check_data_size(context: Dict[str, Any]) -> bool:
    """Determines processing path based on data size"""
    return context.get("data_size", 0) > 1000


async def run_conditional_workflow():
    """Run the conditional workflow"""
    workflow = ZumaWorkflow(
        "Conditional Processing Workflow",
        steps=[
            DataLoadStep("Load Data"),
            ZumaConditionalStep(
                "Processing Path Decision",
                condition=check_data_size,
                true_component=BatchProcessingStep("Batch Process"),
                false_component=SimpleProcessingStep("Simple Process"),
            ),
            ResultSaveStep("Save Results"),
        ],
    )

    # Run workflow with sample data
    initial_context = {"input_data": list(range(2000))}  # Large dataset to trigger batch processing

    runner = ZumaRunner()
    result = await runner.run_workflow(
        workflow, context=initial_context, diagram_output="conditional_workflow"
    )
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    asyncio.run(run_conditional_workflow())
