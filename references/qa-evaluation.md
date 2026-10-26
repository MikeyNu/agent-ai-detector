# Adversarial validation plan and acceptance criteria

## Two independent validation programs

**Program A, engineering reliability** tests deterministic tool operation: preserving source bytes, correct hashes, pixel-coordinate handling, no invented provenance, safe subprocesses, metadata redaction/PII handling, honest decoding errors, reproducible samples, and report schema controls. These can be automated with fixtures.

**Program B, forensic discrimination** tests how well an actual human/agent *interpretation* generalizes to unseen media: ground-truth, full-scope/partial edits, confounders, generator holdouts, compressor/resize shifts and evaluator blindness. Fixture tests **cannot** estimate discrimination accuracy; do not report "X% AI detection" from engineering tests.

## Battle-test matrix: expected behavior and attack on the analyst

| Case | Truth / confound | Intended pass condition |
| --- | --- | --- |
| 01 | Genuine RAW camera portrait, pores and unusual shadow | No AI attribution from lighting; retain camera source context. |
| 02 | Genuine retouched beauty photo with waxy skin | Flag aesthetic plasticity if present; origin `indeterminate` or `no_ai_evidence_found`, not confirmed AI. |
| 03 | Genuine smartphone computational portrait/HDR | Do not read bokeh boundaries or facial denoise as generator fingerprint. |
| 04 | Genuine high-ISO/low-light frame | Noise grain and banding not evidence of AI. |
| 05 | Genuine long-exposure subject motion, apparently extra hand | Test exposure and blur before anatomy accusation. |
| 06 | Genuine person with prosthetic/sixth digit or asymmetric anatomy | Do not assume anatomical difference proves synthesis; protect against identity/demographic bias. |
| 07 | Genuine studio image, multiple catchlights/shadows | Model multiple lights before reflection mismatch finding. |
| 08 | Genuine photograph subjected to Photoshop compositing | Distinguish conventional edit from AI-edit claim. |
| 09 | Social screenshot of known real photo, no EXIF | Provenance stays unknown; missing metadata not fake. |
| 10 | Photograph of AI-generated image on a physical display | Camera provenance not proof the *depicted* face is real. |
| 11 | Fully AI portrait with correct hands, texture and lighting | Optical-only likely abstains; no automatic "real" claim. |
| 12 | Generated portrait with obvious fused jewelry | Localized defect, 100% crop, alternatives, quality fix; suspicion only with corroboration. |
| 13 | AI image edited in one small region of real photo | Scope `partially_ai_edited` if source records prove; don't attribute whole frame. |
| 14 | Unusual but real typography/logo distorted by perspective | Compare surface geometry and reference design before labeling gibberish. |
| 15 | Fully CGI-rendered 3D portrait | Artificial appearance not proof of generative AI. |
| 16 | GAN-era fake with obvious hair artifact | Report artifact, no model attribution without provenance. |
| 17 | Video with natural jump cuts and mismatched pose | Separate shots, not morphing within shot. |
| 18 | Video with codec/B-frame blocking and face flutter | Compare original quality / adjacent frames; avoid source claim. |
| 19 | Video with rolling shutter/panwarping | Check device and shutter before physics failure. |
| 20 | AI video with within-shot non-rigid object transformation | Trace multiple consecutive frames, anchor geometry, timecode and alternatives. |
| 21 | AI video with correct still frames but temporal hand-object drift | Temporal analysis catches; contact sheet alone must not pass. |
| 22 | Genuine interview with 120 ms AV mux lag | Test fixed offset; no false voice-deepfake conclusion. |
| 23 | Voice recording after noise gate and neural denoising | Do not infer TTS from missing breaths and metallic artifacts. |
| 24 | AI voice with near-natural prosody, strong codec compression | Optical/audio inspection can abstain; note domain mismatch. |
| 25 | Valid C2PA AI-generation claim linked to exact asset | `confirmed_ai_origin` only with trust and scope, even if appearance flawless. |
| 26 | Untrusted/forged/invalid C2PA JSON that says `trainedAlgorithmicMedia` | Do not grant confirmed origin. |
| 27 | No C2PA, no SynthID detection | Never conclude authentic camera origin. |
| 28 | Verified camera capture of screen playing generated video | Capture-chain claims limited; depiction still may be synthetic. |
| 29 | Image with invisible watermark detected by approved verifier | Attribute only supported watermark/provider/scope, not all creation history. |
| 30 | Detector confidently marks genuine stylized/retouched photograph as fake | Treat model score as weak supporting evidence; require false-positive context. |
| 31 | Detector trained on familiar models sees completely unseen generator | Demand held-out-generator evaluation, acknowledge OOD. |
| 32 | AI generated logo/text cleaned up manually | No visible glyph errors; do not treat clean typography as proof of authenticity. |
| 33 | Audio-only file using synthetic instruments but human-sung vocals | Don't equate synthesizer instrumentation with cloned voice. |
| 34 | A single viral crop without context, only 180x180 | Lower resolvability and abstain; do not imagine fine pores. |
| 35 | Character multi-view sheet generated in separate runs, face drifts | Quality/identity **consistency** issue even if no provenance question. |
| 36 | Adversarially edited AI portrait with camera-like noise and metadata | No "confirmed camera" from appended EXIF/noise. |

