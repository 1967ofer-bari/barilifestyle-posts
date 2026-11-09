BariLifestyle postes

## tools/reel – automatic reels
`python3 tools/reel/make_reel.py CONFIG.json posts/YYYY-MM-DD.mp4` builds a 14-second 1080x1920 reel in the brand style
with original, generated background music (tools/reel/music.py – no third-party audio), plus a matching
1080x1350 JPEG (same name, .jpg) for Facebook. CONFIG keys are listed at the top of make_reel.py.

## tools/tip – weekly tip images (infographics)
`python3 tools/tip/render_tip.py CONFIG.json tips/YYYY-MM-DD.jpg` renders a 1080x1350 JPEG in the BariLifestyle
tip style (logo, Ofer's portrait, sage/petrol/bronze palette, Rubik font bundled in tools/tip/fonts).
Two layouts: `infographic` (6/8/9/10 cards) and `tip` (3 steps). Config keys are documented at the top of the script;
examples in tips/configs/. The script exits with code 2 and names the element if any text overflows – shorten and rerun.
Tip images are published on Fridays (posts go out Sundays and Wednesdays).
