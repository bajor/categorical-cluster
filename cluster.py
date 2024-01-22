import copy
from utils import (
    next_iteration_of_algo,
    # cluster_has_more_than_one_country,
    initial_similarity_against_all,
    clean_up_first_iteration,
    remove_duplicates_from_first_iteration,
    similarity_agains_all,
    get_empty_similarity_first_iteration,
    get_round_of_empty_clusters_first_iteration,
    algo_merge,
)


def perform_clustering(
    prepared_data,
    min_elements_in_cluster,
    min_similarity_first_iteration,
    min_similarity_next_itarations=None,
    clustering_log_initial_iteration_func=None,
    clustering_log_next_iterations_func=None,
):
    if not min_similarity_next_itarations:
        min_similarity_next_itarations=min_similarity_first_iteration


    final_clusters = []

    # data = [prepare_records(x) for x in data]

    # combined_dict = {}
    # for record in copy.deepcopy(prepared_data):
    #     combined_dict[record["video_id"]] = record

    (
        empty_similarity_clusters,
        pairs_to_merge,
        previous_clusters,
    ) = first_iteration_of_algo(
        prepared_data,
        min_similarity_first_iteration,
        min_videos_in_clusters=min_elements_in_cluster,
        clustering_logs_func=clustering_log_initial_iteration_func,
    )

    if empty_similarity_clusters:
        final_clusters.extend(empty_similarity_clusters)

    while len(pairs_to_merge) > 0:
        new_pairs_to_merge, new_clusters = next_iteration_of_algo(
            pairs_to_merge,
            previous_clusters,
            final_clusters,
            min_similarity=min_similarity_next_itarations,
            min_videos_in_cluster=min_elements_in_cluster,
            clustering_logs_func=clustering_log_next_iterations_func,
        )
        pairs_to_merge = new_pairs_to_merge
        previous_clusters = new_clusters

        if len(pairs_to_merge) == 0:
            new_clusters = [x["all_videos"] for x in new_clusters]

            final_clusters_copy = copy.deepcopy(final_clusters)
            final_clusters_videos = []
            for cluster in final_clusters_copy:
                videos = [x[0] for x in cluster]
                final_clusters_videos.append(set(videos))

            new_clusters_videos = []
            for cluster in new_clusters:
                videos = [x[0] for x in cluster]
                new_clusters_videos.append(set(videos))

            for cluster, cluster_video in zip(new_clusters, new_clusters_videos):
                if cluster_video in final_clusters_videos:
                    continue
                final_clusters.append(cluster)

    # final_clusters = [x for x in final_clusters if cluster_has_more_than_one_country(x)]
    final_clusters = sorted(final_clusters, key=lambda x: len(x))

    return final_clusters


def first_iteration_of_algo(combined, min_similarity, min_videos_in_clusters, clustering_logs_func=None):
    summary = []
    for record in combined:
        summary.append(
            initial_similarity_against_all(
                record, combined, min_similarity, clustering_logs_func
            )
        )
    summary = [x for x in summary if x["similarity"]]
    clusters = clean_up_first_iteration(summary)
    clusters = remove_duplicates_from_first_iteration(clusters)
    clusters = sorted(clusters, key=lambda x: len(x["all_videos"]))
    clusters_copy = copy.deepcopy(clusters)
    similars = similarity_agains_all(
        clusters_copy, min_similarity, clustering_logs_func
    )
    touched_cluster_ids, empty_similarity, pairs_to_merge = algo_merge(
        clusters, similars
    )
    untouched_empty_similarity = get_empty_similarity_first_iteration(
        clusters, touched_cluster_ids, empty_similarity
    )
    empty_similarity_clusters = get_round_of_empty_clusters_first_iteration(
        untouched_empty_similarity, similars, min_videos_in_clusters
    )
    return empty_similarity_clusters, pairs_to_merge, clusters
