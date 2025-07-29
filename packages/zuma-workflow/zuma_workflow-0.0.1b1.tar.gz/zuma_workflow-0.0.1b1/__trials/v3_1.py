import asyncio
import inspect
import json
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


import asyncio
import inspect
import json
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


# Example action implementations
class ZumaOpenPortal(ZumaActionStep):
    def __init__(self, portal_type: str = "default"):
        super().__init__(
            name="ZumaOpenPortal",
            description=f"Opens {portal_type} portal via Zuma",
            portal_type=portal_type,
        )

    async def execute(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        portal_type: str = "default",
    ) -> Dict[str, Any]:
        db_connection = dependencies.get("db_connection", "No DB Connection")
        logger.info(f"[ZUMA] Opening {portal_type} portal using {db_connection}...")
        await asyncio.sleep(0.1)
        return {"portal_open": True, "portal_type": portal_type}


class ZumaClosePortal(ZumaActionStep):
    async def execute(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver", "No Selenium Driver")
        logger.info(f"[ZUMA] Closing portal using {selenium_driver}...")
        await asyncio.sleep(0.1)
        return {"portal_closed": True}


class ZumaSearchAction(ZumaActionStep):
    def __init__(self, search_term: str = "default"):
        super().__init__(
            name="ZumaSearchAction",
            description=f"Zuma search for: {search_term}",
            search_term=search_term,
        )

    async def execute(
        self, context: Dict[str, Any], search_term: str = "default"
    ) -> Dict[str, Any]:
        logger.info(f"[ZUMA] Performing search for '{search_term}' in form...")
        await asyncio.sleep(0.1)
        return {
            "search_result": f"Zuma results found for '{search_term}'",
            "search_term": search_term,
        }


class ZumaSwitchToDraft(ZumaActionStep):
    async def execute(self) -> Dict[str, Any]:
        logger.info("[ZUMA] Switching to draft mode...")
        await asyncio.sleep(0.1)
        return {"mode": "draft"}


class ZumaEditFields(ZumaActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        mode = context.get("mode", "unknown")
        logger.info(f"[ZUMA] Editing fields in {mode} mode...")
        await asyncio.sleep(0.1)
        return {"fields_edited": True, "edit_mode": mode}


class ZumaConditionalSave(ZumaActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        should_save = context.get("fields_edited", False)
        if should_save:
            logger.info("[ZUMA] Saving changes (fields were edited)...")
            await asyncio.sleep(0.1)
            return {"saved": True, "save_reason": "fields_edited"}
        else:
            logger.info("[ZUMA] Skipping save (no fields edited)...")
            return {"saved": False, "save_reason": "no_changes"}


# Example usage
async def zuma_example():
    """Example usage of Zuma workflow engine."""

    runner = ZumaRunner()

    # Example 1: Basic Zuma workflow
    basic_workflow = ZumaWorkflow(
        "Basic Portal Workflow",
        steps=[
            ZumaOpenPortal("admin"),
            ZumaSearchAction("user_data"),
            ZumaSwitchToDraft(),
            ZumaEditFields(),
            ZumaConditionalSave(),
            ZumaClosePortal(),
        ],
    )

    # Example 2: Complex workflow with parallel execution
    complex_workflow = ZumaWorkflow(
        "Complex Data Processing",
        steps=[
            ZumaOpenPortal("data"),
            ZumaParallelAction(
                "Parallel Data Operations",
                steps=[
                    ZumaSearchAction("dataset_1"),
                    ZumaSearchAction("dataset_2"),
                    ZumaSearchAction("dataset_3"),
                ],
                fail_fast=False,
                max_concurrency=2,
            ),
            ZumaEditFields(),
            ZumaConditionalStep(
                "Save if Edited",
                condition=lambda ctx: ctx.get("fields_edited", False),
                true_component=ZumaConditionalSave(),
                false_component=None,
            ),
            ZumaClosePortal(),
        ],
    )

    # Setup context and dependencies
    context = {"user_id": "demo_user", "session_id": "abc123"}
    dependencies = {
        "db_connection": "PostgreSQL Connection Pool",
        "selenium_driver": "Chrome WebDriver v91",
        "api_client": "REST API Client",
    }

    # Run workflows
    workflows = [
        ("Basic Zuma Workflow", basic_workflow),
        ("Complex Zuma Workflow", complex_workflow),
    ]

    all_results = []

    for workflow_name, workflow in workflows:
        logger.info(f"[ZUMA] {'='*60}")
        logger.info(f"[ZUMA] Running: {workflow_name}")
        logger.info(f"[ZUMA] {'='*60}")

        try:
            result = await runner.run_workflow(workflow, context.copy(), dependencies)

            logger.info(f"[ZUMA] --- Execution Summary for {workflow_name} ---")
            runner.print_execution_summary(result)

            # Create detailed result dictionary
            workflow_result = {
                "workflow_name": workflow_name,
                "execution_result": runner.create_detailed_result_json(result),
                "execution_status": result.status.value,
                "total_duration_seconds": result.duration,
                "execution_timestamp": (
                    result.start_time.isoformat() if result.start_time else None
                ),
            }

            all_results.append(workflow_result)

        except Exception as e:
            logger.error(f"[ZUMA] Workflow failed with exception: {e}")

    # Print final JSON results
    logger.info("[ZUMA] " + "=" * 80)
    logger.info("[ZUMA] WORKFLOW EXECUTION RESULTS (JSON)")
    logger.info("[ZUMA] " + "=" * 80)
    print(json.dumps(all_results, indent=2, default=str))

    return all_results


if __name__ == "__main__":
    asyncio.run(zuma_example())
