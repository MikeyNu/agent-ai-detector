---
name: agent-ai-detector
description: Evidence-led forensic review of images, portraits, videos and audio for potential generative-AI creation or modification. Use when asked whether media looks AI-generated, to locate visual or temporal defects, audit photorealism, distinguish camera artifacts from synthesis, verify provenance, or recommend precise fixes. Produces inspectable region/timecode findings and calibrated conclusions, not unsupported binary assertions.
license: MIT
compatibility: Python 3.10+ for optional inspection scripts; Pillow for contact sheets/crops; FFmpeg/ffprobe for video and audio; optional c2patool for provenance. Visual reasoning works without these tools.
metadata:
  author: MikeyNu
  version: "1.0.0"
---

# Forensic media inspection and synthetic-artifact QA

## Non-negotiable operating rule

**Never equate appearance with proof of origin.** This skill has two independent outputs: (A) observed quality, including photorealism and localized inconsistencies, and (B) evidence about whether and how AI was involved. A synthetic portrait may be flawless; a genuine portrait may look synthetic after beautification, HDR, unusual lighting or compression. When the evidence is ambiguous, answer **indeterminate**. No model, visual inspection trick or absence of metadata can reliably classify every contemporary image or video.

Do not claim that you have zoomed, sampled, inspected metadata, verified a watermark or compared frames unless you actually performed that step and retained the evidence. Never identify a person from a face, infer sensitive attributes, or allege that a real person's portrait is fake based on their appearance. In consequential cases, request the original file/source chain and recommend independent forensic review.

## Activate and choose a lane

- **Origin investigation**: "Is this real or AI?", "is this portrait synthetic?", manipulated photos, suspected face swaps, authenticity checks, misinformation.
- **Production quality audit**: "Does this look AI-generated?", "find AI slop", "remove artificial skin", consistency and artifact audits on generated visuals. Diagnose defects without declaring provenance.
- **Generation remediation**: "How do I make this believable?", "fix deformation, glossy skin, morphing". Give precise corrections but do not misrepresent synthetic media as genuine evidence, defeat provenance/watermarks or facilitate impersonation.

## Inspection contract

1. **Scope**: Record the exact claim, file received, media type, user intent, provenance custody, resolution/duration and transformations (original, screenshot, social repost, crop, edited export). Prefer the original asset. Is the question about `fully_generated`, `partially_ai_edited`, `conventionally_edited` or simply `photorealism`? These are different questions.
2. **Preserve and inventory**: Hash input (SHA-256); keep source immutable; capture dimensions, codec, frame rate, color information, metadata and tool availability. Optionally run `python scripts/inspect_media.py INPUT --out OUTPUT_DIR`. Never mistake its diagnostic products for a detector's output. Check C2PA with a genuine validator and other supported watermarks only with authorized tools.
3. **Blind global viewing first**: At fit-to-screen, describe content, illumination, camera viewpoint, depth of field, scene geometry and overall plausible alternatives **before searching for defects**. Do not adopt the user's suggested verdict.
4. **Forensic close pass**: Inspect at native pixel scale (100%) and crop suspicious regions, including counterexamples from apparently normal regions. Review hands, fingertips, ear/hair/accessory boundaries, eyes/catchlights, teeth, skin pores, textiles, text/logos, shadows, reflections, perspective, contact/occlusion and background objects. Use `references/image-forensics.md`. Zoomed nearest-neighbor previews replicate pixels; they do not reveal extra resolution. Do not use generative upscaling to manufacture evidence.
5. **Video-specific pass**: Examine motion at normal speed, then adjacent frames before/after each suspected issue. Separate shot cuts from hallucinated morphs; track object identity, hand-object contact, occlusion, specular paths, shadow continuity, physical motion and audio-lip synchrony. Timecode all incidents. See `references/video-forensics.md`.
6. **Audio-specific pass**: Listen in full context and at normal speed first, then inspect candidate spans for prosodic transitions, phoneme articulation, breath and room continuity, overlapping voices and AV sync. Spectrogram/codec oddities are only supporting cues. See `references/audio-forensics.md`.
7. **Attempt to falsify every flag**: Ask what normal capture, optics, exposure, HDR/beauty processing, makeup, motion blur, rolling shutter, perspective, lighting, compression, focus, multicam editing or a practical effect could explain it. Compare a similar non-suspicious region. A defect counts as AI evidence only insofar as plausible alternatives have been investigated.
8. **Integrate independent evidence**: Keep provenance/capture-chain claims, optical observations, temporal/audio measurements, source context and model-detector scores in separate evidence families. Do not count five symptoms of the same compression glitch as five independent findings. Record untested checks and contradictions. Consult `references/provenance-and-methods.md`.
9. **Adjudicate conservatively** using the decision labels and rules below. Attach coordinates or timecodes, severity, mechanisms, alternative explanations, reproduction steps, and suggested fixes. Use `references/report-template.md`; validate machine-readable reports with `python scripts/validate_report.py REPORT.json`.
10. **Quality gate**: Perform a second adversarial pass attempting to overturn your conclusion. No confident attribution from aesthetic style, single odd finger, missing EXIF, a third-party score, or a social-media screenshot. Use `references/qa-evaluation.md` for benchmark protocols and failure cases.

