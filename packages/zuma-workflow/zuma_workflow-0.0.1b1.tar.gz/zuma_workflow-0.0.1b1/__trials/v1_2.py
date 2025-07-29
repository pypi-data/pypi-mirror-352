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

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass


class ActionStep(WorkflowComponent):
    """
    An atomic action step. It wraps a callable (action) that processes the
    workflow's context.
    """

    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.action = action

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f">>> Executing Action: {self.name}")
        result = self.action(context)
        return result


class ParallelStep(WorkflowComponent):
    """
    A container for steps that should be executed in parallel.
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowComponent] = []

    def add_step(self, step: WorkflowComponent):
        self.steps.append(step)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n=== Starting Parallel Steps: {self.name} ===")
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(step.execute, context): step for step in self.steps}
            for future in as_completed(futures):
                step = futures[future]
                context = future.result()
        print(f"=== Completed Parallel Steps: {self.name} ===\n")
        return context


class Workflow(WorkflowComponent):
    """
    A workflow is a sequential container of WorkflowComponents. Note that
    workflows can be nested to create hierarchical processes.
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowComponent] = []

    def add_step(self, step: WorkflowComponent):
        self.steps.append(step)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n=== Starting Workflow: {self.name} ===")
        for step in self.steps:
            context = step.execute(context)
        print(f"=== Completed Workflow: {self.name} ===\n")
        return context


# ------------------------
# Plugin implementations
# ------------------------


# Action: Open Portal
def open_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening portal...")
    context["portal_open"] = True
    return context


@register_plugin("OpenPortal")
class OpenPortal(ActionStep):
    def __init__(self):
        super().__init__("Open Portal", open_portal_action)


# Action: Close Portal
def close_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Closing portal...")
    context["portal_closed"] = True
    return context


@register_plugin("ClosePortal")
class ClosePortal(ActionStep):
    def __init__(self):
        super().__init__("Close Portal", close_portal_action)


# Action: Search (part of Form Edit workflow)
def search_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Performing search in form...")
    context["search_result"] = "Results found"
    return context


@register_plugin("Search")
class SearchAction(ActionStep):
    def __init__(self):
        super().__init__("Search", search_action)


# Action: Switch to Draft (part of Form Edit workflow)
def switch_to_draft_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Switching to draft mode...")
    context["mode"] = "draft"
    return context


@register_plugin("SwitchToDraft")
class SwitchToDraft(ActionStep):
    def __init__(self):
        super().__init__("Switch to Draft", switch_to_draft_action)


# Action: Edit Fields (part of Form Edit workflow)
def edit_fields_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing fields...")
    context["fields_edited"] = True
    return context


@register_plugin("EditFields")
class EditFields(ActionStep):
    def __init__(self):
        super().__init__("Edit Fields", edit_fields_action)


# Action: Edit Tag Details (part of Form Edit workflow)
def edit_tag_details_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing tag details...")
    context["tags_updated"] = True
    return context


@register_plugin("EditTagDetails")
class EditTagDetails(ActionStep):
    def __init__(self):
        super().__init__("Edit Tag Details", edit_tag_details_action)


# Action: Save (can be used in multiple workflows)
def save_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Saving changes...")
    context["saved"] = True
    return context


@register_plugin("Save")
class SaveAction(ActionStep):
    def __init__(self):
        super().__init__("Save", save_action)


# Action: Open Comments (part of Comments workflow)
def open_comments_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening comments section...")
    context["comments_open"] = True
    return context


@register_plugin("OpenComments")
class OpenComments(ActionStep):
    def __init__(self):
        super().__init__("Open Comments", open_comments_action)


# Action: Add Data (for comments)
def add_data_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Adding comment data...")
    context.setdefault("comments", []).append("New comment added")
    return context


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
    main_workflow = Workflow("Main Workflow")

    # Step 1: Open Portal
    main_workflow.add_step(OpenPortal())

    # Step 2: Form Edit workflow - can be extended further!
    form_edit_workflow = Workflow("Form Edit")
    parallel_steps = ParallelStep("Parallel Search and Draft")
    parallel_steps.add_step(SearchAction())
    parallel_steps.add_step(SwitchToDraft())
    form_edit_workflow.add_step(parallel_steps)
    form_edit_workflow.add_step(EditFields())
    form_edit_workflow.add_step(EditTagDetails())
    form_edit_workflow.add_step(SaveAction())
    main_workflow.add_step(form_edit_workflow)

    # Step 3: Comments workflow
    comments_workflow = Workflow("Comments")
    comments_workflow.add_step(OpenComments())
    comments_workflow.add_step(AddData())
    comments_workflow.add_step(SaveAction())  # Reusing the same Save action
    main_workflow.add_step(comments_workflow)

    # Step 4: Close Portal
    main_workflow.add_step(ClosePortal())

    return main_workflow


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
