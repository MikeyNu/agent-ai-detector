# Agent AI Detector

An evidence-first **agent skill** for forensic-looking inspection of images, portraits, videos and audio, with a particular emphasis on finding local visual and temporal artifacts and producing actionable production QA. It deliberately does **not** pretend that optical inspection proves whether a real person or photograph is AI-generated.

> The key separation: **visual plausibility / production quality** and **origin / authenticity evidence** are different outputs. No automatic visual-origin model is bundled.

## Repository layout

- `SKILL.md`: agent-facing entry point. This repository itself is the skill directory.
- `references/`: research, modality playbooks, provenance, forensic decision rules, remediation, evaluation and report template.
- `scripts/inspect_media.py`: optional offline evidence-preparation CLI. SHA-256, image metadata, 100% crops, still/video contact sheets, basic codec inventory, audio waveform preview and read-only C2PA manifest inspection when `c2patool` is installed.
- `scripts/inspect_incident.py`: extract consecutive decoded frames around an incident with decoder-reported timestamps and optional region crops.
- `scripts/validate_report.py`: report structure and epistemic guardrail checks. It does **not** validate the truth of the analyst's observation.
- `examples/sample-report.json`: reproducible schema example with an intentionally inconclusive verdict.
- `tests/`: executable unit and integration tests, including ordinary optical/codec transformations and negative cases.

## Install

Clone the repository to your agent's skill discovery directory with the directory name `agent-ai-detector`, or point your agent to its `SKILL.md`. This follows the [Agent Skills format](https://agentskills.io/specification). Some clients discover user skills under `.agents/skills/agent-ai-detector/` or another application-specific skills path.

The skill text works without installing packages. For utilities:

```bash
python -m pip install -r requirements.txt
python scripts/inspect_media.py /path/to/file.jpg --out /path/to/unique-evidence-dir --crop 25,40,120,90
python scripts/inspect_media.py /path/to/clip.mp4 --out /path/to/unique-clip-report --frames 12
python scripts/inspect_incident.py /path/to/clip.mp4 --out /path/to/unique-incident-report --from-s 12 --to-s 13 --crop 40,20,140,100
python scripts/validate_report.py examples/sample-report.json
python -m unittest discover -s tests -v
```

Video/audio extraction requires external `ffmpeg` and `ffprobe`. `c2patool` is optional and must be configured for correct trust validation. Raw manifest presence alone never counts as trusted C2PA provenance.

## Recommended prompts

- "Inspect this portrait at 100%, locate every demonstrable photorealism defect with original pixel coordinates, challenge each defect with a plausible photographic explanation, and produce a prioritized repair plan. Keep authenticity separate from quality."
- "Inspect this video for frame-to-frame identity, occlusion and hand-object contact continuity; give exact time ranges and adjacent-frame evidence. Do not infer AI from compression or scene cuts."
- "Is this photograph genuinely camera-captured or synthetic? Check source-chain evidence first, describe testable visual observations, and abstain if the evidence is insufficient."
- "Audit the image set for the same character's visual consistency across angles; report deviations, confidence limits and fixes without assuming provenance."

## Safety, uncertainty, privacy

Visual artifacts are **clues**, never generator fingerprints. Beauty retouching, CGI, conventional compositing, HDR, editing software and social-media recompression generate many of the same effects. A clean synthetic portrait can contain no obvious clues. C2PA assertions need valid signatures and issuer trust; metadata absence is not exculpatory. Inverse-process analysis or model scores must be validated on independent real-world datasets before use.

Never submit private/client media to cloud detectors without permission. Outputs may contain face crops, EXIF or other sensitive data. Tool reads locally, never uploads, never alters input. Avoid biometric identification, demographic guesses, and claims about a real individual's identity or character. Do not remove/obscure provenance or present AI-derived creative media as documentary proof. In fraud, legal, health and other consequential contexts, request original files and specialized human review.

## Limits of validation

The repository tests check that **inspection utilities behave correctly and report guardrails are enforced**, using controlled fixtures. They **do not** establish real-world deepfake sensitivity, specificity, robustness or generalization. The evaluation plan specifies external, licensed, ground-truth datasets and unseen-generation testing needed before making accuracy claims.

## License

MIT. Research sources retain their own licenses; the source list links to upstream publications instead of copying their content or benchmark datasets.

### Animated images and forensic frame timing

Animated GIF/WebP files are treated as still images by the general preparation script, which **explicitly warns that only the first frame was inspected**. Export them to an authorized video copy and run incident inspection if temporal authenticity matters. `inspect_incident.py` uses a half-open interval `[--from-s, --to-s)` in seconds **relative to the video stream start** and reports source decoder PTS separately, including any nonzero stream timestamp origin. `--max-frames` is a safety cap, not a complete long-video scan. For privacy and safety, FFmpeg inspection uses a local protocol allowlist and refuses network-input protocols.
