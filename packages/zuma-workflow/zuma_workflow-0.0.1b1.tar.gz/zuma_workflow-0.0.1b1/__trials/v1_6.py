from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List


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

    def __init__(
        self,
        name: str,
        action: Callable[[Dict[str, Any]], Dict[str, Any]],
        dependencies: Dict[str, Any] = None,
    ):
        super().__init__(name)
        self.action = action
        self.dependencies = dependencies or {}

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}>>> Executing Action: {self.name}")
        result = self.action(context, **self.dependencies)
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

    def __init__(
        self,
        name: str,
        steps: List[WorkflowComponent],
        dependencies: Dict[str, Any] = None,
    ):
        super().__init__(name)
        self.steps = steps
        self.dependencies = dependencies or {}

    def execute(self, context: Dict[str, Any], indent: int = 0) -> Dict[str, Any]:
        print(f"{' ' * indent}\n=== Starting Workflow: {self.name} ===")
        for step in self.steps:
            context = step.execute(context, indent + 2)
        print(f"{' ' * indent}=== Completed Workflow: {self.name} ===\n")
        return context


# # Define actions
# def open_portal_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Opening portal...")
#     return {"portal_open": True}


# def close_portal_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Closing portal...")
#     return {"portal_closed": True}


# def search_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Performing search in form...")
#     return {"search_result": "Results found"}


# def switch_to_draft_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Switching to draft mode...")
#     return {"mode": "draft"}


# def edit_fields_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Editing fields...")
#     return {"fields_edited": True}


# def edit_tag_details_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Editing tag details...")
#     return {"tags_updated": True}


# def save_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Saving changes...")
#     return {"saved": True}


# def open_comments_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Opening comments section...")
#     return {"comments_open": True}


# def add_data_action(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
#     print("Adding comment data...")
#     comments = context.get("comments", [])
#     comments.append("New comment added")
#     return {"comments": comments}


# # Create action steps directly
# class OpenPortal(ActionStep):
#     def __init__(self):
#         super().__init__("Open Portal", open_portal_action)


# class ClosePortal(ActionStep):
#     def __init__(self):
#         super().__init__("Close Portal", close_portal_action)


# class SearchAction(ActionStep):
#     def __init__(self):
#         super().__init__("Search", search_action)


# class SwitchToDraft(ActionStep):
#     def __init__(self):
#         super().__init__("Switch to Draft", switch_to_draft_action)


# class EditFields(ActionStep):
#     def __init__(self):
#         super().__init__("Edit Fields", edit_fields_action)


# class EditTagDetails(ActionStep):
#     def __init__(self):
#         super().__init__("Edit Tag Details", edit_tag_details_action)


# class SaveAction(ActionStep):
#     def __init__(self):
#         super().__init__("Save", save_action)


# class OpenComments(ActionStep):
#     def __init__(self):
#         super().__init__("Open Comments", open_comments_action)


# class AddData(ActionStep):
#     def __init__(self):
#         super().__init__("Add Data", add_data_action)


# def build_workflow(dependencies=None) -> Workflow:
#     """
#     Constructs a hierarchical workflow:

#     Main Workflow:
#       1. Open Portal
#       2. Form Edit Workflow:
#           - Parallel Search and Draft
#               - Search
#               - Switch to Draft
#           - Edit Fields
#           - Edit Tag Details
#           - Save
#       3. Comments Workflow:
#           - Open Comments
#           - Add Data
#           - Save
#       4. Close Portal
#     """
#     return Workflow(
#         "Main Workflow",
#         steps=[
#             OpenPortal(),
#             Workflow(
#                 "Form Edit",
#                 steps=[
#                     ParallelStep(
#                         "Parallel Search and Draft",
#                         steps=[SearchAction(), SwitchToDraft()],
#                     ),
#                     EditFields(),
#                     EditTagDetails(),
#                     SaveAction(),
#                 ],
#                 dependencies=dependencies,
#             ),
#             Workflow(
#                 "Comments",
#                 steps=[OpenComments(), AddData(), SaveAction()],
#                 dependencies=dependencies,
#             ),
#             ClosePortal(),
#         ],
#         dependencies=dependencies,
#     )


# if __name__ == "__main__":
#     # Create an initial context (state)
#     context: Dict[str, Any] = {}

#     # Example dependencies
#     dependencies = {
#         "db_connection": "Database Connection",
#         "selenium_driver": "Selenium Driver",
#     }

#     # Build the hierarchical workflow using registered plugins
#     workflow = build_workflow(dependencies)

#     # Execute the workflow with the context
#     final_context = workflow.execute(context)

#     # Print final state for clarity
#     print("Final Workflow Context:")
#     for key, value in final_context.items():
#         print(f"  {key}: {value}")


# Create action steps directly
class OpenPortal(ActionStep):
    ## the action step will be the class name with casing like OpenPortal => Open Portal
    def __init__(self, dependencies: Dict[str, Any] = None):
        self._db = dependencies.get("db_connection")

    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Opening portal...")
        return {"portal_open": True}


class ClosePortal(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        self._driver = dependencies.get("selenium_driver")

    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Closing portal...")
        return {"portal_closed": True}


class SearchAction(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Performing search in form...")
        return {"search_result": "Results found"}


class SwitchToDraft(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Switching to draft mode...")
        return {"mode": "draft"}


class EditFields(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Editing fields...")
        return {"fields_edited": True}


class EditTagDetails(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Editing tag details...")
        return {"tags_updated": True}


class SaveAction(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Saving changes...")
        return {"saved": True}


class OpenComments(ActionStep):
    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Opening comments section...")
        return {"comments_open": True}


class AddData(ActionStep):
    def __init__(self, dependencies: Dict[str, Any] = None):
        self._driver = dependencies.get("selenium_driver")

    def execute(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        print("Adding comment data...")
        comments = context.get("comments", [])
        comments.append("New comment added")
        return {"comments": comments}


def build_workflow(dependencies=None) -> Workflow:
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
                dependencies=dependencies,
            ),
            Workflow(
                "Comments",
                steps=[OpenComments(), AddData(), SaveAction()],
                dependencies=dependencies,
            ),
            ClosePortal(),
        ],
        dependencies=dependencies,
    )


if __name__ == "__main__":
    # Create an initial context (state)
    context: Dict[str, Any] = {}

    # Example dependencies
    dependencies = {
        "db_connection": "Database Connection",
        "selenium_driver": "Selenium Driver",
    }

    # Build the hierarchical workflow using registered plugins
    workflow = build_workflow(dependencies)

    # Execute the workflow with the context
    final_context = workflow.execute(context)

    # Print final state for clarity
    print("Final Workflow Context:")
    for key, value in final_context.items():
        print(f"  {key}: {value}")
