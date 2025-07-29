from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

import matplotlib.patches  # Though not directly used in graphviz html style
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
# Graph Building for Pipeline Style (Graphviz HTML)
# ------------------------


def execution_node_to_html(node: ExecutionNode) -> str:
    """
    Generates an HTML-like string for a Graphviz node label,
    representing the node as a "stage" or "column" with internal items.
    """
    title_bg_color = "#393C43"  # Darker grey for title background
    status_icon = ""
    node_title = node.original_name.upper()

    # Determine title color and status icon based on node type and status
    if node.node_type == "Workflow":
        title_bg_color = "#2E4053"  # Darker blue
    elif node.node_type == "ParallelBlock":
        title_bg_color = "#344E41"  # Darker green
    elif node.node_type == "Action":
        title_bg_color = "#512E5F"  # Darker purple
    elif node.node_type == "SubAction":
        title_bg_color = "#512E5F"  # Darker purple
    elif node.node_type == "SaveAction":
        title_bg_color = "#7D5300"  # Darker gold/brown
    elif node.node_type == "Root":
        node_title = "START"
        title_bg_color = "#4C4C4C"

    if node.status == "Success":
        status_icon = "&#10004; "  # Checkmark
    elif node.status == "Failed":
        status_icon = "&#10008; "  # Cross
    elif node.status == "Mixed":
        status_icon = "&#10070; "  # Diamond
    else:
        status_icon = "&#9200; "  # Hourglass

    header_font_color = "white"
    item_font_color = "#D1D5DB"  # Light grey for items
    border_color = "#4B5563"  # Border for the main table
    table_bg_color = "#2C3035"  # Background for the items area

    html = f'<TABLE STYLE="rounded" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="{table_bg_color}" COLOR="{border_color}">\n'
    html += f'  <TR><TD STYLE="rounded" BGCOLOR="{title_bg_color}" ALIGN="CENTER"><FONT COLOR="{header_font_color}" POINT-SIZE="14">{status_icon}{node_title}</FONT></TD></TR>\n'

    if node.children:
        for i, child_exec_node in enumerate(node.children):
            child_status_icon = ""
            child_item_color = item_font_color
            child_bg_color = "transparent"  # or table_bg_color for no alternating

            # Alternating row color slightly if needed, or keep uniform
            # if i % 2 == 1: child_bg_color = "#31353B" # Slightly different dark shade

            if child_exec_node.status == "Success":
                child_status_icon = "&#10004; "
            elif child_exec_node.status == "Failed":
                child_status_icon = "&#10008; "
                child_item_color = "#FCA5A5"  # Light red for failed text
                # child_bg_color = "#5B212E" # Dark red background for failed item row
            elif child_exec_node.status == "Mixed":
                child_status_icon = "&#10070; "
            else:
                child_status_icon = "&#9200; "

            display_text = f"{child_status_icon}{child_exec_node.original_name} <I>({child_exec_node.node_type})</I>"

            # PORT allows targeting specific cells for edges if ever needed, but not used for drawing edges here.
            html += f'  <TR><TD STYLE="rounded" BGCOLOR="{child_bg_color}" ALIGN="LEFT" PORT="port_{child_exec_node.id}_item"><FONT COLOR="{child_item_color}" POINT-SIZE="10">{display_text}</FONT></TD></TR>\n'

            # Simple heuristic for "Trigger job" button
            is_triggerable = (
                "trigger" in child_exec_node.original_name.lower()
                or "deploy" in child_exec_node.original_name.lower()
                or "run" in child_exec_node.original_name.lower()
                and child_exec_node.node_type == "Action"
            )

            if is_triggerable:  # Add a visual cue for a button
                html += f'  <TR><TD STYLE="rounded" BGCOLOR="{child_bg_color}" ALIGN="RIGHT" PORT="port_{child_exec_node.id}_trigger"><TABLE BORDER="0" CELLPADDING="3" CELLSPACING="0" BGCOLOR="#4A5568" STYLE="rounded"><TR><TD><FONT COLOR="white" POINT-SIZE="9">Trigger Job &#9654;</FONT></TD></TR></TABLE></TD></TR>\n'

    if not node.children and node.node_type not in [
        "Root"
    ]:  # If it's a stage/column but has no listed sub-tasks
        html += f'  <TR><TD ALIGN="LEFT"><FONT COLOR="{item_font_color}" POINT-SIZE="10"><I>(No sub-steps defined)</I></FONT></TD></TR>\n'

    html += "</TABLE>"
    return html


