"""Adversarial semantic contracts. Assertions protect against overclaiming, not real-world errors."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_report as gate  # noqa: E402


def example():
    return json.loads((ROOT / "examples" / "sample-report.json").read_text())


def finding(family, strength="moderate", id_="F02"):
    return {
        "id": id_, "modality": "image", "location": {"bbox_xywh": [10, 10, 10, 10]},
        "observation": "The chain overlaps the surface with no visible junction",
        "hypothesis": "An incomplete compositing operation",
        "alternative_explanations": ["Physical occlusion and shadow"],
        "reproduction": "Compare original native pixels with neighboring region",
        "evidence_family": family, "strength": strength, "quality_severity": "major"
    }


class ReportValidationTests(unittest.TestCase):
    def test_inconclusive_example_valid(self):
        self.assertEqual(gate.validate(example()), [])

    def test_no_fabricated_confirmation_from_visual_artifact(self):
        report = example()
        report["decision"]["origin_label"] = "confirmed_ai_origin"
        report["decision"]["evidence_strength"] = "high"
        errors = gate.validate(report)
        self.assertTrue(any("requires provenance.state" in x for x in errors))
        self.assertTrue(any("binding_verified" in x for x in errors))

    def test_untrusted_c2pa_cannot_confirm(self):
        report = example()
        report["decision"]["origin_label"] = "confirmed_ai_origin"
        report["decision"]["evidence_strength"] = "high"
        report["provenance"].update({"state": "verified_ai_generation", "scope": "partial generated content", "issuer": "Example issuer", "verifier": "example"})
        errors = gate.validate(report)
        self.assertTrue(any("trust_verified" in x for x in errors))
        report["provenance"]["trust_verified"] = True
        report["provenance"]["binding_verified"] = True
        self.assertEqual(gate.validate(report), [])

    def test_visual_only_suspicion_demands_two_independent_families(self):
        report = example()
        report["decision"]["origin_label"] = "suspected_ai_involvement"
        report["findings"] = [finding("geometry", "moderate", "F01")]
        self.assertTrue(any("2 independent" in x for x in gate.validate(report)))
        report["findings"].append(finding("geometry", "moderate", "F02"))
        self.assertTrue(any("2 independent" in x for x in gate.validate(report)))
        report["findings"].append(finding("lighting", "moderate", "F03"))
        self.assertEqual(gate.validate(report), [])

    def test_two_weak_observations_are_not_independent_source_proof(self):
        report = example()
        report["decision"]["origin_label"] = "suspected_ai_involvement"
        report["findings"] = [finding("geometry", "low", "F01"), finding("texture", "low", "F02")]
        self.assertTrue(any("2 independent" in x for x in gate.validate(report)))

    def test_detector_and_metadata_suspicion_cannot_replace_optical_examination(self):
        report = example()
        report["decision"]["origin_label"] = "suspected_ai_involvement"
        report["findings"] = [finding("detector", "high", "F01"), finding("metadata", "high", "F02")]
        self.assertTrue(any("2 independent" in x for x in gate.validate(report)))

    def test_genuine_no_evidence_requires_coverage_not_confirmed_real(self):
        report = example()
        report["decision"]["origin_label"] = "no_ai_evidence_found"
        self.assertTrue(any("review_coverage" in x for x in gate.validate(report)))
        report["review_coverage"] = "Native full image sweep, 5 regions and scene geometry"
        self.assertEqual(gate.validate(report), [])
        report["decision"]["origin_label"] = "confirmed_real"
        self.assertTrue(any("invalid" in x for x in gate.validate(report)))

    def test_bounds_and_alternatives(self):
        report = example()
        report["findings"][0]["location"]["bbox_xywh"] = [1199, 899, 3, 3]
        self.assertTrue(any("outside" in x for x in gate.validate(report)))
        report = example()
        report["findings"][0]["alternative_explanations"] = []
        self.assertTrue(any("plausible alternative" in x for x in gate.validate(report)))

    def test_audio_video_timestamps(self):
        report = example()
        report["asset"]["media_type"] = "video"
        f = report["findings"][0]
        f["modality"] = "video"
        f["evidence_family"] = "temporal"
        f["location"] = {"start_ms": 1200, "end_ms": 700}
        self.assertTrue(any("end_ms>start_ms" in x for x in gate.validate(report)))
        f["location"] = {"start_ms": 700, "end_ms": 1200, "bbox_xywh": [5, 5, 10, 10]}
        self.assertEqual(gate.validate(report), [])

    def test_quality_only_cannot_pretend_to_verify_origin(self):
        report = example()
        report["scope"] = "quality"
        report["decision"]["origin_label"] = "no_ai_evidence_found"
        self.assertTrue(any("Quality-only" in x for x in gate.validate(report)))

    def test_structural_corruption_rejected(self):
        report = example()
        report["asset"]["sha256"] = "abc"
        report["findings"].append(copy.deepcopy(report["findings"][0]))
        errors = gate.validate(report)
        self.assertTrue(any("SHA-256" in x for x in errors))
        self.assertTrue(any("duplicated" in x for x in errors))

    def test_untrusted_camera_attestation_cannot_verify_capture(self):
        report = example()
        report["decision"]["origin_label"] = "verified_capture_provenance"
        report["decision"]["evidence_strength"] = "high"
        report["provenance"]["state"] = "verified_capture"
        self.assertTrue(any("requires nonempty" in x for x in gate.validate(report)))
        report["provenance"].update({"scope": "camera capture of displayed pixels", "issuer": "Camera signing authority", "verifier": "Audited verifier", "binding_verified": True, "trust_verified": True})
        self.assertEqual(gate.validate(report), [])


if __name__ == "__main__":
    unittest.main()
