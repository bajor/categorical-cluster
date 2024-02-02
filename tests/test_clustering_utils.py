import pytest
import unittest
from cluster.clustering_utils import (
    _calculate_similarity,
    _initial_similarity_against_all,
    _remove_duplicates_from_first_iter,
    _similarity_agains_all,
    _merge_algo,
    _get_iteration_of_empty_clusters,
)


class TestCalculateSimilarity(unittest.TestCase):
    def setUp(self):
        self.original = {
            "id": 1,
            "tags": {"tag1", "tag2", "tag3"},
            "similarity_tags": {"tag1", "tag2"},
        }
        self.target = {
            "id": 2,
            "tags": {"tag1", "tag2", "tag4"},
            "similarity_tags": {"tag1", "tag2"},
        }
        self.min_similarity = 0.5
        self.clustering_logs = []

    def test_calculate_similarity(self):
        result = _calculate_similarity(
            self.original, self.target, self.min_similarity, self.clustering_logs
        )
        self.assertEqual((result[0], round(result[1], 2)), (2, 0.67))
        self.assertEqual(self.original["all_tags"], {"tag1", "tag2", "tag3", "tag4"})

    def test_calculate_similarity_below_threshold(self):
        self.min_similarity = 1.1
        result = _calculate_similarity(
            self.original, self.target, self.min_similarity, self.clustering_logs
        )
        self.assertIsNone(result)

    def test_calculate_similarity_no_common_tags(self):
        self.original["similarity_tags"] = {"tag3"}
        result = _calculate_similarity(
            self.original, self.target, self.min_similarity, self.clustering_logs
        )
        self.assertIsNone(result)


class TestInitialSimilarityAgainstAll(unittest.TestCase):
    def setUp(self):
        self.original = {
            "id": 1,
            "tags": {"tag1", "tag2", "tag3"},
            "similarity_tags": {"tag1", "tag2"},
        }
        self.combined = [
            {
                "id": 2,
                "tags": {"tag1", "tag2", "tag4"},
                "similarity_tags": {"tag1", "tag2"},
            },
            {
                "id": 3,
                "tags": {"tag1", "tag5", "tag6"},
                "similarity_tags": {"tag1", "tag5"},
            },
        ]
        self.min_similarity = 0.5
        self.clustering_logs = []

    def test_initial_similarity_against_all(self):
        result = _initial_similarity_against_all(
            self.original, self.combined, self.min_similarity, self.clustering_logs
        )
        self.assertEqual(len(result["similarity"]), 1)
        self.assertEqual(result["similarity"][0][0], 2)
        self.assertAlmostEqual(result["similarity"][0][1], 0.67, places=2)

    def test_initial_similarity_against_all_no_similar_records(self):
        self.min_similarity = 1.1
        result = _initial_similarity_against_all(
            self.original, self.combined, self.min_similarity, self.clustering_logs
        )
        self.assertEqual(len(result["similarity"]), 0)

    def test_initial_similarity_against_all_no_common_tags(self):
        self.original["similarity_tags"] = {"tag3"}
        result = _initial_similarity_against_all(
            self.original, self.combined, self.min_similarity, self.clustering_logs
        )
        self.assertEqual(len(result["similarity"]), 0)


