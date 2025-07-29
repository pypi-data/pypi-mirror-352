from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

# Global registry for plugins (workflow components)
PLUGIN_REGISTRY = {}


def register_plugin(plugin_name: str):
    """
    Decorator to register a workflow plugin by name.
    """

    def wrapper(cls):
        PLUGIN_REGISTRY[plugin_name] = cls
        return cls

    return wrapper


class WorkflowComponent(ABC):
    """
    Base class for any workflow component. Each component must implement
    the execute method, which takes and returns a context dictionary.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        pass


class ActionStep(WorkflowComponent):
    """
    An atomic action step. It wraps a callable (action) that processes the
    workflow's context.
    """

    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Dict[str, Any]]):
        super().__init__(name)
        self.action = action

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}>>> Executing Action: {self.name}")
        result = self.action(context)
        context.update(result)
        return context


class ParallelStep(WorkflowComponent):
    """
    A container for steps that should be executed in parallel.
    """

    def __init__(self, name: str, steps: List[WorkflowComponent]):
        super().__init__(name)
        self.steps = steps

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Parallel Steps: {self.name} ===")
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(step.execute, context, indent + 2): step for step in self.steps
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

    def __init__(self, name: str, steps: List[WorkflowComponent]):
        super().__init__(name)
        self.steps = steps

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Workflow: {self.name} ===")
        for step in self.steps:
            context = step.execute(context, indent + 2)
        print(f"{' ' * indent}=== Completed Workflow: {self.name} ===\n")
        return context


# ------------------------
# Plugin implementations
# ------------------------


# Action: Open Portal
def open_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening portal...")
    return {"portal_open": True}


@register_plugin("OpenPortal")
class OpenPortal(ActionStep):
    def __init__(self):
        super().__init__("Open Portal", open_portal_action)


# Action: Close Portal
def close_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Closing portal...")
    return {"portal_closed": True}


@register_plugin("ClosePortal")
class ClosePortal(ActionStep):
    def __init__(self):
        super().__init__("Close Portal", close_portal_action)


# Action: Search (part of Form Edit workflow)
def search_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Performing search in form...")
    return {"search_result": "Results found"}


@register_plugin("Search")
class SearchAction(ActionStep):
    def __init__(self):
        super().__init__("Search", search_action)


# Action: Switch to Draft (part of Form Edit workflow)
def switch_to_draft_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Switching to draft mode...")
    return {"mode": "draft"}


@register_plugin("SwitchToDraft")
class SwitchToDraft(ActionStep):
    def __init__(self):
        super().__init__("Switch to Draft", switch_to_draft_action)


# Action: Edit Fields (part of Form Edit workflow)
def edit_fields_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing fields...")
    return {"fields_edited": True}


@register_plugin("EditFields")
class EditFields(ActionStep):
    def __init__(self):
        super().__init__("Edit Fields", edit_fields_action)


# Action: Edit Tag Details (part of Form Edit workflow)
def edit_tag_details_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing tag details...")
    return {"tags_updated": True}


@register_plugin("EditTagDetails")
class EditTagDetails(ActionStep):
    def __init__(self):
        super().__init__("Edit Tag Details", edit_tag_details_action)


# Action: Save (can be used in multiple workflows)
def save_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Saving changes...")
    return {"saved": True}


@register_plugin("Save")
class SaveAction(ActionStep):
    def __init__(self):
        super().__init__("Save", save_action)


# Action: Open Comments (part of Comments workflow)
def open_comments_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening comments section...")
    return {"comments_open": True}


@register_plugin("OpenComments")
class OpenComments(ActionStep):
    def __init__(self):
        super().__init__("Open Comments", open_comments_action)


# Action: Add Data (for comments)
def add_data_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Adding comment data...")
    comments = context.get("comments", [])
    comments.append("New comment added")
    return {"comments": comments}


@register_plugin("AddData")
class AddData(ActionStep):
    def __init__(self):
        super().__init__("Add Data", add_data_action)


# ------------------------
# Build and run a sample workflow
# ------------------------


def build_workflow() -> Workflow:
    """
    Constructs a hierarchical workflow:

    Main Workflow:
      1. Open Portal
      2. Form Edit Workflow:
          - Parallel Search and Draft
              - Search
              - Switch to Draft
          - Edit Fields
          - Edit Tag Details
          - Save
      3. Comments Workflow:
          - Open Comments
          - Add Data
          - Save
      4. Close Portal
    """
    return Workflow(
        "Main Workflow",
        steps=[
            OpenPortal(),
            Workflow(
                "Form Edit",
                steps=[
                    ParallelStep(
                        "Parallel Search and Draft",
                        steps=[SearchAction(), SwitchToDraft()],
                    ),
                    EditFields(),
                    EditTagDetails(),
                    SaveAction(),
                ],
            ),
            Workflow("Comments", steps=[OpenComments(), AddData(), SaveAction()]),
            ClosePortal(),
        ],
    )


if __name__ == "__main__":
    # Create an initial context (state)
    context: Dict[str, Any] = {}

    # Build the hierarchical workflow using registered plugins
    workflow = build_workflow()

    # Execute the workflow with the context
    final_context = workflow.execute(context)

    # Print final state for clarity
    print("Final Workflow Context:")
    for key, value in final_context.items():
        print(f"  {key}: {value}")

    # Optionally, list all registered plugins
    print("\nRegistered Plugins:")
    for pname, cls in PLUGIN_REGISTRY.items():
        print(f"  {pname}: {cls.__name__}")
