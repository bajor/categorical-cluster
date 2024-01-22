import pickle
import time
from cluster import perform_clustering
from datetime import datetime
from config import MIN_SIMILARITY_FIRST_ITERATION, MIN_SIMILARITY_NEXT_ITERATIONS, MIN_ENTITIES_IN_CLUSTER
# from plot import add_log_similarity_day_initial, add_log_similarity_day_next
from prepare_records import prepare_data

filename = "combined.p"

with open(filename, 'rb') as file:
    data = pickle.load(file)

print(data[0])

start_time = time.time()

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Processing file - {filename}, started at {current_time}")

data = prepare_data(data)

# print(data)

final_clusters = perform_clustering(
    prepared_data=data,
    min_similarity_first_iteration=MIN_SIMILARITY_FIRST_ITERATION,
    min_similarity_next_itarations=MIN_SIMILARITY_NEXT_ITERATIONS,
    min_elements_in_cluster=MIN_ENTITIES_IN_CLUSTER
    # clustering_log_initial_iteration_func=add_log_similarity_day_initial,
    # clustering_log_next_iterations_func=add_log_similarity_day_next,
)

output_filename = "output.p"

with open(output_filename, 'wb') as file:
    pickle.dump(final_clusters, file)

end_time = time.time()
pipeline_duration = int(end_time - start_time)
minutes = pipeline_duration // 60
seconds = pipeline_duration % 60
formatted_time = f"{minutes:02d}:{seconds:02d}"
print(f"pipeline 3 file - {filename} completed in - {minutes}:{seconds}")