import asyncio
import inspect
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class WorkflowResult:
    """Represents the execution result of a workflow component."""

    def __init__(self, name: str, type: str):  # Added 'type' parameter
        self.name: str = name
        self.type: str = type  # Store the type
        self.status: str = "PENDING"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.children: List["WorkflowResult"] = []  # For nested workflows or parallel steps
        self.context_snapshot: Dict[str, Any] = {}  # To preserve context at step completion

    def to_json(self):
        json_dict = {
            "step_name": self.name,
            "type": self.type,  # Include type in JSON
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
        # This will hold the results of its immediate children
        self.workflow_result_children: List[WorkflowResult] = []

    @abstractmethod
    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        pass

    async def _execute_impl(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> WorkflowResult:
        # Determine the type of the component
        component_type: str
        if isinstance(self, Workflow):
            component_type = "Workflow"
        elif isinstance(self, ParallelAction):  # Changed from ParallelStep
            component_type = "ParallelAction"  # Changed from ParallelStep
        elif isinstance(self, ActionStep):
            component_type = "Action"
        else:
            component_type = "Unknown"  # Fallback, should not happen

        component_result = WorkflowResult(self.name, component_type)  # Pass type to WorkflowResult
        component_result.start_time = datetime.now()

        print(f"{' ' * indent}>>> Executing: {self.name}")

        try:
            # Dynamically prepare arguments based on the execute method's signature
            sig = inspect.signature(self.execute)
            kwargs = {}
            if "context" in sig.parameters:
                kwargs["context"] = context
            if "dependencies" in sig.parameters:
                kwargs["dependencies"] = dependencies
            if "indent" in sig.parameters:
                kwargs["indent"] = indent

            step_result_context = await self.execute(**kwargs)
            context.update(step_result_context)
            component_result.status = "SUCCESS"
        except Exception as e:
            component_result.status = "FAILED"
            component_result.error = str(e)
            print(f"{' ' * indent}!!! Error in {self.name}: {e}")
        finally:
            component_result.end_time = datetime.now()
            component_result.context_snapshot = context.copy()  # Capture context at step completion
            # Add children results if this component is a container (Workflow or ParallelAction)
            if hasattr(self, "workflow_result_children"):
                component_result.children = self.workflow_result_children
            return component_result


class ActionStep(WorkflowComponent):
    """
    An atomic action step. It wraps a callable (action) that processes the
    workflow's context. The class name is used as the action name.
    """

    def __init__(self):
        super().__init__(self.__class__.__name__)

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        # Concrete ActionStep subclasses will implement this.
        raise NotImplementedError("Subclasses must implement the execute method")


class ParallelAction(WorkflowComponent):  # Changed from ParallelStep
    """
    A container for steps that should be executed in parallel.
    """

    def __init__(self, name: str, steps: List[WorkflowComponent]):
        super().__init__(name)
        self.steps = steps

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], indent: int = 0
    ) -> Dict[str, Any]:
        print(
            f"{' ' * indent}\n=== Starting Parallel Actions: {self.name} ==="
        )  # Changed print statement

        tasks = [
            step._execute_impl(
                context.copy(), dependencies, indent + 2
            )  # Pass a copy of context to each parallel branch
            for step in self.steps
        ]

        # Run all tasks concurrently and gather their results
        # _execute_impl already handles exceptions, so return_exceptions=False is fine here.
        self.workflow_result_children = await asyncio.gather(*tasks, return_exceptions=False)

        overall_status = "SUCCESS"
        for sr in self.workflow_result_children:
            if sr.status == "FAILED":
                overall_status = "FAILED"
            elif sr.status == "SUCCESS":
                context.update(sr.context_snapshot)  # Merge successful results back

        print(
            f"{' ' * indent}=== Completed Parallel Actions: {self.name} ===\n"
        )  # Changed print statement

        # Propagate failure if any parallel step failed
        if overall_status == "FAILED":
            # Re-raise an exception to be caught by the parent Workflow's _execute_impl
            raise Exception(f"One or more parallel steps in {self.name} failed.")

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

        self.workflow_result_children = []  # Initialize children results for this workflow

        for step in self.steps:
            step_result: WorkflowResult = await step._execute_impl(
                context, dependencies, indent + 2
            )

            # Append the result of the executed step to this workflow's children
            self.workflow_result_children.append(step_result)

            if step_result.status == "FAILED":
                print(
                    f"{' ' * indent}--- Workflow {self.name} halted due to failed step: {step.name} ---"
                )
                # Stop further execution of steps in this workflow
                raise Exception(f"Step '{step.name}' failed within Workflow '{self.name}'.")

        print(f"{' ' * indent}=== Completed Workflow: {self.name} ===\n")
        return context


# Define actions (unchanged logic, only parameters adapted)
class OpenPortal(ActionStep):
    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        db_connection = dependencies.get("db_connection")
        print(f"Opening portal using {db_connection}...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"portal_open": True}


class ClosePortal(ActionStep):
    async def execute(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver")
        print(f"Closing portal using {selenium_driver}...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"portal_closed": True}


class SearchAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Performing search in form...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"search_result": "Results found"}


class SwitchToDraft(ActionStep):
    async def execute(self) -> Dict[str, Any]:
        print("Switching to draft mode...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"mode": "draft"}


class EditFields(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Editing fields...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"fields_edited": True}


class EditTagDetails(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Editing tag details...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"tags_updated": True}


class SaveAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Saving changes...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"saved": True}


class OpenComments(ActionStep):
    async def execute(self) -> Dict[str, Any]:
        print("Opening comments section...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"comments_open": True}


class AddData(ActionStep):
    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        selenium_driver = dependencies.get("selenium_driver")
        print(f"Adding comment data using {selenium_driver}...")
        await asyncio.sleep(0.1)  # Simulate async I/O
        comments = context.get("comments", [])
        comments.append("New comment added")
        return {"comments": comments}


# --- Example of a failing action ---
class FailingAction(ActionStep):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Attempting to perform a failing action...")
        await asyncio.sleep(0.1)
        if True:  # This will always fail for demonstration
            raise ValueError("Simulated failure in FailingAction!")
        return {"failed_action_done": True}


# Run the workflow
async def main():
    # Create an initial context (state)
    context: Dict[str, Any] = {}

    # Example dependencies
    dependencies = {
        "db_connection": "Database Connection",
        "selenium_driver": "Selenium Driver",
    }

    # Build the hierarchical workflow
    workflow = Workflow(
        "Main Workflow",
        steps=[
            OpenPortal(),
            Workflow(
                "Form Edit",
                steps=[
                    ParallelAction(  # Changed from ParallelStep
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
                    AddData(),
                    SaveAction(),
                ],
            ),
            # FailingAction(), # Uncomment to test failure halting for Main Workflow
            ClosePortal(),
        ],
    )

    overall_workflow_result: WorkflowResult = await workflow._execute_impl(
        context,
        dependencies=dependencies,
    )

    # Print final state for clarity
    print("\nFinal Workflow Context:")
    for key, value in overall_workflow_result.context_snapshot.items():
        print(f"  {key}: {value}")

    print("\nWorkflow Execution JSON Result:")
    # The to_json() method now correctly structures the children
    print(json.dumps(overall_workflow_result.to_json(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
