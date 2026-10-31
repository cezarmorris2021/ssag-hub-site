#!/usr/bin/env python3
"""SSAG CPU Shorts Renderer — real MP4 delivery without a GPU or cloud API.

Creates original text-based vertical educational videos with slide transitions,
captions, and optional offline voice narration. This is NOT photorealistic
character animation and does not fabricate AI video production.
"""
from __future__ import annotations
import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SAFE_SIZES = {"360x640": (360, 640), "720x1280": (720, 1280), "1080x1920": (1080, 1920)}
MAX_SCENES = 12
MIN_SEC = 2
MAX_SEC = 30

def check_project(project: dict) -> tuple[list, str, tuple[int, int]]:
    if not isinstance(project, dict):
        raise ValueError("Project must be a JSON object")
    scenes = project.get("scenes")
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= MAX_SCENES:
        raise ValueError("Supply 1 to 12 original content scenes")
    channel = str(project.get("channel", "SSAG")).strip()[:60]
    if not channel:
        raise ValueError("Channel name required")
    size = str(project.get("size", "720x1280"))
    if size not in SAFE_SIZES:
        raise ValueError("Use an allowed vertical output size")
    total = 0
    for index, s in enumerate(scenes):
        if not isinstance(s, dict):
            raise ValueError("Scene entries must be objects")
        sec = int(s.get("seconds", 5))
        if sec < MIN_SEC or sec > MAX_SEC:
            raise ValueError(f"Scene {index+1} seconds outside 2–30")
        total += sec
        for field, maximum in (("headline", 100), ("body", 450), ("narration", 700)):
            if len(str(s.get(field, ""))) > maximum:
                raise ValueError(f"Scene {index+1} {field} is too long")
        if not str(s.get("headline", "")).strip():
            raise ValueError(f"Scene {index+1} missing headline")
    if total > 180:
        raise ValueError("Output length exceeds 180 seconds")
    return scenes, channel, SAFE_SIZES[size]

def font(size: int, bold: bool):
    files = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"])
    for path in files:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()

def rgb(hexcode: str) -> tuple[int,int,int]:
    v = hexcode.strip().lstrip("#")
    if len(v) != 6 or any(x not in "0123456789abcdefABCDEF" for x in v):
        raise ValueError("Accent color must be 6-digit hex")
    return tuple(int(v[i:i+2], 16) for i in (0,2,4))

def wrapped(draw, text, textfont, width):
    result = []
    for para in str(text).splitlines():
        words = para.split()
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if line and draw.textbbox((0, 0), candidate, font=textfont)[2] > width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result

def slide(scene, channel, accent, number, total, size, path):
    w, h = size
    base=Image.new("RGB", (w,h))
    pixels=base.load()
    for y in range(h):
        t=y/max(h-1,1)
        col=(int(7 + 9*t), int(17+20*t), int(30+22*t))
        for x in range(w):pixels[x,y]=col
    draw=ImageDraw.Draw(base)
    k=w/720
    margin=round(62*k)
    ac=rgb(accent)
    draw.rounded_rectangle((margin,round(104*k),margin+round(13*k),h-round(128*k)),
                           radius=round(8*k), fill=ac)
    draw.text((margin+round(31*k),round(125*k)), channel.upper(),
              fill=(140,202,232),font=font(round(25*k),True))
    draw.text((margin+round(31*k),round(190*k)), f"{number:02d} / {total:02d}",
              fill=ac,font=font(round(24*k),True))
    max_width=w-2*margin-round(42*k)
    header_font=font(round(57*k),True)
    header_lines=wrapped(draw, scene["headline"],header_font,max_width)
    if len(header_lines)>5:
        header_font=font(round(46*k),True)
        header_lines=wrapped(draw,scene["headline"],header_font,max_width)
    if len(header_lines)>7:
        raise ValueError("Headline too long for the frame")
    y=round(312*k)
    step=round(70*k) if header_font.size>=round(50*k) else round(58*k)
    for line in header_lines:
        draw.text((margin+round(31*k),y),line,fill=(242,250,255),font=header_font,stroke_width=0)
        y+=step
    y+=round(45*k)
    bodyfont=font(round(31*k),False)
    for line in wrapped(draw,scene.get("body",""),bodyfont,max_width):
        if y>h-round(235*k):
            raise ValueError("Scene body exceeds frame; shorten the text")
        draw.text((margin+round(31*k),y),line,fill=(184,210,228),font=bodyfont)
        y+=round(48*k)
    draw.rounded_rectangle((margin+round(25*k),h-round(150*k),w-margin,h-round(118*k)),
                           radius=round(10*k),fill=(20,56,77))
    draw.rectangle((margin+round(25*k),h-round(150*k),
                    margin+round(25*k)+round((w-2*margin-round(25*k))*number/total),h-round(118*k)),fill=ac)
    draw.text((margin+round(31*k),h-round(95*k)),"SSAG • ORIGINAL CONTENT",
              fill=(120,158,183),font=font(round(19*k),True))
    base.save(path)

