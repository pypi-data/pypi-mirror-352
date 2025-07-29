"""
Simple Sequential Workflow Example

This example demonstrates:
1. Creating basic action steps
2. Building a sequential workflow
3. Running the workflow with the ZumaRunner
"""

import asyncio
from typing import Any, Dict

from zuma import ZumaActionStep, ZumaRunner, ZumaWorkflow


class DataFetchStep(ZumaActionStep):
    """Step that simulates fetching data from a source"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Fetching data...")
        # Simulate network delay
        await asyncio.sleep(1)
        return {"data": "fetched_data_123"}


class ProcessingStep(ZumaActionStep):
    """Step that processes the fetched data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data")
        print(f"[{self.name}] Processing data: {data}")
        # Simulate processing
        await asyncio.sleep(0.5)
        return {"processed_data": f"processed_{data}"}


class ResultSaveStep(ZumaActionStep):
    """Step that saves the processed results"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        processed_data = context.get("processed_data")
        print(f"[{self.name}] Saving results: {processed_data}")
        # Simulate database save
        await asyncio.sleep(0.3)
        return {"saved": True, "timestamp": "2024-03-14T12:00:00Z"}


async def run_simple_workflow():
    """Creates and runs a simple sequential workflow"""

    # Create workflow with sequential steps
    workflow = ZumaWorkflow(
        "Simple Sequential Workflow",
        steps=[
            DataFetchStep("Fetch Data"),
            ProcessingStep("Process Data"),
            ResultSaveStep("Save Results"),
        ],
    )

    # Create runner and execute workflow
    runner = ZumaRunner()
    result = await runner.run_workflow(workflow, diagram_output="simple")

    # Print execution summary
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    # Run the workflow
    asyncio.run(run_simple_workflow())
