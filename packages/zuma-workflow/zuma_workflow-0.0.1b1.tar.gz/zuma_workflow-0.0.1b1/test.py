import asyncio
import random
from typing import Any, Dict

from loguru import logger

from zuma import (
    ZumaActionStep,
    ZumaExecutionError,
    ZumaParallelAction,
    ZumaRunner,
    ZumaWorkflow,
)


class ZumaFakeLoadAction(ZumaActionStep):
    """Action that simulates work with sleep delays"""

    def __init__(self, task_name: str, load_seconds: float = 1.0):
        super().__init__(
            name=f"FakeLoad_{task_name}",
            description=f"Simulates {load_seconds}s load for {task_name}",
            task_name=task_name,
            load_seconds=load_seconds,
        )

    async def execute(
        self,
        context: Dict[str, Any],
        task_name: str = "unknown",
        load_seconds: float = 1.0,
    ) -> Dict[str, Any]:
        logger.info(f"[ZUMA] Starting fake load task: {task_name} ({load_seconds}s)")
        await asyncio.sleep(load_seconds)
        result_data = f"completed_task_{task_name}_{random.randint(100, 999)}"
        logger.info(f"[ZUMA] Completed fake load task: {task_name}")
        return {f"result_{task_name}": result_data, "task_duration": load_seconds}


# Scenario 2 & 3: Batch Processing Action (for 20 actions)
class ZumaBatchProcessAction(ZumaActionStep):
    """Action for batch processing scenarios"""

    def __init__(self, batch_id: int, should_fail: bool = False):
        super().__init__(
            name=f"BatchProcess_{batch_id:02d}",
            description=f"Batch processing task {batch_id}",
            batch_id=batch_id,
            should_fail=should_fail,
        )
        self.batch_id = batch_id
        self.should_fail = should_fail

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        processing_time = random.uniform(0.1, 0.5)  # Random processing time

        logger.info(
            f"[ZUMA] Processing batch {self.batch_id:02d} (estimated {processing_time:.2f}s)"
        )
        await asyncio.sleep(processing_time)

        if self.should_fail:
            raise ZumaExecutionError(
                f"Batch {self.batch_id:02d} failed due to simulated error", self.name
            )

        processed_items = random.randint(50, 200)
        logger.info(f"[ZUMA] Batch {self.batch_id:02d} processed {processed_items} items")

        return {
            f"batch_{self.batch_id:02d}_processed": processed_items,
            f"batch_{self.batch_id:02d}_duration": processing_time,
        }


# Scenario 4: Actions that can fail
class ZumaValidationAction(ZumaActionStep):
    """Action that validates data and can fail"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        logger.info("[ZUMA] Validating input data...")
        await asyncio.sleep(0.2)

        # Simulate validation failure
        if not context.get("valid_input", True):
            raise ZumaExecutionError("Input validation failed - missing required fields", self.name)

        return {"validation_passed": True}


class ZumaDataProcessAction(ZumaActionStep):
    """Action that processes data"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        logger.info("[ZUMA] Processing validated data...")
        await asyncio.sleep(0.3)

        if not context.get("validation_passed"):
            raise ZumaExecutionError("Cannot process - validation not passed", self.name)

        return {"data_processed": True, "record_count": 1500}


