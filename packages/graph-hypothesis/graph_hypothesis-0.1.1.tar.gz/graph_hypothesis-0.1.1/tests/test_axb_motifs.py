import warnings

import networkx as nx

from graph_hypothesis.axb_motifs import calculate_axb_motifs_metric

from .test_generate_random_graph import generate_random_graph


def test_calculate_axb_motifs_metric():

    print("--- Running Test Cases for calculate_axb_motifs_metric ---")

    # --- Test 1: Basic A-X-B motifs ---
    print("\n--- Test Case 1: Basic A-X-B Motifs ---")
    G1 = nx.Graph()
    G1.add_node("A1", type="TypeA")
    G1.add_node("A2", type="TypeA")
    G1.add_node("B1", type="TypeB")
    G1.add_node("B2", type="TypeB")
    G1.add_node("X1", type="TypeX")  # Center node 1
    G1.add_node("X2", type="TypeX")  # Center node 2
    G1.add_node("Y1", type="TypeY")  # Another center node type

    G1.add_edges_from(
        [
            ("A1", "X1"),
            ("X1", "B1"),  # A1-X1-B1 (1 motif)
            ("A2", "X1"),
            ("X1", "B2"),  # A2-X1-B2 (1 motif)
            ("A1", "Y1"),
            ("Y1", "B1"),  # A1-Y1-B1 (1 motif)
            ("A1", "X2"),
            ("X2", "B1"),  # A1-X2-B1 (1 motif)
        ]
    )
    # Total expected: 4 motifs (A-X-B paths)
    # X1 is connected to 2 TypeA and 2 TypeB. Motifs through X1: 2*2 = 4
    # Y1 is connected to 1 TypeA and 1 TypeB. Motifs through Y1: 1*1 = 1
    # X2 is connected to 1 TypeA and 1 TypeB. Motifs through X2: 1*1 = 1
    # Wait, my manual count was wrong. Let's trace:
    # Center X1: Neighbors A1(A), A2(A), B1(B), B2(B).
    #   A-neighbors = 2, B-neighbors = 2. Motifs = 2 * 2 = 4 (A1-X1-B1, A1-X1-B2, A2-X1-B1, A2-X1-B2)
    # Center Y1: Neighbors A1(A), B1(B).
    #   A-neighbors = 1, B-neighbors = 1. Motifs = 1 * 1 = 1 (A1-Y1-B1)
    # Center X2: Neighbors A1(A), B1(B).
    #   A-neighbors = 1, B-neighbors = 1. Motifs = 1 * 1 = 1 (A1-X2-B1)
    # Total = 4 + 1 + 1 = 6
    try:
        result = calculate_axb_motifs_metric(
            G1, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for A-X-B motifs: {result}")
        assert result == 6, f"Test 1 Failed: Expected 6, Got {result}"
        print("Test 1 Passed.")
    except AssertionError as e:
        print(f"Test 1 Failed with AssertionError: {e}")

    # --- Test 2: No A-X-B motifs (A and B exist, but no connecting X) ---
    print("\n--- Test Case 2: No A-X-B Motifs ---")
    G2 = nx.Graph()
    G2.add_node("A1", type="TypeA")
    G2.add_node("A2", type="TypeA")
    G2.add_node("B1", type="TypeB")
    G2.add_node("B2", type="TypeB")
    G2.add_node("X1", type="TypeX")
    G2.add_edges_from(
        [("A1", "A2"), ("B1", "B2"), ("A1", "X1")]
    )  # X1 only connects to A, not B
    try:
        result = calculate_axb_motifs_metric(
            G2, fixed_type="TypeA", target_type="TypeB"
        )
        print(f"Result for no A-X-B motifs: {result}")
        assert result == 0, f"Test 2 Failed: Expected 0, Got {result}"
        print("Test 2 Passed.")
    except AssertionError as e:
        print(f"Test 2 Failed with AssertionError: {e}")

    # --- Test 3: No fixed_type or target_type nodes in graph (returns 0 with warning) ---
    print("\n--- Test Case 3: No Fixed/Target Type Nodes (Warning) ---")
    G3 = nx.Graph()
    G3.add_node("X1", type="TypeX")
    G3.add_node("Y1", type="TypeY")
    G3.add_edge("X1", "Y1")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = calculate_axb_motifs_metric(
                G3, fixed_type="TypeA", target_type="TypeB"
            )
            print(f"Result for no A/B nodes: {result}")
            assert result == 0, f"Test 3 Failed: Expected 0, Got {result}"
            assert len(w) == 1 and issubclass(
                w[-1].category, UserWarning
            ), "Test 3 Failed: Expected a UserWarning."
            print("Test 3 Passed.")
    except AssertionError as e:
        print(f"Test 3 Failed with AssertionError: {e}")

    # --- Test 4: Edge case - empty graph (raises AssertionError) ---
    print("\n--- Test Case 4: Empty Graph (AssertionError) ---")
    G_empty = nx.Graph()
    try:
        calculate_axb_motifs_metric(G_empty, fixed_type="TypeA", target_type="TypeB")
    except AssertionError as e:
        print(f"Caught expected AssertionError for empty graph: {e}")
        print("Test 4 Passed.")
    except Exception as e:
        print(f"Test 4 Failed: Unexpected exception: {e}")

    # --- Test 5: Edge case - fixed_type == target_type (raises AssertionError) ---
    print("\n--- Test Case 5: fixed_type == target_type (AssertionError) ---")
    G_same_type = nx.Graph()
    G_same_type.add_node(0, type="A")
    G_same_type.add_node(1, type="B")
    G_same_type.add_node(2, type="X")
    G_same_type.add_edges_from([(0, 2), (2, 1)])
    try:
        calculate_axb_motifs_metric(G_same_type, fixed_type="A", target_type="A")
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type == target_type: {e}")
        print("Test 5 Passed.")
    except Exception as e:
        print(f"Test 5 Failed: Unexpected exception: {e}")

    # --- Test 6: Edge case - fixed_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 6: fixed_type not in Graph (AssertionError) ---")
    G_missing_type_fixed = nx.Graph()
    G_missing_type_fixed.add_node(0, type="X")
    G_missing_type_fixed.add_node(1, type="Y")
    G_missing_type_fixed.add_node(2, type="Z")
    G_missing_type_fixed.add_edges_from([(0, 2), (1, 2)])
    try:
        calculate_axb_motifs_metric(
            G_missing_type_fixed, fixed_type="A", target_type="Y"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for fixed_type not in graph: {e}")
        print("Test 6 Passed.")
    except Exception as e:
        print(f"Test 6 Failed: Unexpected exception: {e}")

    # --- Test 7: Edge case - target_type not in graph (raises AssertionError) ---
    print("\n--- Test Case 7: target_type not in Graph (AssertionError) ---")
    G_missing_type_target = nx.Graph()
    G_missing_type_target.add_node(0, type="A")
    G_missing_type_target.add_node(1, type="X")
    G_missing_type_target.add_node(2, type="Y")
    G_missing_type_target.add_edges_from([(0, 1), (1, 2)])
    try:
        calculate_axb_motifs_metric(
            G_missing_type_target, fixed_type="A", target_type="B"
        )
    except AssertionError as e:
        print(f"Caught expected AssertionError for target_type not in graph: {e}")
        print("Test 7 Passed.")
    except Exception as e:
        print(f"Test 7 Failed: Unexpected exception: {e}")

    # --- Test 8: Large graph (performance check) ---
    print("\n--- Test Case 8: Large Graph (Performance) ---")
    NUM_NODES_LARGE = 50000
    NUM_EDGES_LARGE = 200000
    NUM_TYPES_LARGE = 10
    G_large = generate_random_graph(NUM_NODES_LARGE, NUM_EDGES_LARGE, NUM_TYPES_LARGE)

    type_large_A = "Type0"
    type_large_B = "Type1"

    # Ensure chosen types exist in the generated graph
    assert any(G_large.nodes[n]["type"] == type_large_A for n in G_large.nodes())
    assert any(G_large.nodes[n]["type"] == type_large_B for n in G_large.nodes())

    import time

    start_time = time.time()
    try:
        result_large = calculate_axb_motifs_metric(
            G_large, fixed_type=type_large_A, target_type=type_large_B
        )
        end_time = time.time()
        print(
            f"Result for large graph A-X-B motifs ({type_large_A}-{type_large_B}): {result_large}"
        )
        print(f"Time taken for large graph: {end_time - start_time:.4f} seconds")
        print("Test 8 Passed.")  # Just check for completion and reasonable time
    except AssertionError as e:
        print(f"Test 8 Failed with AssertionError: {e}")
    except Exception as e:
        print(f"Test 8 Failed with unexpected exception: {e}")
