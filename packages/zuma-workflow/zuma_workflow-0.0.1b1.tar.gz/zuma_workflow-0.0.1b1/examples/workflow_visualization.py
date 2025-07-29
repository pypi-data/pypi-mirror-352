"""
Workflow Visualization Example

This example demonstrates:
1. Basic workflow visualization
2. Retry mechanism visualization
3. Parallel processing visualization
4. Nested workflow visualization
"""

import asyncio
import random
from typing import Dict, Any

from zuma import (
    ZumaWorkflow,
    ZumaActionStep,
    ZumaParallelAction,
    ZumaRunner,
    ZumaExecutionError,
)


class UnreliableAPIStep(ZumaActionStep):
    """Simulates an unreliable API with random failures"""

    def __init__(self, name: str, failure_rate: float = 0.7):
        super().__init__(
            name=name,
            description="Simulates API calls with random failures",
            retries=3,  # Try up to 3 times
            retry_delay=1.0,  # Wait 1 second between retries
        )
        self.failure_rate = failure_rate
        self.attempt = 0
        # Randomly choose which attempt will succeed (1-based)
        self.successful_attempt = random.randint(1, 3)

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        self.attempt += 1
        print(f"[{self.name}] Attempt {self.attempt} to call API...")

        # Force success on the chosen attempt
        if self.attempt == self.successful_attempt:
            await asyncio.sleep(0.5)  # Simulate API call
            return {"api_response": "success", "attempts": self.attempt}

        # Otherwise use random failure rate
        if random.random() < self.failure_rate:
            raise ZumaExecutionError("API request failed - service unavailable")

        await asyncio.sleep(0.5)  # Simulate API call
        return {"api_response": "success", "attempts": self.attempt}


class ValidationStep(ZumaActionStep):
    """Validates the success of previous operation"""

    def __init__(self, name: str):
        super().__init__(name=name, description="Validates operation success")

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        # Check if we have the expected success indicators from previous step
        if "api_response" in context:
            print(f"[{self.name}] Operation succeeded and connected successfully")
            return {"validation": "success"}
        else:
            raise ZumaExecutionError("Failed to validate operation success")


class ParallelProcessingStep(ZumaActionStep):
    """Processes data in parallel"""

    def __init__(self, name: str, process_time: float = 0.5):
        super().__init__(name=name, description="Parallel data processing")
        self.process_time = process_time

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Processing data...")
        await asyncio.sleep(self.process_time)  # Simulate processing
        return {"processed": True}


async def run_visualization_examples():
    """Run examples of different workflow visualizations"""

    # Create parallel processing workflow
    parallel_workflow = ZumaWorkflow(
        "Parallel Processing",
        steps=[
            ZumaParallelAction(
                "Data Processing",
                steps=[
                    ParallelProcessingStep("Process CSV"),
                    ParallelProcessingStep("Process JSON"),
                    ParallelProcessingStep("Process XML"),
                ],
                max_concurrency=2,  # Process 2 file types at a time
            )
        ],
    )

    # Create retry workflow
    retry_workflow = ZumaWorkflow(
        "Retry Mechanism Demo",
        steps=[
            UnreliableAPIStep("API Call"),
            ValidationStep("API Validation"),
        ],
    )

    # Create combined workflow
    combined_workflow = ZumaWorkflow(
        "Combined Workflow Demo",
        steps=[
            parallel_workflow,
            retry_workflow,
        ],
    )

    # Run workflows and generate diagrams
    runner = ZumaRunner()

    # Generate diagram for parallel processing
    result = await runner.run_workflow(
        parallel_workflow,
        generate_diagram=True,
        diagram_output="parallel_processing",
    )
    runner.print_execution_summary(result)

    # Generate diagram for retry mechanism
    result = await runner.run_workflow(
        retry_workflow,
        generate_diagram=True,
        diagram_output="retry_mechanism",
    )
    runner.print_execution_summary(result)

    # Generate diagram for combined workflow
    result = await runner.run_workflow(
        combined_workflow,
        generate_diagram=True,
        diagram_output="combined_workflow",
    )
    runner.print_execution_summary(result)


if __name__ == "__main__":
    asyncio.run(run_visualization_examples())
