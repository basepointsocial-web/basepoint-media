"""Basepoint Reel maker: spec JSON -> Kokoro voiceover per scene -> HTML animation -> MP4 (1080x1920, 30fps).
usage: python3 reel.py spec.json out.mp4
spec = {"voice":"af_heart","speed":1.05,"scenes":[{"vo":"...", "html":"<inner html>", "min":3.0}, ...]}
Scene HTML conventions: any element with class "r" reveals in order (fade + slide up), staggered across the
scene's voiceover; data-at="0.4" overrides (fraction of the scene). Class "pop" scales in. Class "draw" on an SVG
draws its strokes. The header logo is added automatically except on scenes with "nologo": true.
"""
import asyncio, json, os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
F = R + "ibm-plex-{}/package/fonts/complete/woff2/IBMPlex{}-{}.woff2"
FPS = 30
LOGO = """<svg width="{s}" height="{s}" viewBox="0 0 100 100"><g stroke="#EF7B3F" stroke-width="7" stroke-linecap="round" fill="none">
<circle cx="50" cy="50" r="30"/><line x1="50" y1="6" x2="50" y2="26"/><line x1="50" y1="74" x2="50" y2="94"/>
<line x1="6" y1="50" x2="26" y2="50"/><line x1="74" y1="50" x2="94" y2="50"/></g><circle cx="50" cy="50" r="9" fill="#EF7B3F"/></svg>"""
CSS = f"""
@font-face{{font-family:'Plex Mono';font-weight:500;src:url('file://{F.format('mono-2.5.0','Mono','Medium')}')}}
@font-face{{font-family:'Plex Mono';font-weight:700;src:url('file://{F.format('mono-2.5.0','Mono','Bold')}')}}
@font-face{{font-family:'Plex Sans';font-weight:400;src:url('file://{F.format('sans-1.1.0','Sans','Regular')}')}}
@font-face{{font-family:'Plex Sans';font-weight:500;src:url('file://{F.format('sans-1.1.0','Sans','Medium')}')}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#1F3B73}}
#bg{{position:absolute;inset:0;background:#1F3B73;background-image:linear-gradient(rgba(140,170,230,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(140,170,230,.13) 1px,transparent 1px);background-size:54px 54px}}
.sc{{position:absolute;inset:0;padding:400px 100px 420px;color:#fff;font-family:'Plex Sans';display:none}}
.brand{{position:absolute;top:230px;left:100px;display:flex;align-items:center;gap:20px;font-family:'Plex Mono';font-weight:700;font-size:32px;letter-spacing:4px;color:#fff}}
.brand small{{font-weight:500;font-size:22px;color:#C9D3E6;letter-spacing:3px;margin-left:4px}}
h1{{font-family:'Plex Mono';font-weight:700;margin:0;line-height:1.08;letter-spacing:-1px;font-size:96px}}
h2{{font-family:'Plex Mono';font-weight:700;margin:0;line-height:1.12;font-size:76px}}
p{{margin:0}} .o{{color:#EF7B3F}} .bar{{width:150px;height:12px;background:#EF7B3F}}
.chip{{display:inline-flex;align-items:center;gap:22px;background:#fff;color:#1F3B73;border-radius:18px;padding:22px 30px;font-family:'Plex Mono';font-weight:700;font-size:40px;margin:0 0 22px}}
.btn{{background:#fff;color:#1F3B73;border-radius:18px;display:flex;justify-content:space-between;align-items:center;font-family:'Plex Mono';padding:40px 46px}}
.r,.pop{{will-change:transform,opacity}}
"""
JS = """
const scenes=[...document.querySelectorAll('.sc')];
const ease=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
function prep(){ scenes.forEach(s=>{ const rs=[...s.querySelectorAll('.r,.pop')]; const n=rs.length;
  rs.forEach((e,i)=>{ if(e.dataset.at===undefined) e.dataset.at = n>1 ? (0.04 + 0.78*i/(n-1)).toFixed(3) : '0.05'; });
  s.querySelectorAll('svg.draw path, svg.draw line, svg.draw polyline, svg.draw circle, svg.draw rect').forEach(p=>{
    const L=p.getTotalLength?p.getTotalLength():1000; p.style.strokeDasharray=L; p.style.strokeDashoffset=L; p.dataset.len=L;});
}); }
window.seek=function(t){ // t seconds
  for(const s of scenes){ const a=+s.dataset.start, b=+s.dataset.end; const on = t>=a && t<b; s.style.display=on?'block':'none';
    if(!on) continue; const d=b-a, u=(t-a);
    // whole-scene fade in/out (0.25s)
    s.style.opacity = Math.min(1, u/0.25, (b-t)/0.25 + (s.dataset.last?1:0));
    s.querySelectorAll('.r').forEach(e=>{ const k=ease((u - (+e.dataset.at)*d)/0.45); e.style.opacity=k; e.style.transform=`translateY(${(1-k)*40}px)`; });
    s.querySelectorAll('.pop').forEach(e=>{ const x=Math.min(Math.max((u - (+e.dataset.at)*d)/0.4,0),1); const k=x<1? 1.12*ease(x)-0.12*x*x : 1; e.style.opacity=Math.min(1,x*2); e.style.transform=`scale(${0.6+0.4*k})`; });
    s.querySelectorAll('svg.draw').forEach(sv=>{ const at=+(sv.dataset.at||0), dur=+(sv.dataset.dur||0.6); const k=ease((u/d-at)/dur);
      sv.querySelectorAll('[data-len]').forEach(p=>p.style.strokeDashoffset=(1-k)*p.dataset.len); });
    s.querySelectorAll('.spin').forEach(e=>{ const k=ease(u/1.0); e.style.transform=`rotate(${(1-k)*-180}deg) scale(${0.5+0.5*k})`; e.style.opacity=k; });
  }
};
prep();
"""

