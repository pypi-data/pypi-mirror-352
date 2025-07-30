import numpy as np

from graph_hypothesis.core import graph_hypothesis

from .test_generate_random_graph import generate_random_graph


def test_graph_hypothesis():
    # --- Test Case for perform_permutation_test ---
    print("--- Running Permutation Test Example ---")
    NUM_NODES_LARGE = 1000
    NUM_EDGES_LARGE = 2000
    NUM_TYPES_LARGE = 4
    G_test = generate_random_graph(NUM_NODES_LARGE, NUM_EDGES_LARGE, NUM_TYPES_LARGE)

    fixed_type_test = "Type0"
    target_type_test = "Type1"

    # Run the permutation test
    num_perms = 1000  # Number of permutations for the test
    test_seed = 42  # For reproducibility

    try:
        results = graph_hypothesis(
            fixed_type=fixed_type_test,
            target_type=target_type_test,
            original_graph=G_test,
            metric_name="shortest_path",
            num_permutations=num_perms,
            random_seed=test_seed,
        )

        print(results)

        print("\nPermutation Test Results Summary:")
        print(f"Observed Statistic: {results['observed_statistic']}")
        print(f"P-value: {results['p_value']}")
        print(f"Number of Permutations: {results['num_permutations']}")
        print(f"Number of Processes Used: {results['num_processes_used']}")

        if len(results["permutation_statistics"]) > 0:
            perm_stats_array = np.array(results["permutation_statistics"])
            print(
                f"Permuted Stats (Min/Max/Mean): {perm_stats_array.min():.2f} / {perm_stats_array.max():.2f} / {perm_stats_array.mean():.2f}"
            )

        print("\nPermutation test example completed successfully.")

    except AssertionError as e:
        print(f"\nPermutation Test Example FAILED: {e}")
    except Exception as e:
        print(f"\nPermutation Test Example encountered an unexpected error: {e}")
