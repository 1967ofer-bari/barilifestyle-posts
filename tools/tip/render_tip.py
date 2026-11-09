#!/usr/bin/env python3
"""Render a BariLifestyle tip image (1080x1350 JPEG) from a JSON config.

Usage:  python3 tools/tip/render_tip.py CONFIG.json tips/YYYY-MM-DD.jpg

Two layouts (key "type"):

infographic – a summary grid ("10 habits ..."):
  count      the number, shown inside the title in the accent colour, e.g. "10" → "10 הרגלים להצלחה"
  title      e.g. "הרגלים להצלחה"           (<= 3 words)
  chip       e.g. "אחרי ניתוח בריאטרי"      (<= 4 words)
  subtitle   one short line
  section    bar above the grid, e.g. "10 ההרגלים המרכזיים"
  items      6, 8, 9 or 10 x {"title" (<= 3 words), "text" (<= 6 words), "icon"}
  box1/box2  {"title", "text" (<= 18 words)}  – box1 green, box2 warm ("חשוב לדעת")
  bottom     headline of the dark bottom bar, e.g. "השורה התחתונה: התנהגות היא המפתח"

tip – one weekly tip broken into steps:
  badge      e.g. "טיפ השבוע #2"
  title      the big question / statement (<= 4 words)
  chip       sub-headline (<= 5 words)
  intro      1–2 sentences (<= 30 words)
  section    e.g. "3 צעדים פשוטים"
  items      exactly 3 x {"title" (<= 2 words), "text" (<= 14 words), "icon"}
  box1/box2  {"title", "text" (<= 18 words)}
  bottom     e.g. "שמרו את הפוסט לרגע שתצטרכו"

Optional for both: "accent" (hex, default bronze #A9763A).
Icons: see ICONS below. The bottom bar always says
"עוד טיפים ומידע תמצאו באוסף הכלים והספרים שלנו" + www.barilifestyle.com.

The script fails (exit 2) and names the element if any text overflows its box,
so shorten the text and run again.
"""
import html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
E = html.escape

