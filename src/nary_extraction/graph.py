from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from .schemas import State

from .nodes import (
    node1_detect_events,
    node2_classify_events,
    node3_core_entity,
    node4_split_objects,
    node5_roles,
    node6_finalize,
)


def build_graph():

    workflow = StateGraph(
        State
    )

    # Nodes

    workflow.add_node(
        "detect_events",
        node1_detect_events,
    )

    workflow.add_node(
        "classify_events",
        node2_classify_events,
    )

    workflow.add_node(
        "core_entity",
        node3_core_entity,
    )

    workflow.add_node(
        "split_objects",
        node4_split_objects,
    )

    workflow.add_node(
        "roles",
        node5_roles,
    )

    workflow.add_node(
        "finalize",
        node6_finalize,
    )

    # Edges

    workflow.add_edge(
        START,
        "detect_events",
    )

    workflow.add_edge(
        "detect_events",
        "classify_events",
    )

    workflow.add_edge(
        "classify_events",
        "core_entity",
    )

    workflow.add_edge(
        "core_entity",
        "split_objects",
    )

    workflow.add_edge(
        "split_objects",
        "roles",
    )

    workflow.add_edge(
        "roles",
        "finalize",
    )

    workflow.add_edge(
        "finalize",
        END,
    )

    return workflow.compile()
