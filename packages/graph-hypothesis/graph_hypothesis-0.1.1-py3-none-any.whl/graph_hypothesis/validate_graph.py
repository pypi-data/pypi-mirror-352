from typing import Any, Union

import networkx as nx


def validate_graph_parameters(
    graph: nx.Graph, fixed_type: Any, target_type: Any
) -> Union[bool, float]:
    """
    Validates general NetworkX graph properties and the compatibility of
    'fixed_type' and 'target_type' parameters.

    This function checks:
    1.  The graph is an undirected NetworkX Graph (nx.Graph).
    2.  The graph is unweighted (no 'weight' attribute on edges, or all are 1).
    3.  Every node has a 'type' attribute.
    4.  The total number of distinct node types does not exceed 100.
    5.  The graph is not empty (has at least one node).
    6.  `fixed_type` and `target_type` are distinct.
    7.  Both `fixed_type` and `target_type` exist as node types in the graph.

    Args:
        graph (nx.Graph): The NetworkX graph object to validate.
        fixed_type (Any): The type of nodes designated as the fixed type.
        target_type (Any): The type of nodes designated as the target type.

    Returns:
        Union[bool, float]:
            - **True** if all validation checks pass.
            - **np.nan** if `fixed_type` or `target_type` nodes are found
              to be entirely absent in the graph, indicating the metric is undefined
              and typically handled with a warning.

    Raises:
        AssertionError:
            - If `graph` is not an `nx.Graph` or is an `nx.DiGraph`.
            - If `graph` contains weighted edges with values other than 1.
            - If any node is missing the 'type' attribute.
            - If the number of distinct node types exceeds 100.
            - If the input `graph` is empty (has no nodes).
            - If `fixed_type` is the same as `target_type`.
            - If `fixed_type` is not found as an existing node type in the graph.
            - If `target_type` is not found as an existing node type in the graph.
    """
    MAX_DISTINCT_NODE_TYPES = 100

    # 1. Assert that the graph is an undirected NetworkX Graph instance
    assert isinstance(
        graph, nx.Graph
    ), "Input graph must be an undirected NetworkX Graph (nx.Graph) instance."
    assert not isinstance(
        graph, nx.DiGraph
    ), "Input graph must be an undirected NetworkX Graph (nx.Graph) instance, not a DiGraph."

    # 5. Assert graph is not empty
    assert (
        graph.number_of_nodes() > 0
    ), "Input graph cannot be empty (must have at least one node)."

    # 2. Check for weighted edges
    for u, v, data in graph.edges(data=True):
        if "weight" in data:
            assert (
                data["weight"] == 1
            ), "Graph contains weighted edges. Expected unweighted graph (no 'weight' attributes or all weights are 1)."

    # 3. Check for node types and count distinct types
    distinct_types = set()
    for node in graph.nodes():
        assert (
            "type" in graph.nodes[node]
        ), f"Node {node} is missing the required 'type' attribute."
        distinct_types.add(graph.nodes[node]["type"])

    # 4. Enforce the cap on distinct node types
    assert (
        len(distinct_types) <= MAX_DISTINCT_NODE_TYPES
    ), f"Number of distinct node types ({len(distinct_types)}) exceeds the maximum allowed limit of {MAX_DISTINCT_NODE_TYPES}."

    # Get all distinct node types present in the graph (already computed)
    all_distinct_types = distinct_types

    # 6. Assertions for fixed_type and target_type
    assert (
        fixed_type != target_type
    ), f"fixed_type ('{fixed_type}') and target_type ('{target_type}') cannot be the same."

    # 7. Assert fixed_type and target_type are present in the graph's node types
    assert (
        fixed_type in all_distinct_types
    ), f"fixed_type ('{fixed_type}') is not found as a node type in the graph."
    assert (
        target_type in all_distinct_types
    ), f"target_type ('{target_type}') is not found as a node type in the graph."

    return True


