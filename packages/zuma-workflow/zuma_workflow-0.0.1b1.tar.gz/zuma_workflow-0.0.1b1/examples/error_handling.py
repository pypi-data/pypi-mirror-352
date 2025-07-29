"""
Error Handling Example

This example demonstrates:
1. Error handling in workflow steps
2. Retry mechanisms
3. Continue-on-failure behavior
4. Custom error handling
"""

import asyncio
import random
from typing import Any, Dict

from zuma import ZumaActionStep, ZumaExecutionError, ZumaRunner, ZumaWorkflow


class ValidatingStep(ZumaActionStep):
    """Step that validates input data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        data = context.get("data")
        print(f"[{self.name}] Validating data: {data}")

        if not self.validate_data(data):
            raise ZumaExecutionError("Data validation failed")

        return {"validated": True, "data": data}

    def validate_data(self, data):
        return isinstance(data, str) and len(data) > 0


class UnreliableNetworkStep(ZumaActionStep):
    """Step that simulates unreliable network operations"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Attempting network operation...")

        # Simulate random network failures
        if random.random() < 0.5:  # 50% chance of failure
            raise ZumaExecutionError("Network connection failed")

        await asyncio.sleep(0.5)  # Simulate network delay
        return {"network_status": "connected", "timestamp": "2024-03-14T12:00:00Z"}


class DatabaseSaveStep(ZumaActionStep):
    """Step that simulates database operations"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        if not context.get("validated"):
            raise ZumaExecutionError("Cannot save unvalidated data")

        data = context.get("data")
        print(f"[{self.name}] Saving data to database: {data}")
        await asyncio.sleep(0.3)  # Simulate database operation

        return {"saved": True, "timestamp": "2024-03-14T12:00:00Z"}


async def run_error_handling_workflow():
    """Run the error handling workflow"""
    workflow = ZumaWorkflow(
        "Error Handling Workflow",
        steps=[
            ValidatingStep("Validate Data", description="Validates input data format", retries=3),
            UnreliableNetworkStep(
                "Network Operation",
                description="Performs unreliable network operation",
                retries=5,
                timeout=1.0,
            ),
            DatabaseSaveStep(
                "Save to Database",
                description="Saves validated data to database",
                retries=2,
            ),
        ],
        continue_on_failure=True,
    )

    # Run workflow with sample data
    initial_context = {
        "data": "sample_data_123"  # Valid data
        # "data": None  # Invalid data to trigger validation error
    }

    runner = ZumaRunner()
    result = await runner.run_workflow(
        workflow, context=initial_context, diagram_output="error_handling"
    )
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    asyncio.run(run_error_handling_workflow())
