"""
Simple Sequential Workflow Example

This example demonstrates:
1. Creating basic action steps
2. Building a sequential workflow
3. Running the workflow with the ZumaRunner
"""

import asyncio
from typing import Any, Dict

import json

from loguru import logger

from zuma import ZumaActionStep, ZumaRunner, ZumaWorkflow


class DataFetchStep(ZumaActionStep):
    """Step that simulates fetching data from a source"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Fetching data...")
        # Simulate network delay
        await asyncio.sleep(1)
        return {"data": "fetched_data_123"}


class ProcessingStep(ZumaActionStep):
    """Step that processes the fetched data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data")
        logger.info(f"[{self.name}] Processing data: {data}")
        # Simulate processing
        await asyncio.sleep(0.5)
        return {"processed_data": f"processed_{data}"}


class ResultSaveStep(ZumaActionStep):
    """Step that saves the processed results"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        processed_data = context.get("processed_data")
        logger.info(f"[{self.name}] Saving results: {processed_data}")
        # Simulate database save
        await asyncio.sleep(0.3)
        return {"saved": True, "timestamp": "2024-03-14T12:00:00Z"}


class GetEmailStep(ZumaActionStep):
    """Step to get email of the user"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        return {"email": "john_doe@example.com"}


class SendEmailStep(ZumaActionStep):
    """Step to send email of the user"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        email = context.get("email")
        logger.info(
            f" [{self.name}] Sending email to {email}... with data: {context['processed_data']}"
        )
        return {"sent": True, "email": email}


async def run_simple_workflow():
    """Creates and runs a simple sequential workflow"""

    # Create workflow with sequential steps
    workflow = ZumaWorkflow(
        "Simple Sequential Workflow",
        steps=[
            DataFetchStep("Fetch Data"),
            ProcessingStep("Process Data"),
            ResultSaveStep("Save Results"),
            ZumaWorkflow(
                "Email Workflow",
                steps=[
                    GetEmailStep("Get Email"),
                    SendEmailStep("Send Email"),
                ],
            ),
        ],
    )

    # Create runner and execute workflow
    runner = ZumaRunner()
    result = await runner.run_workflow(workflow, diagram_output="workflow_in_workflow")

    # Get detailed JSON result
    detailed_result = runner.create_detailed_result_json(result)
    with open("result.json", "w") as f:
        json.dump(detailed_result, f, indent=2)

    # Print execution summary
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    # Run the workflow
    asyncio.run(run_simple_workflow())