ICONS = {
 "protein": '<path d="M24 6c-8 0-14 12-14 21a14 14 0 0 0 28 0C38 18 32 6 24 6z"/><circle cx="24" cy="29" r="6"/>',
 "clock": '<circle cx="24" cy="26" r="16"/><path d="M24 17v9l6 4M19 5h10"/>',
 "no-drink": '<path d="M13 8h22l-3 32H16z"/><path d="M14 18h20"/><path d="M8 40L40 8"/>',
 "water": '<path d="M24 6s-13 15-13 24a13 13 0 0 0 26 0C37 21 24 6 24 6z"/><path d="M18 31a6 6 0 0 0 6 6"/>',
 "pill": '<rect x="7" y="17" width="34" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M19 15l10 18"/>',
 "plate": '<circle cx="26" cy="25" r="15"/><circle cx="26" cy="25" r="8"/><path d="M6 10v28M3 10v8a3 3 0 0 0 6 0v-8"/>',
 "dumbbell": '<path d="M14 24h20"/><rect x="6" y="15" width="8" height="18" rx="2"/><rect x="34" y="15" width="8" height="18" rx="2"/><path d="M3 20v8M45 20v8"/>',
 "heart-q": '<path d="M24 40S7 30 7 18a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z"/><path d="M21 19a3 3 0 1 1 4 3c-1 .5-1 1.5-1 2.5M24 29v.5"/>',
 "moon": '<path d="M38 30A16 16 0 0 1 18 10a16 16 0 1 0 20 20z"/><path d="M33 8v6M30 11h6"/>',
 "people": '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="18" r="5"/><path d="M5 38c1-7 6-11 12-11s11 4 12 11M28 38c1-5 4-8 8-8s7 3 8 8"/>',
 "stop": '<path d="M17 7h14l10 10v14L31 41H17L7 31V17z"/><path d="M18 24h12"/>',
 "gauge": '<path d="M6 32a18 18 0 0 1 36 0"/><path d="M24 32l9-10"/><circle cx="24" cy="32" r="2.5"/>',
 "fork-road": '<path d="M24 42V24M24 24L12 10M24 24l12-14"/><path d="M8 14V8h6M40 14V8h-6"/>',
 "brain": '<path d="M20 8a6 6 0 0 0-6 6 6 6 0 0 0-4 10 6 6 0 0 0 4 10 6 6 0 0 0 6 6h4V8z"/><path d="M28 8a6 6 0 0 1 6 6 6 6 0 0 1 4 10 6 6 0 0 1-4 10 6 6 0 0 1-6 6h-4V8z"/>',
 "mirror": '<ellipse cx="24" cy="19" rx="11" ry="14"/><path d="M24 33v9M17 42h14"/>',
 "contract": '<path d="M12 5h17l8 8v30H12z"/><path d="M29 5v8h8M17 21h14M17 27h14M17 35l3 2 6-5"/>',
 "camera": '<rect x="5" y="14" width="38" height="25" rx="4"/><circle cx="24" cy="26" r="7"/><path d="M17 14l3-5h8l3 5"/>',
 "walk": '<circle cx="26" cy="7" r="3.5"/><path d="M24 14l-5 10 6 5 2 13M24 14l6 8 7 2M19 24l-6 3M25 29l-7 13"/>',
 "leaf": '<path d="M40 8C20 8 8 18 8 32c0 4 2 8 2 8s4 2 8 2c14 0 22-14 22-34z"/><path d="M10 40C18 30 26 24 34 18"/>',
 "target": '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="10"/><circle cx="24" cy="24" r="3"/>',
 "bulb": '<path d="M17 30a12 12 0 1 1 14 0v5H17z"/><path d="M19 41h10"/>',
 "calendar": '<rect x="6" y="9" width="36" height="32" rx="4"/><path d="M6 18h36M15 5v8M33 5v8M15 27h6M27 27h6M15 34h6"/>',
 "chat": '<path d="M7 9h34v22H22l-9 8v-8H7z"/><path d="M15 18h18M15 24h11"/>',
 "shield": '<path d="M24 5l16 6v12c0 10-7 17-16 20C15 40 8 33 8 23V11z"/><path d="M17 24l5 5 9-10"/>',
 "star": '<path d="M24 6l5.5 11.5 12.5 1.7-9 8.8 2.2 12.5L24 34.6 12.8 40.5 15 28l-9-8.8 12.5-1.7z"/>',
 "book": '<path d="M24 12c-5-4-12-4-18-3v29c6-1 13-1 18 3 5-4 12-4 18-3V9c-6-1-13-1-18 3z"/><path d="M24 12v29"/>',
 "scale-balance": '<path d="M24 6v36M14 42h20M8 14h32"/><path d="M8 14l-5 12a5 5 0 0 0 10 0zM40 14l-5 12a5 5 0 0 0 10 0z"/>',
}

def icon(name):
    body = ICONS.get(name) or ICONS["bulb"]
    return f'<svg viewBox="0 0 48 48" aria-hidden="true">{body}</svg>'

FONTS = "".join(
    f'@font-face{{font-family:Rubik;src:url({(HERE/"fonts"/f"rubik-{s}-{w}-normal.woff2").as_uri()});font-weight:{w};'
    + ('unicode-range:U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F;' if s == "hebrew" else '') + '}'
    for w in (500, 700, 800, 900) for s in ("hebrew", "latin"))

