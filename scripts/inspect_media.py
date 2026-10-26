#!/usr/bin/env python3
"""Read-only forensic media inventory and contact-sheet preparation.

No AI detector is run. No file or tag is interpreted as an authenticity verdict.
Frames are requested at approximate times, not reported as exact decoded PTS.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import warnings

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError as exc:
    raise SystemExit("Pillow is required: python -m pip install -r requirements.txt") from exc

Image.MAX_IMAGE_PIXELS = 75_000_000
warnings.simplefilter("error", Image.DecompressionBombWarning)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".gif", ".heic", ".heif"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mts"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg", ".opus", ".aiff"}
EXIF_FIELDS = {"Make", "Model", "Software", "DateTime", "DateTimeOriginal", "DateTimeDigitized", "Orientation", "LensModel", "ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], timeout: int = 45) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(command, capture_output=True, check=False, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Tool timed out: {Path(command[0]).name}") from exc


def parse_crop(text: str) -> tuple[int, int, int, int]:
    try:
        numbers = tuple(int(x.strip()) for x in text.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Crop must be integer x,y,width,height") from exc
    if len(numbers) != 4 or numbers[0] < 0 or numbers[1] < 0 or numbers[2] <= 0 or numbers[3] <= 0:
        raise argparse.ArgumentTypeError("Crop must be nonnegative x/y and positive width/height")
    return numbers  # type: ignore[return-value]


def classify(path: Path) -> str:
    if path.suffix.lower() in IMAGE_SUFFIXES:
        return "image"
    if path.suffix.lower() in VIDEO_SUFFIXES:
        return "video"
    if path.suffix.lower() in AUDIO_SUFFIXES:
        return "audio"
    # Unusual image extension: sniff only if Pillow can open.
    try:
        with Image.open(path) as sample:
            sample.verify()
        return "image"
    except (OSError, ValueError, SyntaxError):
        raise ValueError("Unrecognized file type; use a supported image, video or audio extension") from None


def exif_summary(img: Image.Image) -> dict[str, str]:
    from PIL.ExifTags import TAGS
    results: dict[str, str] = {}
    try:
        for code, value in img.getexif().items():
            field = TAGS.get(code, str(code))
            if field in EXIF_FIELDS:
                results[field] = str(value)[:200]
    except (OSError, ValueError, TypeError):
        pass
    return results


def validate_bbox(bbox: tuple[int, int, int, int], width: int, height: int) -> None:
    x, y, w, h = bbox
    if x + w > width or y + h > height:
        raise ValueError(f"Crop {bbox} exceeds the oriented original's {width}x{height} pixels")


def make_contact_sheet(images: list[tuple[str, Path]], output: Path, *, tile_w: int = 360, tile_h: int = 248, cols: int = 3) -> None:
    if not images:
        return
    cols = min(cols, len(images))
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    for index, (label, filename) in enumerate(images):
        with Image.open(filename) as img:
            tile = ImageOps.contain(img.convert("RGB"), (tile_w - 16, tile_h - 37), Image.Resampling.LANCZOS)
        pos_x = (index % cols) * tile_w
        pos_y = (index // cols) * tile_h
        sheet.paste(tile, (pos_x + (tile_w - tile.width) // 2, pos_y + 5))
        draw.text((pos_x + 8, pos_y + tile_h - 26), label[:48], fill="#111111")
    sheet.save(output)


def inspect_image(path: Path, out: Path, crops: list[tuple[int, int, int, int]]) -> dict:
    with Image.open(path) as original:
        summary = {
            "original_format": original.format,
            "original_size": list(original.size),
            "source_animated": bool(getattr(original, "is_animated", False)),
            "source_frame_count": int(getattr(original, "n_frames", 1)),
            "exif_whitelist_no_gps": exif_summary(original),
            "metadata_keys_present": sorted(str(k) for k in original.info if k not in {"exif", "icc_profile", "xmp"}),
            "icc_profile_present": "icc_profile" in original.info,
        }
        # Preserve original source; orientation is applied only to derivatives.
        oriented = ImageOps.exif_transpose(original)
        oriented.load()
        if oriented.width * oriented.height > 75_000_000:
            raise ValueError("Image exceeds the 75-megapixel safety limit")
        rgb = oriented.convert("RGB")
    width, height = rgb.size
    summary["oriented_pixel_size"] = [width, height]
    for crop in crops:
        validate_bbox(crop, width, height)
    reduced = ImageOps.contain(rgb, (1600, 1200), Image.Resampling.LANCZOS)
    preview = reduced.copy()
    draw = ImageDraw.Draw(preview)
    for index, (x, y, w, h) in enumerate(crops, 1):
        box = [round(v) for v in (x * preview.width / width, y * preview.height / height, (x + w) * preview.width / width, (y + h) * preview.height / height)]
        draw.rectangle(box, outline="#fa3e2a", width=2)
        draw.text((box[0] + 2, max(0, box[1] - 13)), f"R{index:02d}", fill="#b52010")
    preview.save(out / "overview_derived.png")
    summary["derived_overview"] = "overview_derived.png"
    summary["crops"] = []
    for index, (x, y, w, h) in enumerate(crops, 1):
        native = rgb.crop((x, y, x + w, y + h))
        basename = f"crop_{index:02d}_native.png"
        native.save(out / basename)
        # Nearest-neighbor merely duplicates pixels. Do not upscale with generative AI.
        enlarged_name = None
        if w * h <= 1_500_000:
            enlarged = native.resize((w * 4, h * 4), Image.Resampling.NEAREST)
            enlarged_name = f"crop_{index:02d}_nearest4x.png"
            enlarged.save(out / enlarged_name)
        summary["crops"].append({"id": f"R{index:02d}", "bbox_xywh": [x, y, w, h], "native_file": basename, "nearest_neighbor_preview": enlarged_name, "warning": "Enlargement skipped for memory safety" if not enlarged_name else "Pixel replication only; not added detail"})
    return summary


def probe(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        return {"status": "unavailable", "note": "ffprobe not installed; no codec analysis performed"}
    result = run(["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe,data", "-print_format", "json", "-show_format", "-show_streams", str(path)], timeout=45)
    if result.returncode != 0:
        return {"status": "failed", "error": result.stderr.decode("utf-8", "replace")[:1000]}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "unparseable"}
    stream_fields = {"index", "start_time", "codec_type", "codec_name", "width", "height", "avg_frame_rate", "r_frame_rate", "time_base", "duration", "nb_frames", "pix_fmt", "sample_rate", "channels", "channel_layout", "sample_fmt", "bit_rate", "color_primaries", "color_transfer", "field_order"}
    result_streams = [{key: item[key] for key in stream_fields if key in item} for item in data.get("streams", [])]
    fmt = data.get("format", {})
    return {"status": "available", "container": {key: fmt[key] for key in ("format_name", "start_time", "duration", "bit_rate", "size") if key in fmt}, "streams": result_streams, "tags_omitted_for_privacy": True}


def inspect_video(path: Path, out: Path, frame_count: int, metadata: dict) -> dict:
    if not shutil.which("ffmpeg"):
        return {"status": "unavailable", "note": "ffmpeg not installed; no frames extracted"}
    if metadata.get("status") != "available":
        return {"status": "unavailable", "note": "Valid ffprobe metadata required to sample video"}
    video_streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        return {"status": "no_video_stream"}
    try:
        duration = float(metadata.get("container", {}).get("duration", "0"))
    except (TypeError, ValueError):
        duration = 0.0
    if not 0 < duration < 24 * 60 * 60:
        return {"status": "duration_unavailable", "note": "No valid bounded duration; manual inspection needed"}
    samples = []
    frames_for_sheet: list[tuple[str, Path]] = []
    for idx in range(frame_count):
        # Seek away from final end-of-file; times are requested, not decoded PTS.
        requested = min(max(0.0, duration * (idx + 0.5) / frame_count), max(0, duration - 0.025))
        filename = f"frame_{idx + 1:02d}_requested_{requested:.3f}s.png"
        dest = out / filename
        proc = run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-protocol_whitelist", "file,pipe,data", "-ss", f"{requested:.6f}", "-i", str(path), "-map", "0:v:0", "-frames:v", "1", str(dest)], timeout=40)
        row = {"requested_seek_seconds": round(requested, 6), "actual_decoded_pts": None, "exact_pts_verified": False}
        if proc.returncode == 0 and dest.exists() and dest.stat().st_size:
            row["derived_frame"] = filename
            frames_for_sheet.append((f"request {requested:.2f}s", dest))
        else:
            row["error"] = proc.stderr.decode("utf-8", "replace")[:260] or "Frame not decoded"
        samples.append(row)
    if frames_for_sheet:
        make_contact_sheet(frames_for_sheet, out / "video_contact_sheet_derived.png")
    return {"status": "sampled" if frames_for_sheet else "failed", "sample_count": len(frames_for_sheet), "samples": samples, "derived_contact_sheet": "video_contact_sheet_derived.png" if frames_for_sheet else None, "warning": "Seeking approximates requested time; actual decoded presentation timestamps were not measured. A contact sheet is not continuous-frame verification."}


def inspect_audio(path: Path, out: Path, metadata: dict) -> dict:
    if not shutil.which("ffmpeg") or metadata.get("status") != "available":
        return {"status": "unavailable", "note": "ffmpeg and valid ffprobe inventory required"}
    streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
    if not streams:
        return {"status": "no_audio_stream"}
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-protocol_whitelist", "file,pipe,data", "-i", str(path), "-map", "0:a:0", "-t", "60", "-ac", "1", "-ar", "8000", "-f", "s16le", "pipe:1"]
    proc = run(command, timeout=45)
    if proc.returncode != 0 or not proc.stdout:
        return {"status": "failed", "error": proc.stderr.decode("utf-8", "replace")[:400]}
    values = array("h")
    values.frombytes(proc.stdout[: len(proc.stdout) // 2 * 2])
    if sys.byteorder != "little":
        values.byteswap()
    if not values:
        return {"status": "failed", "error": "No audio samples"}
    canvas = Image.new("RGB", (1200, 320), "#f7f7f7")
    draw = ImageDraw.Draw(canvas)
    draw.line((0, 160, 1199, 160), fill="#aaaaaa")
    count = len(values)
    for column in range(1200):
        start = column * count // 1200
        end = max(start + 1, (column + 1) * count // 1200)
        segment = values[start:min(end, count)]
        if not segment:
            continue
        lo, hi = min(segment), max(segment)
        draw.line((column, 160 - hi / 32768 * 145, column, 160 - lo / 32768 * 145), fill="#333333")
    canvas.save(out / "waveform_first_60s_derived.png")
    return {"status": "preview_created", "source_stream": streams[0].get("index"), "audio_seconds_previewed": round(len(values) / 8000, 3), "derived_waveform": "waveform_first_60s_derived.png", "warning": "Downmixed, resampled waveform is a navigation aid, not original PCM or a deepfake detector."}


def inspect_c2pa(path: Path, out: Path) -> dict:
    if not shutil.which("c2patool"):
        return {"status": "not_checked", "note": "c2patool unavailable; missing check is not evidence of origin"}
    proc = run(["c2patool", str(path)], timeout=45)
    if proc.returncode != 0:
        return {"status": "tool_error_or_no_manifest", "note": proc.stderr.decode("utf-8", "replace")[:500], "warning": "Cannot infer AI or camera origin"}
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"status": "unparseable_report", "warning": "No provenance conclusion"}
    (out / "c2pa_raw_report.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "raw_report_saved", "file": "c2pa_raw_report.json", "warning": "Manifest report presence is NOT independent trust and content-binding validation. Examine validity, issuer and trusted certificates separately."}


def prepare(args: argparse.Namespace) -> dict:
    path = args.input.expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("Input must be a local regular file")
    out = args.out.expanduser().resolve()
    if out == path or path in out.parents:
        raise ValueError("Output directory cannot be the input file or inside it")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("Output directory already exists and is not empty; choose a new location")
    if args.frames < 2 or args.frames > 16:
        raise ValueError("Frames must be between 2 and 16")
    media_type = classify(path)
    if media_type != "image" and args.crop:
        raise ValueError("--crop is only supported for still images; extract a video frame first")
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0",
        "read_only_analysis": True,
        "origin_classification": "not_attempted",
        "visual_inspection_performed_by_script": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input": {"file_name": path.name, "media_type": media_type, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)},
        "tool_availability": {tool: bool(shutil.which(tool)) for tool in ("ffmpeg", "ffprobe", "c2patool")},
        "derivatives_are_not_evidence_of_origin": True,
        "limitations": ["No generative-origin classifier was run", "Derived previews may hide or introduce resampling artifacts", "Raw C2PA reports require separate trust and signature adjudication"],
    }
    if media_type == "image":
        report["image"] = inspect_image(path, out, args.crop)
        if report["image"]["source_animated"]:
            report["limitations"].append("Animated image: this script inspected the first frame only; temporal review required")
    else:
        report["ffprobe"] = probe(path)
        if media_type == "video":
            report["video"] = inspect_video(path, out, args.frames, report["ffprobe"])
        report["audio"] = inspect_audio(path, out, report["ffprobe"])
    report["c2pa"] = inspect_c2pa(path, out)
    (out / "inspection.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare forensic inspection aids without classifying AI or authenticity")
    parser.add_argument("input", type=Path, help="Unmodified local input image, video or audio file")
    parser.add_argument("--out", required=True, type=Path, help="New or empty evidence output directory")
    parser.add_argument("--frames", type=int, default=8, help="Video overview frames, 2..16 (not consecutive-frame analysis)")
    parser.add_argument("--crop", type=parse_crop, action="append", default=[], help="Image region in oriented original pixels: x,y,width,height; repeatable")
    args = parser.parse_args(argv)
    try:
        report = prepare(args)
    except (OSError, ValueError, RuntimeError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "prepared_not_classified", "sha256": report["input"]["sha256"], "type": report["input"]["media_type"], "report": str(args.out / "inspection.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
