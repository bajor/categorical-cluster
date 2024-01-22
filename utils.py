import copy


def prepare_records(record):
    country = set(record["country"])
    record["country"] = country
    tags = set(record["tags"])
    record["tags"] = tags
    return record


def create_tags_map(records):
    tags_map = dict()
    for record in records:
        for tag in record["tags"]:
            if tag not in tags_map:
                tags_map[tag] = 1
            else:
                tags_map[tag] = tags_map[tag] + 1
    return {k: v for k, v in tags_map.items() if v > 1}


def calculate_similarity(original, target, min_similarity, clustering_logs_func=None):
    smaller_count = min(len(original["tags"]), len(target["tags"]))
    common_part = original["similarity_tags"] & target["similarity_tags"]
    target_video_id = target["video_id"]
    similarity = len(common_part) / smaller_count
    if clustering_logs_func and (similarity != 0.0):
        clustering_logs_func(similarity)
    if similarity > min_similarity:
        if "all_tags" in original:
            original["all_tags"].update(target["tags"])
        else:
            original["all_tags"] = original["tags"]
            original["all_tags"].update(target["tags"])
        return (target_video_id, similarity, target["country"])


def initial_similarity_against_all(
    original, combined, min_similarity, clustering_logs_func=None
):
    similarity = []
    for record in combined:
        if record["video_id"] != original["video_id"]:
            similarity_result = calculate_similarity(
                original, record, min_similarity, clustering_logs_func
            )
            if similarity_result:
                similarity.append(similarity_result)
    similarity = sorted(similarity, key=lambda x: x[1])
    original["similarity"] = similarity
    return original


def clean_up_first_iteration(summary):
    clusters = []
    cluster_id = 0
    for s in summary:
        cluster = {}
        cluster_video_ids = []
        first_video_id = s["video_id"]
        first_country = s["country"]
        cluster_video_ids.append((first_video_id, first_country))
        video_ids = [(x[0], x[2]) for x in s["similarity"]]
        for video_id in video_ids:
            present_video_ids = [x[0] for x in cluster_video_ids]
            if video_id[0] not in present_video_ids:
                cluster_video_ids.append(tuple(video_id))
        all_tags = s["all_tags"]
        cluster["for_finding_duplicates"] = set([x[0] for x in cluster_video_ids])
        cluster["id"] = cluster_id
        cluster_id += 1
        cluster["all_videos"] = cluster_video_ids
        cluster["all_tags"] = set(all_tags)
        clusters.append(cluster)
    return clusters


def remove_duplicates_from_first_iteration(clusters):
    unique_clusters = []
    unique_cluster_identifiers = []
    for cluster in clusters:
        current_video_ids = cluster["for_finding_duplicates"]
        if not current_video_ids in unique_cluster_identifiers:
            unique_cluster_identifiers.append(current_video_ids)
            del cluster["for_finding_duplicates"]
            unique_clusters.append(cluster)
    return unique_clusters


def similarity_agains_all(clusters, min_similarity, clustering_logs_func=None):
    for cluster in clusters:
        similarity = []
        for cluster_to_compare in clusters:
            if cluster["id"] != cluster_to_compare["id"]:
                if len(cluster["all_tags"]) > len(cluster_to_compare["all_tags"]):
                    common_tags = cluster["all_tags"].intersection(
                        cluster_to_compare["all_tags"]
                    )
                    similarity_percent = len(common_tags) / len(
                        cluster_to_compare["all_tags"]
                    )

                    if clustering_logs_func and (similarity_percent != 0.0):
                        clustering_logs_func(similarity_percent)

                    if similarity_percent >= min_similarity:
                        similarity.append(
                            {
                                "id": cluster_to_compare["id"],
                                "similarity_percent": similarity_percent,
                            }
                        )
                else:
                    common_tags = cluster["all_tags"].intersection(
                        cluster_to_compare["all_tags"]
                    )
                    similarity_percent = len(common_tags) / len(cluster["all_tags"])

                    if clustering_logs_func and (similarity_percent != 0.0):
                        clustering_logs_func(similarity_percent)

                    if similarity_percent >= min_similarity:
                        similarity.append(
                            {
                                "id": cluster_to_compare["id"],
                                "similarity_percent": similarity_percent,
                            }
                        )
        cluster["similarity"] = similarity
    for cluster in clusters:
        del cluster["all_tags"]
    return clusters


