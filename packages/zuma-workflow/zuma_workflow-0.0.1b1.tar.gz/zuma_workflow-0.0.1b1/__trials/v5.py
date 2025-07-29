from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List


class ExecutionNode:
    """
    Represents a single execution step (or node) in the workflow.
    """

    counter = 0  # Global unique node identifier

    def __init__(self, name: str, depth: int, node_type: str = "Generic", original_name: str = ""):
        self.name = name  # Formatted name like "Workflow: XYZ"
        self.status = "Pending"
        self.children: List["ExecutionNode"] = []
        self.depth = depth
        self.id = ExecutionNode.counter
        ExecutionNode.counter += 1
        self.node_type = node_type
        self.original_name = (
            original_name if original_name else name.split(": ")[-1]
        )  # Store the raw name

    def add_child(self, child: "ExecutionNode"):
        self.children.append(child)


# ------------------------
# Core Workflow System (mostly unchanged from previous versions)
# ------------------------
PLUGIN_REGISTRY = {}


def register_plugin(plugin_name: str):
    def decorator(cls):
        PLUGIN_REGISTRY[plugin_name] = cls
        return cls

    return decorator


class WorkflowComponent(ABC):
    @abstractmethod
    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        pass


class ActionStep(WorkflowComponent):
    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.action = action

    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        current_node_type = "SaveAction" if self.name == "Save" else "Action"
        # Could add more specific types based on name for HTML styling if needed
        # e.g. if "trigger" in self.name.lower(): current_node_type = "TriggerAction"

        node = ExecutionNode(
            name=f"Action: {self.name}",  # This name is mostly for internal reference now
            depth=depth,
            node_type=current_node_type,
            original_name=self.name,  # This is used for display in HTML
        )
        if parent:
            parent.add_child(node)

        print(f"{'>'* (depth+1)} Executing Action: {self.name}")
        current_context = context.copy()
        try:
            result_context = self.action(current_context)
            node.status = "Success"
            current_context.update(result_context)
        except Exception as ex:
            print(f"Error in action '{self.name}': {ex}")
            node.status = "Failed"
        return current_context


class Workflow(WorkflowComponent):
    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowComponent] = []

    def add_step(self, step: WorkflowComponent):
        self.steps.append(step)

    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        node = ExecutionNode(
            name=f"Workflow: {self.name}",
            depth=depth,
            node_type="Workflow",
            original_name=self.name,
        )
        if parent:
            parent.add_child(node)

        print(f"\n{'='* (depth+1)} Starting Workflow: {self.name} {'='* (depth+1)}")
        current_context = context.copy()

        for (
            step_component
        ) in self.steps:  # step_component is an instance of ActionStep, Workflow, etc.
            current_context = step_component.execute(
                current_context,
                parent=node,
                depth=depth + 1,  # node is the ExecutionNode of this Workflow
            )

        if node.children:  # Children are ExecutionNodes of the steps of this workflow
            statuses = [child.status for child in node.children]
            if all(s == "Success" for s in statuses):
                node.status = "Success"
            elif any(s == "Failed" for s in statuses):
                node.status = "Failed"
            elif any(s == "Mixed" for s in statuses):
                node.status = "Mixed"
            else:
                node.status = "Mixed"  # Default for other combinations
        else:  # Empty workflow
            node.status = "Success"

        print(
            f"{'='* (depth+1)} Completed Workflow: {self.name} (Status: {node.status}) {'='* (depth+1)}\n"
        )
        return current_context


class ParallelWorkflowComponent(WorkflowComponent):
    def __init__(self, name: str):
        self.name = name
        self.branches: List[WorkflowComponent] = []

    def add_branch(self, component: WorkflowComponent):
        self.branches.append(component)

    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        node = ExecutionNode(
            name=f"Parallel: {self.name}",
            depth=depth,
            node_type="ParallelBlock",
            original_name=self.name,
        )
        if parent:
            parent.add_child(node)

        print(f"\n{'-'* (depth+1)} Starting Parallel Block: {self.name} {'-'* (depth+1)}")
        merged_context = context.copy()

        # Note: True parallel execution would require threading/asyncio.
        # Here, branches are executed sequentially, but their ExecutionNodes are children of the ParallelBlock node.
        for i, branch_component in enumerate(self.branches):
            print(f"{'-'* (depth+1)} Starting Branch {i+1}/{len(self.branches)} in {self.name}")
            branch_context_input = context.copy()  # Each branch gets a copy of parent's context
            # The children ExecutionNodes created by branch_component.execute() will be added to 'node' (ParallelBlock's node)
            branch_result_context = branch_component.execute(
                branch_context_input, parent=node, depth=depth + 1
            )
            merged_context.update(branch_result_context)  # Simple merge
            print(f"{'-'* (depth+1)} Completed Branch {i+1}/{len(self.branches)} in {self.name}")

        if node.children:  # Children are the ExecutionNodes of the branches
            statuses = [child.status for child in node.children]
            if all(s == "Success" for s in statuses):
                node.status = "Success"
            elif any(s == "Failed" for s in statuses):
                node.status = "Failed"
            elif any(s == "Mixed" for s in statuses):
                node.status = "Mixed"
            else:
                node.status = "Mixed"
        else:  # No branches
            node.status = "Success"

        print(
            f"{'-'* (depth+1)} Completed Parallel Block: {self.name} (Status: {node.status}) {'-'* (depth+1)}\n"
        )
        return merged_context


# ------------------------
# Plugin Implementations (ensure they return context)
# ------------------------
def open_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening portal...")
    context["portal_open"] = True
    return context


