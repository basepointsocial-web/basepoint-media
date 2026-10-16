"""Build a 'More Time For This' Reel: stock clip (cropped 9:16) + ambient sound + fading text.
usage: python3 adbuild.py out.mp4 clip.mp4 sound.mp3 "Line one" [xfrac=0.5] [clip_start=0] [snd_start=0] [dur=14.5] [vol=1.0]
"""
import asyncio, os, subprocess, sys, json, html as H
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
F = R + "ibm-plex-{}/package/fonts/complete/woff2/IBMPlex{}-{}.woff2"

def text_png(line, path):
    page = f"""<html><head><style>
@font-face{{font-family:'PS';font-weight:500;src:url('file://{F.format('sans-1.1.0','Sans','Medium')}')}}
@font-face{{font-family:'PM';font-weight:700;src:url('file://{F.format('mono-2.5.0','Mono','Bold')}')}}
html,body{{margin:0;width:1080px;height:1920px;background:transparent}}
.g{{position:absolute;left:-200px;right:-200px;top:610px;height:700px;background:radial-gradient(ellipse at center,rgba(0,0,0,.38) 0%,rgba(0,0,0,.18) 45%,rgba(0,0,0,0) 72%)}}
.w{{position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);text-align:center;color:#fff;
text-shadow:0 2px 26px rgba(0,0,0,.6),0 1px 5px rgba(0,0,0,.45)}}
h1{{font-family:'PS';font-weight:500;font-size:80px;line-height:1.14;margin:0;letter-spacing:-.5px}}
p{{font-family:'PM';font-weight:700;font-size:48px;letter-spacing:2px;margin:60px 0 0}}
</style></head><body><div class=g></div><div class=w><h1>{H.escape(line)}</h1><p>DM "SAMPLE" to start.</p></div></body></html>"""
    hp = path + ".html"; open(hp, "w").write(page)
    async def go():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1920})
            await pg.goto("file://" + os.path.abspath(hp)); await pg.wait_for_timeout(400)
            await pg.screenshot(path=path, omit_background=True); await b.close()
    asyncio.run(go())

def build(out, clip, snd, line, xfrac=0.5, cs=0.0, ss=0.0, dur=14.5, vol=1.0):
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                      "stream=width,height", "-show_entries", "format=duration", "-of", "json", clip]))
    w, h = info["streams"][0]["width"], info["streams"][0]["height"]; cdur = float(info["format"]["duration"])
    cw = int(h * 9 / 16) // 2 * 2; x = int((w - cw) * xfrac)
    tp = out + ".text.png"; text_png(line, tp)
    # slow the clip slightly if it is shorter than the Reel, so it never runs out
    speed = min(1.0, (cdur - cs) / dur)
    pts = f"setpts={1/speed:.4f}*PTS," if speed < 1 else ""
    sharpen = "unsharp=5:5:0.6:5:5:0.0," if h < 1000 else ""
    fc = (f"[0:v]trim=start={cs},setpts=PTS-STARTPTS,{pts}crop={cw}:{h}:{x}:0,scale=1080:1920:flags=lanczos,{sharpen}fps=30,setsar=1,format=yuv420p[bg];"
          f"[1:v]format=rgba,fade=t=in:st=5:d=2.5:alpha=1[t];"
          f"[bg][t]overlay=0:0,fade=t=in:st=0:d=0.8,fade=t=out:st={dur-0.8}:d=0.8[v];"
          f"[2:a]atrim=start={ss},asetpts=PTS-STARTPTS,aloop=loop=-1:size=2e9,atrim=duration={dur},"
          f"afade=t=in:d=1,afade=t=out:st={dur-1.3}:d=1.3,volume={vol}[a]")
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", clip, "-loop", "1", "-t", str(dur), "-i", tp, "-i", snd,
                           "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(dur), "-c:v", "libx264", "-crf", "19",
                           "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(out, "ok", f"speed={speed:.2f}")

if __name__ == "__main__":
    a = sys.argv
    build(a[1], a[2], a[3], a[4], *(float(v) for v in a[5:]))
