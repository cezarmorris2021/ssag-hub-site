# SSAG Motion Studio — actual GPU worker

This repository provides a real private motion-transfer job API, **not an AI model** and **not a CPU simulation**. The AI engine is the external open-source [Motion Mirror](https://github.com/halli75/motion-mirror) and its Wan2.1-VACE weights. The upstream CLI converts a character image plus one reference-motion video into a generated MP4.

## Deployment readiness (2026-10-30)

| Component | Status |
| --- | --- |
| Mobile-first owner UI | Implemented in `../index.html` |
| API auth, local media validation, queue, download, deletion | Implemented in `server.py`; hardware run not yet tested |
| GPU inferencing | **BLOCKED** — no usable CUDA GPU host is connected |
| Models downloaded / installed on GPU | Not verified |
| End-to-end real video with reference motion | **NOT VERIFIED** |
| Paid customer delivery | Not available until rights, GPU, uptime and actual quality are verified |

The site must not claim that it can render a video until `GET /api/status` shows `render_ready: true` **and a complete real job generates an MP4**. No fallback `mock` backend is used.

### Requirements

An actual NVIDIA CUDA-capable GPU. Motion Mirror's upstream notes roughly 9 GB free VRAM, **32 GB system RAM** and ~20 GB model cache for its lighter 1.3B backend, and documents slow rendering with CPU offload. That is **not** an Android-phone, free Vercel, GitHub Pages or ordinary Render CPU workload. Runtime and customer output quality are not guaranteed.

* 64-bit Linux + Python 3.11+ + NVIDIA/CUDA drivers + [FFmpeg](https://ffmpeg.org/)
* A GPU instance the business controls with persistent private storage; don't expose raw Uvicorn to the public internet
* Motion Mirror software and weights (downloaded only after license review)
* TLS (HTTPS) reverse proxy with CORS restricted to the SSAG interface's origin
* A randomly generated `SSAG_API_KEY` in environment variables; never commit it or show it to clients
* Permission to use the person's likeness (guardian permission for minors) and rights to use the dance reference; avoid unlicensed music

### Install the upstream generator on a qualifying GPU machine

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg git python3-venv
python3 -m venv /opt/ssag-motion-venv
source /opt/ssag-motion-venv/bin/activate
python -m pip install -U pip
# Select the PyTorch CUDA wheel matching your GPU driver:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
git clone https://github.com/halli75/motion-mirror.git /opt/motion-mirror
pip install -e "/opt/motion-mirror[cuda,gpu-inference]"
motion-mirror download --model dwpose
motion-mirror download --model wan-1.3b-vace
# Copy this worker directory to the GPU host:
cd /opt/ssag-motion-worker
pip install -r requirements.txt
export SSAG_API_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
export SSAG_ALLOWED_ORIGINS=https://cezarmorris2021.github.io
export SSAG_PRIVATE_STORAGE=/var/lib/ssag-motion-private
python -m uvicorn server:api --host 127.0.0.1 --port 8787 --workers 1
```

This starts a LOCAL service; to access it from the mobile SSAG interface, configure an HTTPS reverse proxy (Caddy or equivalent) pointing to port 8787, with a protected owner-only network policy. Never expose a plain HTTP key or open GPU control to untrusted browsers. Keep the secret in the terminal or secrets manager, not in the public source code. The current code uses one in-process queue and SQLite and therefore **must run with one Uvicorn worker** and a persistent disk. It is not a distributed queue.

### Use

1. Visit [SSAG Motion Studio](https://cezarmorris2021.github.io/ssag-hub-site/motion-studio/).
2. Choose a photo of a consenting subject and an authorized reference clip (Memphis Jookin' for the owner's request).
3. Enter your HTTPS GPU worker URL and owner API key. Click **Check rendering capability**.
4. If the real engine and CUDA are present, generation unlocks; clicking Generate transmits both files to **your worker**.
5. Poll job until `ready`, download the MP4 and delete job media. Private media expires in 24 hours when cleanup runs. A failed render **must** be recorded as failed, never marketed as delivered.

### API

* `GET /health` — superficial process reachability only. **Not** an AI readiness check.
* `GET /api/status` — auth required; verified CUDA+CLI+FFmpeg prerequisites.
* `POST /api/jobs` — multipart photo, dance, consent=true; owner header required.
* `GET /api/jobs/{id}` — queue, processing, ready, failed and failure reason.
* `GET /api/jobs/{id}/download` — streams actual video; HTTP 409 unless ready.
* `DELETE /api/jobs/{id}` — removes completed/queued jobs; 409 during active GPU execution (retry after completion).

**Important limits:** This is an internal owner workstation, not a finished customer portal. The shared owner key **must not** be distributed to customers. Add per-customer identities, private uploads, consent records, payment, audit logging, moderation and object-storage lifecycle before commercial use. A private GPU worker does not guarantee faithful faces/footwork; validate outputs first. Keep model-weight licenses and commercial restrictions under review: Motion Mirror notes that some optional fast adapters are noncommercial.

### Validation gate

See [GitHub engineering issue #1](https://github.com/cezarmorris2021/ssag-hub-site/issues/1). Until a real end-to-end mp4 is obtained on authorized infrastructure, report **GPU BLOCKED / NOT VERIFIED** to SSAG Business Command Watch every three hours. Never treat a health endpoint, page load, or sample/mock as production success.
