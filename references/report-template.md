# Inspection report contract

Return a short human summary plus a machine-readable evidence ledger. Report the original asset, limitations and exact inspected evidence; don't fill unperformed tests with imagined observations.

## Human-facing report

```text
Case: [case ID]                 Scope: [image/video/audio, origin/quality/both]
Input: [basename, SHA-256, dimensions/duration, file lineage]
Origin assessment: [confirmed_ai_origin / verified_capture_provenance /
                    suspected_ai_involvement / no_ai_evidence_found / indeterminate]
Origin evidence strength: [low/moderate/high, not a probability]
Visual/audio production QA: [passes_visual_qa / needs_revision / not_assessed]
Limits: [missing original, unknown codec lineage, low resolution, unavailable verifier]

Strongest supporting evidence:
F01 image [x,y,w,h] or video/audio [start_ms..end_ms]: exact observation
  Mechanism hypothesis: ...
  Reproduce: ...
  Alternatives tested: ...
  Status: ...

Counterevidence and contradictions: ...
Checks NOT performed: ...
Prioritized remediation: ...
Source/provenance evidence: issuer, cryptographic validation scope,
   verifier/version, and asset binding, or "not independently verified".
Verdict explanation: ...
```

## Machine-readable schema

Example: `examples/sample-report.json`. Validate it with `python scripts/validate_report.py path.json` before publication. Required:

```json
{
  "case_id": "client-2026-001",
  "asset": { "sha256": "64 lowercase hex digits", "media_type": "image|video|audio", "source_kind": "original|derived|unknown" },
  "scope": "origin|quality|both",
  "provenance": { "state": "not_verified|verified_ai_generation|verified_capture|conflicting", "scope": "description or null", "issuer": "description or null", "verifier": "description or null", "binding_verified": false, "trust_verified": false },
  "findings": [],
  "decision": { "origin_label": "indeterminate", "evidence_strength": "low", "quality_label": "not_assessed", "rationale": "Reason including uncertainty" },
  "limitations": ["Insufficient original source information"],
  "checks_not_performed": ["C2PA trust validation"]
}
```

Individual finding shape:

```json
{
  "id": "F01",
  "modality": "image",
  "location": { "bbox_xywh": [100, 200, 60, 80] },
  "observation": "Chain appears to end without visible anchor at ear under native crop",
  "hypothesis": "Occlusion mask or synthetic jewelry topology discontinuity",
  "alternative_explanations": ["Behind hair strand", "Conventional retouching"],
  "reproduction": "Open source SHA, examine 100% crop image_1.png and adjacent context",
  "evidence_family": "geometry",
  "strength": "moderate",
  "quality_severity": "major"
}
```

For video incidents, `scripts/inspect_incident.py` reports both absolute decoded PTS and time relative to video stream start, when parseable; disclose which timeline you used. For video or audio use `location: {"start_ms": 400, "end_ms": 900}` and optional `bbox_xywh` for a localized video frame. For metadata/provenance findings use `modality: "provenance"`, `location: {"record": "C2PA manifest"}`. Do not use false high precision for approximate seek timestamps.

### Enforcement notes

- `confirmed_ai_origin` requires provenance `state=verified_ai_generation`, nonempty scope/issuer/verifier and true trust + binding flags. Claims derived only from "AI-looking skin" cannot validate.
- `verified_capture_provenance` requires validated capture record with the same scope and binding checks, but does not assert the photographed scene or person is genuine.
- `suspected_ai_involvement` requires two **independent** at-least-moderate optical/temporal/audio evidence families; the validator verifies family names and completeness of observations/alternatives, not whether the findings are objectively true. This is a minimum, never a proof threshold.
- `no_ai_evidence_found` is a bounded review outcome, not proof of origin. Report inspected coverage and limitations.
- Any reviewer may choose `indeterminate`, including in difficult cases with some anomalies; this is acceptable behavior.
- Severity relates to production defects, not probability of AI involvement. Every finding must include an alternative explanation, except authenticated provenance records.
