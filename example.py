import pickle
from cluster.categorical_cluster import cluster


MIN_SIMILARITY_FIRST_ITERATION = 0.5
MIN_SIMILARITY_NEXT_ITERATIONS = 0.45
MIN_ENTITIES_IN_CLUSTER = 4


with open("dataset/sample_dataset.p", "rb") as file:
    data = pickle.load(file)


clusters = cluster(
    data=data,
    min_elements_in_cluster=MIN_ENTITIES_IN_CLUSTER,
    min_similarity_first_iter=MIN_SIMILARITY_FIRST_ITERATION,
    min_similarity_next_iters=MIN_SIMILARITY_NEXT_ITERATIONS,
    print_start_end=True,
)


with open("output.p", "wb") as file:
    pickle.dump(clusters, file)
