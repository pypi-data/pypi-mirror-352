import asyncio
import inspect
import json
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# Enhanced enums for better type safety
class ExecutionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class ComponentType(Enum):
    WORKFLOW = "Workflow"
    PARALLEL_ACTION = "ParallelAction"
    ACTION = "Action"
    CONDITIONAL = "Conditional"


# Custom exceptions
class WorkflowExecutionError(Exception):
    """Custom exception to signal workflow execution failure."""

    def __init__(self, message: str, component_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.component_name = component_name
        self.original_error = original_error


class WorkflowValidationError(Exception):
    """Exception for workflow validation errors."""

    pass


# Enhanced result tracking with dataclass
@dataclass
class WorkflowResult:
    """Represents the execution result of a workflow component."""

    name: str
    type: ComponentType
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    children: List["WorkflowResult"] = field(default_factory=list)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

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
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
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
def execution_context(component_name: str, logger: logging.Logger = None):
    """Context manager for tracking execution lifecycle."""
    if logger:
        logger.info(f"Starting execution: {component_name}")
    start_time = datetime.now()
    try:
        yield
        if logger:
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed execution: {component_name} ({duration:.2f}s)")
    except Exception as e:
        if logger:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed execution: {component_name} ({duration:.2f}s) - {e}")
        raise


class WorkflowComponent(ABC):
    """
    Enhanced base class for workflow components with better error handling,
    validation, and execution tracking.
    """

    def __init__(self, name: str, description: str = None, metadata: Dict[str, Any] = None):
        self.name = name
        self.description = description or f"{self.__class__.__name__}: {name}"
        self.metadata = metadata or {}
        self.workflow_result_children: List[WorkflowResult] = []
        self._logger = logging.getLogger(f"workflow.{self.__class__.__name__}")

    @property
    def component_type(self) -> ComponentType:
        """Get the component type for this instance."""
        type_mapping = {
            "Workflow": ComponentType.WORKFLOW,
            "ParallelAction": ComponentType.PARALLEL_ACTION,
            "ActionStep": ComponentType.ACTION,
            "ConditionalStep": ComponentType.CONDITIONAL,
        }
        return type_mapping.get(self.__class__.__name__, ComponentType.ACTION)

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
            errors.append("Component name cannot be empty")
        return errors

    async def _execute_impl(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        indent: int = 0,
        dry_run: bool = False,
    ) -> WorkflowResult:
        """Enhanced execution implementation with better error handling."""
        component_result = WorkflowResult(
            name=self.name, type=self.component_type, metadata=self.metadata.copy()
        )

        # Validation
        validation_errors = self.validate()
        if validation_errors:
            component_result.status = ExecutionStatus.FAILED
            component_result.error = f"Validation failed: {'; '.join(validation_errors)}"
            return component_result

        component_result.start_time = datetime.now()
        component_result.status = ExecutionStatus.RUNNING

        indent_str = " " * indent
        print(f"{indent_str}>>> Executing: {self.name} ({self.component_type.value})")

        if dry_run:
            print(f"{indent_str}    [DRY RUN MODE]")
            component_result.status = ExecutionStatus.SKIPPED
            component_result.end_time = datetime.now()
            return component_result

        try:
            with execution_context(self.name, self._logger):
                # Prepare execution parameters
                sig = inspect.signature(self.execute)
                kwargs_to_pass = self._prepare_execution_kwargs(sig, context, dependencies, indent)

                # Execute the component
                step_result_context = await self.execute(**kwargs_to_pass)

                # Validate returned context
                if not isinstance(step_result_context, dict):
                    raise WorkflowExecutionError(
                        f"Component {self.name} must return a dictionary, got {type(step_result_context)}",
                        self.name,
                    )

                # Update context with results
                context.update(step_result_context)
                component_result.status = ExecutionStatus.SUCCESS

        except Exception as e:
            component_result.status = ExecutionStatus.FAILED
            component_result.error = str(e)
            print(f"{indent_str}!!! Error in {self.name}: {e}")
            self._logger.error(f"Execution failed for {self.name}: {e}", exc_info=True)

        finally:
            component_result.end_time = datetime.now()
            component_result.context_snapshot = context.copy()

            # Attach children results if available
            if hasattr(self, "workflow_result_children") and self.workflow_result_children:
                component_result.children = self.workflow_result_children

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

        # Handle ActionStep specific parameters
        if isinstance(self, ActionStep):
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


class ActionStep(WorkflowComponent):
    """Enhanced action step with better parameter handling."""

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
        """Validate action step configuration."""
        errors = super().validate()
        if self.retries < 0:
            errors.append("Retries must be non-negative")
        if self.timeout is not None and self.timeout <= 0:
            errors.append("Timeout must be positive")
        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Default implementation - subclasses should override."""
        raise NotImplementedError(
            f"Subclasses of ActionStep must implement the execute method. "
            f"Class {self.__class__.__name__} has not implemented this method."
        )


class ConditionalStep(WorkflowComponent):
    """New component for conditional execution."""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        true_component: WorkflowComponent,
        false_component: WorkflowComponent = None,
    ):
        super().__init__(name, f"Conditional: {name}")
        self.condition = condition
        self.true_component = true_component
        self.false_component = false_component

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Execute conditional logic."""
        try:
            condition_result = self.condition(context)
            selected_component = self.true_component if condition_result else self.false_component

            if selected_component:
                print(
                    f"{' ' * indent}Condition evaluated to {condition_result}, executing: {selected_component.name}"
                )
                result = await selected_component._execute_impl(context, dependencies, indent + 2)
                self.workflow_result_children = [result]

                if result.status == ExecutionStatus.FAILED:
                    raise WorkflowExecutionError(
                        f"Conditional branch failed: {selected_component.name}"
                    )

                return result.context_snapshot
            else:
                print(
                    f"{' ' * indent}Condition evaluated to {condition_result}, no component to execute"
                )
                return {}

        except Exception as e:
            raise WorkflowExecutionError(f"Conditional evaluation failed: {str(e)}", self.name, e)


class ParallelAction(WorkflowComponent):
    """Enhanced parallel execution with better failure handling."""

    def __init__(
        self,
        name: str,
        steps: List[WorkflowComponent],
        fail_fast: bool = True,
        max_concurrency: Optional[int] = None,
    ):
        super().__init__(name, f"Parallel execution: {name}")
        self.steps = steps
        self.fail_fast = fail_fast  # Whether to stop on first failure
        self.max_concurrency = max_concurrency

    def validate(self) -> List[str]:
        """Validate parallel action configuration."""
        errors = super().validate()
        if not self.steps:
            errors.append("ParallelAction must have at least one step")
        if self.max_concurrency is not None and self.max_concurrency < 1:
            errors.append("max_concurrency must be positive")

        # Validate child components
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            for error in step_errors:
                errors.append(f"Step {i} ({step.name}): {error}")

        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Enhanced parallel execution with concurrency control."""
        print(f"{' ' * indent}\n=== Starting Parallel Actions: {self.name} ===")

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
                self.workflow_result_children = await asyncio.gather(
                    *tasks, return_exceptions=False
                )
            except Exception as e:
                # Handle partial results in case of failure
                completed_tasks = [task for task in tasks if task.done()]
                self.workflow_result_children = []
                for task in completed_tasks:
                    try:
                        result = await task
                        self.workflow_result_children.append(result)
                    except:
                        pass
                raise WorkflowExecutionError(
                    f"Parallel execution failed in {self.name}: {str(e)}", self.name, e
                )
        else:
            # Gather with exception handling - don't fail fast
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.workflow_result_children = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create a failed result for the exception
                    failed_result = WorkflowResult(
                        name=self.steps[i].name,
                        type=self.steps[i].component_type,
                        status=ExecutionStatus.FAILED,
                        error=str(result),
                    )
                    self.workflow_result_children.append(failed_result)
                else:
                    self.workflow_result_children.append(result)

        # Merge successful results into context
        successful_results = [
            r for r in self.workflow_result_children if r.status == ExecutionStatus.SUCCESS
        ]
        failed_results = [
            r for r in self.workflow_result_children if r.status == ExecutionStatus.FAILED
        ]

        # Update context with successful results
        for result in successful_results:
            context.update(result.context_snapshot)

        print(
            f"{' ' * indent}=== Completed Parallel Actions: {self.name} "
            f"(Success: {len(successful_results)}, Failed: {len(failed_results)}) ===\n"
        )

        if failed_results and self.fail_fast:
            raise WorkflowExecutionError(
                f"Parallel action {self.name} had {len(failed_results)} failed steps"
            )

        return context


class Workflow(WorkflowComponent):
    """Enhanced workflow with better control flow and error handling."""

    def __init__(
        self,
        name: str,
        steps: List[WorkflowComponent],
        continue_on_failure: bool = False,
        description: str = None,
    ):
        super().__init__(name, description or f"Workflow: {name}")
        self.steps = steps
        self.continue_on_failure = continue_on_failure

    def validate(self) -> List[str]:
        """Validate workflow configuration."""
        errors = super().validate()
        if not self.steps:
            errors.append("Workflow must have at least one step")

        # Validate child components
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            for error in step_errors:
                errors.append(f"Step {i} ({step.name}): {error}")

        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        """Enhanced workflow execution with better error handling."""
        print(f"{' ' * indent}\n=== Starting Workflow: {self.name} ===")

        self.workflow_result_children = []
        workflow_failed = False

        for i, step in enumerate(self.steps):
            if workflow_failed and not self.continue_on_failure:
                # Mark remaining steps as cancelled
                cancelled_result = WorkflowResult(
                    name=step.name,
                    type=step.component_type,
                    status=ExecutionStatus.CANCELLED,
                )
                self.workflow_result_children.append(cancelled_result)
                continue

            try:
                step_result = await step._execute_impl(context, dependencies, indent + 2)
                self.workflow_result_children.append(step_result)

                if step_result.status == ExecutionStatus.FAILED:
                    if not self.continue_on_failure:
                        print(
                            f"{' ' * indent}--- Workflow {self.name} halted at step: {step.name} ---"
                        )
                        workflow_failed = True
                    else:
                        print(
                            f"{' ' * indent}--- Step {step.name} failed, but continuing workflow ---"
                        )

            except Exception as e:
                # Create failed result for unexpected exceptions
                failed_result = WorkflowResult(
                    name=step.name,
                    type=step.component_type,
                    status=ExecutionStatus.FAILED,
                    error=str(e),
                )
                self.workflow_result_children.append(failed_result)

                if not self.continue_on_failure:
                    workflow_failed = True
                    print(
                        f"{' ' * indent}--- Workflow {self.name} halted due to exception in {step.name}: {e} ---"
                    )

        successful_steps = len(
            [r for r in self.workflow_result_children if r.status == ExecutionStatus.SUCCESS]
        )
        failed_steps = len(
            [r for r in self.workflow_result_children if r.status == ExecutionStatus.FAILED]
        )

        print(
            f"{' ' * indent}=== Completed Workflow: {self.name} "
            f"(Success: {successful_steps}, Failed: {failed_steps}) ===\n"
        )

        if workflow_failed and not self.continue_on_failure:
            raise WorkflowExecutionError(f"Workflow '{self.name}' failed due to step failure")

        return context


# Example action implementations with enhanced features
class OpenPortal(ActionStep):
    def __init__(self, portal_type: str = "default"):
        super().__init__(
            name="OpenPortal",
            description=f"Opens {portal_type} portal",
            portal_type=portal_type,
        )

    async def execute(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        portal_type: str = "default",
    ) -> Dict[str, Any]:
        db_connection = dependencies.get("db_connection", "No DB Connection")
        print(f"Opening {portal_type} portal using {db_connection}...")
        await asyncio.sleep(0.1)
        return {"portal_open": True, "portal_type": portal_type}


class ClosePortal(ActionStep):
    async def execute(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver", "No Selenium Driver")
        print(f"Closing portal using {selenium_driver}...")
        await asyncio.sleep(0.1)
        return {"portal_closed": True}


class SearchAction(ActionStep):
    def __init__(self, search_term: str = "default"):
        super().__init__(
            name="SearchAction",
            description=f"Search for: {search_term}",
            search_term=search_term,
        )

    async def execute(
        self, context: Dict[str, Any], search_term: str = "default"
    ) -> Dict[str, Any]:
        print(f"Performing search for '{search_term}' in form...")
        await asyncio.sleep(0.1)
        return {
            "search_result": f"Results found for '{search_term}'",
            "search_term": search_term,
        }


class SwitchToDraft(ActionStep):
    async def execute(self) -> Dict[str, Any]:
        print("Switching to draft mode...")
        await asyncio.sleep(0.1)
        return {"mode": "draft"}


class EditFields(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        mode = context.get("mode", "unknown")
        print(f"Editing fields in {mode} mode...")
        await asyncio.sleep(0.1)
        return {"fields_edited": True, "edit_mode": mode}


class ConditionalSave(ActionStep):
    """Example of conditional logic within an action."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        should_save = context.get("fields_edited", False)
        if should_save:
            print("Saving changes (fields were edited)...")
            await asyncio.sleep(0.1)
            return {"saved": True, "save_reason": "fields_edited"}
        else:
            print("Skipping save (no fields edited)...")
            return {"saved": False, "save_reason": "no_changes"}


class ControlledFailingAction(ActionStep):
    def __init__(self, should_fail: bool = True, failure_message: str = "Simulated failure"):
        super().__init__(
            name="ControlledFailingAction",
            should_fail=should_fail,
            failure_message=failure_message,
        )

    async def execute(
        self, should_fail: bool = True, failure_message: str = "Simulated failure"
    ) -> Dict[str, Any]:
        print(f"Executing action (will fail: {should_fail})...")
        await asyncio.sleep(0.1)
        if should_fail:
            raise ValueError(failure_message)
        return {"controlled_action_completed": True}


# Enhanced workflow runner with better reporting
class WorkflowRunner:
    """Enhanced workflow runner with comprehensive execution tracking."""

    def __init__(self, enable_logging: bool = True):
        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger("WorkflowRunner")

    async def run_workflow(
        self,
        workflow: Workflow,
        context: Dict[str, Any] = None,
        dependencies: Dict[str, Any] = None,
        dry_run: bool = False,
    ) -> WorkflowResult:
        """Run a workflow with comprehensive error handling and reporting."""
        context = context or {}
        dependencies = dependencies or {}

        # Validate workflow before execution
        validation_errors = workflow.validate()
        if validation_errors:
            self.logger.error(f"Workflow validation failed: {validation_errors}")
            raise WorkflowValidationError(
                f"Workflow validation failed: {'; '.join(validation_errors)}"
            )

        self.logger.info(
            f"Starting workflow execution: {workflow.name}" + (" (DRY RUN)" if dry_run else "")
        )

        try:
            result = await workflow._execute_impl(context, dependencies, dry_run=dry_run)

            if result.status == ExecutionStatus.SUCCESS:
                self.logger.info(f"Workflow completed successfully: {workflow.name}")
            else:
                self.logger.warning(
                    f"Workflow completed with status {result.status.value}: {workflow.name}"
                )

            return result

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow.name} - {e}")
            raise

    def print_execution_summary(self, result: WorkflowResult, indent: int = 0):
        """Print a comprehensive execution summary."""
        indent_str = "  " * indent
        status_symbol = {
            ExecutionStatus.SUCCESS: "✓",
            ExecutionStatus.FAILED: "✗",
            ExecutionStatus.CANCELLED: "○",
            ExecutionStatus.SKIPPED: "→",
            ExecutionStatus.PENDING: "?",
            ExecutionStatus.RUNNING: "…",
        }

        symbol = status_symbol.get(result.status, "?")
        duration_str = f" ({result.duration:.2f}s)" if result.duration else ""

        print(f"{indent_str}{symbol} {result.name} [{result.status.value}]{duration_str}")

        if result.error:
            print(f"{indent_str}  Error: {result.error}")

        for child in result.children:
            self.print_execution_summary(child, indent + 1)


