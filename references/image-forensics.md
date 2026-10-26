# Image and portrait optical-forensics playbook

The purpose is to *localize and describe* anomalies, not to map a style to a particular generator. Every cue below has a known non-AI explanation. No category is dispositive in isolation. Inspect original decoded pixels without AI enlargement; if only a social screenshot is available, lower confidence and report the limitations.

## Three-pass procedure

**Pass 1: composition and imaging model.** Before zooming, infer plausible camera position, approximate focal length class, subject distances, physical materials, primary and fill lights, environment, motion/exposure and depth of field. Write two falsifiable hypotheses, e.g. "single broad softbox explains eye catchlights" and "multi-light studio explains opposing shadows". Resist using an image's overall prettiness, symmetry, color grade, genre or Black/white skin tones as an AI indicator.

**Pass 2: systematic high-risk regions.** Sweep from high-salience topology (hands, overlapping silhouettes, text) to physics (light, reflection, perspective) to microtexture (skin, cloth, noise). Crop candidate regions at native resolution alongside the relevant context. Review 100% first, optionally 200% to 400% **nearest-neighbor only**, explicitly stating it is enlarged pixels, not new detail. Display processed diagnostic products next to original, never instead of original.

**Pass 3: counterexamples and mechanism checks.** Try to reproduce the anomaly through optics, editing, lighting, motion, physical material, JPEG ringing or sensor noise. Check unsuspicious regions where the same mechanism ought to apply. If alternative mechanisms remain equally plausible, downgrade/abstain. Do not infer optical certainty from aesthetics.

## High-value optical tests and common confounds

| Observation to test (not verdict) | What to inspect / localized test | Common genuine or conventional alternatives |
| --- | --- | --- |
| **Finger/joint topology** | Count *visibly distinguishable* fingers, test joint ordering and occluded digit continuation, watch grasp/contact points. Mark bbox. | Motion blur, hidden fingers, extreme perspective, prosthetics, accessories, a composite or generative fill. Never diagnose anatomy from one blur. |
| **Object continuity / intersections** | Follow straps, earrings, headphone wires, straps, necklace chains, laces and clothing seams from entry to exit; check impossible mergers or terminations. | Occlusion, translucency, crop, shallow DOF, real tangles, Photoshop clone/repair. |
| **Eyes and catchlights** | Compare each iris and corneal reflection against light sources, image geometry, wet surface specularity, gaze axis. | Distinct eye orientation and corneal curvature, multiple modifiers, lenses, flash, contacts, motion. Perfectly identical catchlights not necessary. |
| **Skin microstructure** | View cheeks, eyelids, lips, forehead, nose, hands. Test whether fine pores, peach fuzz, wrinkles and specular highlights exhibit plausible *local* variations, not uniform painted smoothing. | Makeup, dermatology differences, beauty filters, high-key lighting, noise reduction, low resolution, color grade. Smooth skin is not proof. |
| **Oil/wax/plastic look** | Compare high-frequency and mid-frequency contrast, pore-retention through highlights, specular shape and roughness across different tissues/materials. | Moisturizer, perspiration, flash, diffusion filter, plastic skin retouching, CG rendering. This is a **quality defect** unless provenance supports generation. |
| **Teeth and tongue** | Count visible tooth boundaries only where resolvable; check lip contact, gum contour, occlusion, symmetry; compare mouth texture with source resolution. | Veneers, braces, motion smear, highlights, compression and inpainting. |
| **Hair and hairline** | Trace individual strands into/behind ears, glasses, hats; look for texture dissolving into background or physically impossible layering. | Motion, backlit flyaways, shallow DOF, hair products, wigs, edge sharpening and masking. Natural coiled hair has complex, variable texture and must not be treated as suspicious for being difficult to resolve. |
| **Text, logos, glyphs** | Check legibility, repeated letters, line-break logic, spacing, fonts, consistent orientation on planar surfaces. Compare *what the text should say* only if reliable independent reference exists. | Low resolution, fabric deformation, reflections, camera angle, stylized lettering, real typos, conventional edits. OCR failure is not AI proof. |
| **Mirrors, windows, glass** | Estimate object positions and reflection planes; test correspondence of distinctive features, camera placement and specular highlights. | Curved mirrors, multiple pane reflections, polarization, tint, compositing, off-axis crop, occlusion. |
| **Cast shadows and lighting** | Locate projected shadows, ambient occlusion at contact, falloff, color temperature, plausible multiple lights and blockers. | Studio multilight rigs, bounce, flashes, composite images, indirect illumination and HDR local tone mapping. |
| **Perspective and scale** | Follow repeated parallel edges toward vanishing points; check limb proportions in 3D, table horizon, floor contact and occlusion. | Wide angle lens, rolling shutter, camera tilt, tilt-shift, panorama stitching, intentional illustration. |
| **Fabric and materials** | Follow seam topology, buttons, pocket geometry, logo continuity, weave variation, fabric gravity and folds. | Fashion asymmetry, wrinkles, garment damage, motion, styling, alteration. |
| **Background recurrence** | Check semantically meaningful objects, repeated chairs, windows, asymmetric pattern continuity and clipping. | Architectural repetition, decor motifs, bokeh, lens aberration, panorama stitches. |
| **Noise/resampling inconsistency** | At matched brightness compare noise residual behavior across subject/background, edge ringing, quantization, CFA remnants if raw available. | Denoising, sharpening, local edits, sensor pipelines, social recompression, image enlargement, CGI. This is *technical localization*, not an AI detector. |
| **Lens and capture behavior** | Depth-of-field consistency by depth, foreground/background blur shape, chromatic aberration direction, vignetting, motion smear. | Computational portraits, synthetic bokeh, tilt-shift, smartphone HDR, focus stacking and conventional compositing. |

