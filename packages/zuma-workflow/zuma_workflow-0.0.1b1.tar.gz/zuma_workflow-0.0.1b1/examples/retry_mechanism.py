"""
Retry Mechanism Example

This example demonstrates:
1. Different retry strategies
2. Custom retry policies
3. Timeout handling
4. Exponential backoff
"""

import asyncio
import random
import time
from typing import Any, Dict

from zuma import ZumaActionStep, ZumaExecutionError, ZumaRunner, ZumaWorkflow


class UnreliableAPIStep(ZumaActionStep):
    """Simulates an unreliable API with random failures"""

    def __init__(self, name: str, failure_rate: float = 0.7):
        super().__init__(
            name=name,
            description="Simulates API calls with random failures",
            retries=5,  # Try up to 5 times
            retry_delay=1.0,  # Wait 1 second between retries
        )
        self.failure_rate = failure_rate
        self.attempt = 0

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        self.attempt += 1
        print(f"[{self.name}] Attempt {self.attempt} to call API...")

        if random.random() < self.failure_rate and self.attempt < 5:
            raise ZumaExecutionError("API request failed - service unavailable")

        await asyncio.sleep(0.5)  # Simulate API call
        return {"api_response": "success", "attempts": self.attempt}


class ExponentialBackoffStep(ZumaActionStep):
    """Demonstrates exponential backoff retry strategy"""

    def __init__(self, name: str):
        super().__init__(
            name=name,
            description="Uses exponential backoff for retries",
            retries=4,  # Try up to 4 times
            retry_delay=1.0,  # Initial delay of 1 second
            retry_backoff=2.0,  # Double the delay after each retry
        )
        self.attempt = 0

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        self.attempt += 1
        print(f"[{self.name}] Attempt {self.attempt} with {self.retry_delay}s delay...")

        if self.attempt < 4:  # Succeed on the 4th attempt
            raise ZumaExecutionError(f"Operation failed - retrying with {self.retry_delay}s delay")

        await asyncio.sleep(0.5)  # Simulate operation
        return {"operation": "success", "attempts": self.attempt}


class TimeoutStep(ZumaActionStep):
    """Demonstrates timeout handling with retries"""

    def __init__(self, name: str):
        super().__init__(
            name=name,
            description="Handles timeouts with retries",
            retries=3,
            retry_delay=1.0,
            timeout=2.0,  # Operation times out after 2 seconds
        )
        self.attempt = 0

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        self.attempt += 1
        print(f"[{self.name}] Attempt {self.attempt} with {self.timeout}s timeout...")

        # Simulate varying response times
        response_time = random.uniform(1.0, 3.0)
        if response_time > self.timeout:
            raise ZumaExecutionError(f"Operation timed out after {self.timeout} seconds")

        await asyncio.sleep(response_time)
        return {
            "operation": "success",
            "response_time": response_time,
            "attempts": self.attempt,
        }


class CustomRetryStep(ZumaActionStep):
    """Demonstrates custom retry logic"""

    def __init__(self, name: str):
        super().__init__(
            name=name,
            description="Uses custom retry strategy",
            retries=5,
        )
        self.attempt = 0
        self.start_time = None

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        if self.start_time is None:
            self.start_time = time.time()

        self.attempt += 1
        elapsed = time.time() - self.start_time
        print(f"[{self.name}] Attempt {self.attempt} after {elapsed:.1f}s from start...")

        # Custom failure conditions
        if elapsed < 5.0:  # Fail for the first 5 seconds
            raise ZumaExecutionError("Operation not yet ready")

        await asyncio.sleep(0.5)  # Simulate operation
        return {
            "operation": "success",
            "attempts": self.attempt,
            "total_time": elapsed,
        }


async def run_retry_examples():
    """Run examples of different retry mechanisms"""

    # Create workflow with different retry strategies
    workflow = ZumaWorkflow(
        "Retry Mechanisms Demo",
        steps=[
            UnreliableAPIStep("Unreliable API"),
            ExponentialBackoffStep("Exponential Backoff"),
            TimeoutStep("Timeout Handler"),
            CustomRetryStep("Custom Retry Logic"),
        ],
        continue_on_failure=False,  # Stop on first permanent failure
    )

    # Run workflow
    runner = ZumaRunner()
    result = await runner.run_workflow(workflow, diagram_output="retry_mechanism")
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    asyncio.run(run_retry_examples())