## Conclusion taxonomy

| Origin label | Use only when |
| --- | --- |
| `confirmed_ai_origin` | Validated, attributable and correctly scoped generation/AI-edit provenance (or independently authenticated original generation records). State the asserted scope; signature verification does not establish factual truth. |
| `verified_capture_provenance` | Validated capture chain attests to the camera/file in scope. **Does not prove the scene depicted was real**: cameras can photograph screens or staged scenes. |
| `suspected_ai_involvement` | At least two genuinely independent, localized, reproducible anomalies survive alternative-explanation checks. Not proof of AI; visual inconsistencies also arise from other edits. |
| `no_ai_evidence_found` | Material has been examined in adequate quality without relevant signs. **Not proof of human/camera origin**. |
| `indeterminate` | Insufficient data, ambiguous cues, contradictory evidence, small/processed media, or material outside tested detector domain. Default rather than guessing. |

Report qualitative **evidence strength** (low/moderate/high) separately from the label; never invent a statistical probability or "99% accurate" score. `high` for origin only when warranted by authenticated provenance or similarly authoritative records. The separate quality result is `passes_visual_qa`, `needs_revision`, or `not_assessed`. A clean visual audit is not an authenticity certification.

## Required evidence ledger

For each finding write: `ID | modality | coordinate/time | observed pixels/sound/motion | test/reproduction | proposed mechanism | plausible non-AI explanation | independent family | strength | recommendation`. Mark an absent finding as absent, not "passed" if it was never tested. Use bounding boxes in original oriented pixel coordinates as `[x,y,width,height]`; video/audio time is milliseconds from file start (with uncertainty if seeking/VFR). Provide at least one context crop/adjacent frame for each asserted visual defect.

Origin conclusion must be justified by its strongest underlying evidence, not by averaging weak aesthetics. Give the user a separate revision queue ordered by severity and visibility: **critical** (identifiability, object topology, motion), **major** (lighting, texture, interaction), **minor** (cosmetic). Never claim rendering fixes can prove authenticity.

## Tooling and progressive references

- For technical optical cue matrices and false positives: `references/image-forensics.md`.
- For frame comparison, camera physics and AV timing: `references/video-forensics.md`.
- For a multi-angle character sheet and cross-shot character consistency: `references/character-consistency.md`.
- For speech and other audio: `references/audio-forensics.md`.
- For provenance, C2PA, invisible watermarks and detector interpretation: `references/provenance-and-methods.md`.
- For specific repair instructions and naturalistic production QA: `references/remediation-playbook.md`.
- For strict tests, hard negatives, benchmark leakage and acceptance gates: `references/qa-evaluation.md`.
- For output format and example report: `references/report-template.md` and `examples/sample-report.json`.
- For source evidence and research notes: `references/research-and-sources.md`.

### Command-line quick start

```bash
python -m pip install -r requirements.txt
python scripts/inspect_media.py portrait.png --out inspection-portrait --crop 120,90,80,60
python scripts/inspect_media.py video.mp4 --out inspection-video --frames 12
python scripts/inspect_incident.py video.mp4 --out incident-12s --from-s 12 --to-s 13 --crop 40,20,140,100
python scripts/inspect_media.py speech.wav --out inspection-audio
python scripts/validate_report.py examples/sample-report.json
python -m unittest discover -s tests -v
```

`inspect_media.py` prepares read-only metadata, hashes, native-resolution crops, contact sheets and waveform previews. `inspect_incident.py` produces consecutive decoded frames and decoder-reported PTS around a suspicious interval, with optional region crops. **It does not classify origin, run neural detectors, infer trust or authenticate people.** Optional external binaries: `ffmpeg`, `ffprobe`, `c2patool`. Only use on material you are authorized to inspect. Retain original originals securely; extracted frames and metadata may be sensitive. Consult `README.md` before sharing reports or samples.
