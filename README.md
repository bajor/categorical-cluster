# Installation

#############################################

TODO

#############################################

# Example

This code reads the pickle file of the example dataset provided in this repository, performs clustering on it, and saves the results in `output.p`.

```
import pickle
from categorical_cluster import cluster


MIN_SIMILARITY_FIRST_ITERATION = 0.5    # Value from 0 to 1 - % of similarity among entities in clusters
MIN_SIMILARITY_NEXT_ITERATIONS = 0.45   # Value from 0 to 1 - % of similarity among entities in clusters
MIN_ENTITIES_IN_CLUSTER = 4             # Minimum elements that cluster can consist of


# Read example dataset avaliable in repo
with open("dataset/sample_dataset.p", "rb") as file:
    data = pickle.load(file)


# Perform clustering
clusters = perform_clustering(
    data=data,
    min_elements_in_cluster=MIN_ENTITIES_IN_CLUSTER,
    min_similarity_first_iter=MIN_SIMILARITY_FIRST_ITERATION,
    min_similarity_next_iters=MIN_SIMILARITY_NEXT_ITERATIONS,
)


# Save result
with open("output.p", "wb") as file:
    pickle.dump(clusters, file)
```

Input data is a list of rows with "tags"(described later):

```
['envelope laser rectangle', 'casually explained', 'stand up comedy', 'comedy', 'animation', 'animated comedy', 'satire', 'how to', 'advice', 'funny', 'stand up', 'comedian', 'hilarious', 'humor']
```

Output would be clusters of input rows with their initial indexes (row numbers from the original input list):

```
[{'source_data': ['golf', 'golf highlights', 'ryder cup', 'ryder cup highlights', '2022 ryder cup', '2023 golf', 'marco simone', 'marco simone course', 'marco simone golf', 'luke donald', 'zach johnson', 'u.s. team', 'european team', 'europe golf', 'u.s. golf', 'ryder cup trophy'], 'source_row_number': 22}, {'source_data': ['golf', 'golf highlights', 'ryder cup', 'ryder cup highlights', '2022 ryder cup', '2023 golf', 'marco simone', 'marco simone course', 'marco simone golf', 'luke donald', 'zach johnson', 'u.s. team', 'european team', 'europe golf', 'u.s. golf', 'ryder cup trophy'], 'source_row_number': 235}, {'source_data': ['golf', 'golf highlights', 'ryder cup', 'ryder cup highlights', '2022 ryder cup', '2023 golf', 'marco simone', 'marco simone course', 'marco simone golf', 'luke donald', 'zach johnson', 'u.s. team', 'european team', 'europe golf', 'u.s. golf', 'ryder cup trophy'], 'source_row_number': 484}, {'source_data': ['golf', 'golf highlights', 'ryder cup', 'ryder cup highlights', '2022 ryder cup', '2023 golf', 'marco simone', 'marco simone course', 'marco simone golf', 'luke donald', 'zach johnson', 'u.s. team', 'european team', 'europe golf', 'u.s. golf', 'ryder cup trophy'], 'source_row_number': 538}, {'source_data': ['golf', 'golf highlights', 'ryder cup', 'ryder cup highlights', '2022 ryder cup', '2023 golf', 'marco simone', 'marco simone course', 'marco simone golf', 'luke donald', 'zach johnson', 'u.s. team', 'european team', 'europe golf', 'u.s. golf', 'ryder cup trophy', 'highlights | day 3 | 2023 ryder cup', 'watch highlights of the day 3 at the 2023 ryder cup held at marco simone golf & country club.', '2023 ryder cup held at marco simone golf', 'marco simone golf & country club.', 'highlights of the day 3', 'ryder cup'], 'source_row_number': 627}]
```

An example demonstrating the usage of logs can be found in the `example_logs.py` file. This example shows how to use logs to determine the similarity parameters.

# Description

This package is specifically designed for clustering categorical data. The input should be provided as a list of lists, where each inner list represents a set of "tags" for a particular record. The more similar the tags between two records, the more likely they are to be in the same cluster.

This package was initially developed for clustering YouTube videos. The sample data provided in the file "example_dataset.p" can be used to try out this package. This sample data is a collection of unique tags and elements of the titles of YouTube videos that were trending in 2023.

The clustering process is carried out in the following steps:

1. **Encoding Process**: In this step, all tags are mapped to integers. This is done to facilitate the comparison of tags between different records. The mapping is done such that each unique tag is assigned a unique integer.

2. **Filtering Process**: After the encoding process, records are filtered based on their tags. Records that only contain tags that do not occur in any other records in the dataset are filtered out. This is done to ensure that the clustering process only considers records that have some level of similarity with other records in the dataset.

These steps ensure that the clustering process is efficient and accurate, providing meaningful clusters of records based on their tags.

3. **Clustering Process**: The clustering process consists of two stages - initial and next iterations.
   Both stages perform the same operations but are divided so that the results can be determined by specifying parameters for each separately. In the first iteration, the similarity threshold is `min_similarity_first_iter`. In subsequent iterations, the threshold is `min_similarity_next_iters`.

**Clustering Loop** looks as follows:

1. For each cluster (initially each record is a single cluster), similarities to every other cluster are calculated and compared against a threshold.
2. If a given cluster does not have at least one similar record (based on initial similarity treshold), it's dropped.
3. We look for two most similar clusters and merge this pair into one cluster. Following calculations will be done against result of merge, not initial element.
4. If for a given iteration a certain cluster does not have any new similar elements, we check against `min_elements_in_cluster`. If it's met, we put it into the `final_clusters` list.
5. This process is repeated until no more clusters to merge are met.

This process ensures that the clusters formed are meaningful and based on the similarity of tags between the records.

Please note that during the clustering process, a single record could potentially be assigned to more than one cluster.

# Logging

During the clustering process, logs are generated that capture the calculated similarities while running the clustering algorithm. These logs contain the values of the calculated similarities and the number of occurrences of these values.

By analyzing these logs, you can determine the optimal similarity parameters for your specific use case. This can help in fine-tuning the clustering process to achieve more accurate and meaningful clusters.

Here is an example of how these logs look like:

![Example of logs](Figure_1.png)

In the above figure, the x-axis represents the similarity values and the y-axis represents the number of occurrences of these values. By analyzing this graph, you can determine the most common similarity values in your data, which can be used to set the similarity parameters for the clustering algorithm.

The function below can be used to generate the plot shown above. It takes a list of similarity values as input and plots a histogram of these values.

```
import matplotlib.pyplot as plt


def plot_similarity_values(values):
    values = [round((x), 2) for x in values]
    plt.hist(values, bins=100, edgecolor="k", alpha=0.7)
    plt.title("Histogram of Values Rounded to 0.01")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()
```

# Future plans, draft:

    1. Enable multiprocessing, rewrite into maps:
        If there are no other ideas for parallelizing this, can do map and reduce at each iteration - that is:
        for each cluster, compare it to all other clusters - map
        then again map - look at which of the next clusters is the most coherent - leave the most coherent, if have pairs e.g. (1,3) with a coherence of 93% and a pair (3,5) with a coherence of 50% - combine pair 1 and 3 together creating a new cluster and do nothing with element 5 (leave it for the next iteration).
    2. You pass pandas dataframe and columns to cluster on - I return dataframe with new column - label
    3. Optimize calculating similarity - don't calculate it at each iteration, rather calculate against merged pair
