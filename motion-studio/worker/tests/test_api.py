import os
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

# No real uploads, customer likenesses, or GPU models in these unit tests.
os.environ["SSAG_API_KEY"] = "test-owner-key-never-use-in-production-123456789"
_TEMP = tempfile.TemporaryDirectory()
os.environ["SSAG_PRIVATE_STORAGE"] = _TEMP.name
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import server


class MotionStudioApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.api)
        cls.key = {"X-SSAG-Key": os.environ["SSAG_API_KEY"]}

    def test_liveness_does_not_claim_render_ready(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["video_claim"], "unverified")

    def test_status_requires_owner_secret(self):
        self.assertEqual(self.client.get("/api/status").status_code, 401)
        self.assertEqual(self.client.get("/api/status", headers={"X-SSAG-Key":"wrong"}).status_code, 401)

    def test_engine_reports_prerequisites_not_simulation(self):
        r = self.client.get("/api/status", headers=self.key)
        self.assertEqual(r.status_code, 200)
        s = r.json()
        self.assertIn("engine_installed", s)
        self.assertIn("gpu_ready", s)
        self.assertIn("render_ready", s)
        self.assertEqual(s["render_ready"], s["engine_installed"] and s["gpu_ready"] and s["ffmpeg_installed"])

    def test_job_not_accepted_without_real_gpu(self):
        original = server.engine_state
        server.engine_state = lambda: {"render_ready":False}
        try:
            r = self.client.post("/api/jobs", headers=self.key, files={
                "photo":("test.png", b"not an image", "image/png"),
                "dance":("test.mp4", b"not a video", "video/mp4"),
            }, data={"consent":"true"})
            self.assertEqual(r.status_code, 503)
            self.assertIn("No files accepted", r.json()["detail"])
        finally:
            server.engine_state = original

    def test_explicit_deletion_removes_private_job(self):
        job_id = str(uuid.uuid4())
        folder = Path(_TEMP.name) / job_id
        folder.mkdir()
        (folder/"innocuous.txt").write_text("test only")
        with server.database() as db:
            db.execute(
                "INSERT INTO jobs(id,status,message,error,created,updated) VALUES(?,?,?,?,?,?)",
                (job_id, "failed", "test", "", time.time(), time.time()))
        r = self.client.delete("/api/jobs/"+job_id, headers=self.key)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(folder.exists())
        self.assertEqual(self.client.get("/api/jobs/"+job_id,headers=self.key).status_code,404)

if __name__=="__main__":
    unittest.main()