if __name__ == "__main__":

    # --- Test Cases for validate_graph_parameters ---
    print("--- Running Test Cases for validate_graph_parameters ---")

    # Test 1: Valid unweighted, undirected graph with node types
    print("\n--- Test Case 1: Valid Graph ---")
    G1 = nx.Graph()
    G1.add_node(0, type="A")
    G1.add_node(1, type="B")
    G1.add_edges_from([(0, 1)])
    try:
        result1 = validate_graph_parameters(G1, fixed_type="A", target_type="B")
        print(f"Result for G1: {result1}")
        assert result1 is True, f"Test 1 Failed: Expected True, Got {result1}"
        print("Test 1 Passed.")
    except AssertionError as e:
        print(f"Test 1 Failed with AssertionError: {e}")

    # Test 2: Invalid (directed) graph
    print("\n--- Test Case 2: Invalid (Directed) Graph ---")
    G_directed = nx.DiGraph()
    G_directed.add_edges_from([(0, 1)])
    # Add types for it to pass initial type existence checks if it gets that far
    G_directed.add_node(0, type="X")
    G_directed.add_node(1, type="Y")
    try:
        validate_graph_parameters(G_directed, fixed_type="X", target_type="Y")
    except AssertionError as e:
        print(f"Caught expected AssertionError for directed graph: {e}")
        print("Test 2 Passed.")
    except Exception as e:
        print(f"Test 2 Failed: Unexpected exception {e}")

    # Test 3: Invalid (weighted) graph
    print("\n--- Test Case 3: Invalid (Weighted) Graph ---")
    G_weighted = nx.Graph()
    G_weighted.add_edge(0, 1, weight=0.5)  # Invalid weight
    G_weighted.add_node(0, type="A")
    G_weighted.add_node(1, type="B")
    try:
        validate_graph_parameters(G_weighted, fixed_type="A", target_type="B")
    except AssertionError as e:
        print(f"Caught expected AssertionError for weighted graph: {e}")
        print("Test 3 Passed.")
    except Exception as e:
        print(f"Test 3 Failed: Unexpected exception {e}")

    # Test 4: Invalid (missing node 'type' attribute)
    print("\n--- Test Case 4: Invalid (Missing Node Type Attribute) ---")
    G_missing_type_attr = nx.Graph()
    G_missing_type_attr.add_node(0)  # Missing type attribute
    G_missing_type_attr.add_node(1, type="B")
    G_missing_type_attr.add_edges_from([(0, 1)])
    try:
        validate_graph_parameters(
            G_missing_type_attr, fixed_type=None, target_type="B"
        )  # fixed_type will also be missing for node 0
    except AssertionError as e:
        print(f"Caught expected AssertionError for missing node type attribute: {e}")
        print("Test 4 Passed.")
    except Exception as e:
        print(f"Test 4 Failed: Unexpected exception {e}")

    # Test 5: Valid graph with explicit weight=1 and node types
    print("\n--- Test Case 5: Valid Graph (Explicit Weight 1) ---")
    G_explicit_weight_one = nx.Graph()
    G_explicit_weight_one.add_node(0, type="X")
    G_explicit_weight_one.add_node(1, type="Y")
    G_explicit_weight_one.add_edge(0, 1, weight=1)
    try:
        result5 = validate_graph_parameters(
            G_explicit_weight_one, fixed_type="X", target_type="Y"
        )
        print(f"Result for G_explicit_weight_one: {result5}")
        assert result5 is True, f"Test 5 Failed: Expected True, Got {result5}"
        print("Test 5 Passed.")
    except AssertionError as e:
        print(f"Test 5 Failed with AssertionError: {e}")

    # --- New Test Cases for added validations ---

    # Test 6: Empty graph (raises AssertionError)
    print("\n--- Test Case 6: Empty Graph (AssertionError) ---")
    G_empty = nx.Graph()
    try:
        validate_graph_parameters(G_empty, fixed_type="A", target_type="B")
    except AssertionError as e:
        print(f"Caught expected AssertionError for empty graph: {e}")
        print("Test 6 Passed.")
    except Exception as e:
        print(f"Test 6 Failed: Unexpected exception {e}")

    # Test 7: fixed_type == target_type (raises AssertionError)
    print("\n--- Test Case 7: fixed_type == target_type (AssertionError) ---")
    G_same_types = nx.Graph()
    G_same_types.add_node(0, type="A")
    G_same_types.add_node(1, type="B")
    G_same_types.add_edge(0, 1)
    try:
        validate_graph_parameters(G_same_types, fixed_type="A", target_type="A")
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type == target_type: {e}")
        print("Test 7 Passed.")
    except Exception as e:
        print(f"Test 7 Failed: Unexpected exception {e}")

    # Test 8: fixed_type not found as a node type (raises AssertionError)
    print("\n--- Test Case 8: fixed_type not in Graph Node Types (AssertionError) ---")
    G_type_not_in_graph = nx.Graph()
    G_type_not_in_graph.add_node(0, type="X")
    G_type_not_in_graph.add_node(1, type="Y")
    G_type_not_in_graph.add_edge(0, 1)
    try:
        validate_graph_parameters(G_type_not_in_graph, fixed_type="A", target_type="Y")
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type not in graph: {e}")
        print("Test 8 Passed.")
    except Exception as e:
        print(f"Test 8 Failed: Unexpected exception {e}")

    # Test 9: target_type not found as a node type (raises AssertionError)
    print("\n--- Test Case 9: target_type not in Graph Node Types (AssertionError) ---")
    G_type_not_in_graph_target = nx.Graph()
    G_type_not_in_graph_target.add_node(0, type="A")
    G_type_not_in_graph_target.add_node(1, type="Y")
    G_type_not_in_graph_target.add_edge(0, 1)
    try:
        validate_graph_parameters(
            G_type_not_in_graph_target, fixed_type="A", target_type="Z"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for target_type not in graph: {e}")
        print("Test 9 Passed.")
    except Exception as e:
        print(f"Test 9 Failed: Unexpected exception {e}")

    # Test 11: Number of distinct node types exceeds 100 (raises AssertionError)
    print("\n--- Test Case 11: Too Many Distinct Node Types (AssertionError) ---")
    G_too_many_types = nx.Graph()
    for i in range(101):  # 101 distinct types
        G_too_many_types.add_node(i, type=f"Type{i}")
    G_too_many_types.add_edge(0, 1)  # Add an edge to ensure it's not empty

    try:
        # We need fixed_type and target_type that exist
        validate_graph_parameters(
            G_too_many_types, fixed_type="Type0", target_type="Type1"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for too many distinct types: {e}")
        print("Test 11 Passed.")
    except Exception as e:
        print(f"Test 11 Failed: Unexpected exception {e}")
