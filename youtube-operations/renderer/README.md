# SSAG CPU Shorts Renderer

Purpose: produce actual original **faceless caption-style Shorts MP4 videos** without paid image/video generators, GPU, or YouTube account login. This is *not* a tool for making a photograph of a person realistically dance.

## Real delivery capabilities
- Generates original title/caption/background frames (no stock images required)
- Builds 9:16 MP4/H.264+AAC videos, with fade transitions and progress markers
- Optional completely offline synthetic English narration with eSpeak; its robotic quality is a **draft** and may need an approved replacement for client work
- Processes JSON scenes exported by the SSAG YouTube Operations workstation or the example project
- Checks presence of actual encoded H.264 video and reports real local output path/size
- Supports 360x640 QA, 720x1280 Shorts and 1080x1920 production output sizes
- Does not auto-publish, generate realistic actor motion, verify factual scripts, license other people's videos or upload personal data

### Run on owner computer
Requires Python 3.11+, FFmpeg/ffprobe, optional eSpeak, and Pillow. No API key.

```bash
python -m pip install -r youtube-operations/renderer/requirements.txt
python youtube-operations/renderer/render.py youtube-operations/renderer/examples/clever-living-lab-short.json --output my-short.mp4
# Optional dry run with offline U.S. English robotic voice
python youtube-operations/renderer/render.py youtube-operations/renderer/examples/clever-living-lab-short.json --output narrated-short.mp4 --offline-voice
```

To create a different video, edit the project JSON `channel`, `title`, `accent`, `size` and `scenes` (each with `headline`, `body`, optional `narration` and `seconds`). This example is original generic instructional content, not an actual published video or existing YouTube channel asset.

### Production handoff
Generate a final MP4, inspect voice/caption readability, obtain client approval, attach an approved and rights-cleared thumbnail, fill out the YouTube workstation manifest, and use the separately authorized OAuth publisher. A manifest or a rendered MP4 alone does not mean it was uploaded or scheduled.

**Status:** source committed; actual CI MP4 render test must pass before renderer can be listed as validated. Even after local encoding passes, published video, channel reach and customer delivery remain unverified.