def algo_merge(clusters, similars):
    touched_cluster_ids = []
    empty_similarity = []
    pairs_to_merge = []
    for cluster, similar in zip(clusters, similars):
        if not similar["similarity"]:
            empty_similarity.append(cluster["id"])
            continue
        if cluster["id"] in empty_similarity:
            continue
        similarity_rank = sorted(
            similar["similarity"], key=lambda x: x["similarity_percent"], reverse=True
        )
        most_similar_cluster = similarity_rank[0]
        if most_similar_cluster["id"] in touched_cluster_ids:
            continue
        pairs_to_merge.append((cluster["id"], most_similar_cluster["id"]))
        touched_cluster_ids.append(cluster["id"])
        touched_cluster_ids.append(most_similar_cluster["id"])
    return touched_cluster_ids, empty_similarity, pairs_to_merge


def get_empty_similarity_first_iteration(
    clusters, touched_cluster_ids, empty_similarity
):
    cluster_ids = [x["id"] for x in clusters]
    cluster_ids = set(cluster_ids)
    untouched_empty_similarity = cluster_ids.difference(set(touched_cluster_ids))
    untouched_empty_similarity = list(
        untouched_empty_similarity.intersection(set(empty_similarity))
    )
    return untouched_empty_similarity


def get_round_of_empty_clusters_first_iteration(
    untouched_empty_similarity, similars, min_videos_in_cluster
):
    result = []
    if untouched_empty_similarity:
        for cluster in untouched_empty_similarity:
            cluster_videos = [x for x in similars if x["id"] == cluster][0]
            cluster_videos = cluster_videos["all_videos"]
            various_countries = set()
            for video_countires in cluster_videos:
                various_countries = various_countries.union(set(video_countires[1]))
            if (len(cluster_videos) >= min_videos_in_cluster) and (
                len(various_countries) >= min_videos_in_cluster 
            ):
                result.append(tuple(cluster_videos))
    return result


def get_cluster(cluster_id, clusters):
    cluster = [x for x in clusters if x["id"] == cluster_id][0]
    return cluster


def merge_pairs(cluster_1, cluster_2, new_cluster_id):
    all_videos = []
    all_videos.extend(cluster_1["all_videos"])
    all_videos.extend(cluster_2["all_videos"])
    all_videos_temp = []
    for video in all_videos:
        if video in all_videos_temp:
            continue
        all_videos_temp.append(video)
    all_videos = all_videos_temp
    all_tags = []
    all_tags.extend(cluster_1["all_tags"])
    all_tags.extend(cluster_2["all_tags"])
    all_tags = set(all_tags)
    new_cluster = {"id": new_cluster_id, "all_videos": all_videos, "all_tags": all_tags}
    return new_cluster


def next_iteration_of_algo(
    pairs_to_merge,
    previous_clusters,
    final_clusters,
    min_similarity,
    min_videos_in_cluster,
    clustering_logs_func=None,
):
    new_cluster_id = 0
    new_clusters = []
    for pair in pairs_to_merge:
        cluster_1 = get_cluster(pair[0], previous_clusters)
        cluster_2 = get_cluster(pair[1], previous_clusters)
        new_cluster = merge_pairs(cluster_1, cluster_2, new_cluster_id)
        new_cluster_id += 1
        new_clusters.append(new_cluster)
    new_clusters = sorted(new_clusters, key=lambda x: len(x["all_videos"]))
    new_clusters_copy = copy.deepcopy(new_clusters)
    similaritries = similarity_agains_all(
        new_clusters, min_similarity, clustering_logs_func
    )
    touched_cluster_ids, empty_similarity, pairs_to_merge = algo_merge(
        new_clusters, similaritries
    )
    untouched_empty_similarity = get_empty_similarity_first_iteration(
        new_clusters, touched_cluster_ids, empty_similarity
    )
    empty_similarity_clusters = get_round_of_empty_clusters_first_iteration(
        untouched_empty_similarity,
        similaritries,
        min_videos_in_cluster=min_videos_in_cluster,
    )
    if empty_similarity_clusters:
        final_clusters.extend(empty_similarity_clusters)
    return pairs_to_merge, new_clusters_copy


def create_tags_map(records):
    tags_map = dict()
    for record in records:
        for tag in record["tags"]:
            if tag not in tags_map:
                tags_map[tag] = 1
            else:
                tags_map[tag] = tags_map[tag] + 1
    return {k: v for k, v in tags_map.items() if v > 1}


def encode_tags_map(tags_map):
    for index, key in enumerate(tags_map.keys()):
        tags_map[key] = index
    return tags_map


def map_tags_to_simplified(records, tags_map):
    for record in records:
        tags = record["tags"]
        tags = [tags_map[x] for x in tags if x in tags_map]
        if tags:
            record["similarity_tags"] = set(tags)
    return records


# def cluster_has_more_than_one_country(cluster):
#     result = set()
#     for record in cluster:
#         result = result.union(set(record[1]))
#     if len(result) > 1:
#         return True
#     return False