CSS = FONTS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden;background:#F6F4EE}
#root{width:1080px;height:1350px;overflow:hidden;background:#F6F4EE;font-family:Rubik,sans-serif;direction:rtl;padding:30px 32px 24px;display:flex;flex-direction:column;gap:16px;color:#2F5A5C}
.hero{display:flex;gap:22px;align-items:stretch}
.hero-main{flex:1;min-width:0;display:flex;flex-direction:column;gap:14px}
.logo{width:270px;height:auto;display:block}
.photo{flex:none;width:260px;min-height:270px;border-radius:20px;overflow:hidden;position:relative;background:#1A1A1A;border:4px solid #8DAA8B}
.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%}
.cap{position:absolute;bottom:0;left:0;right:0;background:rgba(30,60,62,.9);padding:8px 12px;display:flex;flex-direction:column;gap:2px}
.cap b{font-size:19px;font-weight:800;color:#fff}.cap span{font-size:13px;font-weight:500;color:#E6EEE3}
.count{font-size:116px;font-weight:900;line-height:1;color:#fff;background:#2F5A5C;border-radius:18px;padding:8px 20px 12px;flex:none}
.h1{font-size:46px;font-weight:900;line-height:1.05}
.chip{font-weight:900;line-height:1.15;color:#fff;border-radius:10px;padding:5px 14px;align-self:flex-start}
.sub{font-size:19px;font-weight:700;color:#23363A}
.bar{background:#2F5A5C;color:#fff;font-size:26px;font-weight:800;border-radius:12px;padding:8px;display:flex;justify-content:center;align-items:center;gap:14px}
.bar i{width:40px;height:3px;background:#E8C48E;border-radius:2px}
.grid{display:grid;gap:11px;flex:1;min-height:0;grid-auto-rows:1fr}
.card{background:#fff;border:2px solid #D9E3D6;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;align-items:center;min-width:0}
.card-h{width:100%;background:#2F5A5C;color:#fff;font-weight:800;line-height:1.2;text-align:center;padding:8px;display:flex;align-items:center;justify-content:center;overflow-wrap:anywhere}
.num{color:#E8C48E;margin-left:4px}
.ico{border-radius:50%;background:#E6EEE3;display:flex;align-items:center;justify-content:center;flex:none}
.ico svg{stroke:#2F5A5C;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.card-b{margin-bottom:auto;line-height:1.35;color:#23363A;font-weight:500;text-align:center;width:100%;overflow-wrap:anywhere}
.boxes{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.box{border-radius:14px;padding:12px 16px;display:flex;flex-direction:column;gap:4px}
.box b{font-size:21px;font-weight:800}.box p{font-size:17px;font-weight:500;color:#23363A;line-height:1.4}
.b1{background:#E6EEE3;border:2px solid #C5D6C1}.b1 b{color:#2F5A5C}
.b2{background:#F7EBDA;border:2px solid #E3C79C}.b2 b{color:#7A5220}
.bottom{background:#2F5A5C;border-radius:16px;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:auto}
.bottom .t{font-size:25px;font-weight:800;color:#fff}.bottom .s{font-size:17px;font-weight:500;color:#DCE8DA;margin-top:3px}
.links{display:flex;flex-direction:column;align-items:flex-end;gap:2px;font-size:17px;font-weight:700;color:#fff;flex:none;direction:ltr}
.links span:last-child{color:#E8C48E}
.foot{text-align:center;font-size:15px;font-weight:500;color:#4E6266}
.intro{font-size:24px;font-weight:500;color:#23363A;line-height:1.45}
.badge{color:#fff;font-size:22px;font-weight:800;padding:6px 16px;border-radius:999px;flex:none}
"""

def photo():
    return (f'<div class="photo"><img src="{(ROOT/"brand/ofer-portrait.jpg").as_uri()}" alt="">'
            '<div class="cap"><b>עופר לקסמן</b><span>חוקר פסיכולוגיה התנהגותית · BariMF™</span></div></div>')

def logo():
    return f'<img class="logo" src="{(ROOT/"brand/logo-transparent.png").as_uri()}" alt="BariLifestyle">'

def bar(text):
    return f'<div class="bar"><i></i><span>{E(text)}</span><i></i></div>'

def cards(items, cols, big):
    hs, ic, isz, bs, hmin, gap = (32, 150, 82, 30, 0, "auto 0 24px") if big else (21, 92, 52, 19, 66, "auto 0 14px")
    out = []
    for n, it in enumerate(items, 1):
        out.append(
            f'<div class="card"><div class="card-h" style="font-size:{hs}px;min-height:{hmin}px">'
            f'<span><span class="num">{n}.</span>{E(it["title"])}</span></div>'
            f'<div class="ico" style="width:{ic}px;height:{ic}px;margin:{gap}">'
            f'{icon(it.get("icon","bulb")).replace("<svg", f"<svg width={isz} height={isz}", 1)}</div>'
            f'<div class="card-b" style="font-size:{bs}px;padding:0 {18 if big else 10}px {20 if big else 14}px">{E(it["text"])}</div></div>')
    return (f'<div class="grid" style="grid-template-columns:repeat({cols},minmax(0,1fr));gap:{14 if big else 11}px">'
            + "".join(out) + '</div>')

def boxes(c):
    b1, b2 = c["box1"], c["box2"]
    return (f'<div class="boxes"><div class="box b1"><b>{E(b1["title"])}</b><p>{E(b1["text"])}</p></div>'
            f'<div class="box b2"><b>{E(b2["title"])}</b><p>{E(b2["text"])}</p></div></div>')

def bottom(c):
    return (f'<div class="bottom"><div><div class="t">{E(c["bottom"])}</div>'
            '<div class="s">עוד טיפים ומידע תמצאו באוסף הכלים והספרים שלנו</div></div>'
            '<div class="links"><span>@barilifestyle_barimf</span><span>www.barilifestyle.com</span></div></div>'
            '<div class="foot">אתי ועופר לקסמן · ״צועדים בשביל הבריאות״</div>')

def build(c):
    acc = c.get("accent", "#A9763A")
    if c["type"] == "infographic":
        n = len(c["items"])
        cols = {6: 3, 8: 4, 9: 3, 10: 5}.get(n)
        if not cols:
            sys.exit("infographic needs 6, 8, 9 or 10 items")
        hero = (f'<div class="hero"><div class="hero-main">{logo()}'
                f'<div style="display:flex;flex-direction:column;gap:10px;min-width:0">'
                f'<div class="h1" style="font-size:60px"><span style="color:{acc}">{E(c["count"])}</span> {E(c["title"])}</div>'
                f'<div class="chip" style="font-size:32px;background:#2F5A5C">{E(c["chip"])}</div>'
                f'<div class="sub" style="font-size:21px">{E(c["subtitle"])}</div></div></div>{photo()}</div>')
        body = hero + bar(c["section"]) + cards(c["items"], cols, big=(cols <= 3)) + boxes(c) + bottom(c)
    elif c["type"] == "tip":
        if len(c["items"]) != 3:
            sys.exit("tip needs exactly 3 items")
        hero = (f'<div class="hero"><div class="hero-main" style="gap:16px">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">{logo()}'
                f'<div class="badge" style="background:{acc}">{E(c["badge"])}</div></div>'
                f'<div style="font-size:72px;font-weight:900;line-height:1">{E(c["title"])}</div>'
                f'<div class="chip" style="font-size:36px;background:#2F5A5C;padding:6px 16px;border-radius:12px">{E(c["chip"])}</div>'
                f'</div>{photo().replace("min-height:270px","")}</div>')
        body = (hero + f'<div class="intro">{E(c["intro"])}</div>' + bar(c["section"])
                + cards(c["items"], 3, big=True) + boxes(c) + bottom(c))
    else:
        sys.exit("type must be infographic or tip")
    return f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div id="root">{body}</div></body></html>'

CHECK = """() => {
  const bad = [];
  const root = document.getElementById('root');
  const rb = root.getBoundingClientRect();
  for (const el of root.querySelectorAll('*')) {
    if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflow === 'hidden') bad.push('clipped: ' + el.className + ' ' + el.textContent.slice(0,40));
    const r = el.getBoundingClientRect();
    if (r.bottom > rb.bottom - 4 || r.right > rb.right + 1 || r.left < rb.left - 1) bad.push('outside image: ' + (el.className||el.tagName) + ' ' + el.textContent.slice(0,40));
  }
  if (root.scrollHeight > root.clientHeight + 1) bad.push('content taller than image by ' + (root.scrollHeight - root.clientHeight) + 'px');
  return [...new Set(bad)].slice(0, 12);
}"""

def main():
    cfg, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    c = json.loads(cfg.read_text(encoding="utf-8"))
    page = out.with_suffix(".html")
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(build(c), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(page.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        bad = pg.evaluate(CHECK)
        pg.screenshot(path=str(out), type="jpeg", quality=90)
        b.close()
    page.unlink()
    if bad:
        print("OVERFLOW – shorten these texts and run again:\n  " + "\n  ".join(bad)); sys.exit(2)
    print(f"ok {out} ({out.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