def build_audio(spec, kok, outwav):
    sr = 24000; parts = []; times = []; t = 0.0
    lead, gap = 0.35, 0.30
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("vo"):
            v = spec.get("voice", "nicole_warm")
            if v == "nicole_warm":  # Basepoint house voice: Nicole, warmed with 35% Heart (chosen Oct 12)
                g = kok.get_voice_style  # Nicole, warmer + brighter/upbeat but professional (mix A, Oct 12)
                v = 0.45 * g("af_nicole") + 0.25 * g("af_heart") + 0.20 * g("af_bella") + 0.10 * g("af_nova")
            a, sr = kok.create(sc["vo"], voice=v, speed=spec.get("speed", 1.18), lang="en-us")
        else:
            a = np.zeros(1, dtype=np.float32)
        vo_len = len(a) / sr
        dur = max(sc.get("min", 0), lead + vo_len + gap)
        if i == len(spec["scenes"]) - 1: dur += sc.get("hold", 1.5)
        seg = np.zeros(int(dur * sr), dtype=np.float32)
        s0 = int(lead * sr); seg[s0:s0 + len(a)] = a[: len(seg) - s0]
        parts.append(seg); times.append((t, t + dur)); t += dur
    audio = np.concatenate(parts)
    sf.write(outwav, audio, sr)
    return times, t

def build_html(spec, times):
    out = []
    for i, (sc, (a, b)) in enumerate(zip(spec["scenes"], times)):
        logo = "" if sc.get("nologo") else f'<div class="brand">{LOGO.format(s=58)}BASEPOINT<small>SOCIAL</small></div>'
        last = ' data-last="1"' if i == len(times) - 1 else ""
        out.append(f'<div class="sc" data-start="{a:.3f}" data-end="{b:.3f}"{last}>{logo}{sc["html"].replace("LOGO_BIG", LOGO.format(s=230))}</div>')
    return f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div id=bg></div>{''.join(out)}<script>{JS}</script></body></html>"

async def render(html_path, total, outmp4, wav):
    n = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", outmp4], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto("file://" + html_path); await pg.wait_for_timeout(600)
        for i in range(n):
            await pg.evaluate(f"seek({i / FPS})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
        await b.close()
    ff.stdin.close(); ff.wait()

def main(specf, outmp4):
    spec = json.load(open(specf))
    kok = Kokoro(os.path.join(HERE, "kokoro-v1.0.onnx"), os.path.join(HERE, "voices-v1.0.bin"))
    base = os.path.splitext(outmp4)[0]
    wav = base + "_vo.wav"
    times, total = build_audio(spec, kok, wav)
    html = build_html(spec, times); hp = os.path.abspath(base + ".html"); open(hp, "w").write(html)
    asyncio.run(render(hp, total, outmp4, wav))
    print(json.dumps({"out": outmp4, "seconds": round(total, 2), "scenes": [[round(a, 2), round(b, 2)] for a, b in times]}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
