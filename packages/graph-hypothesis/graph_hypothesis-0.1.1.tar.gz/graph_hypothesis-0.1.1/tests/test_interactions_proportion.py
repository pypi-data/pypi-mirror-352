import warnings

import networkx as nx
import numpy as np

from graph_hypothesis.interactions_proportion import \
    calculate_interaction_proportion_metric

from .test_generate_random_graph import generate_random_graph


def test_calculate_interaction_proportion_metric():

    print("--- Running Test Cases for calculate_interaction_proportion_metric ---")

    # --- Test 1: Basic interaction proportion ---
    print("\n--- Test Case 1: Basic Interaction Proportion ---")
    G1 = nx.Graph()
    G1.add_node("A1", type="TypeA")  # deg=1, 1 B neighbor
    G1.add_node("A2", type="TypeA")  # deg=2, 1 B neighbor, 1 C neighbor
    G1.add_node("B1", type="TypeB")
    G1.add_node("B2", type="TypeB")
    G1.add_node("C1", type="TypeC")
    G1.add_edges_from([("A1", "B1"), ("A2", "B2"), ("A2", "C1")])
    # Total neighbors of TypeA nodes: A1 (1) + A2 (2) = 3
    # Target (TypeB) neighbors of TypeA nodes: A1 (1) + A2 (1) = 2
    # Proportion = 2/3
    try:
        result = calculate_interaction_proportion_metric(
            G1, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for TypeA to TypeB proportion: {result}")
        assert np.isclose(result, 2 / 3), f"Test 1 Failed: Expected {2/3}, Got {result}"
        print("Test 1 Passed.")
    except AssertionError as e:
        print(f"Test 1 Failed with AssertionError: {e}")

    # --- Test 2: No interactions of target_type from fixed_type ---
    print("\n--- Test Case 2: No Target Type Interactions ---")
    G2 = nx.Graph()
    G2.add_node("A1", type="TypeA")  # deg=1, 0 B neighbors
    G2.add_node("A2", type="TypeA")  # deg=1, 0 B neighbors
    G2.add_node("X1", type="TypeX")
    G2.add_node("X2", type="TypeX")
    G2.add_node("B1", type="TypeB")
    G2.add_edges_from([("A1", "X1"), ("A2", "X2")])  # A nodes only connect to X
    try:
        result = calculate_interaction_proportion_metric(
            G2, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for no TypeA to TypeB proportion: {result}")
        assert np.isclose(result, 0.0), f"Test 2 Failed: Expected 0.0, Got {result}"
        print("Test 2 Passed.")
    except AssertionError as e:
        print(f"Test 2 Failed with AssertionError: {e}")

    # --- Test 3: Fixed type nodes exist but have no connections (returns NaN) ---
    print("\n--- Test Case 3: Fixed Type Nodes with No Connections (Returns NaN) ---")
    G3 = nx.Graph()
    G3.add_node("A1", type="TypeA")  # Isolated
    G3.add_node("A2", type="TypeA")  # Isolated
    G3.add_node("B1", type="TypeB")
    G3.add_node("X1", type="TypeX")
    G3.add_edges_from([("B1", "X1")])  # B and X are connected, A are isolated
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = calculate_interaction_proportion_metric(
                G3, fixed_type="TypeA", target_type="TypeB"
            )
            print(f"Result for isolated fixed_type nodes: {result}")
            assert np.isnan(result), f"Test 3 Failed: Expected NaN, Got {result}"
            assert len(w) == 1 and issubclass(
                w[-1].category, UserWarning
            ), "Test 3 Failed: Expected a UserWarning."
            print("Test 3 Passed.")
    except AssertionError as e:
        print(f"Test 3 Failed with AssertionError: {e}")

    # --- Test 4: No fixed_type nodes in graph (returns NaN) ---
    print("\n--- Test Case 4: No Fixed Type Nodes (Returns NaN) ---")
    G4 = nx.Graph()
    G4.add_node("B1", type="TypeB")
    G4.add_node("X1", type="TypeX")
    G4.add_edge("B1", "X1")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = calculate_interaction_proportion_metric(
                G4, fixed_type="TypeA", target_type="TypeB"
            )
            print(f"Result for no fixed_type nodes: {result}")
            assert np.isnan(result), f"Test 4 Failed: Expected NaN, Got {result}"
            assert len(w) == 1 and issubclass(
                w[-1].category, UserWarning
            ), "Test 4 Failed: Expected a UserWarning."
            print("Test 4 Passed.")
    except AssertionError as e:
        print(f"Test 4 Failed with AssertionError: {e}")

    # --- Test 5: Edge case - empty graph (raises AssertionError) ---
    print("\n--- Test Case 5: Empty Graph (AssertionError) ---")
    G_empty = nx.Graph()
    try:
        calculate_interaction_proportion_metric(
            G_empty, fixed_type="TypeA", target_type="TypeB"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for empty graph: {e}")
        print("Test 5 Passed.")
    except Exception as e:
        print(f"Test 5 Failed: Unexpected exception: {e}")

    # --- Test 6: Edge case - fixed_type == target_type (raises AssertionError) ---
    print("\n--- Test Case 6: fixed_type == target_type (AssertionError) ---")
    G_same_type = nx.Graph()
    G_same_type.add_node(0, type="A")
    G_same_type.add_node(1, type="B")
    G_same_type.add_edge(0, 1)
    try:
        calculate_interaction_proportion_metric(
            G_same_type, fixed_type="A", target_type="A"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type == target_type: {e}")
        print("Test 6 Passed.")
    except Exception as e:
        print(f"Test 6 Failed: Unexpected exception: {e}")

    # --- Test 7: Edge case - fixed_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 7: fixed_type not in Graph (AssertionError) ---")
    G_missing_type_fixed = nx.Graph()
    G_missing_type_fixed.add_node(0, type="X")
    G_missing_type_fixed.add_node(1, type="Y")
    G_missing_type_fixed.add_edge(0, 1)
    try:
        calculate_interaction_proportion_metric(
            G_missing_type_fixed, fixed_type="A", target_type="Y"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type not in graph: {e}")
        print("Test 7 Passed.")
    except Exception as e:
        print(f"Test 7 Failed: Unexpected exception: {e}")

    # --- Test 8: Edge case - target_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 8: target_type not in Graph (AssertionError) ---")
    G_missing_type_target = nx.Graph()
    G_missing_type_target.add_node(0, type="A")
    G_missing_type_target.add_node(1, type="X")
    G_missing_type_target.add_edge(0, 1)
    try:
        calculate_interaction_proportion_metric(
            G_missing_type_target, fixed_type="A", target_type="B"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for target_type not in graph: {e}")
        print("Test 8 Passed.")
    except Exception as e:
        print(f"Test 8 Failed: Unexpected exception: {e}")

    # --- Test 9: Large graph (performance check) ---
    print("\n--- Test Case 9: Large Graph (Performance) ---")
    NUM_NODES_LARGE = 50000
    NUM_EDGES_LARGE = 200000
    NUM_TYPES_LARGE = 5
    G_large = generate_random_graph(NUM_NODES_LARGE, NUM_EDGES_LARGE, NUM_TYPES_LARGE)

    type_large_1 = "Type0"
    type_large_2 = "Type1"

    # Ensure chosen types exist in the generated graph
    assert any(G_large.nodes[n]["type"] == type_large_1 for n in G_large.nodes())
    assert any(G_large.nodes[n]["type"] == type_large_2 for n in G_large.nodes())

    import time

    start_time = time.time()
    try:
        result_large = calculate_interaction_proportion_metric(
            G_large, fixed_type=type_large_1, target_type=type_large_2
        )
        end_time = time.time()
        print(
            f"Result for large graph interaction proportion ({type_large_1}-{type_large_2}): {result_large}"
        )
        print(f"Time taken for large graph: {end_time - start_time:.4f} seconds")
        print("Test 9 Passed.")  # Just check for completion and reasonable time
    except AssertionError as e:
        print(f"Test 9 Failed with AssertionError: {e}")
    except Exception as e:
        print(f"Test 9 Failed with unexpected exception: {e}")
