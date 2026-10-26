# Multi-image and multi-shot character continuity audit

A character sheet is a **designed character consistency** problem, not verification of a real person's identity. Assess whether the same *intended* character design persists across shot scale, view angle, lens, pose, lighting and time. Synthetic faces may appear realistic individually yet subtly change between views. Real actors can appear different from lighting, expression and perspective, so invariants must be chosen carefully.

## Shot coverage and locked reference

For a production requiring a synthetic news presenter or spokesperson, request a locked canonical reference that records approved face landmarks, hairstyle, makeup level, skin appearance and outfit/accessories. Inspect each **separate high-resolution source frame** before arranging a collage. A collage is for review, not a replacement for inspecting source images.

Minimum practical sheet (when production schedule permits): neutral frontal close-up, front 3/4 left and right, full left and right profile, medium desk shot, medium standing shot, wide/full-body, expression variant, hands with relevant props and an optional 1-to-3-second speaking or gesture motion test. More angles are helpful only when consistently controlled and independently inspected.

## Invariants versus legitimate variables

| Candidate | Normally expected within the same production scene | Expected physical variation |
| --- | --- | --- |
| Eye spacing, skull/face shape, nose bridge/tip | Stable 3D proportions (after allowing for projection) | Apparent 2D spacing changes with yaw, focal length and crop |
| Ears, earlobes, hairline and brows | Coherent underlying forms and attachment | Occlusion by hair, cast shadows, styling, expression |
| Mouth/teeth | Stable dental shape when visible and comparable | Expression and camera view change how teeth are exposed |
| Freckles, pores, fine skin markings | Similar spatial placement when intentionally retained | Makeup, focus, resolution, grading, image-to-image variability |
| Hair texture, parting and silhouette | Same hairstyle and maintenance across the sequence | Flyaways, movement, wind, hair occlusion, lighting |
| Outfit, necklace, earrings, badge, headset | Same approved styling and correct geometry | Pose deformation and material response |
| Height, proportions and limbs | Coherent anatomical design within same shot sequence | Perspective, footwear, posture and lens distortion |
| Lighting and catchlights | Physically plausible *per shot*, consistent with scene | Different cameras and lighting setups legitimately alter them |

## Comparison method

1. Preserve individual originals and SHA-256, record shot role (front/profile/medium/wide), intended character reference and known generation/editor settings. Never judge only the assembled contact sheet.
2. Normalize **display size for reviewing only**, not pixel data. Compare frontal-to-frontal at equivalent crop and similar expressions first. Do not use 2D pixel subtraction or face embedding scores across different yaw as an identity proof.
3. Build a table of each approved invariant with `same`, `plausibly variable`, `unresolved`, or `material mismatch`. Reference which image pairs and native crops support each finding.
4. Compare 3/4 and profile shots for *geometry continuity*, not whether 2D facial landmarks are identical. Look for unexplained changes in ear shape, hairline, nose silhouette, jewelry and cheek/jaw architecture.
5. Audit each image independently for anatomy, microtexture, lighting, reflections, typography and accessory topology using image-forensics checklist.
6. For video shots compare sequential continuity and confirm the same outfit, backdrop and props persist within shots; use `scripts/inspect_incident.py` around any morphing.
7. Obtain independent second review blinded to which views are latest revisions. Report disagreements as open issues; revise the **outlier**, not all images by copying it.
8. Before assembling the final non-generative collage, verify each file separately, align color profile and background treatment deliberately, and keep original exports linked to each cell.

## Character sheet remediation

If multiple versions appear to depict "similar people" rather than the same designed person, return to the approved *master* and regenerate or retouch only divergent viewpoints with consistent scene assumptions. Maintain stable skin microtexture and morphology. Avoid a common failure mode: generating each angle with a loosely similar text prompt rather than a true shared reference, resulting in new faces. Preserve authentic-looking expression asymmetry without introducing feature drift.

**Pass**: all required shot roles accounted for, invariant table has no unexplained material mismatch, all individual images pass local artifact QA, visible defects are annotated, and reviewers can trace source files. **Fail**: missing shot/source, unresolved face geometry drift, topological artifact, claimed exact identity from biometric guess, or "100% real human" origin claim on a fully synthetic character. A cohesive character sheet does not prove that it depicts a real person.
