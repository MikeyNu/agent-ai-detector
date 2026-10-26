#!/usr/bin/env python3
"""Extract consecutive actual decoded video frames with their ffmpeg showinfo PTS.

A focused navigation aid for human temporal inspection, NOT an AI detector.
The source stays unmodified and frame timestamps are recorded only when matched
against decoder showinfo. The filter always uses original stream timing.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys

from PIL import Image

from inspect_media import classify, make_contact_sheet, run, sha256_file, validate_bbox, probe

PTS_RE = re.compile(r"\bpts_time:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))")


def extract_incident(source: Path, destination: Path, start: float, end: float, max_frames: int, crop: tuple[int, int, int, int] | None = None) -> dict:
    source = source.expanduser().resolve(strict=True)
    destination = destination.expanduser().resolve()
    if not source.is_file() or classify(source) != "video":
        raise ValueError("Input must be a supported local video file")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("Both ffmpeg and ffprobe must be installed")
    if not (0 <= start < end and end - start <= 20):
        raise ValueError("Use 0 <= --from-s < --to-s with a window <= 20 seconds")
    if max_frames < 2 or max_frames > 120:
        raise ValueError("max-frames must be between 2 and 120")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Destination exists and is not empty")
    info = probe(source)
    if info.get("status") != "available":
        raise RuntimeError("ffprobe could not inventory video stream")
    video_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        raise ValueError("Media contains no video stream")
    try:
        timeline_origin = float(video_streams[0].get("start_time", info.get("container", {}).get("start_time", 0)))
    except (TypeError, ValueError):
        timeline_origin = 0.0
    try:
        duration = float(info.get("container", {}).get("duration", "nan"))
    except (ValueError, TypeError):
        duration = float("nan")
    if duration > 0 and start >= duration:
        raise ValueError("Start time is beyond video duration")
    destination.mkdir(parents=True, exist_ok=True)
    # Decode around requested region, preserving input timestamps after faster seek.
    seek = max(0.0, start - 1.5)
    # Escaped commas are filter-graph syntax, NOT a shell command.
    # Half-open interval [start, end); filter t is absolute stream PTS.
    absolute_start, absolute_end = start + timeline_origin, end + timeline_origin
    select_filter = f"select=gte(t\\,{absolute_start:.6f})*lt(t\\,{absolute_end:.6f}),showinfo"
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info", "-protocol_whitelist", "file,pipe,data",
               "-ss", f"{seek:.6f}", "-copyts", "-i", str(source), "-map", "0:v:0", "-vf", select_filter,
               "-fps_mode", "passthrough", "-frames:v", str(max_frames), str(destination / "frame_%05d.png")]
    result = run(command, timeout=120)
    if result.returncode != 0:
        raise RuntimeError("ffmpeg extraction failed: " + result.stderr.decode("utf-8", "replace")[-600:])
    paths = sorted(destination.glob("frame_*.png"))
    if not paths:
        raise RuntimeError("No frames could be extracted for that time interval")
    # showinfo emits exactly one matching line for each passing frame if supported.
    pts = [float(match.group(1)) for line in result.stderr.decode("utf-8", "replace").splitlines()
           if "showinfo" in line for match in PTS_RE.finditer(line)]
    trusted_pts = len(pts) == len(paths)
    frames = []
    contact = []
    cropped_contact = []
    for idx, file in enumerate(paths):
        exact_pts = pts[idx] if trusted_pts else None
        frames.append({"frame_file": file.name, "decoded_pts_seconds": exact_pts, "relative_to_stream_start_seconds": round(exact_pts - timeline_origin, 6) if exact_pts is not None else None, "pts_from_decoder": trusted_pts})
        contact.append((f"{exact_pts:.3f}s" if exact_pts is not None else f"frame {idx + 1}", file))
        if crop:
            with Image.open(file) as im:
                validate_bbox(crop, *im.size)
                x, y, w, h = crop
                region = im.crop((x, y, x+w, y+h))
                dest = destination / f"region_{idx + 1:05d}_native.png"
                region.save(dest)
            cropped_contact.append((f"{exact_pts:.3f}s" if exact_pts is not None else f"frame {idx + 1}", dest))
    make_contact_sheet(contact, destination / "consecutive_frames_sheet_derived.png", cols=4)
    if cropped_contact:
        make_contact_sheet(cropped_contact, destination / "consecutive_region_sheet_derived.png", cols=4)
    data = {
        "schema_version": "1.0", "created_utc": datetime.now(timezone.utc).isoformat(),
        "origin_classification": "not_attempted", "source_filename": source.name, "source_sha256": sha256_file(source),
        "requested_from_seconds": start, "requested_to_seconds_exclusive": end, "video_stream_start_pts_seconds": timeline_origin, "frame_count": len(frames),
        "frames": frames, "decoded_pts_status": "parsed_from_showinfo" if trusted_pts else "unavailable",
        "truncated_by_frame_limit": len(frames) == max_frames,
        "crop_bbox_xywh": list(crop) if crop else None,
        "warnings": ["Derived PNG frames and contact sheets are NOT origin evidence without interpretation.",
                     "Timestamp accuracy depends on source PTS/time base; seek and VFR metadata should be checked.",
                     "If frame limit was reached, later frames in the requested interval may be omitted."],
    }
    (destination / "incident.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Inspect native adjacent video frames; no AI origin prediction")
    p.add_argument("input", type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--from-s", dest="start", type=float, required=True)
    p.add_argument("--to-s", dest="end", type=float, required=True)
    p.add_argument("--max-frames", type=int, default=60)
    from inspect_media import parse_crop
    p.add_argument("--crop", type=parse_crop, default=None, help="Optional constant frame region x,y,w,h in source pixels")
    a = p.parse_args(argv)
    try:
        result = extract_incident(a.input, a.out, a.start, a.end, a.max_frames, a.crop)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "incident_prepared_not_classified", "frames": result["frame_count"], "pts_status": result["decoded_pts_status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
