import warnings
from collections import deque
from typing import Any

import networkx as nx
import numpy as np

from .validate_graph import validate_graph_parameters


def _shortest_path_to_closest_type(
    graph: nx.Graph, source_node: Any, target_type: Any
) -> float:
    """
    Helper function: Finds the shortest path length from a source_node to its
    closest node of target_type using BFS. Stops once the first node of target_type
    is found.

    Args:
        graph (nx.Graph): The input undirected, unweighted NetworkX graph.
        source_node (Any): The node from which to start the search.
        target_type (Any): The node type to search for.

    Returns:
        float: The shortest path length (int) to the closest node of target_type,
               or float('inf') if no node of target_type is reachable from the
               source_node (excluding the source_node itself).

    Raises:
        AssertionError:
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as a node type in the graph.
            - If `target_type` is not found as a node type in the graph.
    """
    q = deque([(source_node, 0)])  # (node, distance)
    visited = {source_node}

    while q:
        current_node, dist = q.popleft()

        # If the current node is of the target_type and is *not* the source itself,
        # we've found the closest.
        if (
            current_node != source_node
            and graph.nodes[current_node].get("type") == target_type
        ):
            return float(dist)  # Return as float to match float('inf')

        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                q.append((neighbor, dist + 1))

    # If the queue is empty and target_type node was not found or unreachable
    return float("inf")


def calculate_shortest_path_metric(
    graph: nx.Graph, fixed_type: Any, target_type: Any
) -> float:
    """
    Calculates the average shortest path length from each node of 'fixed_type'
    to its *closest* reachable node of 'target_type'.



    Args:
        graph (nx.Graph): The input undirected, unweighted NetworkX graph.
                          Each node must have a 'type' attribute.
        fixed_type (Any): The type of nodes to consider as starting points.
        target_type (Any): The type of nodes to consider as the closest reachable type.


    Returns:
        float: The average shortest path length from fixed_type nodes to their closest
               reachable target_type node.
               - Returns np.nan if no paths are found from any (sampled) fixed_type
                 node to any target_type node, indicating that the metric is
                 undefined and hypothesis testing may not be valid.
               - Excludes unreachable fixed_type nodes from the average calculation,
                 issuing a warning if such nodes exist.
               This value may be an approximation if sampling was applied.

    Raises:
        AssertionError:
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as a node type in the graph.
            - If `target_type` is not found as a node type in the graph.
    """

    # Validate core graph properties (undirected, unweighted, node types, type count cap)
    validate_graph_parameters(graph, fixed_type, target_type)

    fixed_nodes_all = [
        n for n, data in graph.nodes(data=True) if data.get("type") == fixed_type
    ]
    target_nodes_exists = any(
        data.get("type") == target_type for n, data in graph.nodes(data=True)
    )

    if not fixed_nodes_all or not target_nodes_exists:
        warnings.warn(
            f"No {fixed_type} or {target_type} nodes found in the graph."
            f" Returning NaN as the metric is undefined."
        )
        return np.nan

    num_fixed_nodes = len(fixed_nodes_all)
    fixed_nodes_for_bfs = fixed_nodes_all

    total_path_length = 0
    path_count = 0
    unreachable_nodes_count = 0

    for u in fixed_nodes_for_bfs:
        path_len = _shortest_path_to_closest_type(graph, u, target_type)

        if path_len != float("inf"):  # Only add if a path was found
            total_path_length += path_len
            path_count += 1
        else:
            unreachable_nodes_count += 1

    if path_count == 0:
        warnings.warn(
            f"No paths found from any "
            f"{fixed_type} node to any {target_type} node. "
            f"Hypothesis testing for this metric may not be valid. Returning NaN."
        )
        return np.nan

    if unreachable_nodes_count > 0:
        warnings.warn(
            f"{unreachable_nodes_count} out of {len(fixed_nodes_for_bfs)} "
            f"{fixed_type} nodes could not reach any {target_type} node. "
            f"These nodes are excluded from the average calculation."
        )

    return total_path_length / path_count
