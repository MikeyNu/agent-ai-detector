import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import inspect_incident as incident  # noqa: E402


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe required")
class IncidentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_video(self, start_offset: int = 0) -> Path:
        src = self.root / f"offset_{start_offset}.mp4"
        # Video with 10 frames per second, with optional stream start timestamp.
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=96x64:rate=10:duration=2",
                        "-vf", "setpts=PTS+2/TB" if start_offset else "null", "-c:v", "mpeg4", "-pix_fmt", "yuv420p", str(src)], capture_output=True, check=True)
        return src

    def test_adjacent_decoded_frames_have_actual_pts_and_native_crops(self):
        src = self.make_video()
        result = incident.extract_incident(src, self.root / "incident", 0.5, 1.2, 20, (4, 4, 20, 12))
        self.assertEqual(result["origin_classification"], "not_attempted")
        self.assertEqual(result["decoded_pts_status"], "parsed_from_showinfo")
        self.assertEqual(result["frame_count"], 7)
        self.assertEqual(result["frames"][0]["decoded_pts_seconds"], 0.5)
        self.assertTrue(all(0.5 <= frame["relative_to_stream_start_seconds"] < 1.2 for frame in result["frames"]))
        out = self.root / "incident"
        self.assertTrue((out / "consecutive_frames_sheet_derived.png").exists())
        self.assertTrue((out / "consecutive_region_sheet_derived.png").exists())
        self.assertTrue((out / "region_00001_native.png").exists())
        self.assertEqual(json.loads((out / "incident.json").read_text())["frame_count"], 7)

    def test_nonzero_stream_origin_keeps_relative_time_separate(self):
        src = self.make_video(start_offset=2)
        result = incident.extract_incident(src, self.root / "offset", 0.5, 1.2, 20)
        self.assertEqual(result["video_stream_start_pts_seconds"], 2)
        self.assertEqual(result["frames"][0]["decoded_pts_seconds"], 2.5)
        self.assertEqual(result["frames"][0]["relative_to_stream_start_seconds"], 0.5)

    def test_reject_bad_window_and_outside_source_crop(self):
        src = self.make_video()
        with self.assertRaisesRegex(ValueError, "window"):
            incident.extract_incident(src, self.root / "bad", 1.2, 0.5, 10)
        with self.assertRaisesRegex(ValueError, "exceeds"):
            incident.extract_incident(src, self.root / "badcrop", 0.5, 0.9, 10, (100, 10, 20, 10))


if __name__ == "__main__":
    unittest.main()
