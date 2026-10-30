"""SSAG Motion Studio: private GPU-backed job worker. No fake renders.

Run with one Uvicorn process. Deploy only behind HTTPS with a long API key
and a persistent private disk. Real video requires the external Motion Mirror
CLI, its model weights, ffmpeg and an NVIDIA CUDA GPU.
"""
from __future__ import annotations
import hmac
import os
import queue
import shutil
import sqlite3
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

APP_KEY = os.environ.get("SSAG_API_KEY", "")
if len(APP_KEY) < 24:
    raise RuntimeError("SSAG_API_KEY must be set to a random 24+ character value.")
ROOT = Path(os.environ.get("SSAG_PRIVATE_STORAGE", "./private_jobs")).expanduser().resolve()
ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
try:
    ROOT.chmod(0o700)
except OSError:
    pass
DB = ROOT / "queue.sqlite3"
TTL = 24 * 3600
MAX_PHOTO = 15 * 1024 * 1024
MAX_VIDEO = 80 * 1024 * 1024
ALLOWED_ORIGINS = [
    x.strip().rstrip("/")
    for x in os.environ.get(
        "SSAG_ALLOWED_ORIGINS", "https://cezarmorris2021.github.io"
    ).split(",") if x.strip()
]
q: queue.Queue[str] = queue.Queue()
api = FastAPI(title="SSAG Motion Studio GPU Worker", docs_url=None, redoc_url=None)
api.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["X-SSAG-Key", "Content-Type"],
)

@contextmanager
def database():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()