## Specific portrait checklist

Record which are **tested**, **not testable** or **not applicable**:

1. Face landmarks and head-to-neck connection at jaw, ears, collar, hairline. An apparent asymmetry can be normal anatomy or perspective.
2. Both eyes: gaze, iris/pupil contours, eyelid intersections, catchlights and shadowing consistent with the lighting context. Do not assume symmetry as a baseline.
3. Skin: fine grain and roughness across cheek, temple, nose, forehead, neck, forearms, knuckles. Look for unnatural uniformity versus normal controlled retouching.
4. Teeth, tongue, mouth, nostril and ear topology at available resolution. Do not hallucinate occluded details.
5. Clothes and accessories continuity (glasses hinge, necklace, earrings, shirt collar, seams).
6. Hands, grips and anatomical continuations. Escalate only when the topology is visibly impossible, not when a finger is hidden.
7. Contact/occlusion between subject and desk, microphone, chair, laptop, hat and jewelry.
8. Highlights, reflections and shadows, accounting for modifiers and ambient bounce.
9. Background story: logical desk props, readable content, cables, wall/floor continuity, plausible text.
10. Image formation: sensor and codec pipelines, DOF and possible retouching. Whether "looks too good" does **not** enter origin determination.

## Spatial evidence registration

Use original orientation after EXIF rotation. For each issue capture `[x,y,w,h]` in pixels and original `width,height`; note whether it appears at normal presentation size. Distinguish: `observation = "left earring chain abruptly terminates at cheek boundary"` from `hypothesis = "generative synthesis may have failed chain continuity"`. Follow with at least one *counterhypothesis* (hair occlusion or masking). If only tiny thumbnails exist, many microtexture and anatomy claims are untestable.

For multiple views of a designed character, compare stable facial geometry, hairstyle, freckles/scars only when intentionally invariant, eyebrow architecture, eye spacing, dental features, earlobe silhouette, garment continuity and plausible camera/lens changes. Use a **consistency** finding, not an identity verification or claim of a real-person match. See `references/remediation-playbook.md`.

## Misleading image-processing diagnostics

- **Error level analysis (ELA)** is a JPEG recompression visualization. It does not differentiate synthetic from photographic content and can be triggered by overlays, editing, different compression and resaving. Do not cite ELA brightness alone as AI evidence.
- **Fourier or frequency spikes** can arise from resizing, sampling and compression; models can suppress generator footprints. Requires controlled reference datasets and validated scoring.
- **EXIF missing / Photoshop present** indicates neither fake nor real. Screen captures and message platforms frequently strip or replace fields; EXIF is editable.
- **PRNU and CFA** can assist qualified camera source analysis with controlled references, original or high-quality files and validated processing. Modern computational capture breaks naive assumptions; a camera can photograph a generated image on a display.
- **AI 'detector' online verdicts** are model outputs, not evidence of certainty. Record model version, expected input, calibration data, image preprocessing, and error rates on *similar* real images and unseen generators.
- **Reverse image search** can locate earlier publications and source context but matching a website is not itself proof of origin. Respect rights and privacy.

## Severity rubric for **quality**, not origin

- **Critical**: impossible anatomy or object continuity obvious at viewing size, repeated face mutations across views, unreadable hero-level text, catastrophic reflection/interaction failure.
- **Major**: plastic skin or unnatural microtexture obvious at output size, mismatched lighting, dissolving clothing/accessories, noticeable edge halos.
- **Minor**: subtle isolated artifact invisible in ordinary presentation, small bokeh discrepancies, color tuning issues.

Ask whether the issue really impacts the production's intended delivery size. Separately mark evidence strength; a major quality problem is not necessarily strong AI-origin evidence.
