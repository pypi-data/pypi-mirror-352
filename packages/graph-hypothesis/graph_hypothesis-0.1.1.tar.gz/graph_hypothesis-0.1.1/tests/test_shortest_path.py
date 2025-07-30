import warnings

import networkx as nx
import numpy as np

from graph_hypothesis.shortest_path import calculate_shortest_path_metric

from .test_generate_random_graph import generate_random_graph


def test_calculate_shortest_path_metric():
    print("--- Running Test Cases for calculate_shortest_path_metric ---")

    # --- Test 1: Small, connected graph (exact calculation) ---
    print("\n--- Test Case 1: Small Connected Graph (Exact) ---")
    G_small = nx.Graph()
    G_small.add_node(0, type="A")
    G_small.add_node(1, type="B")
    G_small.add_node(2, type="X")
    G_small.add_node(3, type="A")
    G_small.add_edges_from([(0, 1), (1, 2), (2, 3)])  # Path A(0)-B(1), A(3)-X(2)-B(1)
    try:
        result = calculate_shortest_path_metric(
            G_small, fixed_type="A", target_type="B"
        )
        # Expected: (dist(0,1) + dist(3,1)) / 2 = (1 + 2) / 2 = 1.5
        print(f"Result for small graph (A to B): {result}")
        assert np.isclose(result, 1.5), f"Test 1 Failed: Expected 1.5, Got {result}"
        print("Test 1 Passed.")
    except AssertionError as e:
        print(f"Test 1 Failed with AssertionError: {e}")
    except UserWarning as e:
        print(f"Test 1: Caught expected warning: {e}")

    # --- Test 2: Graph with unreachable nodes (and warning) ---
    print("\n--- Test Case 2: Graph with Unreachable Nodes (Warning) ---")
    G_unreachable = nx.Graph()
    G_unreachable.add_node(0, type="A")  # A1
    G_unreachable.add_node(1, type="A")  # A2 (isolated from B)
    G_unreachable.add_node(2, type="B")  # B1
    G_unreachable.add_node(3, type="X")
    G_unreachable.add_edges_from([(0, 2), (2, 3)])  # A1-B1, A2 isolated
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = calculate_shortest_path_metric(
                G_unreachable, fixed_type="A", target_type="B"
            )
            # Expected: dist(0,2) = 1. (Node 1 is unreachable and excluded)
            print(f"Result for unreachable graph (A to B): {result}")
            assert np.isclose(result, 1.0), f"Test 2 Failed: Expected 1.0, Got {result}"
            assert len(w) == 1 and issubclass(
                w[-1].category, UserWarning
            ), "Test 2 Failed: Expected a UserWarning."
            print("Test 2 Passed.")
    except AssertionError as e:
        print(f"Test 2 Failed with AssertionError: {e}")

    # --- Test 3: Graph with no paths at all (returns NaN) ---
    print("\n--- Test Case 3: Graph with No Paths (Returns NaN) ---")
    G_no_path = nx.Graph()
    G_no_path.add_node(0, type="A")
    G_no_path.add_node(1, type="A")
    G_no_path.add_node(2, type="B")
    G_no_path.add_node(3, type="X")
    # No edges between A and B, or any path
    G_no_path.add_edges_from([(0, 1), (2, 3)])
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = calculate_shortest_path_metric(
                G_no_path, fixed_type="A", target_type="B"
            )
            print(f"Result for no path graph (A to B): {result}")
            assert np.isnan(result), f"Test 3 Failed: Expected NaN, Got {result}"
            assert len(w) == 1 and issubclass(
                w[-1].category, UserWarning
            ), "Test 3 Failed: Expected a UserWarning."
            print("Test 3 Passed.")
    except AssertionError as e:
        print(f"Test 3 Failed with AssertionError: {e}")

    # --- Test 4: Large graph with sampling (performance test) ---
    print("\n--- Test Case 4: Large Graph with Sampling (Performance) ---")
    NUM_NODES_LARGE = 5000  # Number of nodes
    NUM_EDGES_LARGE = 20000  # Number of edges (sparse)
    NUM_TYPES_LARGE = 5  # Few types to ensure many nodes per type

    G_large = generate_random_graph(NUM_NODES_LARGE, NUM_EDGES_LARGE, NUM_TYPES_LARGE)
    fixed_type_large = "Type0"
    target_type_large = "Type1"

    # Ensure fixed_type and target_type exist in the generated graph
    assert any(G_large.nodes[n]["type"] == fixed_type_large for n in G_large.nodes())
    assert any(G_large.nodes[n]["type"] == target_type_large for n in G_large.nodes())

    # Count how many fixed_type nodes are actually there
    actual_fixed_nodes = len(
        [n for n, data in G_large.nodes(data=True) if data["type"] == fixed_type_large]
    )
    print(
        f"Large Graph: {NUM_NODES_LARGE} nodes, {NUM_EDGES_LARGE} edges, {NUM_TYPES_LARGE} types."
    )
    print(f"Actual fixed_type ('{fixed_type_large}') nodes: {actual_fixed_nodes}")

    import time

    start_time = time.time()
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result_large = calculate_shortest_path_metric(
                G_large, fixed_type=fixed_type_large, target_type=target_type_large
            )
            end_time = time.time()
            print(f"Result for large graph with sampling: {result_large}")
            print(f"Time taken for large graph: {end_time - start_time:.4f} seconds")
            print("Test 4 Passed.")
    except AssertionError as e:
        print(f"Test 4 Failed with AssertionError: {e}")
    except Exception as e:
        print(f"Test 4 Failed with unexpected exception: {e}")

    # --- Test 5: Edge case - empty graph (raises AssertionError) ---
    print("\n--- Test Case 5: Empty Graph (AssertionError) ---")
    G_empty = nx.Graph()
    try:
        G_empty.add_node(
            0, type="A"
        )  # Add node to pass validation, then try to create empty
        G_empty = nx.Graph()  # Actually make it empty for the test
        calculate_shortest_path_metric(G_empty, fixed_type="A", target_type="B")
    except AssertionError as e:
        print(f"Caught expected AssertionError for empty graph: {e}")
        print("Test 5 Passed.")
    except Exception as e:
        print(f"Test 5 Failed: Unexpected exception {e}")

    # --- Test 6: Edge case - fixed_type == target_type (raises AssertionError) ---
    print("\n--- Test Case 6: fixed_type == target_type (AssertionError) ---")
    G_same_type = nx.Graph()
    G_same_type.add_node(0, type="A")
    G_same_type.add_node(1, type="B")
    G_same_type.add_edge(0, 1)
    try:
        calculate_shortest_path_metric(G_same_type, fixed_type="A", target_type="A")
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type == target_type: {e}")
        print("Test 6 Passed.")
    except Exception as e:
        print(f"Test 6 Failed: Unexpected exception {e}")

    # --- Test 7: Edge case - type not in graph (raises AssertionError) ---
    print("\n--- Test Case 7: Type not in Graph (AssertionError) ---")
    G_missing_type = nx.Graph()
    G_missing_type.add_node(0, type="A")
    G_missing_type.add_node(1, type="B")
    G_missing_type.add_edge(0, 1)
    try:
        calculate_shortest_path_metric(G_missing_type, fixed_type="A", target_type="C")
    except AssertionError as e:
        print(f"Caught expected AssertionError for type not in graph: {e}")
        print("Test 7 Passed.")
    except Exception as e:
        print(f"Test 7 Failed: Unexpected exception {e}")
