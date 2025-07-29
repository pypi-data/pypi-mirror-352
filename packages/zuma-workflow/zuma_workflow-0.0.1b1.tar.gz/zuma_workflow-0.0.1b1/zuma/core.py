import asyncio
import inspect
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import shutil

from loguru import logger

from .exception import ZumaExecutionError, ZumaValidationError
from .types import ZumaComponentType, ZumaExecutionStatus, ZumaResult


class ZumaContextProcessor(ABC):
    """Base class for context processors that transform data between steps."""

    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process and transform the context data.

        Args:
            context: The current workflow context

        Returns:
            The processed context
        """
        pass

    def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make the processor callable for convenience."""
        return self.process(context)


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
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        required_contexts: List[str] = None,
        **kwargs,
    ):
        name = kwargs.pop("name", self.__class__.__name__)
        super().__init__(name, description)
        self._action_args = args
        self._action_kwargs = kwargs
        self.retries = retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._progress = {"completed": 0, "total": 0, "message": ""}
        self.required_contexts = required_contexts or []

    def update_progress(self, completed: int, total: int, message: str = None):
        """Update progress information for this step."""
        self._progress["completed"] = completed
        self._progress["total"] = total
        if message:
            self._progress["message"] = message

        # Update metadata with progress information
        self.metadata.update(
            {
                "progress": {
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total * 100) if total > 0 else 0,
                    "message": message or self._progress["message"],
                }
            }
        )

        # Log progress update
        percentage = (completed / total * 100) if total > 0 else 0
        logger.info(
            f"[ZUMA] Progress - {self.name}: {completed}/{total} ({percentage:.1f}%) "
            f"{message if message else ''}"
        )

    async def _execute_with_retry(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Execute with retry logic."""
        last_error = None
        attempt = 0

        while attempt <= self.retries:
            try:
                if attempt > 0:
                    logger.info(
                        f"[ZUMA] Retrying {self.name} (Attempt {attempt + 1}/{self.retries + 1})"
                    )
                    await asyncio.sleep(self.retry_delay)

                if self.timeout:
                    # Execute with timeout
                    try:
                        async with asyncio.timeout(self.timeout):
                            return await self.execute(context, dependencies, **kwargs)
                    except asyncio.TimeoutError:
                        raise ZumaExecutionError(
                            f"Step {self.name} timed out after {self.timeout} seconds"
                        )
                else:
                    # Execute without timeout
                    return await self.execute(context, dependencies, **kwargs)

            except Exception as e:
                last_error = e
                attempt += 1
                if attempt <= self.retries:
                    logger.warning(
                        f"[ZUMA] Step {self.name} failed (attempt {attempt}/{self.retries + 1}): {str(e)}"
                    )
                else:
                    break

        # If we get here, all retries failed
        raise ZumaExecutionError(
            f"Step {self.name} failed after {attempt} attempts: {str(last_error)}",
            self.name,
            last_error,
        )

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

        # Validate required contexts
        missing_contexts = self._validate_context(context)
        if missing_contexts:
            component_result.status = ZumaExecutionStatus.FAILED
            component_result.error = f"Missing required contexts: {', '.join(missing_contexts)}"
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
                # Execute the component with retry logic
                step_result_context = await self._execute_with_retry(context, dependencies)

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

    def validate(self) -> List[str]:
        """Validate Zuma action step configuration."""
        errors = super().validate()
        if self.retries < 0:
            errors.append("Zuma action retries must be non-negative")
        if self.timeout is not None and self.timeout <= 0:
            errors.append("Zuma action timeout must be positive")
        if self.retry_delay < 0:
            errors.append("Zuma retry delay must be non-negative")
        return errors

    def _validate_context(self, context: Dict[str, Any]) -> List[str]:
        """Validate that all required context keys are present."""
        missing_contexts = []
        for required_key in self.required_contexts:
            if required_key not in context:
                missing_contexts.append(required_key)
        return missing_contexts

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Optional[Dict[str, Any]]:
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
        context_processors: List[ZumaContextProcessor] = None,
    ):
        super().__init__(name, description or f"Zuma Workflow: {name}")
        self.steps = steps
        self.continue_on_failure = continue_on_failure
        self.context_processors = context_processors or []

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

    def _apply_context_processors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all context processors to the context."""
        processed_context = context.copy()
        for processor in self.context_processors:
            try:
                processed_context = processor(processed_context)
                if not isinstance(processed_context, dict):
                    raise ZumaExecutionError(
                        f"Context processor {processor.__class__.__name__} must return a dictionary"
                    )
            except Exception as e:
                raise ZumaExecutionError(
                    f"Context processor {processor.__class__.__name__} failed: {str(e)}"
                )
        return processed_context

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Enhanced Zuma workflow execution with better error handling."""
        logger.info(f"[ZUMA] {' ' * indent}=== Starting Zuma Workflow: {self.name} ===")

        self.zuma_result_children = []
        workflow_failed = False
        current_context = context.copy()

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
                # Apply context processors before step execution
                processed_context = self._apply_context_processors(current_context)

                step_result = await step._execute_impl(processed_context, dependencies, indent + 2)
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
                else:
                    # Update current context with step results
                    current_context.update(step_result.context_snapshot)

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

        return current_context


# Enhanced Zuma workflow runner with better reporting
class ZumaRunner:
    """Enhanced Zuma workflow runner with comprehensive execution tracking."""

    def __init__(self):
        self._check_graphviz_available()
        self.graphviz_available = False

    def _check_graphviz_available(self):
        """Check if Graphviz is installed and available."""
        dot_path = shutil.which("dot")
        self.graphviz_available = dot_path is not None
        if not self.graphviz_available:
            logger.warning(
                "[ZUMA] Graphviz is not installed or not in PATH. Workflow diagrams will be disabled. "
                "To enable diagrams, please install Graphviz:\n"
                "- Windows: Download from https://graphviz.org/download/\n"
                "- Linux: sudo apt-get install graphviz\n"
                "- macOS: brew install graphviz"
            )

    def _get_node_style(self, status: ZumaExecutionStatus) -> str:
        """Get node style based on status."""
        # Status colors in Mermaid format
        status_colors = {
            ZumaExecutionStatus.SUCCESS: "#00C853",
            ZumaExecutionStatus.FAILED: "#D50000",
            ZumaExecutionStatus.CANCELLED: "#757575",
            ZumaExecutionStatus.SKIPPED: "#FFB300",
            ZumaExecutionStatus.PENDING: "#2196F3",
            ZumaExecutionStatus.RUNNING: "#7B1FA2",
        }
        return status_colors.get(status, "#000000")

    def create_workflow_diagram(
        self, result: ZumaResult, output_file: str = "workflow_diagram"
    ) -> str:
        """Create a Mermaid workflow diagram definition file.

        Args:
            result: The ZumaResult object to visualize
            output_file: The output file path without extension

        Returns:
            The path to the generated Mermaid file
        """
        mermaid_lines = [
            "%%{init: {'theme': 'dark', 'themeVariables': { 'darkMode': true }}}%%",
            "flowchart TD",
            "    %% Global styles",
            "    linkStyle default stroke:#666666,stroke-width:1px",
        ]

        def get_simplified_name(name: str) -> str:
            """Get simplified name for the node by removing common prefixes/suffixes."""
            name = name.replace("DataValidationStep", "Data Validation")
            name = name.replace("DataProcessStep", "Process")
            name = name.replace("DataAggregationStep", "Data Aggregation")
            name = name.replace("DataFetchStep", "DataFetch")
            name = name.replace("Step", "")
            name = name.replace("Workflow", "")
            name = name.strip()
            return name

        def process_retry_workflow(result: ZumaResult, nodes: list, edges: list):
            """Process workflow nodes with retry attempts."""
            if not result.metadata.get("retries"):
                # If no retries, process normally
                return process_workflow(result, nodes, edges)

            # Add main flow nodes at the top
            main_node_id = f"{id(result)}_main"
            nodes.append(f'    {main_node_id}["{get_simplified_name(result.name)}"]')
            nodes.append(
                f"    style {main_node_id} fill:#2A2A2A,color:#FFFFFF,stroke:#666666,stroke-width:2px"
            )

            # Add validation node at the top (after main)
            validation_id = f"{id(result)}_validation"
            nodes.append(f"    {validation_id}[Validate]")
            nodes.append(
                f"    style {validation_id} fill:#2A2A2A,color:#FFFFFF,stroke:#666666,stroke-width:2px"
            )

            # Connect main flow at top
            edges.append(f"    {main_node_id} --> {validation_id}")

            # Create nodes for retry attempts below
            max_retries = result.metadata.get("retries", 0)
            last_attempt_id = None
            first_attempt_id = None

            for attempt in range(1, max_retries + 2):  # +2 for initial try and error handler
                attempt_id = f"{id(result)}_attempt_{attempt}"
                if attempt <= max_retries + 1:
                    nodes.append(f"    {attempt_id}[Attempt {attempt}]")
                    nodes.append(
                        f"    style {attempt_id} fill:#2A2A2A,color:#FFFFFF,stroke:#666666,stroke-width:2px"
                    )

                    if not first_attempt_id:
                        first_attempt_id = attempt_id
                        # Connect main node to first retry attempt
                        edges.append(f"    {main_node_id} -.-|Fail| {attempt_id}")

                    # Connect attempts in sequence
                    if last_attempt_id:
                        edges.append(f"    {last_attempt_id} -.-|Fail| {attempt_id}")

                    # Connect success back to validation
                    edges.append(f"    {attempt_id} -->|Success| {validation_id}")

                    last_attempt_id = attempt_id

            # Add error handler at the bottom
            error_id = f"{id(result)}_error"
            nodes.append(f"    {error_id}[Handle Error]")
            nodes.append(
                f"    style {error_id} fill:#2A2A2A,color:#FFFFFF,stroke:#666666,stroke-width:2px"
            )

            # Connect last attempt to error handler
            edges.append(f"    {last_attempt_id} -.-|Fail| {error_id}")
            # Error handler rejoins at validation
            edges.append(f"    {error_id} --> {validation_id}")

            return [validation_id]

        def process_workflow(result: ZumaResult, nodes: list, edges: list, parent_id: str = None):
            """Process workflow nodes and edges."""
            # Check if this is a retry workflow
            if result.metadata.get("retries") is not None:
                return process_retry_workflow(result, nodes, edges)

            current_id = str(id(result))

            # Create node label with simplified name
            label = get_simplified_name(result.name)
            if result.duration and result.duration > 0.01:  # Only show significant durations
                label += f"<br/>({result.duration:.2f}s)"

            # Add the node
            nodes.append(f'    {current_id}["{label}"]')
            style = self._get_node_style(result.status)
            nodes.append(
                f"    style {current_id} fill:#2A2A2A,color:#FFFFFF,stroke:{style},stroke-width:2px"
            )

            # Connect to parent if exists
            if parent_id:
                edges.append(f"    {parent_id} --> {current_id}")

            # Process children
            last_id = current_id
            for child in result.children:
                child_ends = process_workflow(child, nodes, edges, current_id)
                if child_ends:
                    last_id = child_ends[0]

            return [last_id]

        # Process workflow
        edges = []
        last_ids = process_workflow(result, nodes := [], edges, None)

        # Combine nodes and edges
        mermaid_lines.extend(nodes)
        mermaid_lines.extend(edges)

        # Write to file
        output_path = f"{output_file}.mermaid"
        with open(output_path, "w") as f:
            f.write("\n".join(mermaid_lines))

        logger.info(f"[ZUMA] Workflow diagram definition saved as {output_path}")
        return output_path

    async def run_workflow(
        self,
        workflow: ZumaWorkflow,
        context: Dict[str, Any] = None,
        dependencies: Dict[str, Any] = None,
        dry_run: bool = False,
        generate_diagram: bool = True,
        diagram_output: str = None,
    ) -> ZumaResult:
        """Run a Zuma workflow with comprehensive error handling and reporting.

        Args:
            workflow: The workflow to execute
            context: Initial context dictionary
            dependencies: Dependencies dictionary
            dry_run: Whether to perform a dry run
            generate_diagram: Whether to generate a Mermaid diagram definition
            diagram_output: Custom output path for the diagram (without extension)

        Returns:
            The workflow execution result
        """
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

            # Generate Mermaid diagram definition if requested
            if generate_diagram:
                diagram_path = (
                    diagram_output or f"workflow_{workflow.name.lower().replace(' ', '_')}"
                )
                self.create_workflow_diagram(result, diagram_path)

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
