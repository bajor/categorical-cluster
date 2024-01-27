from typing import Optional, Tuple
import copy
import time
from datetime import datetime


def _print_start_time() -> datetime:
    """
    This function prints the start time of the clustering process.

    Returns:
        datetime: The start time of the clustering process.
    """
    start_time = time.time()
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Clustering started at {current_time}")
    return start_time


def _print_end_time(start_time):
    """
    This function prints the duration of the clustering process.
    """
    end_time = time.time()
    pipeline_duration = int(end_time - start_time)
    minutes = pipeline_duration // 60
    seconds = pipeline_duration % 60
    print(f"Clustering completed in - {minutes}:{seconds}")


def _prepare_output(clusters: list, initial_data: list) -> list:
    """
    This function prepares the output by associating each cluster with its source data and row number.

    Args:
        clusters (list): The list of clusters.
        initial_data (list): The initial data used for clustering.

    Returns:
        list: The list of clusters with associated source data and row number.
    """
    for i in range(len(clusters)):
        clusters[i] = [
            {"source_data": initial_data[x], "source_row_number": x}
            for x in clusters[i]
        ]
    return clusters


def _prepare_data(data: list) -> list:
    """
    This function prepares the data for clustering.

    Args:
        data (list): The raw data to be prepared. This data is a list of tags, where each tag is a string. 
        The function will process this data for clustering, including encoding the tags for similarity comparison.

    Returns:
        list: The prepared data, where each element is a dictionary containing an 'id' key 
        representing the index of the data in the original list, a 'tags' key containing the 
        original data, and a 'similarity_tags' key containing the encoded tags for similarity 
        comparison. The list only includes elements where 'similarity_tags' key exists.
    """
    for i in range(len(data)):
        data[i] = {"id": i, "tags": data[i]}
    all_tags_map = _create_tags_map(data)
    all_tags_map = _encode_tags_map(all_tags_map)
    data = _map_tags_to_simplified(data, all_tags_map)
    data = [x for x in data if "similarity_tags" in x]
    data = [_prepare_records(x) for x in data]
    return data


def _prepare_records(record: dict) -> dict:
    """
    This function prepares the record by converting the tags to a set.

    Args:
        record (dict): The record to be prepared.

    Returns:
        dict: The prepared record.
    """
    tags = set(record["tags"])
    record["tags"] = tags
    return record


def _create_tags_map(records: list) -> dict:
    """
    This function creates a map of tags from the records. Each tag is mapped to its frequency of occurrence 
    across all records. Only tags that occur more than once are included in the final map.

    Args:
        records (list): The list of records. Each record is a dictionary containing an 'id' key 
        representing the index of the record in the original list, a 'tags' key containing the 
        original tags, and a 'similarity_tags' key containing the encoded tags for similarity 
        comparison.

    Returns:
        dict: The map of tags. Each key is a tag, and its corresponding value is the frequency of 
        occurrence of that tag across all records. Only tags that occur more than once are included.
    """
    tags_map = dict()
    for record in records:
        for tag in record["tags"]:
            if tag not in tags_map:
                tags_map[tag] = 1
            else:
                tags_map[tag] = tags_map[tag] + 1
    return {k: v for k, v in tags_map.items() if v > 1}


def _calculate_similarity(original: dict, target: dict, min_similarity: float, clustering_logs: Optional[list] = None) -> Optional[Tuple[int, float]]:
    """
    This function calculates the similarity between the original and target records based on their tags. 
    If the similarity is greater than the minimum similarity threshold, it updates the original record's 
    tags and returns the target record's id and the calculated similarity.

    Args:
        original (dict): The original record. It is a dictionary containing an 'id' key representing the 
        index of the record in the original list, a 'tags' key containing the original tags, and a 
        'similarity_tags' key containing the encoded tags for similarity comparison.

        target (dict): The target record. It is a dictionary similar to the original record.

        min_similarity (float): The minimum similarity threshold. Only similarities greater than this 
        threshold are considered.

        clustering_logs (list, optional): A list to log the calculated similarities. If provided, 
        non-zero similarities are appended to this list.

    Returns:
        tuple: A tuple containing the target record's id and the calculated similarity, if the similarity 
        is greater than the minimum similarity threshold. Otherwise, None is returned.
    """
    smaller_count = min(len(original["tags"]), len(target["tags"]))
    common_part = original["similarity_tags"] & target["similarity_tags"]
    target_id = target["id"]
    similarity = len(common_part) / smaller_count
    if clustering_logs and (similarity != 0.0):
        clustering_logs.append(similarity)
    if similarity > min_similarity:
        if "all_tags" in original:
            original["all_tags"].update(target["tags"])
        else:
            original["all_tags"] = original["tags"]
            original["all_tags"].update(target["tags"])
        return (target_id, similarity)