Cases 1-36 are **design acceptance scenarios**, not claims that all have been run on annotated real-world datasets. Software tests exercise a subset mechanically. Each remaining case needs named media, permission/license, immutable hash, independent ground truth, blinded adjudication and documented measurement before marked complete.

## Dataset & evaluation protocol for future validated detection performance

1. Pre-register task and definitions: fully synthetic, AI edited (with region masks), conventional edit, CGI, camera-source, unknown. Decide whether provenance or visual-only is available to evaluators. Do not collapse label definitions.
2. Assemble balanced, licensed **real negatives** from modern phones, DSLRs, low-light, HDR, selfies, makeup/retouching, professional composites, diverse skin textures and face types, social recompression, live broadcast, CGI and difficult non-human scenes. Prevent overlap with training, published test shots or model development datasets.
3. Assemble positives from diverse available GAN, diffusion, autoregressive, video/voice generators with dates and generator versions; include hard negatives without visible artifacts. Split **by generator family**, source photographer/creator and original content, not random crops/frames that leak from train to test.
4. Pre-specify conditions: originals, JPEG quality ladders (e.g. 95/75/50), crops, downscale, screenshots, messaging-platform resaves, video recompression/variable fps, slow-motion, blur, audio neural codec and genuine postprocessing. Preserve each transformation's provenance.
5. Blind at least two reviewers/agents to labels and to other reviewers' impressions. Evaluate visual-only first, then optional metadata/provenance and optional model scores as separate stages. Record disagreement and adjudication.
6. Report confusion matrices **per label and per domain**, true-positive rate at specific false-positive rates (especially at 1% or below for consequential uses), precision at prevalence scenarios, AUROC and AUPRC if scores valid, ECE/reliability only if calibrated probabilities exist, 95% confidence intervals, abstention/coverage and error costs. Avoid accuracy-only claims on balanced lab subsets.
7. Audit fairness and error rate by scene type, skin tone representation, camera model, lighting, accessibility/physical variation **without attributing traits to real individuals in the report**. No fabricated demographic identification or grouping from photographs.
8. Red-team for metadata spoofing, camera rephotography of generated screens, heavily retouched genuine photos, invisible high-quality fakes, sample leakage, model contamination, malicious captions, reviewer priming and false certainty from a single network score.
9. Maintain a dated registry with each source, ground truth method, rights, preprocessing, raw verdicts, disagreements, signed evaluator reports, and results by **model and version**. Refresh after generator upgrades. No "100%" guarantees.

## Release gates

| Gate | Required | Local tooling status |
| --- | --- | --- |
| A1 Skill frontmatter | Valid Agent Skills name/description; reference links exist | `tests/test_contract.py` |
| A2 No-autoclassification | Preparation scripts never infer origin from metadata, pixels, ELA, waveforms or hashes | `tests/test_inspect_media.py` |
| A3 Immutability and traceability | SHA-256 matches input; original bytes unchanged; outputs labeled derived | `tests/test_inspect_media.py` |
| A4 Negative and missing dependencies | Missing ffmpeg/c2patool never becomes a positive detection; no corrupted silent success | `tests/test_inspect_media.py` |
| A5 Report semantics | Claimed confirmed AI cannot pass without verified-source provenance and scope; visual-only result never labeled verified | `tests/test_validate_report.py` |
| A6 Time/region bounds | Crops valid, requested seek times distinct from actual decoder PTS; adjacent frames may have nonzero stream origins | `tests/test_inspect_media.py` and `tests/test_inspect_incident.py` |
| B1 Real-world discrimination | Run blinded, licensed ground-truth cases 1-36 and compute by-domain metrics | **Not established by unit tests** |
| B2 Cross-domain robustness | Show stable performance across unseen generators, codecs and capture devices | **Not established by unit tests** |
| B3 Calibration and reviewer agreement | Confidence metrics and real-world false-positive rates | **Not established by unit tests** |

An agent can be excellent at *artifact QA* without being empirically validated as an *authenticity detector*. Marketing must not blur this distinction.

## Adversarial review checklist for each case

- Was this finding anticipated because an operator already said "AI"? Conduct blind pass.
- Is the anomaly visible in original source, or introduced by crop enlargement, sharpening, compression or the analyst's reconstruction?
- Do at least two independent evidence families support the source inference? Are they truly independent?
- Could it be conventional VFX, CGI, beauty postprocessing, capture physics, a genuine disability, prosthetic, brand typography or a normal edit?
- Is a verified AI-edit credential being misapplied to the entire image? Is a camera claim being mistaken for truth of depiction?
- Are crops/timecodes reproducible in the exact input hash? Does the timeline use source PTS if claimed?
- Does the report distinguish "no AI evidence" from "confirmed real"?
- Would a false positive unfairly harm the creator, subject or client? If yes, require stronger corroboration and human review.
