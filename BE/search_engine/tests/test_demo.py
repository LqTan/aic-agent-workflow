from unittest import TestCase

from search_engine.demo import inspect, search


class DemoEngineTests(TestCase):
    def test_vietnamese_bicycle_query_ranks_bicycle_scene_first(self):
        results = search(
            query="Tìm người đi xe đạp ngoài đường",
            collection_ids=[],
            top_k=3,
        )
        self.assertEqual(results[0]["keyframe_id"], "DEMO_V001_000001")
        self.assertIn("bicycle", results[0]["matched_objects"])

    def test_inspect_reports_demo_index(self):
        result = inspect(query="xe máy", collection_ids=[], top_k=5)
        self.assertEqual(result["index"]["format_version"], "demo-1")
        self.assertEqual(result["index"]["record_count"], 6)
