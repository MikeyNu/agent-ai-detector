# Creative production remediation: fix what looks artificial

**Scope:** Improve the visual and auditory quality of authorized creative material while retaining truthful provenance. A visible artifact can exist in AI, CGI, composites and real photography. Remediation changes production quality, **not** evidence of authentic origin. Do not alter or strip watermarks, falsify capture metadata, or make fabricated evidence appear genuine.

## Repair strategy by defect

| Reproducible defect | Likely production cause | Preferred targeted repair | Acceptance check |
| --- | --- | --- | --- |
| Wax-like, hyper-glossy portrait skin | Excessive denoising, inappropriate specular roughness, global beautification, over-smoothing or generation texture | Return to original pixels if possible; reduce skin frequency suppression, preserve natural heterogeneity by facial zone, rebalance localized highlights/roughness; for new image generation request plausible fine-scale pores, nonuniform microtexture and subdued makeup, not generic "ultra-real". | At intended display size and 100%, pore/texture variation is plausible without noisy fake "skin overlay" or sharpened edges. |
| Repeated/equal eyes, identical eyelashes | Symmetry regularization, copy/paste, poor modeling | Re-render or retouch only the affected eyelid/iris geometry while preserving consistent character features; check gaze and lighting. | Eye geometry plausible under pose; catchlights physically defensible. |
| Six fingers or joined fingertips | Topology failure in generation, retouching or segmentation | Re-pose and regenerate difficult hand region with accurate grasp context; use an independent photo/reference or physically modeled hand; manual draw over silhouette and joint transitions. | Anatomy and object contact remain plausible at normal size and original resolution, including subsequent views. |
| Necklace/earring/hair fuses into skin | Masking, occlusion or generation continuity failure | Rebuild strand/chain path with consistent front/back order, anchors, contact shadow and hair strands; adjust source perspective where required. | Continuity traceable end-to-end and across shots. |
| Garbled sign/logotype/UI text | Text rendering under low resolution, warped plane or synthesis | Replace with typeset/vector typography after image production, track homography to surface, apply appropriate perspective and lighting. For company marks use approved source artwork. | Every character legible and accurate in final resolution, spelling, kerning, perspective and movement. |
| Shadows disagree across objects | Inconsistent generative illumination or composite relight | Define key/fill/bounce lights and object placement; match contact and cast shadows, penumbra, exposure and color temperature. | All selected surfaces and time samples agree with the same plausible rig. |
| Reflection mismatch | Scene geometry not tracked | Solve reflection plane/camera and object positions; render/photograph correct reflected contribution. | Mirror/window reflection continuity holds under camera changes. |
| Background objects morph during video | Framewise generation drift or temporal editing | Regenerate using stable scene/reference anchors, motion-tracking, consistent image-to-video reference; replace isolated frames using tracked compositing only if continuity can be validated. | Scrub contiguous frames: walls, objects, accessories do not change unexpectedly. |
| Mouth does not match speech | AV track offset, inadequate phoneme shaping or regenerated face | First correct timeline/audio mux offsets; then revise mouth closures/plosives per actual audio with tracked edit or re-record. | Sound and visible labials align across entire phrase, not just at scene start. |
| Floating feet / impossible movement | Physics or kinematic inconsistency | Solve anchor points, gravity/contact, object trajectory and cast shadows; reanimate with validated motion and plausible camera shutter. | Motion reads correctly in real time and frame-step; impacts and shadows track contact. |
| Flat/overcompressed synthetic voice | Vocoder limitation, noise suppression, overlimited render | Return to high-quality source; adjust breath/prosody/syllable pronunciation; apply restrained dynamic processing and acoustically consistent room treatment. | Normal-speed listening reveals natural phrase-level dynamics without false metallic texture or abrupt room changes. |
| Different face across reference angles | Weak identity conditioning, inconsistent crops/poses | Make a controlled **same-character** reference set: front, 3/4 L/R, profile L/R, medium and full-body shots; lock hairstyle, bone structure, skin finish and core wardrobe. Use stable master image and shared reference; revise *outliers*, don't alter invariant features to hide drift. | Independent side-by-side comparisons find consistent stable design under pose/illumination changes. |

## Safer generation-direction recipe

A quality-focused prompt may specify: **physically plausible anatomy and occlusion, naturally varying skin pore scale across facial zones, realistic highlight roll-off, asymmetry from expression and pose, soft facial hair, coherent shadows and reflections, authentic camera viewpoint, restrained post-processing, a clean garment/prop topology, readable vector-produced text where possible**. Use region-specific negative phrasing for likely defects (e.g. "no merged jewelry links; no wax-like specular sheen; no duplicated eyelashes; no stray text glyphs; no object morphing between frames") instead of an unbounded list of model names or "not AI" magic words. Modern tools do not guarantee compliance with negatives.

### Recommended iteration loop

1. Lock art direction and capture simulation. Record exact model, version, seed/reference settings, export size and scene assumptions when available.
2. Generate or edit one shot/region at a time if the defect is localized; changing the whole image can introduce new defects and character drift.
3. Export **lossless or highest-quality intermediate** and preserve baseline source. Avoid serial upscale/denoise passes that manufacture a skin-like texture but obscure original evidence.
4. Run the same optical or temporal checklist on repaired region **and at least three neighbors**, checking for fresh inconsistencies.
5. For video, test both still frame integrity and 1x playback over the repaired cut, including shot boundaries and audio sync.
6. Require an independent second pass that does not know which version was generated vs edited. Confirm final output at delivery dimensions.
7. Preserve generation/edit provenance. If publishing as synthetic, disclose as appropriate; don't recast synthetic faces as documentary evidence.

## Cinematic portrait and news-anchor specific guidance

For a photorealistic broadcast presenter character, anchor the following: face proportions (eyes, nose, mouth, cheek/jaw), hairline and edges of hair, earrings and outfit, makeup softness, skin texture and specular response, posture, believable mouth articulations, studio catchlights, real-world lighting continuity and hands at desk. A Black South African presenter should be represented naturally rather than through exaggerated skin/texture stereotypes. Across angle sheets, fix the *same character* rather than creating merely similar people. Use accurate lens/perspective differences in profile and 3/4 views. A polished broadcast scene may legitimately use retouching and studio makeup; do not label that inherently artificial.

A final approval can be **"visually passes for the intended production setting"** without claiming **"an authentic camera photo of a real human"**. If images are fully generated, keep an explicit provenance declaration in the production record.
