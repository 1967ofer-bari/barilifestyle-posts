"""Saturday-night website video for BariLifestyle: a short 9:16 slideshow made ONLY from images
on barilifestyle.com, with original background music, ending with a call to visit the site.

Usage: python3 tools/reel/site_reel.py CONFIG.json OUT.mp4
Also writes OUT with .jpg extension: a 1080x1350 closing card for Facebook (no "קישור בביו" line).

CONFIG keys:
  hook1, hook2     – opening lines over a darkened site image (≤ 7 words each; must stop the scroll)
  hook_image       – image for the opening (site image name, e.g. "eti-before.jpg", or a full URL)
  slides           – 3–4 items: {"images": [1 or 2 names], "text": "≤ 9 words, may use <b>..</b>",
                     "tags": optional labels per image (e.g. ["לפני","היום"]),
                     "fit": true to show a wide image whole instead of cropping}
  cta              – closing line (≤ 6 words), e.g. "הסיפור המלא שלנו – באתר"
  cta_image        – round photo on the closing card (site image name)
  url              – shown on the closing card (default barilifestyle.com)
  page             – the site page the post links to (e.g. https://barilifestyle.com/about/), for the caption
  mood             – calm | warm | uplifting | energetic (music.py); music_seed default = output file name
Images are downloaded from https://barilifestyle.com/img/<name> at render time (nothing is stored in the repo).
Length: 2.6 s hook + 3 s per slide + 4 s closing (4 slides ≈ 18.6 s)."""
import json, pathlib, subprocess, sys, tempfile, urllib.request
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
SITE = "https://barilifestyle.com/img/"
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2]).resolve()
FPS = 30

with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    cache = {}
    def img(name):
        if name not in cache:
            url = name if name.startswith("http") else SITE + name
            dest = td / f"i{len(cache)}{pathlib.Path(url).suffix or '.jpg'}"
            req = urllib.request.Request(url, headers={"User-Agent": "BariLifestyle-posts"})
            dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())
            cache[name] = dest.as_uri()
        return cache[name]
    c = dict(cfg)
    c["hook_image"] = img(cfg["hook_image"])
    c["cta_image"] = img(cfg["cta_image"])
    c["logo"] = (REPO / "brand" / "logo.jpg").as_uri()
    c["slides"] = [dict(s, images=[img(n) for n in s["images"]]) for s in cfg["slides"]]
    page = HERE / f"_site_render_{out.stem}.html"
    page.write_text((HERE / "site_reel.html").read_text(encoding="utf-8")
                    .replace("__CONFIG__", json.dumps(c, ensure_ascii=False)), encoding="utf-8")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--allow-file-access-from-files"])
            pg = b.new_page(viewport={"width": 1080, "height": 1920})
            pg.goto(page.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
            D = pg.evaluate("DURATION")
            n = int(round(FPS * D))
            for i in range(n):
                pg.evaluate(f"render({i / FPS})")
                pg.screenshot(path=str(td / f"f{i:04d}.jpg"), type="jpeg", quality=92)
            pg.evaluate(f"render({D}, true)")
            pg.screenshot(path=str(td / "fb.png"))
            b.close()
    finally:
        page.unlink(missing_ok=True)
    wav = td / "m.wav"
    subprocess.run([sys.executable, "-I", str(HERE / "music.py"), str(wav), str(D), cfg.get("mood", "warm"),
                    str(cfg.get("music_seed", out.stem))], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(td / "f%04d.jpg"), "-i", str(wav),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(td / "fb.png"),
                    "-vf", "crop=1080:1350:0:285", "-q:v", "3", str(out.with_suffix(".jpg"))], check=True)
print("ok", out, f"{D:.1f}s")
