BariLifestyle postes

## tools/reel – automatic reels with original music
- `python3 tools/reel/make_reel.py CONFIG.json posts/YYYY-MM-DD.mp4` – animated 14-second 1080x1920 reel in the brand style,
  plus a matching 1080x1350 JPEG (same name, .jpg) for Facebook. CONFIG keys are listed at the top of make_reel.py;
  set `"mood"` to fit the content.
- `python3 tools/reel/image_to_reel.py IMAGE.jpg OUT.mp4 MOOD [SECONDS]` – turns any 4:5 post image into a 12-second
  9:16 reel (image fully visible, slow zoom, blurred background) with music – used so image posts also go to
  Instagram with music.
- `tools/reel/music.py` – ORIGINAL music synthesised from scratch (no samples, no third-party audio, no rights issues).
  Every post gets its own unique track: the seed (default: output file name / post date) picks key, chords, melody,
  rhythm and tempo. Moods: calm (mindset, reflection, personal story), warm (story, community, products/services),
  uplifting (motivation, achievements, teasers), energetic (fitness, workouts, challenges).

## tools/reel/site_reel.py – Saturday-night website video (from 21.11.2026)
- `python3 tools/reel/site_reel.py site/configs/YYYY-MM-DD.json site/YYYY-MM-DD.mp4` – ~18-second 9:16 slideshow made ONLY
  from images on barilifestyle.com (downloaded at render time), original music, closing card with the site address.
  Also writes `site/YYYY-MM-DD.jpg` (1080x1350 closing card) for Facebook. Config keys are listed at the top of the script.
- Published every Saturday at 20:30: Instagram gets the video ("קישור בביו"), Facebook gets the closing card with a
  clickable link to the page (with utm_campaign=saturday_site).
