import unittest
import re
from llm_to_mcp_integration_engine import llm_to_mcp_integration_custom

class TestCustomIntegration(unittest.TestCase):

    def test_regex_grid_extraction(self):
        raw_llm_answer = """
Sure, let me reason this out…
3 2 3 2 3 2
7 8 7 8 7 8
2 3 2 3 2 3
8 7 8 7 8 7
3 2 3 2 3 2
7 8 7 8 7 8
Hope that helps!
"""
        ROW_LEN = 6
        ROW_RE  = rf"(?:\d+\s+){{{ROW_LEN-1}}}\d+"
        GRID_RE = re.compile(rf"{ROW_RE}(?:\n{ROW_RE})+")

        tools = [{"name": "extract_grid", "pattern": GRID_RE, "capture_group": 0}]

        expected_grid_str = """3 2 3 2 3 2
7 8 7 8 7 8
2 3 2 3 2 3
8 7 8 7 8 7
3 2 3 2 3 2
7 8 7 8 7 8"""

        expected_grid_list = [
            [3, 2, 3, 2, 3, 2],
            [7, 8, 7, 8, 7, 8],
            [2, 3, 2, 3, 2, 3],
            [8, 7, 8, 7, 8, 7],
            [3, 2, 3, 2, 3, 2],
            [7, 8, 7, 8, 7, 8]
        ]

        parsed = llm_to_mcp_integration_custom(
            tools_list=tools,
            llm_response=raw_llm_answer,
            json_validation=False
        )

        self.assertIn("extract_grid", parsed)
        self.assertEqual(parsed["extract_grid"], expected_grid_str)

        # Optionally, test the parsed list of lists
        grid_from_parsed = [list(map(int, r.split())) for r in parsed["extract_grid"].splitlines()]
        self.assertEqual(grid_from_parsed, expected_grid_list)

    def test_regex_grid_extraction_no_match(self):
        raw_llm_answer = "This text does not contain the grid."
        ROW_LEN = 6
        ROW_RE  = rf"(?:\d+\s+){{{ROW_LEN-1}}}\d+"
        GRID_RE = re.compile(rf"{ROW_RE}(?:\n{ROW_RE})+")
        tools = [{"name": "extract_grid", "pattern": GRID_RE, "capture_group": 0}]

        parsed = llm_to_mcp_integration_custom(
            tools_list=tools,
            llm_response=raw_llm_answer,
            json_validation=False
        )
        self.assertIn("extract_grid", parsed)
        self.assertIsNone(parsed["extract_grid"])

if __name__ == '__main__':
    unittest.main()
