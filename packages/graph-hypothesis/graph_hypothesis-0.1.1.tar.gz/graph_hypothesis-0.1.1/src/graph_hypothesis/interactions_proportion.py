import warnings
from typing import Any

import networkx as nx
import numpy as np

from .validate_graph import validate_graph_parameters


def calculate_interaction_proportion_metric(
    graph: nx.Graph, fixed_type: Any, target_type: Any
) -> float:
    """
    Calculates the interaction proportion: the proportion of neighbors of
    'fixed_type' nodes that are 'target_type' nodes.

    This metric quantifies how likely nodes of `fixed_type` are to connect to
    nodes of `target_type`, relative to all their connections. It's a measure
    of mixing or segregation propensity from the perspective of `fixed_type` nodes.

    Args:
        graph (nx.Graph): The input undirected, unweighted NetworkX graph.
                          Each node must have a 'type' attribute.
        fixed_type (Any): The type of nodes whose neighborhood composition is being examined.
        target_type (Any): The type of neighbors being counted.

    Returns:
        float: The proportion of neighbors of `fixed_type` nodes that are `target_type` nodes.
               Returns np.nan if no `fixed_type` nodes exist or if `fixed_type` nodes
               have no connections at all (to avoid division by zero and indicate
               an undefined metric).

    Raises:
        AssertionError:
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as a node type in the graph.
            - If `target_type` is not found as a node type in the graph.
    """
    # Validate core graph properties (undirected, unweighted, node types, type count cap)
    validate_graph_parameters(graph, fixed_type, target_type)

    total_neighbors_of_fixed_type = 0
    target_neighbors_of_fixed_type = 0

    fixed_nodes = [
        n for n, data in graph.nodes(data=True) if data.get("type") == fixed_type
    ]
    nodes_of_target_type_exist = any(
        graph.nodes[n]["type"] == target_type for n in graph.nodes()
    )

    if not fixed_nodes or not nodes_of_target_type_exist:
        warnings.warn(
            f"No '{fixed_type}' or '{target_type}' nodes found in the graph. "
            f"Returning NaN as the interaction proportion is undefined."
        )
        return np.nan

    for u in fixed_nodes:
        for v in graph.neighbors(u):
            total_neighbors_of_fixed_type += 1
            if graph.nodes[v].get("type") == target_type:
                target_neighbors_of_fixed_type += 1

    if total_neighbors_of_fixed_type == 0:
        warnings.warn(
            f"Nodes of type '{fixed_type}' exist but have no connections. "
            f"Returning NaN as the interaction proportion is undefined."
        )
        return np.nan

    return target_neighbors_of_fixed_type / total_neighbors_of_fixed_type
