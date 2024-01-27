from typing import Optional, Tuple
import copy
from clustering_utils import (
    _next_iteration_of_algo,
    _initial_similarity_against_all,
    _clean_up_first_iteration,
    _remove_duplicates_from_first_iter,
    _similarity_agains_all,
    _get_empty_similarity_first_iter,
    _get_iteration_of_empty_clusters,
    _merge_algo,
    _prepare_data,
    _prepare_output,
    _print_start_time,
    _print_end_time,
)


def perform_clustering(
    data: list,
    min_elements_in_cluster: int,
    min_similarity_first_iter: float,
    min_similarity_next_iters: float = None,
    clustering_log_initial: list = None,
    clustering_log_next: list = None,
    print_start_end: bool = False,
) -> list:
    """
    This function performs clustering on the given data.

    Parameters:
    data (list): The data to be clustered.
    min_elements_in_cluster (int): The minimum number of elements in a cluster.
    min_similarity_first_iter (float): The minimum similarity for the first iteration.
    min_similarity_next_iters (float, optional): The minimum similarity for the next iterations. Defaults to similarity_first_iteration.
    clustering_log_initial (list, optional): The initial clustering log.
    clustering_log_next (list, optional): The next clustering log.
    print_start_end (bool, optional): Whether to print the start and end time.

    Returns:
    list: The final clusters after performing clustering.
    """
    if print_start_end:
        start_time = _print_start_time()

    original_data = copy.deepcopy(data)
    data = _prepare_data(data)

    if not min_similarity_next_iters:
        min_similarity_next_iters = min_similarity_first_iter

    final_clusters = []

    (
        empty_similarity_clusters,
        pairs_to_merge,
        previous_clusters,
    ) = _first_iteration_of_algo(
        data,
        min_similarity_first_iter,
        min_elements_in_cluster=min_elements_in_cluster,
        clustering_logs=clustering_log_initial,
    )

    if empty_similarity_clusters:
        final_clusters.extend(empty_similarity_clusters)

    while len(pairs_to_merge) > 0:
        new_pairs_to_merge, new_clusters = _next_iteration_of_algo(
            pairs_to_merge,
            previous_clusters,
            final_clusters,
            min_similarity=min_similarity_next_iters,
            min_elements_in_cluster=min_elements_in_cluster,
            clustering_logs=clustering_log_next,
        )
        pairs_to_merge = new_pairs_to_merge
        previous_clusters = new_clusters

        if len(pairs_to_merge) == 0:
            remaining_clusters = new_clusters
            remaining_clusters = [x["all_elements"] for x in remaining_clusters]

            for i in range(len(remaining_clusters)):
                for j in range(len(remaining_clusters[i])):
                    if isinstance(remaining_clusters[i][j], tuple):
                        remaining_clusters[i][j] = remaining_clusters[i][j][0]
                remaining_clusters[i] = tuple(set(remaining_clusters[i]))

            for remaining_cluster in remaining_clusters:
                if not remaining_cluster in final_clusters:
                    final_clusters.append(remaining_cluster)

    final_clusters = sorted(final_clusters, key=lambda x: len(x))

    if print_start_end:
        _print_end_time(start_time)
    return _prepare_output(final_clusters, original_data)


def _first_iteration_of_algo(
    combined: list,
    min_similarity: float,
    min_elements_in_cluster: int,
    clustering_logs: Optional[list] = None,
) -> Tuple[list, list, list]:
    """
    This function performs the first iteration of the clustering algorithm.

    Args:
        combined (list): The combined data to be clustered.
        min_similarity (float): The minimum similarity threshold for clustering.
        min_elements_in_cluster (int): The minimum number of elements in a cluster.
        clustering_logs (list, optional): Logs for the clustering process. Defaults to None.

    Returns:
        Tuple[list, list, list]: Returns a tuple containing lists of empty similarity clusters, pairs to merge, and clusters.
    """
    summary = []
    for record in combined:
        summary.append(
            _initial_similarity_against_all(
                record, combined, min_similarity, clustering_logs
            )
        )
    summary = [x for x in summary if x["similarity"]]
    clusters = _clean_up_first_iteration(summary)
    clusters = _remove_duplicates_from_first_iter(clusters)
    clusters = sorted(clusters, key=lambda x: len(x["all_elements"]))
    clusters_copy = copy.deepcopy(clusters)
    similars = _similarity_agains_all(clusters_copy, min_similarity, clustering_logs)
    touched_cluster_ids, empty_similarity, pairs_to_merge = _merge_algo(
        clusters, similars
    )
    untouched_empty_similarity = _get_empty_similarity_first_iter(
        clusters, touched_cluster_ids, empty_similarity
    )
    empty_similarity_clusters = _get_iteration_of_empty_clusters(
        untouched_empty_similarity, similars, min_elements_in_cluster
    )
    return empty_similarity_clusters, pairs_to_merge, clusters