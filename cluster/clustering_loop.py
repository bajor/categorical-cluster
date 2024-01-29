import copy
from typing import Optional, Tuple, List, Dict

from cluster.clustering_utils import (
    _merge_algo,
    _get_cluster,
    _merge_pairs,
    _initial_similarity_against_all,
    _clean_up_first_iteration,
    _remove_duplicates_from_first_iter,
    _similarity_agains_all,
    _get_empty_similarity_first_iter,
    _get_iteration_of_empty_clusters,
    _merge_algo,
)


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


def _next_iteration_of_algo(
    pairs_to_merge: List[Tuple[int, int]],
    previous_clusters: List[Dict],
    final_clusters: List[Dict],
    min_similarity: float,
    min_elements_in_cluster: int,
    clustering_logs: Optional[List] = None,
) -> Tuple[List[Tuple[int, int]], List[Dict]]:
    """
    This function performs all remaining iterations of clustering after first iteration is completed.

    Args:
        pairs_to_merge (List[Tuple[int, int]]): Pairs of clusters to be merged.
        previous_clusters (List[Dict]): Clusters from the previous iteration.
        final_clusters (List[Dict]): Completed list of cluster at this iteration.
        min_similarity (float): The minimum similarity threshold for clustering.
        min_elements_in_cluster (int): The minimum number of elements in a cluster.
        clustering_logs (List, optional): Logs for the clustering process. Defaults to None.

    Returns:
        Tuple[List[Tuple[int, int]], List[Dict]]: Returns a tuple containing lists of pairs to merge and new clusters.
    """
    new_cluster_id = 0
    new_clusters = []

    for pair in pairs_to_merge:
        cluster_1 = _get_cluster(pair[0], previous_clusters)
        cluster_2 = _get_cluster(pair[1], previous_clusters)
        new_cluster = _merge_pairs(cluster_1, cluster_2, new_cluster_id)
        new_cluster_id += 1
        new_clusters.append(new_cluster)
    new_clusters = sorted(new_clusters, key=lambda x: len(x["all_elements"]))
    new_clusters_copy = copy.deepcopy(new_clusters)
    similaritries = _similarity_agains_all(
        new_clusters, min_similarity, clustering_logs
    )
    touched_cluster_ids, empty_similarity, pairs_to_merge = _merge_algo(
        new_clusters, similaritries
    )
    untouched_empty_similarity = _get_empty_similarity_first_iter(
        new_clusters, touched_cluster_ids, empty_similarity
    )
    empty_similarity_clusters = _get_iteration_of_empty_clusters(
        untouched_empty_similarity,
        similaritries,
        min_elements_in_cluster=min_elements_in_cluster,
    )
    if empty_similarity_clusters:
        final_clusters.extend(empty_similarity_clusters)
    return pairs_to_merge, new_clusters_copy