class ZumaDatabaseSaveAction(ZumaActionStep):
    """Action that saves to database and can fail"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        logger.info("[ZUMA] Saving to database...")
        await asyncio.sleep(0.4)

        # Simulate database connection failure
        if context.get("simulate_db_failure", False):
            raise ZumaExecutionError("Database connection timeout", self.name)

        record_count = context.get("record_count", 0)
        return {"saved_to_db": True, "saved_records": record_count}


async def run_scenario_1_parallel_with_load():
    """Scenario 1: Parallel execution with fake load (sleep)"""

    logger.info("[ZUMA] " + "=" * 60)
    logger.info("[ZUMA] SCENARIO 1: Parallel Execution with Fake Load")
    logger.info("[ZUMA] " + "=" * 60)

    workflow = ZumaWorkflow(
        "Parallel Load Testing",
        steps=[
            ZumaParallelAction(
                "Heavy Load Tasks",
                steps=[
                    ZumaFakeLoadAction("DatabaseQuery", 2.0),
                    ZumaFakeLoadAction("APICall", 1.5),
                    ZumaFakeLoadAction("FileProcessing", 2.5),
                    ZumaFakeLoadAction("ImageResize", 1.8),
                    ZumaFakeLoadAction("DataValidation", 1.2),
                ],
                fail_fast=True,
                max_concurrency=3,  # Limit concurrent tasks
            )
        ],
    )

    runner = ZumaRunner()
    context = {"test_scenario": "parallel_load"}
    dependencies = {"system_resources": "available"}

    result = await runner.run_workflow(workflow, context, dependencies)
    runner.print_execution_summary(result)
    return result


async def run_scenario_2_parallel_20_actions():
    """Scenario 2: Parallel execution with 20 actions"""

    logger.info("[ZUMA] " + "=" * 60)
    logger.info("[ZUMA] SCENARIO 2: Parallel Execution - 20 Actions")
    logger.info("[ZUMA] " + "=" * 60)

    # Create 20 batch processing actions
    batch_actions = [ZumaBatchProcessAction(i + 1, should_fail=False) for i in range(20)]

    workflow = ZumaWorkflow(
        "Massive Batch Processing",
        steps=[
            ZumaParallelAction(
                "20 Batch Operations",
                steps=batch_actions,
                fail_fast=False,  # Continue even if some fail
                max_concurrency=5,  # Process 5 at a time
            )
        ],
    )

    runner = ZumaRunner()
    context = {"batch_size": 20, "processing_mode": "parallel"}
    dependencies = {"worker_pool": "initialized", "queue_manager": "active"}

    result = await runner.run_workflow(workflow, context, dependencies)
    runner.print_execution_summary(result)
    return result


async def run_scenario_3_parallel_20_with_failures():
    """Scenario 3: Parallel execution with 20 actions, some randomly fail"""

    logger.info("[ZUMA] " + "=" * 60)
    logger.info("[ZUMA] SCENARIO 3: Parallel Execution - 20 Actions with Random Failures")
    logger.info("[ZUMA] " + "=" * 60)

    # Create 20 batch actions, randomly set some to fail
    batch_actions = []
    failed_batches = random.sample(range(1, 21), 5)  # Randomly select 5 to fail

    for i in range(20):
        batch_id = i + 1
        should_fail = batch_id in failed_batches
        batch_actions.append(ZumaBatchProcessAction(batch_id, should_fail=should_fail))

    logger.info(f"[ZUMA] Batches that will fail: {sorted(failed_batches)}")

    workflow = ZumaWorkflow(
        "Batch Processing with Failures",
        steps=[
            ZumaParallelAction(
                "20 Batch Operations (Some Will Fail)",
                steps=batch_actions,
                fail_fast=False,  # Continue processing despite failures
                max_concurrency=4,
            )
        ],
    )

    runner = ZumaRunner()
    context = {"batch_size": 20, "fault_tolerance": "enabled"}
    dependencies = {"retry_mechanism": "disabled", "error_handler": "log_only"}

    result = await runner.run_workflow(workflow, context, dependencies)
    runner.print_execution_summary(result)
    return result


async def run_scenario_4_normal_workflow_with_failure():
    """Scenario 4: Normal workflow with failure scenario"""

    logger.info("[ZUMA] " + "=" * 60)
    logger.info("[ZUMA] SCENARIO 4: Normal Workflow with Failure")
    logger.info("[ZUMA] " + "=" * 60)

    workflow = ZumaWorkflow(
        "Data Processing Pipeline",
        steps=[
            ZumaValidationAction(name="InputValidation"),
            ZumaDataProcessAction(name="DataProcessing"),
            ZumaDatabaseSaveAction(name="DatabaseSave"),
            ZumaFinalCleanup(name="FinalCleanup"),  # Using the proper implementation
        ],
        continue_on_failure=False,  # Stop on first failure
    )

    runner = ZumaRunner()

    # Test with valid scenario first
    logger.info("[ZUMA] --- Testing SUCCESS scenario ---")
    context_success = {"valid_input": True, "simulate_db_failure": False}
    dependencies = {"database": "connected", "validator": "ready"}

    try:
        result_success = await runner.run_workflow(workflow, context_success, dependencies)
        runner.print_execution_summary(result_success)
    except Exception as e:
        logger.error(f"[ZUMA] Expected failure in success scenario: {e}")

    # Test with failure scenario
    logger.info("[ZUMA] --- Testing FAILURE scenario ---")
    context_failure = {
        "valid_input": False,  # This will cause validation to fail
        "simulate_db_failure": True,
    }

    try:
        result_failure = await runner.run_workflow(workflow, context_failure, dependencies)
        runner.print_execution_summary(result_failure)
    except Exception as e:
        logger.error(f"[ZUMA] Workflow failed as expected: {e}")

    return None


# Implementation of missing FinalCleanup action for completeness
class ZumaFinalCleanup(ZumaActionStep):
    """Action that performs final cleanup"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        logger.info("[ZUMA] Performing final cleanup...")
        await asyncio.sleep(0.1)
        return {"cleanup_completed": True}


