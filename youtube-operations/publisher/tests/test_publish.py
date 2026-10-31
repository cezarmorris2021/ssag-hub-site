import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publish import validate_manifest

def manifest():
    return dict(title="Owner-approved original video",description="This is an original educational example",tags=["original","tutorial"],
       channel_id="UC1234567890123456789012",channel_verified=True,approved=True,
       rights_confirmed=True,made_for_kids=False,contains_synthetic_media=False)

class UploadSafetyTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.video=Path(self.dir.name)/"test.mp4"
        self.video.write_bytes(b"not an upload"*200)
    def tearDown(self):
        self.dir.cleanup()
    def test_approved_package_is_private_first(self):
        m=manifest();p=validate_manifest(m,self.video)
        self.assertEqual(p["status"]["privacyStatus"],"private")
        self.assertEqual(p["status"]["selfDeclaredMadeForKids"],False)
    def test_owner_approval_required(self):
        m=manifest();m["approved"]=False
        with self.assertRaisesRegex(ValueError,"approval"):validate_manifest(m,self.video)
    def test_rights_required(self):
        m=manifest();m["rights_confirmed"]=False
        with self.assertRaisesRegex(ValueError,"Rights"):validate_manifest(m,self.video)
    def test_channel_identity_required(self):
        m=manifest();m["channel_verified"]=False
        with self.assertRaisesRegex(ValueError,"destination"):validate_manifest(m,self.video)
    def test_no_video_is_invalid(self):
        m=manifest()
        with self.assertRaisesRegex(ValueError,"real local video"):validate_manifest(m,Path(self.dir.name)/"absent.mp4")
    def test_schedule_must_be_future(self):
        m=manifest();m["publish_at"]=(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(ValueError,"future"):validate_manifest(m,self.video)
    def test_timezone_must_be_explicit(self):
        m=manifest();m["publish_at"]="2027-01-01T09:00:00"
        with self.assertRaisesRegex(ValueError,"timezone"):validate_manifest(m,self.video)
    def test_youtube_title_length_is_limited(self):
        m=manifest();m["title"]="T"*101
        with self.assertRaisesRegex(ValueError,"100"):validate_manifest(m,self.video)
    def test_synthetic_media_selection_is_explicit(self):
        m=manifest();m.pop("contains_synthetic_media")
        with self.assertRaisesRegex(ValueError,"synthetic"):validate_manifest(m,self.video)

if __name__=="__main__":unittest.main()
