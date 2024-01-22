import copy
from utils import (
    prepare_records,
    create_tags_map,
    encode_tags_map,
    map_tags_to_simplified,
)


def prepare_data(data):
    all_tags_map = create_tags_map(data)
    all_tags_map = encode_tags_map(all_tags_map)
    data = map_tags_to_simplified(data, all_tags_map)
    data = [x for x in data if "similarity_tags" in x]

    data = [prepare_records(x) for x in data]

    # combined_dict = {}
    # for record in copy.deepcopy(data):
    #     combined_dict[record["video_id"]] = record

    # return combined_dict

    return data