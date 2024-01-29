import copy

from cluster.clustering_loop import _first_iteration_of_algo, _next_iteration_of_algo
from cluster.prepare_data import (
    _prepare_data,
    _prepare_output,
    _print_end_time,
    _print_start_time,
)


def cluster(
    data: list,
    min_elements_in_cluster: int,
    min_similarity_first_iter: float,
    min_similarity_next_iters: float = None,
    similarity_log_initial_iter: list = None,
    similrity_log_next_iter: list = None,
    print_start_end: bool = False,
) -> list:
    """
    This function performs clustering on the given data.

    Args:
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
        clustering_logs=similarity_log_initial_iter,
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
            clustering_logs=similrity_log_next_iter,
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
