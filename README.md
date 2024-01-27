This package is specifically designed for clustering categorical data. The input should be provided as a list of lists, where each inner list represents a set of "tags" for a particular record. 

In this project, "tags" refer to the values in each record of the input data. This package is designed for clustering categorical data. Each record in the input data is a collection of categorical values, which we refer to as "tags". These tags are used to determine the similarity between different records, which in turn is used to cluster the records together. The more similar the tags between two records, the more likely they are to be in the same cluster.

This package was initially developed for clustering YouTube videos. The clustering is based on the unique tags and elements of the video titles. The sample data provided in the file "sample_data.p" can be used to try out this package. This sample data is a collection of unique tags and elements of the titles of YouTube videos that were trending in 2023.

The clustering process is carried out in the following steps:

1. **Encoding Process**: In this step, all tags are mapped to integers. This is done to facilitate the comparison of tags between different records. The mapping is done such that each unique tag is assigned a unique integer.

2. **Filtering Process**: After the encoding process, records are filtered based on their tags. Records that only contain tags that do not occur in any other records in the dataset are filtered out. This is done to ensure that the clustering process only considers records that have some level of similarity with other records in the dataset.

These steps ensure that the clustering process is efficient and accurate, providing meaningful clusters of records based on their tags.

3. **Clustering Process**: The clustering process consists of two stages - initial and next iterations. Both stages perform the same operations but are divided so that the results can be determined by specifying parameters for each separately. The process is as follows:

    1. For each cluster, similarities to every other cluster are calculated and compared against a threshold.
    2. If a given cluster does not have at least one similar element, it's dropped.
    3. We look for the most similar elements and merge them into one cluster. Following calculations will be done against result of merge, not initial element.
    4. If for a given iteration a certain cluster does not have any new similar elements, we check against `min_elements_in_cluster`. If it's met, we put it into the `final_clusters` list.
    5. This process is repeated until no remaining clusters are left.

This process ensures that the clusters formed are meaningful and based on the similarity of tags between the records.

Please note that during the clustering process, a single record could potentially be assigned to more than one cluster. 


# TODO next versions
    1. Enable multiprocessing, rewrite into maps:
    ```
        If there are no other ideas for parallelizing this, we can do map and reduce at each iteration - that is:
        for each cluster, we compare it to all other clusters - map
        then again map - we look at which of the next clusters is the most coherent - we leave the most coherent, if we have pairs e.g. (1,3) with a coherence of 93% and a pair (3,5) with a coherence of 50% - we combine pair 1 and 3 together creating a new cluster and we do nothing with element 5 (we leave it for the next iteration).
    ```
    2. You pass pandas dataframe and columns to cluster on - I return dataframe with new column - label

    3. Optimize calculating similarity - don't calculate it at each iteration, rather calculate against merged pair



#########################################

add code example how to use it with provided dataset and how to read result

add - how to use plots and logs

#########################################



# TODO version 1.0
```
regaring extra dependencies pandas and plotly:
    - cannot have any extra dependencies, it's pointless
    - let's provide in README code to plot files produces by logs.py
    - let's provide code to prepare input for this package out of pandas dataframe
```
- prepare logs. It should save to folder, into csv with timestamp of run and parameters saved in file name
    - plot and dataset should be optional, preferably in separate package. Maybe even just laying in the separete repo and link in readme to it.
- tests
- docstrings
- create first iteration of the package


# TODO next versions
    1. enable multiprocessing, rewrite into maps:
    ```
        jesli nie bedzie innych pomysłów na zrównoleglenie tego to można na każdej iteracji robić map and reduce - czyli:
        dla każdego klastra porównujemy go do wszystkich innych klastrów - map
        następnie znowu map - patrzymy który z kolejnych klastrów jest najbardziej spójny - zostawiamy najbardziej spójne, jeśli mamy pary np. (1,3) o spójności 93% i parę (3,5) o spójności 50% - łączymy parę 1 i 3 razem tworząc nowy klaster a z elementem 5 nic nie robimy (zostawiamy na kolejną iterację).
    ```
    2. you pass dataframe and columns to cluster on - I return dataframe with new column - label

    3. optimize calculatating similarity - don't calculate it at each iteration, rather calcuate agains merged pair