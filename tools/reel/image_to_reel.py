"""Turn a 4:5 post image into a short 9:16 Instagram reel with gentle motion and original music.

Usage: python3 tools/reel/image_to_reel.py IMAGE.jpg OUT.mp4 [MOOD] [SECONDS]
MOOD: calm | warm | uplifting | energetic (see music.py); default warm. SECONDS default 12.
The music seed is the OUT file name, so every post gets its own unique track.
The image stays fully readable: it sits centred on a blurred copy of itself and zooms in very slowly."""
import pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
img, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
mood = sys.argv[3] if len(sys.argv) > 3 else "warm"
dur = float(sys.argv[4]) if len(sys.argv) > 4 else 12.0
FPS = 30
frames = int(dur * FPS)

with tempfile.TemporaryDirectory() as td:
    wav = pathlib.Path(td) / "m.wav"
    subprocess.run([sys.executable, "-I", str(HERE / "music.py"), str(wav), str(dur), mood, out.stem], check=True)
    fc = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,"
        f"eq=brightness=-0.06:saturation=0.85,setsar=1[bg];"
        f"[0:v]scale=w='trunc((960+80*n/{frames})/2)*2':h=-2:eval=frame,setsar=1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fade=t=in:st=0:d=0.4[v]"
    )
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", str(img),
                    "-i", str(wav), "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
print("ok", out, mood)