# Demo function
async def main():
    """Enhanced demo with multiple workflow patterns."""

    runner = WorkflowRunner()

    # Example 1: Basic workflow with conditional logic
    basic_workflow = Workflow(
        "Basic Portal Workflow",
        steps=[
            OpenPortal("admin"),
            SearchAction("user_data"),
            SwitchToDraft(),
            EditFields(),
            ConditionalSave(),
            ClosePortal(),
        ],
    )

    # Example 2: Workflow with parallel execution and failure handling
    complex_workflow = Workflow(
        "Complex Data Processing",
        steps=[
            OpenPortal("data"),
            ParallelAction(
                "Parallel Data Operations",
                steps=[
                    SearchAction("dataset_1"),
                    SearchAction("dataset_2"),
                    SearchAction("dataset_3"),
                    # ControlledFailingAction(should_fail=False),  # Won't fail
                ],
                fail_fast=False,  # Continue even if some steps fail
                max_concurrency=2,  # Limit concurrent execution
            ),
            EditFields(),
            ConditionalStep(
                "Save if Edited",
                condition=lambda ctx: ctx.get("fields_edited", False),
                true_component=ConditionalSave(),
                false_component=None,
            ),
            ClosePortal(),
        ],
        continue_on_failure=False,  # Stop on failure
    )

    # Example 3: Workflow with controlled failure
    failure_demo_workflow = Workflow(
        "Failure Handling Demo",
        steps=[
            OpenPortal("test"),
            SearchAction("test_data"),
            ControlledFailingAction(should_fail=True, failure_message="Intentional demo failure"),
            EditFields(),  # This will be cancelled
            ClosePortal(),  # This will be cancelled
        ],
    )

    context = {"user_id": "demo_user", "session_id": "abc123"}
    dependencies = {
        "db_connection": "PostgreSQL Connection Pool",
        "selenium_driver": "Chrome WebDriver v91",
        "api_client": "REST API Client",
    }

    workflows = [
        ("Basic Workflow", basic_workflow),
        ("Complex Workflow", complex_workflow),
        ("Failure Demo", failure_demo_workflow),
    ]

    for workflow_name, workflow in workflows:
        print(f"\n{'='*60}")
        print(f"Running: {workflow_name}")
        print(f"{'='*60}")

        try:
            result = await runner.run_workflow(workflow, context.copy(), dependencies)

            print(f"\n--- Execution Summary for {workflow_name} ---")
            runner.print_execution_summary(result)

            print("\n--- Final Context ---")
            for key, value in result.context_snapshot.items():
                print(f"  {key}: {value}")

        except Exception as e:
            print(f"Workflow failed with exception: {e}")

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
