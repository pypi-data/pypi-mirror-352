import warnings
from typing import \
    List  # Keep existing types, add List for permutation_statistics

import numpy as np


def hypothesis_tester(
    observed_statistic: float, permutation_statistics: List[float], test_type: str
) -> float:
    """
    Calculates the p-value for a permutation test based on the observed statistic,
    a distribution of permuted statistics, and the specified test type.

    Args:
        observed_statistic (float): The metric value calculated on the original graph.
        permutation_statistics (List[float]): A list of metric values from all permuted graphs.
                                             May contain np.nan values.
        test_type (str): The type of hypothesis test to perform for p-value calculation.
                         Can be 'greater' (one-sided, observed > random),
                         'less' (one-sided, observed < random), or
                         'two-sided' (observed is extreme in either direction).

    Returns:
        float: The calculated p-value, or np.nan if no valid permutation
               statistics could be generated.

    Raises:
        AssertionError:
            - If `test_type` is not one of 'greater', 'less', or 'two-sided'.
            - If `observed_statistic` is not one of type 'float'.
            - If `permutation_statistics` not list of 'float'.
    """
    valid_test_types = {"greater", "less", "two-sided"}
    assert (
        test_type in valid_test_types
    ), f"Invalid test_type: '{test_type}'. Choose from {list(valid_test_types)}."

    assert isinstance(observed_statistic, float) or isinstance(
        observed_statistic, int
    ), "variable 'observed_statistic' not float or int"
    assert isinstance(
        permutation_statistics, list
    ), "variable 'permutation_statistics' not list"
    for i in permutation_statistics:
        assert isinstance(i, float) or isinstance(
            i, int
        ), "variable 'permutation_statistics' not list of floats/ints"

    # Filter out any NaN values from permutation_statistics
    # It's important to use a NumPy array for efficient element-wise comparisons and summation
    valid_permutation_stats = np.array(
        [s for s in permutation_statistics if not np.isnan(s)]
    )
    number_valid_permutations = len(valid_permutation_stats)
    if number_valid_permutations == 0:
        warnings.warn(
            "No valid permutation statistics could be generated. Returning NaN p-value.",
            UserWarning,
        )
        return np.nan

    if number_valid_permutations < 1000:
        warnings.warn(
            f"Only {number_valid_permutations} permutation statistics could be generated. p-value may be unreliable",
            UserWarning,
        )

    p_value = np.nan  # Default in case calculation is undefined

    if test_type == "greater":
        # One-tailed test: Is the observed statistic significantly greater than random?
        extreme_count = np.sum(valid_permutation_stats >= observed_statistic)
        p_value = (extreme_count + 1) / (len(valid_permutation_stats) + 1)

    elif test_type == "less":
        # One-tailed test: Is the observed statistic significantly less than random?
        extreme_count = np.sum(valid_permutation_stats <= observed_statistic)
        p_value = (extreme_count + 1) / (len(valid_permutation_stats) + 1)

    elif test_type == "two-sided":
        # Two-tailed test: Is the observed statistic significantly different (either greater or less) than random?
        # This approach calculates the absolute difference from the mean of the permutation distribution.
        mean_perm_stat = np.mean(valid_permutation_stats)

        # Calculate how 'extreme' the observed statistic is relative to the mean of the null distribution
        observed_distance_from_mean = np.abs(observed_statistic - mean_perm_stat)

        # Count how many permuted statistics are as far or farther from the mean as the observed one
        extreme_count = np.sum(
            np.abs(valid_permutation_stats - mean_perm_stat)
            >= observed_distance_from_mean
        )

        p_value = (extreme_count + 1) / (len(valid_permutation_stats) + 1)

    return p_value
