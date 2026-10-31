import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from render import check_project, render

class ShortsRenderingTests(unittest.TestCase):
    def test_reject_unbounded_script(self):
        with self.assertRaisesRegex(ValueError,"12"):
            check_project({"channel":"Test","scenes":[{"headline":"Hi","seconds":2}]*13})
    def test_reject_blank_headline(self):
        with self.assertRaisesRegex(ValueError,"headline"):
            check_project({"channel":"Test","scenes":[{"headline":"","seconds":2}]})
    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg unavailable")
    def test_real_h264_mp4_is_produced(self):
        sample={"channel":"SSAG Original QA","title":"Sample", "size":"360x640",
                "scenes":[{"headline":"Real video output","body":"Not a simulation.","seconds":2},
                          {"headline":"Ready to review","body":"Human approval remains required.","seconds":2}]}
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"actual-video.mp4"
            result=render(sample,out,voice=False)
            self.assertEqual(result["status"],"REAL_MP4_RENDERED")
            self.assertEqual(result["scenes"],2)
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size,1024)
            self.assertEqual(result["size"],"360x640")

if __name__=="__main__": unittest.main()
