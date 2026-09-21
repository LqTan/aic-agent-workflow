from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "BE" / "data_processing"
FRAME_ROOT = DATA_ROOT / "keyframes" / "DEMO_V001"
VIDEO_ROOT = DATA_ROOT / "videos"

SCENES = [
    ("001", "NGƯỜI ĐI XE ĐẠP", "person · bicycle · street", "#0F766E", "bicycle"),
    ("002", "PHỤ NỮ ÁO ĐỎ ĐI BỘ", "woman · red shirt · walking", "#BE123C", "walking"),
    ("003", "NGƯỜI ĐÀN ÔNG ĐI XE MÁY", "man · motorcycle · street", "#1D4ED8", "motorcycle"),
    ("004", "Ô TÔ TRÊN ĐƯỜNG PHỐ", "person · car · driving", "#7C3AED", "car"),
    ("005", "TRẺ EM CHẠY CÙNG CHÓ", "child · dog · beach", "#C2410C", "dog"),
    ("006", "PHỤ NỮ DÙNG ĐIỆN THOẠI", "woman · phone · office", "#334155", "phone"),
]


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def create_frame(index: int, code: str, title: str, concepts: str, color: str, icon: str):
    image = Image.new("RGB", (1280, 720), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1280, 130), fill=color)
    draw.text((64, 42), "AIC 2026 · DEMO KEYFRAME", fill="white", font=font(34, True))
    draw.rounded_rectangle((70, 190, 1210, 610), radius=28, fill="white", outline="#CBD5E1", width=3)
    draw.ellipse((120, 250, 350, 480), fill=color)
    draw.text((170, 305), str(index), fill="white", font=font(96, True))
    draw.text((410, 250), title, fill="#0F172A", font=font(46, True))
    draw.text((410, 335), concepts, fill="#475569", font=font(30))
    draw.text((410, 410), f"tool: CLIP + metadata · label: {icon}", fill=color, font=font(26, True))
    draw.text((70, 665), "Dữ liệu minh họa cục bộ — chuyển sang AIC thật bằng biến môi trường", fill="#64748B", font=font(22))
    image.save(FRAME_ROOT / f"{code}.png", quality=92)


def main():
    FRAME_ROOT.mkdir(parents=True, exist_ok=True)
    VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
    for index, scene in enumerate(SCENES, start=1):
        create_frame(index, *scene)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("Created PNG keyframes. ffmpeg not found; demo video was skipped.")
        return
    concat_file = DATA_ROOT / "demo-video.txt"
    concat_file.write_text(
        "".join(
            f"file '{(FRAME_ROOT / f'{code}.png').as_posix()}'\nduration 3\n"
            for code, *_ in SCENES
        ) + f"file '{(FRAME_ROOT / '006.png').as_posix()}'\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-movflags", "+faststart",
            str(VIDEO_ROOT / "DEMO_V001.mp4"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    concat_file.unlink(missing_ok=True)
    print(f"Demo assets created in {DATA_ROOT}")


if __name__ == "__main__":
    main()
