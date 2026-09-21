from unittest import TestCase

from apps.kis.agent import evaluate_results, local_plan, run_agent


class AgentPlannerTests(TestCase):
    def test_local_planner_extracts_vietnamese_visual_concepts(self):
        plan = local_plan(
            "Tìm cảnh một người đang đi xe đạp ngoài đường",
            ["L21"],
        )
        self.assertEqual(plan.intent, "video_retrieval")
        self.assertIn("person", plan.objects)
        self.assertIn("bicycle", plan.objects)
        self.assertIn("riding", plan.actions)
        self.assertIn("street", plan.scenes)
        self.assertEqual(plan.collection_ids, ("L21",))

    def test_agent_rewrites_and_retries_when_quality_is_low(self):
        calls = []

        def fake_search_tool(*, query, collection_ids, top_k):
            calls.append(query)
            score = 0.15 if len(calls) == 1 else 0.9
            return (
                {"keys": query.split(), "effective_collection_ids": collection_ids},
                [
                    {
                        "score": score,
                        "matched_objects": ["person", "bicycle"],
                    }
                ],
            )

        result = run_agent(
            query="người đi xe đạp",
            collection_ids=[],
            top_k=5,
            quality_threshold=0.6,
            max_attempts=2,
            search_tool=fake_search_tool,
        )
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["decision"], "accepted")
        self.assertEqual(result["attempts"][0]["accepted"], False)
        self.assertEqual(result["attempts"][1]["accepted"], True)
        self.assertEqual(result["trace"][2]["detail"]["action"], "rewrite_and_retry")

    def test_result_quality_rewards_expected_object_coverage(self):
        plan = local_plan("người đi xe đạp", [])
        covered = evaluate_results(
            [{"score": 0.6, "matched_objects": ["person", "bicycle"]}],
            plan,
        )
        uncovered = evaluate_results(
            [{"score": 0.6, "matched_objects": []}],
            plan,
        )
        self.assertGreater(covered, uncovered)