def init_db():
    with database() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS jobs (
           id TEXT PRIMARY KEY, status TEXT NOT NULL, message TEXT NOT NULL,
           error TEXT NOT NULL DEFAULT '', created REAL NOT NULL, updated REAL NOT NULL
        )""")
        db.execute(
            "UPDATE jobs SET status='failed', message='Interrupted by service restart.' "
            "WHERE status IN ('queued','processing')"
        )

def require_auth(x_ssag_key: str | None):
    if not x_ssag_key or not hmac.compare_digest(x_ssag_key, APP_KEY):
        raise HTTPException(status_code=401, detail="Invalid owner key")

def get_job(job_id: str):
    try:
        uuid.UUID(job_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid job ID")
    with database() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Job not found or expired")
        return dict(row)

def update_job(job_id: str, status: str, message: str, error: str = ""):
    with database() as db:
        db.execute("UPDATE jobs SET status=?, message=?, error=?, updated=? WHERE id=?",
                   (status, message, error[:600], time.time(), job_id))

def purge_expired():
    now = time.time()
    with database() as db:
        rows = db.execute(
            "SELECT id FROM jobs WHERE created < ? AND status != 'processing'", (now-TTL,)
        ).fetchall()
        for row in rows:
            shutil.rmtree(ROOT / row["id"], ignore_errors=True)
            db.execute("DELETE FROM jobs WHERE id=?", (row["id"],))

def cleanup_loop():
    # Enforce the 24-hour retention policy even if no one submits new jobs.
    while True:
        time.sleep(3600)
        try:
            purge_expired()
        except Exception:
            # Temporary database or filesystem error: retry next hour.
            pass

def engine_state():
    # Neither the presence of a Python package nor a web page alone proves readiness.
    executable = shutil.which("motion-mirror")
    ffmpeg = bool(shutil.which("ffmpeg"))
    try:
        check = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            check=False, timeout=6
        )
        nvidia = check.returncode == 0 and bool(check.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        nvidia = False
    # PyTorch CUDA must also see the device, or actual generation will fail.
    try:
        cuda = subprocess.run(
            ["python", "-c", "import torch; print(int(torch.cuda.is_available()))"],
            capture_output=True, text=True, timeout=12
        )
        nvidia = nvidia and cuda.returncode == 0 and cuda.stdout.strip() == "1"
    except (OSError, subprocess.TimeoutExpired):
        nvidia = False
    return {
        "engine": "motion-mirror", "engine_installed": bool(executable),
        "gpu_ready": nvidia, "ffmpeg_installed": ffmpeg,
        "render_ready": bool(executable and nvidia and ffmpeg),
        "note": "A live GPU job must succeed before SSAG can claim production readiness."
    }

def render_loop():
    while True:
        job_id = q.get()
        folder = ROOT / job_id
        try:
            with database() as db:
                row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None or row["status"] != "queued":
                continue
            update_job(job_id, "processing", "Rendering actual motion-transfer frames on CUDA.")
            out = folder / "rendered"
            out.mkdir(exist_ok=True)
            args = [
                "motion-mirror", "run", str(folder/"character.png"),
                str(folder/"motion.mp4"), "--backend", "wan-1.3b-vace",
                "--offload-model", "--t5-cpu", "--frames", "81",
                "--resolution", "480x832", "--output-dir", str(out)
            ]
            process = subprocess.run(
                args, cwd=str(folder), capture_output=True,
                text=True, timeout=3600
            )
            if process.returncode != 0:
                raise RuntimeError("Motion Mirror failed: " + (process.stderr or process.stdout)[-500:])
            candidates = sorted(out.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates or candidates[0].stat().st_size < 1024:
                raise RuntimeError("Renderer returned no nonempty MP4")
            shutil.move(str(candidates[0]), str(folder/"result.mp4"))
            update_job(job_id, "ready", "Real video rendered. Download MP4 before expiry.")
        except subprocess.TimeoutExpired:
            update_job(job_id, "failed", "Render timed out.", "GPU render exceeded one hour.")
        except Exception as e:
            update_job(job_id, "failed", "Renderer failed; no video has been produced.", str(e))
        finally:
            q.task_done()

init_db()
purge_expired()
threading.Thread(target=render_loop, name="ssag-gpu-worker", daemon=True).start()
threading.Thread(target=cleanup_loop, name="ssag-retention-cleanup", daemon=True).start()

@api.get("/health")
def health():
    return {"service": "SSAG Motion Studio", "status": "online", "video_claim": "unverified"}

@api.get("/api/status")
def status(x_ssag_key: str | None = Header(default=None)):
    require_auth(x_ssag_key)
    return engine_state()

async def save_limited(upload: UploadFile, target: Path, limit: int):
    written = 0
    with target.open("wb") as dst:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > limit:
                raise HTTPException(status_code=413, detail="File exceeds allowed size.")
            dst.write(chunk)
    if not written:
        raise HTTPException(status_code=400, detail="Empty upload")

@api.post("/api/jobs", status_code=202)
async def submit(
    photo: UploadFile = File(...), dance: UploadFile = File(...),
    consent: str = Form(...), x_ssag_key: str | None = Header(default=None)
):
    require_auth(x_ssag_key)
    if consent.lower() != "true":
        raise HTTPException(status_code=400, detail="Consent required")
    state = engine_state()
    if not state["render_ready"]:
        raise HTTPException(status_code=503, detail="CUDA/Motion Mirror worker not ready. No files accepted.")
    if photo.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=415, detail="Unsupported photo format")
    if dance.content_type not in ("video/mp4", "video/webm"):
        raise HTTPException(status_code=415, detail="Unsupported reference video format")
    purge_expired()
    job_id = str(uuid.uuid4())
    folder = ROOT / job_id
    folder.mkdir(mode=0o700)
    try:
        original_photo = folder / "original_image"
        original_video = folder / "original_video"
        await save_limited(photo, original_photo, MAX_PHOTO)
        await save_limited(dance, original_video, MAX_VIDEO)
        from PIL import Image, UnidentifiedImageError
        try:
            with Image.open(original_photo) as im:
                im.verify()
            with Image.open(original_photo) as im:
                if im.width * im.height > 24000000:
                    raise ValueError("Photo exceeds maximum pixel count")
                im.convert("RGB").save(folder/"character.png", format="PNG")
        except (UnidentifiedImageError, ValueError, OSError):
            raise HTTPException(status_code=400, detail="Invalid or oversized photo")
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_type", "-of", "default=nw=1",
             str(original_video)],
            capture_output=True, text=True, timeout=20
        )
        if probe.returncode != 0 or "codec_type=video" not in probe.stdout:
            raise HTTPException(status_code=400, detail="Invalid reference video")
        normalize = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(original_video), "-t", "5",
             "-vf", "fps=16,scale=480:-2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-movflags", "+faststart", str(folder/"motion.mp4")],
            capture_output=True, text=True, timeout=180
        )
        if normalize.returncode != 0:
            raise HTTPException(status_code=400, detail="Could not normalize reference clip")
        original_photo.unlink(missing_ok=True)
        original_video.unlink(missing_ok=True)
        now = time.time()
        with database() as db:
            db.execute("INSERT INTO jobs(id,status,message,error,created,updated) VALUES(?,?,?,?,?,?)",
                       (job_id,"queued","Waiting for CUDA worker.","",now,now))
        q.put(job_id)
        return {"id":job_id,"status":"queued","message":"Real GPU job queued"}
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise

@api.get("/api/jobs/{job_id}")
def job_status(job_id: str, x_ssag_key: str | None = Header(default=None)):
    require_auth(x_ssag_key)
    j = get_job(job_id)
    return {
        "id":j["id"], "status":j["status"],
        "message":j["message"],"error":j["error"],
        "created_at":datetime.fromtimestamp(j["created"], timezone.utc).isoformat(),
        "expires_at":datetime.fromtimestamp(j["created"]+TTL, timezone.utc).isoformat()
    }

@api.get("/api/jobs/{job_id}/download")
def download(job_id: str, x_ssag_key: str | None = Header(default=None)):
    require_auth(x_ssag_key)
    j = get_job(job_id)
    video = ROOT / j["id"] / "result.mp4"
    if j["status"] != "ready" or not video.is_file():
        raise HTTPException(status_code=409, detail="Video is not ready")
    return FileResponse(str(video), media_type="video/mp4", filename="ssag-motion-"+job_id+".mp4")

@api.delete("/api/jobs/{job_id}")
def delete_job(job_id: str, x_ssag_key: str | None = Header(default=None)):
    require_auth(x_ssag_key)
    j = get_job(job_id)
    if j["status"] == "processing":
        raise HTTPException(status_code=409, detail="Cannot erase active GPU input until rendering finishes")
    with database() as db:
        db.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    shutil.rmtree(ROOT / job_id, ignore_errors=True)
    return {"deleted": True, "id":job_id}