def cmd_run(cmd):
    p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError("Media tool failed: "+p.stderr[-750:])
    return p

def render(project, output: Path, voice: bool = False):
    scenes, channel, (w,h)=check_project(project)
    accent=project.get("accent","#64ccff")
    rgb(accent)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and ffprobe are required")
    if voice and not (shutil.which("espeak-ng") or shutil.which("espeak")):
        raise RuntimeError("Offline narration requires espeak or espeak-ng")
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output file must end in .mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ssag-short-") as folder:
        temp=Path(folder)
        concat=[]
        for i,scene in enumerate(scenes,1):
            img=temp/f"scene-{i:02}.png"
            clip=temp/f"clip-{i:02}.mp4"
            slide(scene,channel,accent,i,len(scenes),(w,h),img)
            seconds=int(scene.get("seconds",5))
            fadeout=max(seconds-0.45, 0.3)
            source=["-f","lavfi","-i","anullsrc=r=44100:cl=stereo"]
            audio=scene.get("narration","") or (scene["headline"]+". "+str(scene.get("body","")))
            if voice and audio.strip():
                wav=temp/f"voice-{i:02}.wav"
                speaker=shutil.which("espeak-ng") or shutil.which("espeak")
                cmd_run([speaker,"-v","en-us","-s","135","-w",str(wav),audio])
                source=["-i",str(wav)]
            args=["ffmpeg","-hide_banner","-loglevel","error","-y",
                  "-loop","1","-framerate","24","-i",str(img),*source,
                  "-t",str(seconds),
                  "-vf",f"format=yuv420p,fade=t=in:st=0:d=0.35,fade=t=out:st={fadeout}:d=0.4",
                  "-c:v","libx264","-preset","ultrafast","-crf","25","-r","24",
                  "-c:a","aac","-b:a","96k","-ac","2","-ar","44100",
                  "-af","apad","-pix_fmt","yuv420p","-shortest",str(clip)]
            cmd_run(args)
            concat.append(clip)
        listing=temp/"clips.txt"
        listing.write_text("".join("file '"+str(p).replace("'","'\\''")+"'\n" for p in concat))
        cmd_run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
                 "-i",str(listing),"-c","copy","-movflags","+faststart",str(output)])
    if not output.exists() or output.stat().st_size < 1024:
        raise RuntimeError("Renderer produced no real MP4")
    info=cmd_run(["ffprobe","-v","error","-select_streams","v:0",
                  "-show_entries","stream=codec_name,width,height",
                  "-of","json",str(output)])
    stream=json.loads(info.stdout).get("streams",[])
    if not stream or stream[0].get("codec_name")!="h264":
        raise RuntimeError("Output was not a verifiable H.264 video")
    return {"status":"REAL_MP4_RENDERED","path":str(output.resolve()),"bytes":output.stat().st_size,
            "size":f"{w}x{h}","scenes":len(scenes),"audio":"offline synthetic voice" if voice else "silent"}

def main(argv=None):
    ap=argparse.ArgumentParser(description="Render SSAG original educational YouTube Shorts without cloud services")
    ap.add_argument("project",type=Path,help="Original short-video project JSON")
    ap.add_argument("--output",type=Path,required=True,help="Output .mp4 file")
    ap.add_argument("--offline-voice",action="store_true",help="Use local synthetic English speech (espeak)")
    ap.add_argument("--validate-only",action="store_true")
    args=ap.parse_args(argv)
    project=json.loads(args.project.read_text(encoding="utf-8"))
    if args.validate_only:
        scenes,channel,size=check_project(project)
        print(json.dumps({"status":"VALIDATED_NOT_RENDERED","scenes":len(scenes),"size":size}))
        return 0
    print(json.dumps(render(project,args.output,voice=args.offline_voice),indent=2))
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except (ValueError,RuntimeError,OSError) as err:
        print("RENDER FAILED:",str(err),file=sys.stderr)
        sys.exit(1)
