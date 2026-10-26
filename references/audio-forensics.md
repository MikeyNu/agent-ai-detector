# Audio forensic triage and synthesis artifact QA

The audio lane covers text-to-speech, voice conversion, voice cloning, overdubs and mixtures with real microphones. Subjective human listening alone is not sufficiently reliable for source identification. Handle voice data as sensitive; do not identify speakers, construct a voiceprint, or infer identity from the recording.

## Pass sequence

1. Obtain the unmodified source if available. Record SHA-256, codec, sample rate, channels, duration, loudness pipeline if known and any obvious packet loss/codec artifacts.
2. Listen in full context at original speed with good monitoring. Identify edits, channel switching, voiceover vs dialog, reverberant environments and possible dubbing.
3. Select *time-bounded* segments of concern with independent countersegments. Listen again to both and, if possible, inspect waveform/spectrogram. A waveform is visualization, **not** a deepfake detector.
4. Audit: phoneme articulation and coarticulation; breath and room noise before/after phrases; pitch/intensity trajectories; timing of emotional emphasis; plosives/sibilants; nasal and fricative texture; reverberation tail; abrupt noise-floor edits; repetitions; language/phoneme specifics; multichannel phase coherence.
5. Distinguish audio **synthetic origin** from voice processing, denoising, pitch correction, broadcast compression, ADR, splicing, speakerphone codecs and a professionally performed read.
6. For video, inspect difficult-to-fake phonemes and mouth closure, but rule out translation dubbing, lip-sync postprocessing and constant track delay first.
7. Seek production files, an authenticated original recording or signed provenance. If using a specialized audio model, specify attack categories, training/evaluation domain, codec, false positive rate and adversarial tests.

## Candidate symptoms and false positives

| Observation | Possible AI-related mechanism | Non-AI alternative |
| --- | --- | --- |
| Repeated similar prosody over many semantically unrelated phrases | Template-like TTS cadence | Scripted broadcast reading, speech coaching, editing. |
| Over-smooth transitions or lack of audible breathing | Synthesis/overdenoising | Noise gate, close mic, careful editing, short recording. |
| Inconsistent voice timbre within a word or sharp transition | Voice conversion splice/model failure | Codec switching, edit boundary, mouth-to-mic distance. |
| Sibilants/fricatives sound watery/metallic | Vocoder limitations | Low-rate AAC/MP3, noise suppression, Bluetooth connection. |
| Room reverb tail does not match scene | Artificial voiceover or inconsistent resynthesis | ADR, acoustic treatment, post mix, mic switching. |
| Phoneme and mouth movements disagree | Audio/video generation or lip editing | Dubbing, mixing delay, loose AV mux, different take. |
| Breath pauses misaligned with long speech | Prosody/respiration generation failure | Edited breath removal, voice acting, short utterance. |

## Interpretation and reporting

ASVspoof 5 includes diverse speakers, attack methods and adversarial conditions, and reports degradation under neural compression and adversarial attacks. A detector calibrated only on clean studio speech can fail on real social or phone recordings. No score may be called a probability of AI origin without external calibration on the relevant data domain.

Report time range in milliseconds, audio stream index, listening observations and whether candidate gaps persist after higher-quality source comparison. Provide the exact **audible phenomenon**, not "the voice sounds robotic" alone. For music and effects, adapt checks to synthesized instruments and sample libraries; electronic instrumentation is not necessarily generative AI. The correct origin label may be `indeterminate`.

## Repair advice for authorized production

For natural-sounding synthetic or edited audio: improve script punctuation and phrase-level pacing, add realistic breath *only where physically appropriate*, avoid high-strength denoise/limiting, match room impulse/reverb and loudness, maintain consistent model voice and phoneme pronunciation, and re-record or re-render troublesome words. If depicted as human testimony, clearly disclose that the voice is synthetic or altered; do not create deceptive impersonations.
