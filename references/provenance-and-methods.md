# Source provenance, forensic methods, detector limitations

## What each method actually establishes

**Signed content credentials (C2PA)**: A valid cryptographic signature and asset binding can attest that a particular issuer signed certain statements about an asset's creation/editing history. Verify actual signature, binding, certificate chain/trust policy, date and embedded ingredients using a trusted viewer or supported `c2patool` configuration. A JSON manifest's presence is **not** signature verification. A signed camera claim is not proof the scene was real: a camera can photograph an AI image on a monitor. A trusted AI-generation assertion supports **AI involvement in the attested scope**, not a claim every pixel is AI or that content is false. Source: C2PA spec and Content Authenticity Initiative FAQ.

**Invisible watermarks**: Provider-specific marks such as SynthID can support attribution when *the authorized verifier* detects an authentic supported signal. They are not visual patterns one can infer by looking. A negative result does not exclude AI from another model, or edits and transformations that weaken signals. Never assert SynthID was checked based solely on human observation, and do not invent a watermark score. Avoid suggesting removal or evasion.

**Raw EXIF/container tags**: Useful contextual clues (software, device, time, codec), but trivially edited, omitted, stripped or rewritten. Neither a camera-model tag nor missing EXIF authenticates a photograph. Compare cross-field coherence and supply original context. Do not publish GPS/device IDs or personal metadata without consent.

**Camera forensics (PRNU, CFA, demosaicing)**: Can be meaningful only with suitable sources, repeated known-source reference captures, alignment, noise models and qualified analysis. Computational smartphone photography changes the signal; simplistic thresholds can yield false positives. A camera-source signature may be consistent with photographing a synthetic display or an AI-assisted photo.

**Error-level analysis and noise/frequency residuals**: These are diagnostic transforms, not binary AI-origin tests. Color grading, JPEG quantization, re-encoding, screenshotting, social network recompression, sharpening and generative editing confound results. Only use controlled comparisons with documented sensitivity/specificity.

**Neural AI detectors**: Treat all outputs as *supporting classifier opinions*. Demand model/version, preprocessing, operating point, licensing, dataset composition, real-negative selection, generator-held-out results, domain-matched false-positive rates, calibration plots and robustness to compression/crops/face retouching. Do not ensemble two detectors trained on correlated data as if the outputs were independent. AIGIBench 2025 and 2026 zero-shot comparisons show broad generalization failures.

**External corroboration**: Source images, camera RAW files and editing-project timelines, credited creator, independent footage, original publication timestamps, scene geometry, reverse-image matches, authenticated production records. Check for circular citations and copied reposts. A true caption/date does not prove media origin; incorrect caption does not imply AI.

## Evidence hierarchy (for an origin claim)

1. **Authenticated, scope-specific provenance** tied cryptographically to the *exact* asset, issuer and allowed trust policy, plus corroborated original production records if possible.
2. **Independent original acquisition and history**: camera RAW provenance, source capture context, project files, trustworthy chain of custody, independently recorded view of same event.
3. **Repeatable, localized, physically inconsistent evidence** that survives alternative mechanism analysis, ideally across modalities and a continuous time window.
4. **Domain-tested detector outputs** with documented false-positive rates and held-out generator families.
5. **Weak aesthetics** (smooth skin, perfect hair, too symmetrical, colorful grading, 'AI vibe'). Useful to flag *quality*, not origin.

These are qualitative tiers, **not** numeric weights. Different evidence categories can conflict. Record contradictory trusted signals rather than choosing whichever agrees with first impression. An AI provenance marker on one ingredient does not prove full-frame AI origin. A camera-source marker does not certify the depicted events or whether an object is synthetic.

## Suggested operator workflow

1. Preserve original media and its SHA-256 before any conversion. Log where it came from and any known edits.
2. Run `inspect_media.py` for immutable source inventory. If `c2patool` is available, the script saves raw `c2pa.json` but **does not mark signatures trusted**.
3. Verify using a maintained external C2PA validator configured for **trusted signer certificates** and content binding. Record verifier name/version, trust policy, manifest validation status, issuer, assertion action(s), attached ingredients and timestamp in report. An absent, invalid or untrusted manifest is not automatically evidence of AI.
4. If provider-specific watermark check is authorized and available, record provider, verification endpoint/version and the precise detection outcome including `not_detected`/`inconclusive`, coverage and known support limits.
5. Check independent source context and use localized optical/temporal cues to prioritize investigation.
6. Avoid assigning a posterior probability unless independently calibrated on ground truth for this specific operational domain.

## Important edge cases

- **A social screenshot of real camera content** has no camera C2PA. Its absence does not imply AI.
- **A camera photograph of an AI image on a screen** may have real camera EXIF or capture credentials; the depicted image remains synthetic. Report scope carefully.
- **A genuine image with Photoshop Generative Fill** is *partially AI edited*, not "fully generated". Localize if records disclose location; without them, do not infer exact edit mask from aesthetics.
- **A fully synthetic image with detailed pores and correct anatomy** can be visually indistinguishable from a photograph. A clean review does not certify authentic origin.
- **CGI, beauty filters and professional retouching** can share smooth skin, unusual noise or reflections. Do not merge them into generative AI.
- **Metadata can be forged**; cross-field provenance without cryptographic checks has limited value.
- **High-stakes claims** merit independent expert review and an authenticated source chain.

## Useful official resources

- C2PA specifications: https://spec.c2pa.org/
- Content Credentials verification: https://verify.contentauthenticity.org/
- c2patool usage: https://github.com/contentauth/c2patool/blob/main/docs/usage.md
- Google SynthID: https://deepmind.google/models/synthid/
- OpenAI content provenance guidance: https://developers.openai.com/api/docs/guides/content-provenance
- NIST OpenMFC tasks: https://mfc.nist.gov/