def _initial_similarity_against_all(
    original, combined, min_similarity, clustering_logs=None
):
    similarity = []
    for record in combined:
        if record["id"] != original["id"]:
            similarity_result = _calculate_similarity(
                original, record, min_similarity, clustering_logs
            )
            if similarity_result:
                similarity.append(similarity_result)
    similarity = sorted(similarity, key=lambda x: x[1])
    original["similarity"] = similarity
    return original


def _clean_up_first_iteration(summary):
    clusters = []
    cluster_id = 0
    for s in summary:
        cluster = {}
        cluster_elements_ids = []
        first_element_id = s["id"]
        cluster_elements_ids.append(first_element_id)
        elements_ids = [x for x in s["similarity"]]
        for element_id in elements_ids:
            present_element_ids = [x for x in cluster_elements_ids]
            if element_id[0] not in present_element_ids:
                cluster_elements_ids.append(tuple(element_id))
        all_tags = s["all_tags"]
        cluster["for_finding_duplicates"] = set([x for x in cluster_elements_ids])
        cluster["id"] = cluster_id
        cluster_id += 1
        cluster["all_elements"] = cluster_elements_ids
        cluster["all_tags"] = set(all_tags)
        clusters.append(cluster)
    return clusters


def _remove_duplicates_from_first_iter(clusters):
    unique_clusters = []
    unique_cluster_identifiers = []
    for cluster in clusters:
        current_element_ids = cluster["for_finding_duplicates"]
        if not current_element_ids in unique_cluster_identifiers:
            unique_cluster_identifiers.append(current_element_ids)
            del cluster["for_finding_duplicates"]
            unique_clusters.append(cluster)
    return unique_clusters


def _similarity_agains_all(clusters, min_similarity, clustering_logs=None):
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

                    if (clustering_logs is not None) and (similarity_percent != 0.0):
                        clustering_logs.append(similarity_percent)

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

                    if (clustering_logs is not None) and (similarity_percent != 0.0):
                        clustering_logs.append(similarity_percent)

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


def _merge_algo(clusters, similars):
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


def _get_empty_similarity_first_iter(clusters, touched_cluster_ids, empty_similarity):
    cluster_ids = [x["id"] for x in clusters]
    cluster_ids = set(cluster_ids)
    untouched_empty_similarity = cluster_ids.difference(set(touched_cluster_ids))
    untouched_empty_similarity = list(
        untouched_empty_similarity.intersection(set(empty_similarity))
    )
    return untouched_empty_similarity


def _get_iteration_of_empty_clusters(
    untouched_empty_similarity, similars, min_elements_in_cluster
):
    result = []
    if untouched_empty_similarity:
        for cluster in untouched_empty_similarity:
            cluster_elements = [x for x in similars if x["id"] == cluster][0]
            cluster_elements = cluster_elements["all_elements"]

            for i in range(len(cluster_elements)):
                if isinstance(cluster_elements[i], tuple):
                    cluster_elements[i] = cluster_elements[i][0]

            cluster_elements = set(cluster_elements)

            if len(cluster_elements) >= min_elements_in_cluster:
                result.append(tuple(sorted(cluster_elements)))
    return result


def get_cluster(cluster_id, clusters):
    cluster = [x for x in clusters if x["id"] == cluster_id][0]
    return cluster


def merge_pairs(cluster_1, cluster_2, new_cluster_id):
    all_elements = []
    all_elements.extend(cluster_1["all_elements"])
    all_elements.extend(cluster_2["all_elements"])
    all_elements_temp = []
    for element in all_elements:
        if element in all_elements_temp:
            continue
        all_elements_temp.append(element)
    all_elements = all_elements_temp
    all_tags = []
    all_tags.extend(cluster_1["all_tags"])
    all_tags.extend(cluster_2["all_tags"])
    all_tags = set(all_tags)
    new_cluster = {
        "id": new_cluster_id,
        "all_elements": all_elements,
        "all_tags": all_tags,
    }
    return new_cluster


def _next_iteration_of_algo(
    pairs_to_merge,
    previous_clusters,
    final_clusters,
    min_similarity,
    min_elements_in_cluster,
    clustering_logs=None,
):
    new_cluster_id = 0
    new_clusters = []
    for pair in pairs_to_merge:
        cluster_1 = get_cluster(pair[0], previous_clusters)
        cluster_2 = get_cluster(pair[1], previous_clusters)
        new_cluster = merge_pairs(cluster_1, cluster_2, new_cluster_id)
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


def _create_tags_map(records):
    tags_map = dict()
    for record in records:
        for tag in record["tags"]:
            if tag not in tags_map:
                tags_map[tag] = 1
            else:
                tags_map[tag] = tags_map[tag] + 1
    return {k: v for k, v in tags_map.items() if v > 1}


def _encode_tags_map(tags_map):
    for index, key in enumerate(tags_map.keys()):
        tags_map[key] = index
    return tags_map


def _map_tags_to_simplified(records, tags_map):
    for record in records:
        tags = record["tags"]
        tags = [tags_map[x] for x in tags if x in tags_map]
        if tags:
            record["similarity_tags"] = set(tags)
    return records