class TestRemoveDuplicatesFromFirstIter(unittest.TestCase):
    def setUp(self):
        self.clusters = [
            {
                "id": 0,
                "for_finding_duplicates": {1, 2, 3},
                "all_elements": [1, (2, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag3"},
            },
            {
                "id": 1,
                "for_finding_duplicates": {1, 2, 3},
                "all_elements": [2, (1, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag4"},
            },
            {
                "id": 2,
                "for_finding_duplicates": {4, 5, 6},
                "all_elements": [4, (5, 0.67), (6, 0.33)],
                "all_tags": {"tag4", "tag5", "tag6"},
            },
        ]

    def test_remove_duplicates_from_first_iter(self):
        result = _remove_duplicates_from_first_iter(self.clusters)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 0)
        self.assertEqual(result[0]["all_elements"], [1, (2, 0.67), (3, 0.33)])
        self.assertEqual(result[0]["all_tags"], {"tag1", "tag2", "tag3"})
        self.assertEqual(result[1]["id"], 2)
        self.assertEqual(result[1]["all_elements"], [4, (5, 0.67), (6, 0.33)])
        self.assertEqual(result[1]["all_tags"], {"tag4", "tag5", "tag6"})


class TestSimilarityAgainstAll(unittest.TestCase):
    def setUp(self):
        self.clusters = [
            {
                "id": 0,
                "all_elements": [1, (2, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag3"},
            },
            {
                "id": 1,
                "all_elements": [2, (1, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag4"},
            },
            {
                "id": 2,
                "all_elements": [4, (5, 0.67), (6, 0.33)],
                "all_tags": {"tag4", "tag5", "tag6"},
            },
        ]
        self.min_similarity = 0.5
        self.clustering_logs = []

    def test_similarity_against_all(self):
        result = _similarity_agains_all(
            self.clusters, self.min_similarity, self.clustering_logs
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["similarity"][0]["id"], 1)
        self.assertAlmostEqual(
            result[0]["similarity"][0]["similarity_percent"], 0.67, places=2
        )

    def test_similarity_against_all_no_similar_clusters(self):
        self.min_similarity = 1.1
        result = _similarity_agains_all(
            self.clusters, self.min_similarity, self.clustering_logs
        )
        for cluster in result:
            self.assertEqual(len(cluster["similarity"]), 0)

    def test_similarity_against_all_no_common_tags(self):
        self.clusters[0]["all_tags"] = {"tag7"}
        result = _similarity_agains_all(
            self.clusters, self.min_similarity, self.clustering_logs
        )
        self.assertEqual(len(result[0]["similarity"]), 0)


class TestMergeAlgo(unittest.TestCase):
    def setUp(self):
        self.clusters = [
            {
                "id": 0,
                "all_elements": [1, (2, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag3"},
            },
            {
                "id": 1,
                "all_elements": [2, (1, 0.67), (3, 0.33)],
                "all_tags": {"tag1", "tag2", "tag4"},
            },
            {
                "id": 2,
                "all_elements": [4, (5, 0.67), (6, 0.33)],
                "all_tags": {"tag4", "tag5", "tag6"},
            },
        ]
        self.similars = [
            {"id": 0, "similarity": [{"id": 1, "similarity_percent": 0.67}]},
            {"id": 1, "similarity": [{"id": 0, "similarity_percent": 0.67}]},
            {"id": 2, "similarity": []},
        ]

    def test_merge_algo(self):
        result = _merge_algo(self.clusters, self.similars)
        self.assertEqual(len(result[0]), 2)  # touched_cluster_ids
        self.assertEqual(len(result[1]), 1)  # empty_similarity
        self.assertEqual(len(result[2]), 1)  # pairs_to_merge
        self.assertEqual(result[0], [0, 1])  # touched_cluster_ids
        self.assertEqual(result[1], [2])  # empty_similarity
        self.assertEqual(result[2], [(0, 1)])  # pairs_to_merge


class TestGetIterationOfEmptyClusters(unittest.TestCase):
    def setUp(self):
        self.untouched_empty_similarity = [1, 2]
        self.similars = [
            {
                "id": 1,
                "all_elements": [1, (2, 0.67), (3, 0.33)],
            },
            {
                "id": 2,
                "all_elements": [4, (5, 0.67), (6, 0.33)],
            },
        ]
        self.min_elements_in_cluster = 2

    def test_get_iteration_of_empty_clusters(self):
        result = _get_iteration_of_empty_clusters(
            self.untouched_empty_similarity, self.similars, self.min_elements_in_cluster
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (1, 2, 3))
        self.assertEqual(result[1], (4, 5, 6))


if __name__ == "__main__":
    unittest.main()
