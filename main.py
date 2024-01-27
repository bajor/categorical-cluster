import pickle
from cluster import perform_clustering


MIN_NON_NONE_COLUMNS = 15
MIN_SIMILARITY_FIRST_ITERATION = 0.5
MIN_SIMILARITY_NEXT_ITERATIONS = 0.45
MIN_ENTITIES_IN_CLUSTER = 4


with open("combined.p", "rb") as file:
    data = pickle.load(file)


clustering_logs_initial = []
clustering_logs_next = []

final_clusters = perform_clustering(
    data=data,
    min_elements_in_cluster=MIN_ENTITIES_IN_CLUSTER,
    min_similarity_first_iter=MIN_SIMILARITY_FIRST_ITERATION,
    min_similarity_next_iters=MIN_SIMILARITY_NEXT_ITERATIONS,
    clustering_log_initial=clustering_logs_initial,
    clustering_log_next=clustering_logs_next,
    print_start_end=True,
)

# print(clustering_logs_next)
# TODO:
# write here code that takes clustering_logs and saves them into csv with current date and parameters and put it into README


with open("output.p", "wb") as file:
    pickle.dump(final_clusters, file)