def build_nx_graph_for_pipeline_style(overall_root_exec_node: ExecutionNode, G_nx: nx.DiGraph):
    if not overall_root_exec_node.children:
        # If the root has no children, maybe draw the root itself as a single stage
        if overall_root_exec_node.node_type == "Root" and not overall_root_exec_node.children:
            # This case means an empty workflow effectively
            html_label = execution_node_to_html(overall_root_exec_node)
            G_nx.add_node(
                overall_root_exec_node.id,
                label=html_label,
                shape="plaintext",
                id_val=overall_root_exec_node.id,
            )
            return  # Nothing more to do

        # This means overall_root_exec_node *is* the main workflow if it wasn't a "Root" type or had children
        # However, the calling convention implies overall_root_exec_node is the "Root" node.
        # Let's assume the first child of "Root" is the main workflow whose children are stages.

    if overall_root_exec_node.children and overall_root_exec_node.node_type == "Root":
        main_workflow_node = overall_root_exec_node.children[
            0
        ]  # This is e.g. "Main Document Processing" Workflow node

        if not main_workflow_node.children:  # Main workflow has no steps/stages
            html_label = execution_node_to_html(
                main_workflow_node
            )  # Draw the main workflow itself as a stage
            G_nx.add_node(
                main_workflow_node.id,
                label=html_label,
                shape="plaintext",
                id_val=main_workflow_node.id,
            )
            return

        stages = (
            main_workflow_node.children
        )  # These are ExecutionNodes for stages like OpenPortal, ParallelBlock, etc.

        for stage_exec_node in stages:
            html_label = execution_node_to_html(stage_exec_node)
            G_nx.add_node(
                stage_exec_node.id,
                label=html_label,
                shape="plaintext",  # Crucial for Graphviz to render HTML
                id_val=stage_exec_node.id,
            )  # Store original id if needed by other parts

        # Add sequential edges between these stages
        for i in range(len(stages) - 1):
            G_nx.add_edge(stages[i].id, stages[i + 1].id)
    else:  # Fallback if structure is not Root -> MainWorkflow -> Stages
        # Just draw the immediate children of the given root as stages
        stages = overall_root_exec_node.children
        for stage_exec_node in stages:
            html_label = execution_node_to_html(stage_exec_node)
            G_nx.add_node(
                stage_exec_node.id,
                label=html_label,
                shape="plaintext",
                id_val=stage_exec_node.id,
            )
        for i in range(len(stages) - 1):
            G_nx.add_edge(stages[i].id, stages[i + 1].id)


def draw_pipeline_graph(root: ExecutionNode, output_filename="workflow_pipeline.png"):
    G_nx = nx.DiGraph()
    if root is None:
        print("Root node is None, cannot draw.")
        return

    build_nx_graph_for_pipeline_style(root, G_nx)

    if not G_nx.nodes:
        print("Graph is empty (no stages found), nothing to draw.")
        return

    try:
        A = nx.nx_agraph.to_agraph(G_nx)

        A.graph_attr["rankdir"] = "LR"
        A.graph_attr["bgcolor"] = "#1E1E1E"  # Even darker background
        A.graph_attr["splines"] = "polyline"  # 'polyline' or 'ortho' for straighter lines
        A.graph_attr["nodesep"] = "1.2"  # Separation between nodes on same rank
        A.graph_attr["ranksep"] = "1.5"  # Separation between ranks (columns)
        A.graph_attr["compound"] = (
            "true"  # Allow edges to clusters (not strictly used here yet but good for future)
        )
        A.graph_attr["fontname"] = "Helvetica, Arial, sans-serif"
        A.graph_attr["outputorder"] = "edgesfirst"

        A.node_attr["shape"] = "plaintext"  # Nodes are defined by their HTML labels
        A.node_attr["fontname"] = "Helvetica, Arial, sans-serif"
        # fontcolor is set within HTML

        A.edge_attr["color"] = "#909090"  # Lighter grey for edges on dark bg
        A.edge_attr["arrowsize"] = "0.7"
        A.edge_attr["penwidth"] = "1.2"
        A.edge_attr["style"] = "solid"

        A.layout(prog="dot")  # Compute layout
        A.draw(output_filename)  # Draw to file
        print(f"Pipeline graph drawn to {output_filename} using pygraphviz 'dot'.")

        # Optional: Display with Matplotlib
        # try:
        #     img = plt.imread(output_filename)
        #     plt.figure(figsize=(max(18, len(G_nx.nodes) * 2), max(12, len(G_nx.nodes)))) # Adjust size
        #     plt.imshow(img)
        #     plt.axis('off')
        #     plt.title(f"Workflow Pipeline (Rendered by Graphviz to {output_filename})")
        #     plt.show()
        # except FileNotFoundError:
        #     print(f"Could not load the image {output_filename} for display.")

    except ImportError:
        print("--------------------------------------------------------------------")
        print("PYGRAPHVIZ IS NOT INSTALLED or Graphviz executables not in PATH.")
        print("This visualization style HEAVILY relies on PyGraphviz and HTML-like labels.")
        print("Please install Graphviz (https://graphviz.org/download/) ")
        print("and then the Python package: pip install pygraphviz")
        print("Displaying a VERY basic fallback using Matplotlib.")
        print("--------------------------------------------------------------------")
        if G_nx.nodes:
            pos = nx.spring_layout(G_nx, k=0.8, iterations=30, seed=42)
            node_labels_fallback = {
                n_id: G_nx.nodes[n_id].get("id_val", str(n_id)) for n_id in G_nx.nodes()
            }
            plt.figure(figsize=(15, 10))
            nx.draw(
                G_nx,
                pos,
                labels=node_labels_fallback,
                with_labels=True,
                node_color="#ADD8E6",
                font_size=7,
                node_shape="s",  # Square
                node_size=3000,
                edge_color="#888888",
                width=1.5,
                arrowsize=15,
            )
            plt.title("Fallback Layout (PyGraphviz REQUIRED for Pipeline Style)")
            plt.show()

    except Exception as e:
        print(f"An error occurred during PyGraphviz processing: {e}")
        print("Please ensure Graphviz is correctly installed and in your system's PATH.")
        # You might see this if dot executable is not found.


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
    draw_pipeline_graph(execution_root)
