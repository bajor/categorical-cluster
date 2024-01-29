from typing import Optional, Tuple, List, Dict


def _calculate_similarity(
    original: dict,
    target: dict,
    min_similarity: float,
    clustering_logs: Optional[list] = None,
) -> Optional[Tuple[int, float]]:
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
    original: dict,
    combined: list,
    min_similarity: float,
    clustering_logs: Optional[list] = None,
) -> dict:
    """
    Args:
        original (dict): The original record.
        combined (list): The combined data to be clustered.
        min_similarity (float): The minimum similarity threshold for clustering.
        clustering_logs (list, optional): Logs for the clustering process. Defaults to None.

    Returns:
        dict: The original record with updated similarity information.
    """
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


def _clean_up_first_iteration(summary: List[Dict]) -> List[Dict]:
    """
    Cleans up the first iteration of the clustering process.

    Args:
        summary (List[Dict]): The summary of the first iteration.

    Returns:
        List[Dict]: The cleaned up clusters.
    """
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


def _remove_duplicates_from_first_iter(clusters: List[Dict]) -> List[Dict]:
    """
    Removes duplicates from the first iteration of clusters.

    Args:
        clusters (List[Dict]): The list of clusters from the first iteration.

    Returns:
        List[Dict]: The list of clusters after removing duplicates.
    """
    unique_clusters = []
    unique_cluster_identifiers = []
    for cluster in clusters:
        current_element_ids = cluster["for_finding_duplicates"]
        if not current_element_ids in unique_cluster_identifiers:
            unique_cluster_identifiers.append(current_element_ids)
            del cluster["for_finding_duplicates"]
            unique_clusters.append(cluster)
    return unique_clusters


def _similarity_agains_all(
    clusters: List[Dict], min_similarity: float, clustering_logs: Optional[List] = None
) -> List[Dict]:
    """
    Computes the similarity of all clusters against each other.

    Args:
        clusters (List[Dict]): List of clusters to compare.
        min_similarity (float): Minimum similarity threshold.
        clustering_logs (Optional[List]): Optional list to store clustering logs.

    Returns:
        List[Dict]: List of clusters with updated similarity information.
    """
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


def _merge_algo(
    clusters: List[Dict], similars: List[Dict]
) -> Tuple[List[int], List[int], List[Tuple[int, int]]]:
    """
    This function merges clusters based on their similarity.

    Args:
        clusters (List[Dict]): List of clusters.
        similars (List[Dict]): List of similar clusters.

    Returns:
        Tuple[List[int], List[int], List[Tuple[int, int]]]: Returns a tuple containing lists of touched cluster ids, empty similarity clusters, and pairs to merge.
    """
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


def _get_empty_similarity_first_iter(
    clusters: List[Dict], touched_cluster_ids: List[int], empty_similarity: List[int]
) -> List[int]:
    """
    This function gets the clusters that have not been touched and have empty similarity.

    Args:
        clusters (List[Dict]): List of clusters.
        touched_cluster_ids (List[int]): List of ids of clusters that have been touched.
        empty_similarity (List[int]): List of ids of clusters with empty similarity.

    Returns:
        List[int]: List of ids of clusters that have not been touched and have empty similarity.
    """
    cluster_ids = [x["id"] for x in clusters]
    cluster_ids = set(cluster_ids)
    untouched_empty_similarity = cluster_ids.difference(set(touched_cluster_ids))
    untouched_empty_similarity = list(
        untouched_empty_similarity.intersection(set(empty_similarity))
    )
    return untouched_empty_similarity


def _get_iteration_of_empty_clusters(
    untouched_empty_similarity: List[int],
    similars: List[Dict],
    min_elements_in_cluster: int,
) -> None:
    """
    This function is used to get the iteration of empty clusters.

    Args:
        untouched_empty_similarity (List[int]): List of untouched clusters with empty similarity.
        similars (List[Dict]): List of similar clusters.
        min_elements_in_cluster (int): Minimum number of elements in a cluster.
    """
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


def _get_cluster(cluster_id: int, clusters: List[Dict]) -> Dict:
    """
    This function retrieves a specific cluster by its id from a list of clusters.

    Args:
        cluster_id (int): The id of the cluster to retrieve.
        clusters (List[Dict]): The list of clusters.

    Returns:
        Dict: The retrieved cluster.
    """
    cluster = [x for x in clusters if x["id"] == cluster_id][0]
    return cluster


def _merge_pairs(cluster_1: Dict, cluster_2: Dict, new_cluster_id: int) -> Dict:
    """
    This function merges two clusters into a new cluster.

    Args:
        cluster_1 (Dict): The first cluster to be merged.
        cluster_2 (Dict): The second cluster to be merged.
        new_cluster_id (int): The id for the new merged cluster.

    Returns:
        Dict: The new merged cluster.
    """
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
