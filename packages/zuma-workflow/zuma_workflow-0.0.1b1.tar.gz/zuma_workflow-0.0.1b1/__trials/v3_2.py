import asyncio
import inspect
import json
import random
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field


# Enhanced enums for better type safety
class ZumaExecutionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class ZumaComponentType(Enum):
    WORKFLOW = "Workflow"
    PARALLEL_ACTION = "ParallelAction"
    ACTION = "Action"
    CONDITIONAL = "Conditional"


# Custom exceptions
class ZumaExecutionError(Exception):
    """Custom exception to signal Zuma workflow execution failure."""

    def __init__(self, message: str, component_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.component_name = component_name
        self.original_error = original_error


class ZumaValidationError(Exception):
    """Exception for Zuma workflow validation errors."""

    pass


# Enhanced result tracking with dataclass
class ZumaResult(BaseModel):
    """Represents the execution result of a Zuma workflow component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: ZumaComponentType
    status: ZumaExecutionStatus = ZumaExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    children: List["ZumaResult"] = Field(default_factory=list)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state (success, failed, cancelled)."""
        return self.status in {
            ZumaExecutionStatus.SUCCESS,
            ZumaExecutionStatus.FAILED,
            ZumaExecutionStatus.CANCELLED,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with improved serialization."""
        result = {
            "step_name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
        }

        if self.error:
            result["error"] = self.error
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_json(self, indent: int = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


# Context manager for better resource handling
@contextmanager
def zuma_execution_context(component_name: str, use_logger: bool = True):
    """Zuma context manager for tracking execution lifecycle."""
    if use_logger:
        logger.info(f"[ZUMA] Starting execution: {component_name}")
    start_time = datetime.now()
    try:
        yield
        if use_logger:
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"[ZUMA] Completed execution: {component_name} ({duration:.2f}s)")
    except Exception as e:
        if use_logger:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"[ZUMA] Failed execution: {component_name} ({duration:.2f}s) - {e}")
        raise


class ZumaComponent(ABC):
    """
    Enhanced base class for Zuma workflow components with better error handling,
    validation, and execution tracking.
    """

    def __init__(self, name: str, description: str = None, metadata: Dict[str, Any] = None):
        self.name = name
        self.description = description or f"{self.__class__.__name__}: {name}"
        self.metadata = metadata or {}
        self.zuma_result_children: List[ZumaResult] = []

    @property
    def component_type(self) -> ZumaComponentType:
        """Get the component type for this instance."""
        type_mapping = {
            "ZumaWorkflow": ZumaComponentType.WORKFLOW,
            "ZumaParallelAction": ZumaComponentType.PARALLEL_ACTION,
            "ZumaActionStep": ZumaComponentType.ACTION,
            "ZumaConditionalStep": ZumaComponentType.CONDITIONAL,
        }
        return type_mapping.get(self.__class__.__name__, ZumaComponentType.ACTION)

    @abstractmethod
    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Execute the component and return updated context."""
        pass

    def validate(self) -> List[str]:
        """Validate component configuration. Return list of validation errors."""
        errors = []
        if not self.name or not self.name.strip():
            errors.append("Zuma component name cannot be empty")
        return errors

    async def _execute_impl(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        indent: int = 0,
        dry_run: bool = False,
    ) -> ZumaResult:
        """Enhanced execution implementation with better error handling."""
        component_result = ZumaResult(
            name=self.name, type=self.component_type, metadata=self.metadata.copy()
        )

        # Validation
        validation_errors = self.validate()
        if validation_errors:
            component_result.status = ZumaExecutionStatus.FAILED
            component_result.error = f"Zuma validation failed: {'; '.join(validation_errors)}"
            return component_result

        component_result.start_time = datetime.now()
        component_result.status = ZumaExecutionStatus.RUNNING

        indent_str = " " * indent
        logger.info(f"[ZUMA] {indent_str}>>> Executing: {self.name} ({self.component_type.value})")

        if dry_run:
            logger.info(f"[ZUMA] {indent_str}    [DRY RUN MODE]")
            component_result.status = ZumaExecutionStatus.SKIPPED
            component_result.end_time = datetime.now()
            return component_result

        try:
            with zuma_execution_context(self.name):
                # Prepare execution parameters
                sig = inspect.signature(self.execute)
                kwargs_to_pass = self._prepare_execution_kwargs(sig, context, dependencies, indent)

                # Execute the component
                step_result_context = await self.execute(**kwargs_to_pass)

                # Validate returned context
                if not isinstance(step_result_context, dict):
                    raise ZumaExecutionError(
                        f"Zuma component {self.name} must return a dictionary, got {type(step_result_context)}",
                        self.name,
                    )

                # Update context with results
                context.update(step_result_context)
                component_result.status = ZumaExecutionStatus.SUCCESS

        except Exception as e:
            component_result.status = ZumaExecutionStatus.FAILED
            component_result.error = str(e)
            logger.error(f"[ZUMA] {indent_str}!!! Error in {self.name}: {e}")
            logger.error(f"[ZUMA] Execution failed for {self.name}: {e}")

        finally:
            component_result.end_time = datetime.now()
            component_result.context_snapshot = context.copy()

            # Attach children results if available
            if hasattr(self, "zuma_result_children") and self.zuma_result_children:
                component_result.children = self.zuma_result_children

        return component_result

    def _prepare_execution_kwargs(
        self,
        signature,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        indent: int,
    ) -> Dict[str, Any]:
        """Prepare keyword arguments for execution based on method signature."""
        kwargs_to_pass = {}

        # Standard parameters
        for param_name in ["context", "dependencies", "indent"]:
            if param_name in signature.parameters:
                kwargs_to_pass[param_name] = locals()[param_name]

        # Handle ZumaActionStep specific parameters
        if isinstance(self, ZumaActionStep):
            # Add configured kwargs
            for key, value in self._action_kwargs.items():
                if key in signature.parameters:
                    kwargs_to_pass[key] = value

            # Handle positional arguments
            if self._action_args and len(self._action_args) > 0:
                first_positional_param = self._get_first_positional_param(signature)
                if first_positional_param:
                    kwargs_to_pass[first_positional_param] = self._action_args[0]

        return kwargs_to_pass

    def _get_first_positional_param(self, signature) -> Optional[str]:
        """Get the first positional parameter name from signature."""
        excluded_params = {"context", "dependencies", "indent", "kwargs", "self"}
        for param_name, param in signature.parameters.items():
            if (
                param_name not in excluded_params
                and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ):
                return param_name
        return None


class ZumaActionStep(ZumaComponent):
    """Enhanced Zuma action step with better parameter handling."""

    def __init__(
        self,
        *args,
        description: str = None,
        retries: int = 0,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        name = kwargs.pop("name", self.__class__.__name__)
        super().__init__(name, description)
        self._action_args = args
        self._action_kwargs = kwargs
        self.retries = retries
        self.timeout = timeout

    def validate(self) -> List[str]:
        """Validate Zuma action step configuration."""
        errors = super().validate()
        if self.retries < 0:
            errors.append("Zuma action retries must be non-negative")
        if self.timeout is not None and self.timeout <= 0:
            errors.append("Zuma action timeout must be positive")
        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Default implementation - subclasses should override."""
        raise NotImplementedError(
            f"Subclasses of ZumaActionStep must implement the execute method. "
            f"Class {self.__class__.__name__} has not implemented this method."
        )


class ZumaConditionalStep(ZumaComponent):
    """New Zuma component for conditional execution."""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        true_component: ZumaComponent,
        false_component: ZumaComponent = None,
    ):
        super().__init__(name, f"Zuma Conditional: {name}")
        self.condition = condition
        self.true_component = true_component
        self.false_component = false_component

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Execute Zuma conditional logic."""
        try:
            condition_result = self.condition(context)
            selected_component = self.true_component if condition_result else self.false_component

            if selected_component:
                logger.info(
                    f"[ZUMA] {' ' * indent}Condition evaluated to {condition_result}, executing: {selected_component.name}"
                )
                result = await selected_component._execute_impl(context, dependencies, indent + 2)
                self.zuma_result_children = [result]

                if result.status == ZumaExecutionStatus.FAILED:
                    raise ZumaExecutionError(
                        f"Zuma conditional branch failed: {selected_component.name}"
                    )

                return result.context_snapshot
            else:
                logger.info(
                    f"[ZUMA] {' ' * indent}Condition evaluated to {condition_result}, no component to execute"
                )
                return {}

        except Exception as e:
            raise ZumaExecutionError(f"Zuma conditional evaluation failed: {str(e)}", self.name, e)


class ZumaParallelAction(ZumaComponent):
    """Enhanced Zuma parallel execution with better failure handling."""

    def __init__(
        self,
        name: str,
        steps: List[ZumaComponent],
        fail_fast: bool = True,
        max_concurrency: Optional[int] = None,
    ):
        super().__init__(name, f"Zuma Parallel execution: {name}")
        self.steps = steps
        self.fail_fast = fail_fast  # Whether to stop on first failure
        self.max_concurrency = max_concurrency

    def validate(self) -> List[str]:
        """Validate Zuma parallel action configuration."""
        errors = super().validate()
        if not self.steps:
            errors.append("ZumaParallelAction must have at least one step")
        if self.max_concurrency is not None and self.max_concurrency < 1:
            errors.append("Zuma max_concurrency must be positive")

        # Validate child components
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            for error in step_errors:
                errors.append(f"Zuma Step {i} ({step.name}): {error}")

        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Enhanced Zuma parallel execution with concurrency control."""
        logger.info(f"[ZUMA] {' ' * indent}=== Starting Zuma Parallel Actions: {self.name} ===")

        if self.max_concurrency:
            semaphore = asyncio.Semaphore(self.max_concurrency)

            async def limited_execute(step):
                async with semaphore:
                    return await step._execute_impl(context.copy(), dependencies, indent + 2)

            tasks = [limited_execute(step) for step in self.steps]
        else:
            tasks = [
                step._execute_impl(context.copy(), dependencies, indent + 2) for step in self.steps
            ]

        if self.fail_fast:
            try:
                self.zuma_result_children = await asyncio.gather(*tasks, return_exceptions=False)
            except Exception as e:
                # Handle partial results in case of failure
                completed_tasks = [task for task in tasks if task.done()]
                self.zuma_result_children = []
                for task in completed_tasks:
                    try:
                        result = await task
                        self.zuma_result_children.append(result)
                    except:
                        pass
                raise ZumaExecutionError(
                    f"Zuma parallel execution failed in {self.name}: {str(e)}",
                    self.name,
                    e,
                )
        else:
            # Gather with exception handling - don't fail fast
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.zuma_result_children = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create a failed result for the exception
                    failed_result = ZumaResult(
                        name=self.steps[i].name,
                        type=self.steps[i].component_type,
                        status=ZumaExecutionStatus.FAILED,
                        error=str(result),
                    )
                    self.zuma_result_children.append(failed_result)
                else:
                    self.zuma_result_children.append(result)

        # Merge successful results into context
        successful_results = [
            r for r in self.zuma_result_children if r.status == ZumaExecutionStatus.SUCCESS
        ]
        failed_results = [
            r for r in self.zuma_result_children if r.status == ZumaExecutionStatus.FAILED
        ]

        # Update context with successful results
        for result in successful_results:
            context.update(result.context_snapshot)

        logger.info(
            f"[ZUMA] {' ' * indent}=== Completed Zuma Parallel Actions: {self.name} "
            f"(Success: {len(successful_results)}, Failed: {len(failed_results)}) ==="
        )

        if failed_results and self.fail_fast:
            raise ZumaExecutionError(
                f"Zuma parallel action {self.name} had {len(failed_results)} failed steps"
            )

        return context


class ZumaWorkflow(ZumaComponent):
    """Enhanced Zuma workflow with better control flow and error handling."""

    def __init__(
        self,
        name: str,
        steps: List[ZumaComponent],
        continue_on_failure: bool = False,
        description: str = None,
    ):
        super().__init__(name, description or f"Zuma Workflow: {name}")
        self.steps = steps
        self.continue_on_failure = continue_on_failure

    def validate(self) -> List[str]:
        """Validate Zuma workflow configuration."""
        errors = super().validate()
        if not self.steps:
            errors.append("Zuma workflow must have at least one step")

        # Validate child components
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            for error in step_errors:
                errors.append(f"Zuma Step {i} ({step.name}): {error}")

        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Enhanced Zuma workflow execution with better error handling."""
        logger.info(f"[ZUMA] {' ' * indent}=== Starting Zuma Workflow: {self.name} ===")

        self.zuma_result_children = []
        workflow_failed = False

        for i, step in enumerate(self.steps):
            if workflow_failed and not self.continue_on_failure:
                # Mark remaining steps as cancelled
                cancelled_result = ZumaResult(
                    name=step.name,
                    type=step.component_type,
                    status=ZumaExecutionStatus.CANCELLED,
                )
                self.zuma_result_children.append(cancelled_result)
                continue

            try:
                step_result = await step._execute_impl(context, dependencies, indent + 2)
                self.zuma_result_children.append(step_result)

                if step_result.status == ZumaExecutionStatus.FAILED:
                    if not self.continue_on_failure:
                        logger.info(
                            f"[ZUMA] {' ' * indent}--- Zuma Workflow {self.name} halted at step: {step.name} ---"
                        )
                        workflow_failed = True
                    else:
                        logger.info(
                            f"[ZUMA] {' ' * indent}--- Zuma Step {step.name} failed, but continuing workflow ---"
                        )

            except Exception as e:
                # Create failed result for unexpected exceptions
                failed_result = ZumaResult(
                    name=step.name,
                    type=step.component_type,
                    status=ZumaExecutionStatus.FAILED,
                    error=str(e),
                )
                self.zuma_result_children.append(failed_result)

                if not self.continue_on_failure:
                    workflow_failed = True
                    logger.info(
                        f"[ZUMA] {' ' * indent}--- Zuma Workflow {self.name} halted due to exception in {step.name}: {e} ---"
                    )

        successful_steps = len(
            [r for r in self.zuma_result_children if r.status == ZumaExecutionStatus.SUCCESS]
        )
        failed_steps = len(
            [r for r in self.zuma_result_children if r.status == ZumaExecutionStatus.FAILED]
        )

        logger.info(
            f"[ZUMA] {' ' * indent}=== Completed Zuma Workflow: {self.name} "
            f"(Success: {successful_steps}, Failed: {failed_steps}) ==="
        )

        if workflow_failed and not self.continue_on_failure:
            raise ZumaExecutionError(f"Zuma Workflow '{self.name}' failed due to step failure")

        return context


# Enhanced Zuma workflow runner with better reporting
class ZumaRunner:
    """Enhanced Zuma workflow runner with comprehensive execution tracking."""

    async def run_workflow(
        self,
        workflow: ZumaWorkflow,
        context: Dict[str, Any] = None,
        dependencies: Dict[str, Any] = None,
        dry_run: bool = False,
    ) -> ZumaResult:
        """Run a Zuma workflow with comprehensive error handling and reporting."""
        context = context or {}
        dependencies = dependencies or {}

        # Validate workflow before execution
        validation_errors = workflow.validate()
        if validation_errors:
            logger.error(f"[ZUMA] Workflow validation failed: {validation_errors}")
            raise ZumaValidationError(
                f"Zuma workflow validation failed: {'; '.join(validation_errors)}"
            )

        logger.info(
            f"[ZUMA] Starting Zuma workflow execution: {workflow.name}"
            + (" (DRY RUN)" if dry_run else "")
        )

        try:
            result = await workflow._execute_impl(context, dependencies, dry_run=dry_run)

            if result.status == ZumaExecutionStatus.SUCCESS:
                logger.info(f"[ZUMA] Zuma workflow completed successfully: {workflow.name}")
            else:
                logger.warning(
                    f"[ZUMA] Zuma workflow completed with status {result.status.value}: {workflow.name}"
                )

            return result

        except Exception as e:
            logger.error(f"[ZUMA] Zuma workflow execution failed: {workflow.name} - {e}")
            raise

    def create_detailed_result_json(self, result: ZumaResult) -> Dict[str, Any]:
        """Create detailed JSON result without context and dependencies."""
        result_dict = {
            "step_name": result.name,
            "type": result.type.value,
            "status": result.status.value,
            "start_time": result.start_time.isoformat() if result.start_time else None,
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration_seconds": result.duration,
        }

        if result.error:
            result_dict["error"] = result.error

        if result.metadata:
            result_dict["metadata"] = result.metadata

        if result.children:
            result_dict["children"] = [
                self.create_detailed_result_json(child) for child in result.children
            ]

        return result_dict

    def print_execution_summary(self, result: ZumaResult, indent: int = 0):
        """Print a comprehensive Zuma execution summary."""
        indent_str = "  " * indent
        status_symbol = {
            ZumaExecutionStatus.SUCCESS: "✓",
            ZumaExecutionStatus.FAILED: "✗",
            ZumaExecutionStatus.CANCELLED: "○",
            ZumaExecutionStatus.SKIPPED: "→",
            ZumaExecutionStatus.PENDING: "?",
            ZumaExecutionStatus.RUNNING: "…",
        }

        symbol = status_symbol.get(result.status, "?")
        duration_str = f" ({result.duration:.2f}s)" if result.duration else ""

        logger.info(
            f"[ZUMA] {indent_str}{symbol} {result.name} [{result.status.value}]{duration_str}"
        )

        if result.error:
            logger.error(f"[ZUMA] {indent_str}  Error: {result.error}")

        for child in result.children:
            self.print_execution_summary(child, indent + 1)


# Scenario 1: Parallel Execution with Fake Load (Sleep)
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

    async def execute(
        self, context: Dict[str, Any], batch_id: int = 0, should_fail: bool = False
    ) -> Dict[str, Any]:
        processing_time = random.uniform(0.1, 0.5)  # Random processing time

        logger.info(f"[ZUMA] Processing batch {batch_id:02d} (estimated {processing_time:.2f}s)")
        await asyncio.sleep(processing_time)

        if should_fail:
            raise ZumaExecutionError(
                f"Batch {batch_id:02d} failed due to simulated error", self.name
            )

        processed_items = random.randint(50, 200)
        logger.info(f"[ZUMA] Batch {batch_id:02d} processed {processed_items} items")

        return {
            f"batch_{batch_id:02d}_processed": processed_items,
            f"batch_{batch_id:02d}_duration": processing_time,
        }


# Scenario 4: Actions that can fail
class ZumaValidationAction(ZumaActionStep):
    """Action that validates data and can fail"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[ZUMA] Validating input data...")
        await asyncio.sleep(0.2)

        # Simulate validation failure
        if not context.get("valid_input", True):
            raise ZumaExecutionError("Input validation failed - missing required fields", self.name)

        return {"validation_passed": True}


class ZumaDataProcessAction(ZumaActionStep):
    """Action that processes data"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[ZUMA] Processing validated data...")
        await asyncio.sleep(0.3)

        if not context.get("validation_passed"):
            raise ZumaExecutionError("Cannot process - validation not passed", self.name)

        return {"data_processed": True, "record_count": 1500}


class ZumaDatabaseSaveAction(ZumaActionStep):
    """Action that saves to database and can fail"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
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
            ZumaActionStep(name="FinalCleanup"),  # This will fail since it's not implemented
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
class ZumaFinalCleanupAction(ZumaActionStep):
    """Cleanup action that completes the workflow"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[ZUMA] Performing final cleanup...")
        await asyncio.sleep(0.1)

        saved_records = context.get("saved_records", 0)
        logger.info(f"[ZUMA] Cleanup complete. Total records processed: {saved_records}")

        return {"cleanup_completed": True, "final_status": "success"}


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
            logger.info(f"\n[ZUMA] Starting {scenario_name}...")
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
    # Run individual scenarios or all at once

    # Run single scenario:
    # asyncio.run(run_scenario_1_parallel_with_load())
    # asyncio.run(run_scenario_2_parallel_20_actions())
    # asyncio.run(run_scenario_3_parallel_20_with_failures())
    # asyncio.run(run_scenario_4_normal_workflow_with_failure())

    # Run all scenarios:
    asyncio.run(run_all_scenarios())
