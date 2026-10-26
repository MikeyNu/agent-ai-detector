"""No third-party spec package needed for a few essential Agent Skills contracts."""
import re
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_required_yaml_frontmatter_and_name(self):
        raw = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(raw.startswith("---\n"))
        _, metadata, body = raw.split("---", 2)
        lines = dict(line.split(":", 1) for line in metadata.strip().splitlines() if ":" in line and not line.startswith("  "))
        self.assertEqual(lines["name"].strip(), "agent-ai-detector")
        self.assertTrue(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", lines["name"].strip()))
        self.assertLessEqual(len(lines["name"].strip()), 64)
        self.assertLessEqual(len(lines["description"].strip()), 1024)
        self.assertGreater(len(body.strip()), 500)
        self.assertLess(len(raw.splitlines()), 500)

    def test_all_referenced_local_docs_scripts_exist(self):
        raw = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        localpaths = set(re.findall(r"(?:references|scripts|examples)/[A-Za-z0-9_./-]+", raw))
        self.assertGreaterEqual(len(localpaths), 10)
        for item in localpaths:
            self.assertTrue((ROOT / item.rstrip(".,:;`)")).is_file(), item)

    def test_no_alleged_accuracy_or_origin_prediction_in_prep_script(self):
        script = (ROOT / "scripts" / "inspect_media.py").read_text(encoding="utf-8")
        self.assertIn('"origin_classification": "not_attempted"', script)
        self.assertIn('"exact_pts_verified": False', script)
        self.assertIn('"visual_inspection_performed_by_script": False', script)
        self.assertIn("trust and content-binding validation", script)
        self.assertIn("-nostdin", script)

    def test_report_example_json_valid_and_research_registry_size(self):
        self.assertIsInstance(json.loads((ROOT / "examples" / "sample-report.json").read_text()), dict)
        citations = re.findall(r"\| R\d+ \|", (ROOT / "references" / "research-and-sources.md").read_text())
        self.assertGreaterEqual(len(citations), 15)


if __name__ == "__main__":
    unittest.main()
