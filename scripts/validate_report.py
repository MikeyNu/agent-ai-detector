#!/usr/bin/env python3
"""Validate structure and conservative inference rules for media-forensic reports.

This is a *report guardrail*, not a verifier of image analysis, watermark signatures,
C2PA certificate trust, detector statistics, or asserted ground truth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

LABELS = {"confirmed_ai_origin", "verified_capture_provenance", "suspected_ai_involvement", "no_ai_evidence_found", "indeterminate"}
STRENGTH = {"low", "moderate", "high"}
QUALITY = {"passes_visual_qa", "needs_revision", "not_assessed"}
PROVENANCE = {"not_verified", "verified_ai_generation", "verified_capture", "conflicting"}
FAMILIES = {"geometry", "lighting", "texture", "temporal", "audio", "source_context", "provenance", "metadata", "detector", "optics", "typography"}
INDEPENDENT_VISUAL_FAMILIES = {"geometry", "lighting", "texture", "temporal", "audio", "optics", "typography"}
MODALITIES = {"image", "video", "audio", "provenance", "metadata"}
SEVERITIES = {"critical", "major", "minor", "none"}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Root must be a JSON object"]
    for key in ("case_id", "scope", "asset", "provenance", "findings", "decision", "limitations", "checks_not_performed"):
        if key not in data:
            errors.append(f"Missing required root field: {key}")
    if not nonempty_str(data.get("case_id")):
        errors.append("case_id must be a nonempty string")
    if data.get("scope") not in {"origin", "quality", "both"}:
        errors.append("scope must be origin|quality|both")
    asset = data.get("asset") if isinstance(data.get("asset"), dict) else {}
    if not HEX_SHA256.fullmatch(str(asset.get("sha256", ""))):
        errors.append("asset.sha256 must be a 64-character lowercase hex SHA-256")
    if asset.get("media_type") not in {"image", "video", "audio"}:
        errors.append("asset.media_type must be image|video|audio")
    if asset.get("source_kind") not in {"original", "derived", "unknown"}:
        errors.append("asset.source_kind must be original|derived|unknown")
    if not isinstance(data.get("limitations"), list) or any(not nonempty_str(item) for item in data.get("limitations", []) if isinstance(data.get("limitations"), list)):
        errors.append("limitations must be a list of nonempty strings")
    if not isinstance(data.get("checks_not_performed"), list) or any(not nonempty_str(item) for item in data.get("checks_not_performed", []) if isinstance(data.get("checks_not_performed"), list)):
        errors.append("checks_not_performed must be a list of nonempty strings")

    provenance = data.get("provenance") if isinstance(data.get("provenance"), dict) else {}
    if provenance.get("state") not in PROVENANCE:
        errors.append("provenance.state is invalid")
    for flag in ("binding_verified", "trust_verified"):
        if type(provenance.get(flag)) is not bool:
            errors.append(f"provenance.{flag} must be boolean")
    decision = data.get("decision") if isinstance(data.get("decision"), dict) else {}
    label = decision.get("origin_label")
    if label not in LABELS:
        errors.append("decision.origin_label is invalid")
    if decision.get("evidence_strength") not in STRENGTH:
        errors.append("decision.evidence_strength must be low|moderate|high")
    if decision.get("quality_label") not in QUALITY:
        errors.append("decision.quality_label is invalid")
    if not nonempty_str(decision.get("rationale")) or len(str(decision.get("rationale", "")).strip()) < 20:
        errors.append("decision.rationale must explain evidence and limitations (at least 20 characters)")
    if data.get("scope") == "quality" and label != "indeterminate":
        errors.append("Quality-only report must keep origin_label=indeterminate")
    if label == "no_ai_evidence_found" and not nonempty_str(data.get("review_coverage")):
        errors.append("no_ai_evidence_found requires review_coverage describing what was actually inspected")

    is_verified = label in {"confirmed_ai_origin", "verified_capture_provenance"}
    if is_verified:
        required_state = "verified_ai_generation" if label == "confirmed_ai_origin" else "verified_capture"
        if provenance.get("state") != required_state:
            errors.append(f"{label} requires provenance.state={required_state}")
        if provenance.get("binding_verified") is not True or provenance.get("trust_verified") is not True:
            errors.append(f"{label} requires trust_verified=true and binding_verified=true")
        for field in ("scope", "issuer", "verifier"):
            if not nonempty_str(provenance.get(field)):
                errors.append(f"{label} requires nonempty provenance.{field}")
    elif decision.get("evidence_strength") == "high":
        errors.append("High origin evidence strength requires authenticated provenance in this report taxonomy")

    findings = data.get("findings") if isinstance(data.get("findings"), list) else None
    if findings is None:
        errors.append("findings must be a list")
        findings = []
    ids: set[str] = set()
    qualifying_families: set[str] = set()
    for i, finding in enumerate(findings):
        field = f"findings[{i}]"
        if not isinstance(finding, dict):
            errors.append(field + " must be an object")
            continue
        id_ = finding.get("id")
        if not nonempty_str(id_):
            errors.append(field + ".id required")
        elif id_ in ids:
            errors.append(field + ".id duplicated")
        else:
            ids.add(id_)
        if finding.get("modality") not in MODALITIES:
            errors.append(field + ".modality invalid")
        if finding.get("evidence_family") not in FAMILIES:
            errors.append(field + ".evidence_family invalid")
        if finding.get("strength") not in STRENGTH:
            errors.append(field + ".strength invalid")
        if finding.get("quality_severity") not in SEVERITIES:
            errors.append(field + ".quality_severity invalid")
        for key in ("observation", "hypothesis", "reproduction"):
            if not nonempty_str(finding.get(key)):
                errors.append(field + "." + key + " must be nonempty")
        loc = finding.get("location")
        if not isinstance(loc, dict):
            errors.append(field + ".location must be an object")
            loc = {}
        modality = finding.get("modality")
        if modality == "image" and "bbox_xywh" not in loc:
            errors.append(field + ".location requires bbox_xywh for image")
        if modality in {"video", "audio"}:
            a, b = loc.get("start_ms"), loc.get("end_ms")
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or isinstance(a, bool) or isinstance(b, bool) or a < 0 or b <= a:
                errors.append(field + ".location requires start_ms>=0 and end_ms>start_ms")
        if modality in {"provenance", "metadata"} and not nonempty_str(loc.get("record")):
            errors.append(field + ".location requires record description")
        if "bbox_xywh" in loc:
            bbox = loc["bbox_xywh"]
            if not isinstance(bbox, list) or len(bbox) != 4 or any(type(n) is not int for n in bbox) or bbox[0] < 0 or bbox[1] < 0 or bbox[2] <= 0 or bbox[3] <= 0:
                errors.append(field + ".location.bbox_xywh must be [nonnegative x,y, positive integer w,h]")
            elif isinstance(asset.get("oriented_pixel_size"), list) and len(asset["oriented_pixel_size"]) == 2:
                w, h = asset["oriented_pixel_size"]
                if bbox[0] + bbox[2] > w or bbox[1] + bbox[3] > h:
                    errors.append(field + ".location.bbox_xywh lies outside source image")
        alternatives = finding.get("alternative_explanations")
        if modality != "provenance" and (not isinstance(alternatives, list) or not alternatives or any(not nonempty_str(x) for x in alternatives)):
            errors.append(field + ".alternative_explanations requires at least one plausible alternative")
        if modality == "provenance" and alternatives is not None and not isinstance(alternatives, list):
            errors.append(field + ".alternative_explanations must be list when supplied")
        if finding.get("strength") in {"moderate", "high"} and finding.get("evidence_family") in INDEPENDENT_VISUAL_FAMILIES:
            qualifying_families.add(finding["evidence_family"])
    if label == "suspected_ai_involvement" and len(qualifying_families) < 2:
        errors.append("suspected_ai_involvement requires 2 independent moderate-or-strong optical/temporal/audio evidence families; metadata/detector score alone cannot qualify")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check forensic evidence report structure and conservative conclusion rules")
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid report: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("FAILED report quality gate:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("PASS: report is structurally valid and passes conclusion guardrails; observations/trust have NOT been independently verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