async def run_all_scenarios():
    """Run all four scenarios"""

    logger.info("[ZUMA] " + "=" * 80)
    logger.info("[ZUMA] RUNNING ALL WORKFLOW SCENARIOS")
    logger.info("[ZUMA] " + "=" * 80)

    scenarios = [
        ("Scenario 1: Parallel with Load", run_scenario_1_parallel_with_load),
        ("Scenario 2: 20 Parallel Actions", run_scenario_2_parallel_20_actions),
        (
            "Scenario 3: 20 Parallel with Failures",
            run_scenario_3_parallel_20_with_failures,
        ),
        (
            "Scenario 4: Normal with Failure",
            run_scenario_4_normal_workflow_with_failure,
        ),
    ]

    results = {}

    for scenario_name, scenario_func in scenarios:
        try:
            logger.info(f"[ZUMA] Starting {scenario_name}...")
            start_time = asyncio.get_event_loop().time()

            result = await scenario_func()

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            results[scenario_name] = {
                "status": "completed",
                "duration": duration,
                "result": result.to_dict() if result else None,
            }

            logger.info(f"[ZUMA] {scenario_name} completed in {duration:.2f}s")

        except Exception as e:
            results[scenario_name] = {
                "status": "failed",
                "error": str(e),
                "duration": 0,
            }
            logger.error(f"[ZUMA] {scenario_name} failed: {e}")

        # Brief pause between scenarios
        await asyncio.sleep(1)

    # Print final summary
    logger.info("[ZUMA] " + "=" * 80)
    logger.info("[ZUMA] EXECUTION SUMMARY")
    logger.info("[ZUMA] " + "=" * 80)

    for scenario_name, result in results.items():
        status = result["status"]
        duration = result.get("duration", 0)

        if status == "completed":
            logger.info(f"[ZUMA] ✓ {scenario_name}: {status.upper()} ({duration:.2f}s)")
        else:
            logger.error(
                f"[ZUMA] ✗ {scenario_name}: {status.upper()} - {result.get('error', 'Unknown error')}"
            )

    return results


# Example usage
if __name__ == "__main__":
    # Run all scenarios by default
    asyncio.run(run_all_scenarios())

    # Individual scenarios can be run by uncommenting:
    # asyncio.run(run_scenario_1_parallel_with_load())
    # asyncio.run(run_scenario_2_parallel_20_actions())
    # asyncio.run(run_scenario_3_parallel_20_with_failures())
    # asyncio.run(run_scenario_4_normal_workflow_with_failure())
