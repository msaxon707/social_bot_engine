from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from pathlib import Path
from datetime import datetime

from .utils import BASE_DIR, ensure_dir, log, load_json


def create_video_for_post(account_name: str, topic: str, post: dict, image_path: Path | None, style_key: str | None = None) -> Path | None:
    if not image_path or not Path(image_path).exists():
        log(f"[{account_name}] No image found for video generation.")
        return None

    try:
        styles = load_json(BASE_DIR / "config" / "styles.json")
        style_cfg = styles.get(style_key or "default", styles.get("default"))
        # video_style = style_cfg.get("video_style")  # not heavily used yet

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        output_dir = BASE_DIR / "generated" / account_name / date_str
        ensure_dir(output_dir)
        output_path = output_dir / f"{time_str}_video.mp4"

        log(f"[{account_name}] Creating video for: {topic}")

        final_size = (1080, 1920)
        duration = 7  # seconds

        background = ImageClip(str(image_path)).set_duration(duration)
        # Resize/crop to 9:16
        background = background.resize(height=1920)
        if background.w < 1080:
            background = background.resize(width=1080)
        background = background.crop(width=1080, height=1920, x_center=background.w / 2, y_center=background.h / 2)

        title_text = post.get("title", topic)

        txt_clip = TextClip(
            title_text,
            fontsize=70,
            color="white",
            stroke_color="black",
            stroke_width=3,
            font="Arial-Bold"
        ).set_duration(duration).set_position(("center", "bottom")).margin(bottom=120)

        final = CompositeVideoClip([background, txt_clip], size=final_size)
        final.write_videofile(str(output_path), fps=30, codec="libx264", audio=False)

        log(f"[{account_name}] Video saved: {output_path}")
        return output_path

    except Exception as e:
        log(f"[{account_name}] Video generation FAILED for '{topic}': {e}")
        return None