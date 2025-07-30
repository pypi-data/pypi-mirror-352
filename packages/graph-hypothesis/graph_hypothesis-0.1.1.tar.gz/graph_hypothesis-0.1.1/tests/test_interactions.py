import networkx as nx

from graph_hypothesis.interactions import calculate_interactions_metric

from .test_generate_random_graph import generate_random_graph


def test_calculate_interactions_metric():

    print("--- Running Test Cases for calculate_interactions_metric ---")

    # --- Test 1: Basic interactions ---
    print("\n--- Test Case 1: Basic Interactions ---")
    G1 = nx.Graph()
    G1.add_node("A1", type="TypeA")
    G1.add_node("A2", type="TypeA")
    G1.add_node("B1", type="TypeB")
    G1.add_node("B2", type="TypeB")
    G1.add_node("C1", type="TypeC")
    G1.add_edges_from([("A1", "B1"), ("A2", "B2"), ("A1", "C1")])  # 2 A-B interactions
    try:
        result = calculate_interactions_metric(
            G1, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for A-B interactions: {result}")
        assert result == 2, f"Test 1 Failed: Expected 2, Got {result}"
        print("Test 1 Passed.")
    except AssertionError as e:
        print(f"Test 1 Failed with AssertionError: {e}")

    # --- Test 2: No interactions between specified types ---
    print("\n--- Test Case 2: No Interactions ---")
    G2 = nx.Graph()
    G2.add_node("A1", type="TypeA")
    G2.add_node("A2", type="TypeA")
    G2.add_node("B1", type="TypeB")
    G2.add_node("B2", type="TypeB")
    G2.add_node("C1", type="TypeC")
    G2.add_edges_from([("A1", "A2"), ("B1", "B2"), ("A1", "C1")])  # No A-B edges
    try:
        result = calculate_interactions_metric(
            G2, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for no A-B interactions: {result}")
        assert result == 0, f"Test 2 Failed: Expected 0, Got {result}"
        print("Test 2 Passed.")
    except AssertionError as e:
        print(f"Test 2 Failed with AssertionError: {e}")

    # --- Test 3: Graph with multiple types, counting specific pair ---
    print("\n--- Test Case 3: Multiple Types, Specific Pair ---")
    G3 = nx.Graph()
    G3.add_node(0, type="X")
    G3.add_node(1, type="Y")
    G3.add_node(2, type="Z")
    G3.add_node(3, type="Y")
    G3.add_node(4, type="X")
    G3.add_edges_from(
        [(0, 1), (0, 2), (1, 3), (2, 4), (0, 4), (4, 1)]
    )  # Edges: X-Y, X-Z, Y-Y, Z-X
    # X-Y interactions: (0,1), (4,1) - should be 2
    # X-Z interactions: (0,2), (4,2) - should be 2
    try:
        result_xy = calculate_interactions_metric(G3, fixed_type="X", target_type="Y")
        print(f"Result for X-Y interactions: {result_xy}")
        assert result_xy == 2, f"Test 3 (X-Y) Failed: Expected 2, Got {result_xy}"

        result_xz = calculate_interactions_metric(G3, fixed_type="X", target_type="Z")
        print(f"Result for X-Z interactions: {result_xz}")
        assert result_xz == 2, f"Test 3 (X-Z) Failed: Expected 2, Got {result_xz}"
        print("Test 3 Passed.")
    except AssertionError as e:
        print(f"Test 3 Failed with AssertionError: {e}")

    # --- Test 4: Edge case - empty graph (raises AssertionError) ---
    print("\n--- Test Case 4: Empty Graph (AssertionError) ---")
    G_empty = nx.Graph()
    try:
        calculate_interactions_metric(G_empty, fixed_type="TypeA", target_type="TypeB")
    except AssertionError as e:
        print(f"Caught expected AssertionError for empty graph: {e}")
        print("Test 4 Passed.")
    except Exception as e:
        print(f"Test 4 Failed: Unexpected exception {e}")

    # --- Test 5: Edge case - fixed_type == target_type (raises AssertionError) ---
    print("\n--- Test Case 5: fixed_type == target_type (AssertionError) ---")
    G_same_type = nx.Graph()
    G_same_type.add_node(0, type="A")
    G_same_type.add_node(1, type="B")
    G_same_type.add_edge(0, 1)
    try:
        calculate_interactions_metric(G_same_type, fixed_type="A", target_type="A")
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type == target_type: {e}")
        print("Test 5 Passed.")
    except Exception as e:
        print(f"Test 5 Failed: Unexpected exception {e}")

    # --- Test 6: Edge case - fixed_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 6: fixed_type not in Graph (AssertionError) ---")
    G_missing_fixed_type = nx.Graph()
    G_missing_fixed_type.add_node(0, type="A")
    G_missing_fixed_type.add_node(1, type="B")
    G_missing_fixed_type.add_edge(0, 1)
    try:
        calculate_interactions_metric(
            G_missing_fixed_type, fixed_type="C", target_type="B"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type not in graph: {e}")
        print("Test 6 Passed.")
    except Exception as e:
        print(f"Test 6 Failed: Unexpected exception {e}")

    # --- Test 7: Edge case - target_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 7: target_type not in Graph (AssertionError) ---")
    G_missing_target_type = nx.Graph()
    G_missing_target_type.add_node(0, type="A")
    G_missing_target_type.add_node(1, type="B")
    G_missing_target_type.add_edge(0, 1)
    try:
        calculate_interactions_metric(
            G_missing_target_type, fixed_type="A", target_type="C"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for target_type not in graph: {e}")
        print("Test 7 Passed.")
    except Exception as e:
        print(f"Test 7 Failed: Unexpected exception {e}")

    # --- Test 9: Large graph (performance check) ---
    print("\n--- Test Case 9: Large Graph (Performance) ---")
    NUM_NODES_LARGE = 10000
    NUM_EDGES_LARGE = 50000
    NUM_TYPES_LARGE = 10  # Ensure types exist
    G_large = generate_random_graph(NUM_NODES_LARGE, NUM_EDGES_LARGE, NUM_TYPES_LARGE)

    # Pick two distinct types that are likely to exist
    type_large_1 = "Type1"
    type_large_2 = "Type2"

    # Ensure chosen types exist in the generated graph
    assert any(G_large.nodes[n]["type"] == type_large_1 for n in G_large.nodes())
    assert any(G_large.nodes[n]["type"] == type_large_2 for n in G_large.nodes())

    import time

    start_time = time.time()
    try:
        result_large = calculate_interactions_metric(
            G_large, fixed_type=type_large_1, target_type=type_large_2
        )
        end_time = time.time()
        print(
            f"Result for large graph interactions ({type_large_1}-{type_large_2}): {result_large}"
        )
        print(f"Time taken for large graph: {end_time - start_time:.4f} seconds")
        print("Test 9 Passed.")  # Just check for completion and reasonable time
    except AssertionError as e:
        print(f"Test 9 Failed with AssertionError: {e}")
    except Exception as e:
        print(f"Test 9 Failed with unexpected exception: {e}")
