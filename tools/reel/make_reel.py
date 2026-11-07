"""Build a BariLifestyle reel (1080x1920, 14 s, original background music).

Usage: python3 tools/reel/make_reel.py CONFIG.json OUT.mp4
CONFIG keys: hook1, hook2, label, title, line1, line2, line3, closing,
optional: url (default barilifestyle.com), image (path relative to repo root, default brand/hero-halo.jpg),
music_variant (0-2, default 0). line1..line3 may contain <b>..</b>.
Also writes OUT with .jpg extension: a 1080x1350 cover/feed frame for Facebook."""
import html, json, pathlib, re, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2]).resolve()
cfg.setdefault("url", "barilifestyle.com")
FPS, D = 30, 14

def esc(v, allow_b=False):
    v = html.escape(v)
    return re.sub(r"&lt;(/?)b&gt;", r"<\1b>", v) if allow_b else v

tpl = (HERE / "reel.html").read_text(encoding="utf-8")
for k in ["hook1", "hook2", "label", "title", "line1", "line2", "line3", "closing", "url"]:
    tpl = tpl.replace("{{%s}}" % k, esc(cfg[k], k.startswith("line")))
if cfg.get("image"):
    tpl = tpl.replace("../../brand/hero-halo.jpg", "../../" + cfg["image"])
page = HERE / "_render.html"
page.write_text(tpl, encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(page.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
        for i in range(FPS * D):
            pg.evaluate(f"render({i / FPS})")
            pg.screenshot(path=str(td / f"f{i:04d}.jpg"), type="jpeg", quality=92)
        b.close()
    wav = td / "m.wav"
    subprocess.run([sys.executable, "-I", str(HERE / "music.py"), str(wav), str(D), str(cfg.get("music_variant", 0))], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(td / "f%04d.jpg"), "-i", str(wav),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    # 4:5 feed image for Facebook / cover: the tip scene at 8.5 s, cropped centre 1080x1350
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "8.5", "-i", str(out), "-frames:v", "1",
                    "-vf", "crop=1080:1350:0:50", "-q:v", "3", str(out.with_suffix(".jpg"))], check=True)
page.unlink()
print("ok", out)
