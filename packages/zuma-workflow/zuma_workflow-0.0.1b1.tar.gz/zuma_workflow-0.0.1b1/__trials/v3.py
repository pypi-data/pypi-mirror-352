from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

import matplotlib.pyplot as plt
import networkx as nx


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
# Graph Building Functions
# ------------------------


def hierarchy_pos_original(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Original vertical hierarchy_pos.
    """
    pos = {}

    def _hierarchy_pos_recursive(
        G_rec, root_rec, left, right, vert_loc_rec, current_pos, parent_rec=None
    ):
        current_pos[root_rec] = ((left + right) / 2, vert_loc_rec)
        children = [child for child in G_rec.neighbors(root_rec) if child != parent_rec]
        if children:
            dx = (right - left) / len(children)
            nextx = left
            for child in children:
                _hierarchy_pos_recursive(
                    G_rec,
                    child,
                    nextx,
                    nextx + dx,
                    vert_loc_rec - vert_gap,
                    current_pos,
                    root_rec,
                )
                nextx += dx
        return current_pos

    if root is not None and root in G:
        return _hierarchy_pos_recursive(G, root, 0, width, vert_loc, {}, None)
    elif G.nodes:  # Fallback if root is not good
        # Try to find a root (node with in_degree 0)
        possible_roots = [node for node, degree in G.in_degree() if degree == 0]
        if possible_roots:
            return _hierarchy_pos_recursive(G, possible_roots[0], 0, width, vert_loc, {}, None)
        else:  # Cycle or other complex graph, fallback to first node
            return _hierarchy_pos_recursive(G, list(G.nodes())[0], 0, width, vert_loc, {}, None)
    return {}


def build_graph_from_execution_node(node: ExecutionNode, G: nx.DiGraph):
    label = f"{node.node_type}: {node.original_name}\n({node.status})"  # For internal use, display label is different
    G.add_node(
        node.id,
        label=label,
        status=node.status,
        depth=node.depth,
        node_type=node.node_type,
        original_name=node.original_name,
    )
    for child in node.children:
        G.add_edge(node.id, child.id)
        build_graph_from_execution_node(child, G)


def draw_execution_tree(root: ExecutionNode):
    G = nx.DiGraph()
    if root is None:
        print("Root node is None, cannot draw tree.")
        return
    build_graph_from_execution_node(root, G)

    if not G.nodes:
        print("Graph is empty, nothing to draw.")
        return

    pos = None
    try:
        # For horizontal layout LR (Left to Right)
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot", args="-Grankdir=LR")
        print("Using pygraphviz 'dot' layout (LR).")
    except ImportError:
        print("PyGraphviz not found or error during layout. Using fallback layout.")
        print("For optimal flowchart layout, please install pygraphviz: pip install pygraphviz")
        original_vert_pos = hierarchy_pos_original(G, root.id if root else None)
        if original_vert_pos:
            # Simple conversion: depth becomes x, spread becomes y
            # Adjust scaling factor for x (depth) and y (spread) as needed
            max_original_y = (
                max(p[1] for p in original_vert_pos.values()) if original_vert_pos else 0
            )
            pos = {
                node_id: (data["depth"] * 2.5, -p[0] * 1.5)
                for node_id, p in original_vert_pos.items()
                if node_id in G and (data := G.nodes[node_id])
            }  # Ensure node_id and data are valid
        if not pos:  # If original_hierarchy_pos also failed or returned empty
            print("Fallback hierarchy_pos also failed. Using spring_layout.")
            pos = nx.spring_layout(G)
    except Exception as e:  # Catch other potential errors from graphviz_layout
        print(f"Error during graphviz layout: {e}. Using spring_layout as fallback.")
        pos = nx.spring_layout(G)

    plt.figure(figsize=(max(18, len(G.nodes) * 1.2), max(12, len(G.nodes) * 0.6)))
    ax = plt.gca()

    # Styling maps
    type_to_color_map = {
        "Action": "lightgreen",
        "SubAction": "mediumpurple",  # Purple for SubAction as per image
        "Workflow": "lightcoral",  # Red-ish for Workflow
        "SaveAction": "khaki",  # Yellow for Save Button
        "ParallelBlock": "lightblue",
        "Root": "whitesmoke",
        "Generic": "lightgray",
    }
    type_to_boxstyle_map = {  # Matplotlib boxstyles
        "Action": "rarrow,pad=0.4",
        "SubAction": "rarrow,pad=0.4",
        "Workflow": "rarrow,pad=0.4",  # "sawtooth,pad=0.5" is another option for block arrow
        "SaveAction": "rarrow,pad=0.4",
        "ParallelBlock": "round,pad=0.5",
        "Root": "circle,pad=0.2",
        "Generic": "round,pad=0.3",
    }

    display_labels_dict = {}
    node_to_bbox_style_dict = {}

    # Ensure a consistent node order for processing if needed, though dicts handle unordered access.
    # ordered_nodes = list(G.nodes()) # Not strictly necessary if using dicts properly

    for node_id, data in G.nodes(data=True):
        original_name = data.get("original_name", "")
        status = data.get("status", "Pending")
        node_type_from_node = data.get("node_type", "Generic")

        effective_node_type = node_type_from_node
        # Determine if an "Action" is a "SubAction"
        if node_type_from_node == "Action":
            preds = list(G.predecessors(node_id))
            if preds:
                parent_data = G.nodes[preds[0]]
                if parent_data.get("node_type") == "Workflow":
                    effective_node_type = "SubAction"

        type_display_name = effective_node_type
        if effective_node_type == "SaveAction":
            type_display_name = "Save Button"
        elif effective_node_type == "Root":
            type_display_name = "Start"

        display_labels_dict[node_id] = f"{type_display_name}\n({original_name})"

        current_color = type_to_color_map.get(effective_node_type, "lightgray")
        if status == "Failed":
            current_color = "orangered"
        elif status == "Mixed":
            current_color = "orange"
        # Success uses the type_color

        boxstyle_str = type_to_boxstyle_map.get(effective_node_type, "round,pad=0.3")
        node_to_bbox_style_dict[node_id] = dict(
            boxstyle=boxstyle_str,
            facecolor=current_color,
            alpha=0.95,
            ec="dimgray",
            lw=1.5,
        )

    # 1. Draw edges
    nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle="-|>",
        arrowsize=18,
        edge_color="dimgray",
        width=1.5,
        node_size=0,
        ax=ax,
    )

    # 2. Draw labels with custom bboxes (these are effectively our "nodes")
    for node_id in G.nodes():  # Iterate G.nodes() to ensure all are processed
        if node_id in pos and node_id in display_labels_dict:  # Ensure node has position and label
            x, y = pos[node_id]
            label_text = display_labels_dict[node_id]
            current_bbox_style = node_to_bbox_style_dict.get(node_id)
            if current_bbox_style:
                ax.text(
                    x,
                    y,
                    label_text,
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="black",  # Smaller font for potentially smaller boxes
                    bbox=current_bbox_style,
                    zorder=3,
                    weight="bold",
                )

    plt.title("Workflow Execution Status (Flowchart Style)", fontsize=16, weight="bold")

    # Auto-scale plot view to fit all nodes
    if pos and pos.values():
        all_x = [p[0] for p in pos.values()]
        all_y = [p[1] for p in pos.values()]
        if all_x and all_y:
            padding_x = (max(all_x) - min(all_x)) * 0.05 + 0.5  # 5% padding + fixed
            padding_y = (max(all_y) - min(all_y)) * 0.05 + 0.5
            plt.xlim(min(all_x) - padding_x, max(all_x) + padding_x)
            plt.ylim(min(all_y) - padding_y, max(all_y) + padding_y)

    plt.axis("off")
    plt.tight_layout(pad=1.0)
    plt.show()


# ------------------------
# Core Workflow System with Plugin Registration
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
        node = ExecutionNode(
            name=f"Action: {self.name}",
            depth=depth,
            node_type=current_node_type,
            original_name=self.name,
        )
        if parent:
            parent.add_child(node)

        print(f"{'>'* (depth+1)} Executing Action: {self.name}")
        current_context = context.copy()
        try:
            result_context = self.action(current_context)  # Pass and expect modified context
            node.status = "Success"
            current_context.update(result_context)  # Merge results
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

        for step in self.steps:
            current_context = step.execute(current_context, parent=node, depth=depth + 1)

        if node.children:
            statuses = [child.status for child in node.children]
            if all(s == "Success" for s in statuses):
                node.status = "Success"
            elif any(s == "Failed" for s in statuses):
                node.status = "Failed"
            elif any(s == "Mixed" for s in statuses):
                node.status = "Mixed"
            else:
                node.status = "Mixed"
        else:
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

        for i, branch_step in enumerate(self.branches):
            print(f"{'-'* (depth+1)} Starting Branch {i+1}/{len(self.branches)} in {self.name}")
            branch_context_input = context.copy()
            branch_result_context = branch_step.execute(
                branch_context_input, parent=node, depth=depth + 1
            )
            merged_context.update(branch_result_context)
            print(f"{'-'* (depth+1)} Completed Branch {i+1}/{len(self.branches)} in {self.name}")

        if node.children:  # Children are the root nodes of the branches
            statuses = [child.status for child in node.children]
            if all(s == "Success" for s in statuses):
                node.status = "Success"
            elif any(s == "Failed" for s in statuses):
                node.status = "Failed"
            elif any(s == "Mixed" for s in statuses):
                node.status = "Mixed"
            else:
                node.status = "Mixed"
        else:
            node.status = "Success"

        print(
            f"{'-'* (depth+1)} Completed Parallel Block: {self.name} (Status: {node.status}) {'-'* (depth+1)}\n"
        )
        return merged_context


# ------------------------
# Plugin Implementations (mostly unchanged, ensure they return context)
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
# Sample Workflow Construction and Execution
# ------------------------
def build_workflow_with_parallel() -> Workflow:
    main_workflow = Workflow("Main Document Processing")
    main_workflow.add_step(PLUGIN_REGISTRY["OpenPortal"]())

    parallel_data_processing = ParallelWorkflowComponent("Data Processing Tasks")

    form_edit_branch = Workflow("Form Edit Operations")
    form_edit_branch.add_step(PLUGIN_REGISTRY["Search"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["SwitchToDraft"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["EditFields"]())
    form_edit_branch.add_step(PLUGIN_REGISTRY["EditTagDetailsFailing"]())  # Failing step
    form_edit_branch.add_step(PLUGIN_REGISTRY["Save"]())
    parallel_data_processing.add_branch(form_edit_branch)

    comments_branch = Workflow("Comment Handling")
    comments_branch.add_step(PLUGIN_REGISTRY["OpenComments"]())
    comments_branch.add_step(PLUGIN_REGISTRY["AddData"]())
    comments_branch.add_step(PLUGIN_REGISTRY["Save"]())
    parallel_data_processing.add_branch(comments_branch)

    main_workflow.add_step(parallel_data_processing)

    def consolidate_action(ctx: Dict[str, Any]) -> Dict[str, Any]:
        print("Consolidating results after parallel execution...")
        ctx["consolidation_complete"] = True
        return ctx

    main_workflow.add_step(ActionStep("Consolidate Results", consolidate_action))
    main_workflow.add_step(PLUGIN_REGISTRY["ClosePortal"]())
    return main_workflow


if __name__ == "__main__":
    ExecutionNode.counter = 0
    context: Dict[str, Any] = {}
    workflow_to_run = build_workflow_with_parallel()

    execution_root = ExecutionNode(
        "Overall Workflow Run",
        depth=-1,
        node_type="Root",
        original_name="Execution Start",
    )
    final_context = workflow_to_run.execute(context, parent=execution_root, depth=0)

    print("\nFinal Workflow Context:")
    for key, value in final_context.items():
        print(f"  {key}: {value}")

    print("\nRegistered Plugins:")
    for pname, cls in PLUGIN_REGISTRY.items():
        print(f"  {pname}: {cls.__name__}")

    draw_execution_tree(execution_root)
