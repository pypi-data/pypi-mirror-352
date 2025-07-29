from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List


class WorkflowComponent(ABC):
    """
    Base class for any workflow component. Each component must implement
    the execute method, which takes and returns a context dictionary.
    """

    def __init__(self, name: str, dependencies: Dict[str, Any] = None):
        self.name = name
        self._dependencies = dependencies or {}

    @abstractmethod
    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        pass

    def _execute_impl(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}>>> Executing: {self.name}")
        result = self.execute(context, indent)
        context.update(result)
        return context


class ActionStep(WorkflowComponent):
    """
    An atomic action step. It wraps a callable (action) that processes the
    workflow's context.
    """

    def __init__(self, name: str, dependencies: Dict[str, Any] = None):
        super().__init__(name, dependencies)

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        pass


class ParallelStep(WorkflowComponent):
    """
    A container for steps that should be executed in parallel.
    """

    def __init__(
        self,
        name: str,
        steps: List[WorkflowComponent],
        dependencies: Dict[str, Any] = None,
    ):
        super().__init__(name, dependencies)
        self.steps = steps

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Parallel Steps: {self.name} ===")
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(step._execute_impl, context, indent + 2): step
                for step in self.steps
            }
            for future in as_completed(futures):
                step = futures[future]
                result = future.result()
                context.update(result)
        print(f"{' ' * indent}=== Completed Parallel Steps: {self.name} ===\n")
        return context


class Workflow(WorkflowComponent):
    """
    A workflow is a sequential container of WorkflowComponents. Note that
    workflows can be nested to create hierarchical processes.
    """

    def __init__(
        self,
        name: str,
        steps: List[WorkflowComponent],
        dependencies: Dict[str, Any] = None,
    ):
        super().__init__(name, dependencies)
        self.steps = steps

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Workflow: {self.name} ===")
        for step in self.steps:
            step._dependencies.update(self._dependencies)
            context = step._execute_impl(context, indent + 2)
        print(f"{' ' * indent}=== Completed Workflow: {self.name} ===\n")
        return context


# Define actions
class OpenPortal(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Open Portal", dependencies)
        self._db = dependencies.get("db_connection")

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Opening portal...")
        return {"portal_open": True}


class ClosePortal(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Close Portal", dependencies)
        self._driver = dependencies.get("selenium_driver")

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Closing portal...")
        return {"portal_closed": True}


class SearchAction(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Search Action", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Performing search in form...")
        return {"search_result": "Results found"}


class SwitchToDraft(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Switch to Draft", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Switching to draft mode...")
        return {"mode": "draft"}


class EditFields(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Edit Fields", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Editing fields...")
        return {"fields_edited": True}


class EditTagDetails(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Edit Tag Details", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Editing tag details...")
        return {"tags_updated": True}


class SaveAction(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Save Action", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Saving changes...")
        return {"saved": True}


class OpenComments(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Open Comments", dependencies)

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Opening comments section...")
        return {"comments_open": True}


class AddData(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        super().__init__("Add Data", dependencies)
        self._driver = dependencies.get("selenium_driver")

    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Adding comment data...")
        comments = context.get("comments", [])
        comments.append("New comment added")
        return {"comments": comments}


# Run the workflow
if __name__ == "__main__":
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
            OpenPortal(dependencies),
            Workflow(
                "Form Edit",
                steps=[
                    ParallelStep(
                        "Parallel Search and Draft",
                        steps=[
                            SearchAction(dependencies),
                            SwitchToDraft(dependencies),
                        ],
                    ),
                    EditFields(dependencies),
                    EditTagDetails(dependencies),
                    SaveAction(dependencies),
                ],
                dependencies=dependencies,
            ),
            Workflow(
                "Comments",
                steps=[
                    OpenComments(dependencies),
                    AddData(dependencies),
                    SaveAction(dependencies),
                ],
                dependencies=dependencies,
            ),
            ClosePortal(dependencies),
        ],
        dependencies=dependencies,
    )

    # Execute the workflow with the context
    final_context = workflow.execute(context)

    # Print final state for clarity
    print("Final Workflow Context:")
    for key, value in final_context.items():
        print(f"  {key}: {value}")
