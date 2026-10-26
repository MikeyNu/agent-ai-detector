"""Engineering tests. These are NOT a dataset-based deepfake detection benchmark."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import inspect_media as media  # noqa: E402


class ImagePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_image_hash_and_native_crop_are_exact_and_source_is_immutable(self):
        source = self.root / "portrait.png"
        img = Image.new("RGB", (32, 24), (80, 100, 120))
        img.putpixel((8, 9), (200, 1, 3))
        img.save(source)
        before = source.read_bytes()
        out = self.root / "analysis"
        args = media.argparse.Namespace(input=source, out=out, frames=8, crop=[(6, 7, 6, 6)])
        report = media.prepare(args)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(report["input"]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(report["origin_classification"], "not_attempted")
        self.assertFalse(report["visual_inspection_performed_by_script"])
        self.assertEqual(report["image"]["crops"][0]["bbox_xywh"], [6, 7, 6, 6])
        with Image.open(out / "crop_01_native.png") as crop:
            self.assertEqual(crop.getpixel((2, 2)), (200, 1, 3))
        with Image.open(out / "crop_01_nearest4x.png") as enlarged:
            self.assertEqual(enlarged.size, (24, 24))
            self.assertEqual(enlarged.getpixel((8, 8)), (200, 1, 3))
        self.assertTrue((out / "overview_derived.png").exists())
        self.assertEqual(json.loads((out / "inspection.json").read_text())["origin_classification"], "not_attempted")

    def test_exif_orientation_affects_bbox_coordinates_not_original(self):
        source = self.root / "phone.jpg"
        img = Image.new("RGB", (40, 20), "white")
        exif = Image.Exif()
        exif[274] = 6  # 90 degree rotation on presentation
        img.save(source, exif=exif)
        before = source.read_bytes()
        report = media.prepare(media.argparse.Namespace(input=source, out=self.root / "oriented", frames=8, crop=[(0, 0, 5, 5)]))
        self.assertEqual(report["image"]["original_size"], [40, 20])
        self.assertEqual(report["image"]["oriented_pixel_size"], [20, 40])
        self.assertEqual(source.read_bytes(), before)

    def test_out_of_bounds_crop_fails_without_claiming_result(self):
        source = self.root / "example.png"
        Image.new("RGB", (20, 30)).save(source)
        args = media.argparse.Namespace(input=source, out=self.root / "oob", frames=8, crop=[(19, 19, 9, 9)])
        with self.assertRaisesRegex(ValueError, "exceeds"):
            media.prepare(args)
        self.assertFalse((self.root / "oob" / "inspection.json").exists())

    def test_preserve_existing_outputs_and_reject_paths(self):
        source = self.root / "example.png"
        Image.new("RGB", (20, 20)).save(source)
        out = self.root / "out"
        out.mkdir()
        (out / "important.txt").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "not empty"):
            media.prepare(media.argparse.Namespace(input=source, out=out, frames=8, crop=[]))
        self.assertEqual((out / "important.txt").read_text(), "preserve")
        with self.assertRaisesRegex(ValueError, "Frames"):
            media.prepare(media.argparse.Namespace(input=source, out=self.root / "other", frames=25, crop=[]))

    def test_crop_parser_rejects_bad_shapes_and_negative_values(self):
        for text in ("1,2,3", "-1,0,12,13", "0,0,0,1", "0,1,2,foo", "1.2,3,4,5"):
            with self.subTest(text=text), self.assertRaises(media.argparse.ArgumentTypeError):
                media.parse_crop(text)
        self.assertEqual(media.parse_crop("0, 2, 3, 7"), (0, 2, 3, 7))

    def test_missing_c2pa_is_unknown_not_negative_evidence(self):
        p = self.root / "image.png"
        Image.new("RGB", (10, 10)).save(p)
        with patch.object(media.shutil, "which", return_value=None):
            report = media.prepare(media.argparse.Namespace(input=p, out=self.root / "no_tools", frames=8, crop=[]))
        self.assertEqual(report["c2pa"]["status"], "not_checked")
        self.assertEqual(report["origin_classification"], "not_attempted")

    def test_unknown_file_rejected(self):
        bad = self.root / "blob.bin"
        bad.write_bytes(b"not a supported image/video/audio")
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            media.classify(bad)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe required")
class VideoAudioPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_video_has_seek_uncertainty_not_fabricated_pts(self):
        src = self.root / "clip.mp4"
        cmd = ["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=64x48:r=8:d=1.2", "-c:v", "mpeg4", "-pix_fmt", "yuv420p", str(src)]
        subprocess.run(cmd, check=True, capture_output=True)
        report = media.prepare(media.argparse.Namespace(input=src, out=self.root / "videoout", frames=3, crop=[]))
        self.assertEqual(report["input"]["media_type"], "video")
        self.assertEqual(report["video"]["status"], "sampled")
        self.assertEqual(report["video"]["sample_count"], 3)
        for sample in report["video"]["samples"]:
            self.assertIsNone(sample["actual_decoded_pts"])
            self.assertFalse(sample["exact_pts_verified"])
        self.assertEqual(report["origin_classification"], "not_attempted")
        self.assertTrue((self.root / "videoout" / "video_contact_sheet_derived.png").exists())

    def test_sine_audio_waveform_does_not_claim_fake(self):
        src = self.root / "tone.wav"
        cmd = ["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", str(src)]
        subprocess.run(cmd, check=True, capture_output=True)
        report = media.prepare(media.argparse.Namespace(input=src, out=self.root / "audioout", frames=8, crop=[]))
        self.assertEqual(report["audio"]["status"], "preview_created")
        self.assertTrue((self.root / "audioout" / "waveform_first_60s_derived.png").exists())
        self.assertEqual(report["origin_classification"], "not_attempted")

    def test_video_crop_flag_is_rejected(self):
        src = self.root / "clip.mp4"
        src.write_bytes(b"invalid mp4")
        with self.assertRaisesRegex(ValueError, "still images"):
            media.prepare(media.argparse.Namespace(input=src, out=self.root / "x", frames=8, crop=[(0, 0, 3, 3)]))


if __name__ == "__main__":
    unittest.main()
