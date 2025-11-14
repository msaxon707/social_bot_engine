# engine/video_generator.py

from moviepy.editor import *
from pathlib import Path
from datetime import datetime

from .utils import BASE_DIR, ensure_dir, log


def create_video_for_post(account_name: str, topic: str, post: dict, image_path: Path | None) -> Path | None:
    """
    Create a simple vertical 9:16 slideshow-style video using the image.
    If no image is found, returns None.
    """

    if not image_path or not Path(image_path).exists():
        log(f"[{account_name}] No image found for video generation.")
        return None

    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        # Save to: /generated/<account>/<date>/<time>_video.mp4
        output_dir = BASE_DIR / "generated" / account_name / date_str
        ensure_dir(output_dir)
        output_path = output_dir / f"{time_str}_video.mp4"

        log(f"[{account_name}] Creating video for: {topic}")

        # 9:16 aspect ratio
        final_size = (1080, 1920)

        # 1) Load the PNG as the video background
        background = ImageClip(str(image_path)).set_duration(7)
        background = background.resize(height=1920).crop(width=1080, height=1920, x_center=background.w/2, y_center=background.h/2)

        # 2) Add title text overlay
        txt = post.get("title", topic)
        txt_clip = TextClip(
            txt,
            fontsize=70,
            color="white",
            stroke_color="black",
            stroke_width=3,
            font="Arial-Bold"
        ).set_duration(7).set_position(("center", "bottom")).margin(bottom=120)

        # 3) Final composite
        final = CompositeVideoClip([background, txt_clip], size=final_size)
        final.write_videofile(str(output_path), fps=30, codec="libx264", audio=False)

        log(f"[{account_name}] Video saved: {output_path}")

        return output_path

    except Exception as e:
        log(f"[{account_name}] Video generation FAILED: {e}")
        return None