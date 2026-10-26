# Video forensics: temporal, optical and audio-visual scrutiny

**Video is not a bag of independent still images.** Many generative defects are inconsistencies in time or in interaction. Real footage, however, often contains jump cuts, dropped frames, compression, motion blur, speed ramps, lens distortion, frame interpolation and stabilization. None alone indicates generation.

## Sampling and watch protocol

1. Inventory source duration, true stream frame rate/time base, codec, bitrate, pixel format, resolution, variable-frame-rate possibility, audio tracks and container timestamp/time offsets. Check source/origin. Do not assume `frame_number / nominal_fps` is exact presentation time for VFR footage.
2. Watch **the complete video at native timing with audio** for camera motion, lighting, edit rhythm and scene cuts. Mark transitions and any likely re-encoding discontinuities.
3. Build overview contact sheet (e.g. 8 to 16 time-distributed frames). Contact sheets are navigation aids, not temporal analysis.
4. For each incident window, inspect **consecutive native frames**, not just two widely separated thumbnails. Start with roughly 0.5 to 2 seconds around event, refine to consecutive frames / original PTS if tooling supports it. Show several frames before and after. Keep shot cut boundaries visible.
5. Replay at normal speed, then slowdown or frame-step without interpolation. Avoid artificially generated slow-motion frames for evidence. Identify whether a real object undergoes physically impossible metamorphosis or merely disocclusion, motion blur or codec corruption.
6. Where audio exists, test timing with independently aligned audio. A single fixed lag from post-production is a different issue from phoneme-dependent impossible articulations. Cross-check any drift against source mux offsets.

## Temporal anomaly matrix

| Family | Localizable question | Counterexample or confounder |
| --- | --- | --- |
| Identity/feature continuity | Does a persistent face, clothing item, object or logo change shape or design **within a continuous shot** independent of pose/lighting? | Occlusion, pose, autofocus, motion smear, makeup, offscreen wardrobe changes, cuts. |
| Hand-object contact | Does the same hand consistently grip a cup/mic, with plausible motion, pressure and occlusion? Does an object teleport while grasped? | Occluded transfer, fast movement, jump edit, shutter sampling. |
| Topology and shape | Do fingers, straps, doors, tools and backgrounds fuse/separate when they should be persistent solids? | Motion blur, compression ghosting, optical distortion, reflections. |
| Temporal reflections | Do specular highlights move with surface orientation, illumination and camera movement; do mirrors keep scene-consistent relative geometry? | Multi-light motion, curved glass, rolling reflections, camera cut. |
| Cast shadows/contact | Does apparent contact shadow track feet, furniture, hands, moving light sources? | Studio lights, relighting/VFX, projected moving lights. |
| Physical trajectories | Track acceleration/gravity, impact, splashes, smoke, cloth/wind, wheel rotation, tool contact and object mass. | Frame interpolation, fast shutter, staged motion, speed ramp, CGI/VFX. |
| Scene persistence | Do signs, windows, room elements and furniture remain spatially consistent during dolly/orbit? | Parallax, occlusion, stitched panoramic footage, changing view, hard cuts. |
| Camera realism | Are camera moves, rolling shutter, motion blur, lens distortion and image stabilization coherent with scene depth? | Phone computational video, gimbal stabilization, post warp, virtual cameras. |
| Lips and audio | Are specific phonemes temporally and physically plausible (labials, jaw opening, consonants) rather than just similar open-mouth motion? | Dubbing, latency, editorial slip, ADR, mouth obstruction, foreign-language dubbing. |
| Audio environment | Is room reverberation/noise bed continuous across speech and camera cuts where expected? | Noise reduction, voiceover, broadcast mic switching and mixing. |

## Incident protocol and evidence IDs

For each incident include `start_ms`, `end_ms`, and the **timeline reference** used; frame IDs or original presentation timestamps if available; location of defect on at least one frame; observed continuity violation; 2+ neighboring frames; normal capture alternatives; possible benign editing; and one reproduction method. Frame sampling timestamps from seeking are **requested** times, not necessarily actual decoded PTS; never claim exactness from a simple `-ss` extraction.

Use same-shot anchors such as a necklace knot, shirt button, wall line or reflection to establish identity continuity. If an entire shot changes its rendering, consider editorial treatment, CGI or style choice rather than automatically labeling AI.

## Video edge-case exercises

- A selfie shot moves past a mirror, revealing impossible geometry; check actual mirror orientation and camera/room layout, not an intuitively wrong mental model.
- Five consecutive frames show an earring vanishing through hair; hair occlusion may explain it. Track strand and edge masks before escalation.
- Interview video has lip delay of 120 ms; check demux/mux and editorial offsets first. A consistent shift is not AI evidence.
- Camera-pan scene has bent building lines; check rolling shutter, wide-angle distortion and stabilization first.
- Face deforms only on B-frames at very low bitrate; compare original/high-quality master before attributing synthesis.
- Product commercial contains fully CG environments; classify as visually created/CGI if documented, not AI-generated just because the camera is virtual.
- A short clip has no anomalies; final origin result remains `no_ai_evidence_found` or `indeterminate`, never `confirmed_real`.

## Escalation

When anomalies may affect legal, financial, personal safety, identity or public credibility decisions, seek original master, editing project, provenance chain and trained media forensic analyst. A detector's per-frame heatmap, embedding distance or face-swap score is a *hypothesis*, not sufficient origin proof without dataset-specific calibration and independently checked provenance.
