from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

import matplotlib.pyplot as plt
import networkx as nx

# ------------------------
# Execution Tree Infrastructure
# ------------------------


class ExecutionNode:
    """
    Represents a single execution step (or node) in the workflow.
    """

    counter = 0  # Global unique node identifier

    def __init__(self, name: str, depth: int):
        self.name = name
        self.status = "Pending"  # Later set to "Success", "Failed", or "Mixed"
        self.children: List["ExecutionNode"] = []
        self.depth = depth
        self.id = ExecutionNode.counter
        ExecutionNode.counter += 1

    def add_child(self, child: "ExecutionNode"):
        self.children.append(child)


# ------------------------
# Graph Building Functions
# ------------------------


def hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Compute a hierarchical layout for a tree.
    This function is adapted from a solution on StackOverflow.
    """

    def _hierarchy_pos(G, root, left, right, vert_loc, pos, parent=None):
        pos[root] = ((left + right) / 2, vert_loc)
        children = list(G.neighbors(root))
        if parent is not None and parent in children:
            children.remove(parent)
        if len(children) > 0:
            dx = (right - left) / len(children)
            nextx = left
            for child in children:
                pos = _hierarchy_pos(G, child, nextx, nextx + dx, vert_loc - vert_gap, pos, root)
                nextx += dx
        return pos

    return _hierarchy_pos(G, root, 0, width, vert_loc, {})


def build_graph_from_execution_node(node: ExecutionNode, G: nx.DiGraph):
    """
    Recursively builds a NetworkX DiGraph from our execution tree.
    """
    # Create a label that shows the node name and its status
    label = f"{node.name}\n({node.status})"
    G.add_node(node.id, label=label, status=node.status)
    for child in node.children:
        G.add_edge(node.id, child.id)
        build_graph_from_execution_node(child, G)


def draw_execution_tree(root: ExecutionNode):
    """
    Draws a hierarchical graph representation of the execution tree using NetworkX and Matplotlib.
    """
    G = nx.DiGraph()
    build_graph_from_execution_node(root, G)
    pos = hierarchy_pos(G, root.id)

    # Map node statuses to colors
    color_map = []
    for _, data in G.nodes(data=True):
        status = data.get("status", "Pending")
        if status == "Success":
            color = "green"
        elif status == "Failed":
            color = "red"
        elif status == "Mixed":
            color = "orange"
        else:
            color = "gray"
        color_map.append(color)

    labels = nx.get_node_attributes(G, "label")
    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        labels=labels,
        node_color=color_map,
        with_labels=True,
        node_size=3000,
        font_size=10,
        font_color="white",
        arrows=True,
    )
    plt.title("Workflow Execution Status")
    plt.show()


# ------------------------
# Core Workflow System with Plugin Registration
# ------------------------

PLUGIN_REGISTRY = {}


def register_plugin(plugin_name: str):
    """Decorator to register a workflow plugin by name."""

    def decorator(cls):
        PLUGIN_REGISTRY[plugin_name] = cls
        return cls

    return decorator


class WorkflowComponent(ABC):
    """
    Abstract base class for any workflow component.
    """

    @abstractmethod
    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        pass


class ActionStep(WorkflowComponent):
    """
    Atomic action step, which wraps a callable.
    """

    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.action = action

    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        # Create an execution node for this action
        node = ExecutionNode(self.name, depth)
        if parent:
            parent.add_child(node)
        print(f">>> Executing Action: {self.name}")
        try:
            result = self.action(context)
            node.status = "Success"
        except Exception as ex:
            print(f"Error in action '{self.name}': {ex}")
            node.status = "Failed"
            result = context  # Continue with the same context
        return result


class Workflow(WorkflowComponent):
    """
    A sequential container of WorkflowComponents that can be nested.
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowComponent] = []

    def add_step(self, step: WorkflowComponent):
        self.steps.append(step)

    def execute(
        self, context: Dict[str, Any], parent: ExecutionNode = None, depth: int = 0
    ) -> Dict[str, Any]:
        # Create an execution node for the workflow container
        node = ExecutionNode(self.name, depth)
        if parent:
            parent.add_child(node)
        print(f"\n=== Starting Workflow: {self.name} ===")
        for step in self.steps:
            context = step.execute(context, parent=node, depth=depth + 1)
        # Determine overall status from children
        if node.children:
            statuses = [child.status for child in node.children]
            if all(s == "Success" for s in statuses):
                node.status = "Success"
            elif any(s == "Failed" for s in statuses):
                node.status = "Failed"
            else:
                node.status = "Mixed"
        else:
            node.status = "Success"
        print(f"=== Completed Workflow: {self.name} ===\n")
        return context


