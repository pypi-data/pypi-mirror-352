import asyncio
import inspect
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class WorkflowExecutionError(Exception):
    """Custom exception to signal workflow execution failure."""

    pass


class WorkflowResult:
    """Represents the execution result of a workflow component."""

    def __init__(self, name: str, type: str):
        self.name: str = name
        self.type: str = type
        self.status: str = "PENDING"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.children: List["WorkflowResult"] = []
        self.context_snapshot: Dict[str, Any] = {}

    def to_json(self):
        json_dict = {
            "step_name": self.name,
            "type": self.type,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
        if self.error:
            json_dict["error"] = self.error
        if self.children:
            json_dict["children"] = [child.to_json() for child in self.children]
        return json_dict


class WorkflowComponent(ABC):
    """
    Base class for any workflow component. Each component must implement
    the execute method, which takes and returns a context dictionary.
    """

    def __init__(self, name: str):
        self.name = name
        self.workflow_result_children: List[WorkflowResult] = []

    @staticmethod
    def _get_component_type(component: "WorkflowComponent") -> str:
        """Helper to determine component type for WorkflowResult."""
        if isinstance(component, Workflow):
            return "Workflow"
        elif isinstance(component, ParallelAction):
            return "ParallelAction"
        elif isinstance(component, ActionStep):
            return "Action"
        return "Unknown"

    @abstractmethod
    async def execute(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        indent: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        pass

    async def _execute_impl(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> WorkflowResult:
        component_type = WorkflowComponent._get_component_type(self)
        component_result = WorkflowResult(self.name, component_type)
        component_result.start_time = datetime.now()

        print(f"{' ' * indent}>>> Executing: {self.name}")

        try:
            sig = inspect.signature(self.execute)
            kwargs_to_pass = {}
            if "context" in sig.parameters:
                kwargs_to_pass["context"] = context
            if "dependencies" in sig.parameters:
                kwargs_to_pass["dependencies"] = dependencies
            if "indent" in sig.parameters:
                kwargs_to_pass["indent"] = indent

            if isinstance(self, ActionStep):
                for key, value in self._action_kwargs.items():
                    if key in sig.parameters:
                        kwargs_to_pass[key] = value

                if self._action_args:
                    first_arg_name = None
                    for param_name, param in sig.parameters.items():
                        if (
                            param_name not in ["context", "dependencies", "indent", "kwargs"]
                            and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                        ):
                            first_arg_name = param_name
                            break
                    if first_arg_name:
                        kwargs_to_pass[first_arg_name] = self._action_args[0]

            step_result_context = await self.execute(**kwargs_to_pass)
            context.update(step_result_context)
            component_result.status = "SUCCESS"
        except Exception as e:
            component_result.status = "FAILED"
            component_result.error = str(e)
            print(f"{' ' * indent}!!! Error in {self.name}: {e}")
        finally:
            component_result.end_time = datetime.now()
            component_result.context_snapshot = context.copy()
            if hasattr(self, "workflow_result_children"):
                component_result.children = self.workflow_result_children
            return component_result


class ActionStep(WorkflowComponent):
    """
    An atomic action step. It wraps a callable (action) that processes the
    workflow's context. The class name is used as the action name.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__)
        self._action_args = args
        self._action_kwargs = kwargs

    async def execute(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        indent: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the execute method")


class ParallelAction(WorkflowComponent):
    """
    A container for steps that should be executed in parallel.
    """

    def __init__(self, name: str, steps: List[WorkflowComponent]):
        super().__init__(name)
        self.steps = steps

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Parallel Actions: {self.name} ===")

        tasks = [
            step._execute_impl(context.copy(), dependencies, indent + 2) for step in self.steps
        ]

        self.workflow_result_children = await asyncio.gather(*tasks, return_exceptions=False)

        overall_status = "SUCCESS"
        for sr in self.workflow_result_children:
            if sr.status == "FAILED":
                overall_status = "FAILED"
            elif sr.status == "SUCCESS":
                context.update(sr.context_snapshot)

        print(f"{' ' * indent}=== Completed Parallel Actions: {self.name} ===\n")

        if overall_status == "FAILED":
            raise WorkflowExecutionError(f"One or more parallel steps in {self.name} failed.")

        return context


class Workflow(WorkflowComponent):
    """
    A workflow is a sequential container of WorkflowComponents. Note that
    workflows can be nested to create hierarchical processes.
    """

    def __init__(self, name: str, steps: List[WorkflowComponent]):
        super().__init__(name)
        self.steps = steps

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Workflow: {self.name} ===")

        self.workflow_result_children = []

        halt_workflow = False

        for step in self.steps:
            if halt_workflow:
                # If workflow is halted, mark remaining steps as CANCELLED
                cancelled_result = WorkflowResult(
                    step.name, WorkflowComponent._get_component_type(step)
                )
                cancelled_result.status = "CANCELLED"
                self.workflow_result_children.append(cancelled_result)
                continue

            step_result: WorkflowResult = await step._execute_impl(
                context, dependencies, indent + 2
            )

            self.workflow_result_children.append(step_result)

            if step_result.status == "FAILED":
                print(
                    f"{' ' * indent}--- Workflow {self.name} halted due to failed step: {step.name} ---"
                )
                halt_workflow = True

        print(f"{' ' * indent}=== Completed Workflow: {self.name} ===\n")

        if halt_workflow:
            raise WorkflowExecutionError(
                f"Workflow '{self.name}' failed due to a child step failure."
            )

        return context


# Define actions
class OpenPortal(ActionStep):
    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        db_connection = dependencies.get("db_connection")
        print(f"Opening portal using {db_connection}...")
        await asyncio.sleep(0.1)
        return {"portal_open": True}


class ClosePortal(ActionStep):
    async def execute(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver")
        print(f"Closing portal using {selenium_driver}...")
        await asyncio.sleep(0.1)
        return {"portal_closed": True}


class SearchAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Performing search in form...")
        await asyncio.sleep(0.1)
        return {"search_result": "Results found"}


class SwitchToDraft(ActionStep):
    async def execute(self) -> Dict[str, Any]:
        print("Switching to draft mode...")
        await asyncio.sleep(0.1)
        return {"mode": "draft"}


class EditFields(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Editing fields...")
        await asyncio.sleep(0.1)
        return {"fields_edited": True}


class EditTagDetails(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Editing tag details...")
        await asyncio.sleep(0.1)
        return {"tags_updated": True}


class SaveAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Saving changes...")
        await asyncio.sleep(0.1)
        return {"saved": True}


class OpenComments(ActionStep):
    async def execute(self) -> Dict[str, Any]:
        print("Opening comments section...")
        await asyncio.sleep(0.1)
        return {"comments_open": True}


class AddData(ActionStep):
    async def execute(
        self,
        context: Dict[str, Any],
        dependencies: Dict[str, Any],
        tag_name: str = None,
    ) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver")
        print(f"Adding comment data using {selenium_driver}...")
        await asyncio.sleep(0.1)
        raise ValueError("not able to add")  # This line causes the action to fail
        comments = context.get("comments", [])
        if tag_name:
            comments.append(f"New comment added with tag: {tag_name}")
        else:
            comments.append("New comment added (no tag specified)")
        return {"comments": comments}


class FailingAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Attempting to perform a failing action...")
        await asyncio.sleep(0.1)
        if True:
            raise ValueError("Simulated failure in FailingAction!")
        return {"failed_action_done": True}


# Run the workflow
async def main():
    context: Dict[str, Any] = {}

    dependencies = {
        "db_connection": "Database Connection",
        "selenium_driver": "Selenium Driver",
    }

    workflow = Workflow(
        "Main Workflow",
        steps=[
            OpenPortal(),
            Workflow(
                "Form Edit",
                steps=[
                    ParallelAction(
                        "Parallel Search and Draft",
                        steps=[
                            SearchAction(),
                            SwitchToDraft(),
                            # FailingAction(), # Uncomment to test failure halting in parallel
                        ],
                    ),
                    EditFields(),
                    EditTagDetails(),
                    SaveAction(),
                ],
            ),
            Workflow(
                "Comments",
                steps=[
                    OpenComments(),
                    AddData("tag1"),  # This will fail
                    AddData("tag2"),  # This will be cancelled
                    SaveAction(),  # This will be cancelled
                ],
            ),
            # FailingAction(), # Uncomment to test failure halting for Main Workflow
            ClosePortal(),  # This will be cancelled if "Comments" workflow fails
        ],
    )

    overall_workflow_result: WorkflowResult = await workflow._execute_impl(
        context,
        dependencies=dependencies,
    )

    print("\nFinal Workflow Context:")
    for key, value in overall_workflow_result.context_snapshot.items():
        print(f"  {key}: {value}")

    print("\nWorkflow Execution JSON Result:")
    print(json.dumps(overall_workflow_result.to_json(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