@register_plugin("OpenPortal")
class OpenPortal(ActionStep):
    def __init__(self):
        super().__init__("Open Portal", open_portal_action)


def close_portal_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Closing portal...")
    context["portal_closed"] = True
    return context


@register_plugin("ClosePortal")
class ClosePortal(ActionStep):
    def __init__(self):
        super().__init__("Close Portal", close_portal_action)


def search_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Performing search...")
    context["search_result"] = "Results found"
    # Simulate a delay
    # import time
    # time.sleep(1)
    return context


@register_plugin("Search")
class SearchAction(ActionStep):
    def __init__(self):
        super().__init__("Search", search_action)


def switch_to_draft_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Switching to draft mode...")
    context["mode"] = "draft"
    return context


@register_plugin("SwitchToDraft")
class SwitchToDraft(ActionStep):
    def __init__(self):
        super().__init__("Switch to Draft", switch_to_draft_action)


def edit_fields_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing fields...")
    context["fields_edited"] = True
    return context


@register_plugin("EditFields")
class EditFields(ActionStep):
    def __init__(self):
        super().__init__("Edit Fields", edit_fields_action)


def failing_edit_tag_details_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Attempting to edit tag details...")
    # import time
    # time.sleep(0.5)
    raise ValueError("Simulated error: Could not update tag details.")


@register_plugin("EditTagDetailsFailing")
class EditTagDetailsFailing(ActionStep):
    def __init__(self):
        super().__init__("Edit Tag Details (Failing)", failing_edit_tag_details_action)


def edit_tag_details_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing tag details...")
    context["tags_updated"] = True
    return context


@register_plugin("EditTagDetails")
class EditTagDetails(ActionStep):
    def __init__(self):
        super().__init__("Edit Tag Details", edit_tag_details_action)


def save_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Saving changes...")
    context["saved_items"] = context.get("saved_items", 0) + 1
    context[f"saved_on_action_{context['saved_items']}"] = True
    return context


@register_plugin("Save")
class SaveAction(ActionStep):
    def __init__(self):
        super().__init__("Save", save_action)


def open_comments_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening comments section...")
    context["comments_open"] = True
    return context


@register_plugin("OpenComments")
class OpenComments(ActionStep):
    def __init__(self):
        super().__init__("Open Comments", open_comments_action)


def add_data_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Adding comment data...")
    context.setdefault("comments", []).append("New comment added by AddData")
    return context


@register_plugin("AddData")
class AddData(ActionStep):
    def __init__(self):
        super().__init__("Add Data", add_data_action)


# ------------------------
# Sample Workflow Construction
# ------------------------
def build_workflow_with_parallel() -> Workflow:
    main_workflow = Workflow(
        "Main Document Processing"
    )  # This becomes the child of "Root" ExecutionNode

    # Stage 1
    main_workflow.add_step(PLUGIN_REGISTRY["OpenPortal"]())  # Becomes a "column"

    # Stage 2: A Parallel Block, which itself is a "column"
    # Its branches ("Form Edit Operations", "Comment Handling") will be listed as items within its HTML table.
    parallel_data_processing = ParallelWorkflowComponent("Data Processing Tasks")

    # Branch A of Parallel Block (This Workflow node's children will be items)
    form_edit_branch = Workflow(
        "Form Edit Operations"
    )  # This is an item *within* parallel_data_processing
    form_edit_branch.add_step(PLUGIN_REGISTRY["Search"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["SwitchToDraft"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["EditFields"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["EditTagDetailsFailing"]())  # Failing step
    form_edit_branch.add_step(PLUGIN_REGISTRY["Save"]())
    parallel_data_processing.add_branch(form_edit_branch)

    # Branch B of Parallel Block
    comments_branch = Workflow("Comment Handling")  # Also an item *within* parallel_data_processing
    comments_branch.add_step(PLUGIN_REGISTRY["OpenComments"]())
    comments_branch.add_step(PLUGIN_REGISTRY["AddData"]())
    comments_branch.add_step(PLUGIN_REGISTRY["Save"]())
    parallel_data_processing.add_branch(comments_branch)

    main_workflow.add_step(parallel_data_processing)  # Parallel block added as a stage

    # Stage 3
    def consolidate_action(ctx: Dict[str, Any]) -> Dict[str, Any]:
        print("Consolidating results after parallel execution...")
        ctx["consolidation_complete"] = True
        return ctx

    main_workflow.add_step(ActionStep("Consolidate Results", consolidate_action))

    # Stage 4
    main_workflow.add_step(PLUGIN_REGISTRY["ClosePortal"]())
    return main_workflow


if __name__ == "__main__":
    ExecutionNode.counter = 0  # Reset for fresh run
    context: Dict[str, Any] = {}
    workflow_to_run = build_workflow_with_parallel()

    # The "Root" node that acts as a parent for the entire visualization
    execution_root = ExecutionNode(
        "Overall Workflow Run",  # Name mostly for debugging
        depth=-1,  # Master root
        node_type="Root",
        original_name="Workflow Execution",  # Displayed name if it were a stage
    )

    # The execution of the main workflow will populate children under execution_root
    final_context = workflow_to_run.execute(context, parent=execution_root, depth=0)

    print("\n--- Final Workflow Context ---")
    for key, value in final_context.items():
        print(f"  {key}: {value}")

    # print("\n--- Registered Plugins ---")
    # for pname, cls in PLUGIN_REGISTRY.items():
    #     print(f"  {pname}: {cls.__name__}")

    print("\nAttempting to generate pipeline graph...")