# ------------------------
# Plugin Implementations
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


# Action: Search (Form Edit)
def search_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Performing search...")
    context["search_result"] = "Results found"
    return context


@register_plugin("Search")
class SearchAction(ActionStep):
    def __init__(self):
        super().__init__("Search", search_action)


# Action: Switch to Draft
def switch_to_draft_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Switching to draft mode...")
    context["mode"] = "draft"
    return context


@register_plugin("SwitchToDraft")
class SwitchToDraft(ActionStep):
    def __init__(self):
        super().__init__("Switch to Draft", switch_to_draft_action)


# Action: Edit Fields
def edit_fields_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing fields...")
    context["fields_edited"] = True
    return context


@register_plugin("EditFields")
class EditFields(ActionStep):
    def __init__(self):
        super().__init__("Edit Fields", edit_fields_action)


# Action: Edit Tag Details
def edit_tag_details_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Editing tag details...")
    context["tags_updated"] = True
    return context


@register_plugin("EditTagDetails")
class EditTagDetails(ActionStep):
    def __init__(self):
        super().__init__("Edit Tag Details", edit_tag_details_action)


# Action: Save (re-used in multiple workflows)
def save_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Saving changes...")
    context["saved"] = True
    return context


@register_plugin("Save")
class SaveAction(ActionStep):
    def __init__(self):
        super().__init__("Save", save_action)


# Action: Open Comments
def open_comments_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Opening comments section...")
    context["comments_open"] = True
    return context


@register_plugin("OpenComments")
class OpenComments(ActionStep):
    def __init__(self):
        super().__init__("Open Comments", open_comments_action)


# Action: Add Comment Data
def add_data_action(context: Dict[str, Any]) -> Dict[str, Any]:
    print("Adding comment data...")
    context.setdefault("comments", []).append("New comment added")
    return context


@register_plugin("AddData")
class AddData(ActionStep):
    def __init__(self):
        super().__init__("Add Data", add_data_action)


# ------------------------
# Sample Workflow Construction and Execution
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
    main_workflow.add_step(OpenPortal())

    form_edit = Workflow("Form Edit")
    form_edit.add_step(SearchAction())
    form_edit.add_step(SwitchToDraft())
    form_edit.add_step(EditFields())
    form_edit.add_step(EditTagDetails())
    form_edit.add_step(SaveAction())
    main_workflow.add_step(form_edit)

    comments = Workflow("Comments")
    comments.add_step(OpenComments())
    comments.add_step(AddData())
    comments.add_step(SaveAction())
    main_workflow.add_step(comments)

    main_workflow.add_step(ClosePortal())
    return main_workflow


if __name__ == "__main__":
    # Initial context for the workflow execution
    context: Dict[str, Any] = {}

    # Build the workflow structure using our plugins
    workflow = build_workflow()

    # Create a root node for the execution tree encompassing the entire run
    execution_root = ExecutionNode("Workflow Execution", depth=0)

    # Execute the workflow; each step logs its result into the execution tree.
    final_context = workflow.execute(context, parent=execution_root, depth=0)

    # Output the final context for verification
    print("Final Workflow Context:")
    for key, value in final_context.items():
        print(f"  {key}: {value}")

    # Optionally print the registered plugins
    print("\nRegistered Plugins:")
    for pname, cls in PLUGIN_REGISTRY.items():
        print(f"  {pname}: {cls.__name__}")

    # Draw the execution tree graph using NetworkX with color-coded status.
    draw_execution_tree(execution_root)
