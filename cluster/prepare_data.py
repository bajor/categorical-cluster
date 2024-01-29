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
