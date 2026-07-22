import os
import sys
import json
import datetime
from logger import logger
from config import Config
from gita_state import load_state, get_current_verse, get_current_music, advance_state
from prompt import get_gita_prompt
from ai_content_generator import generate_gita_post
from template_renderer import render_gita_image
from video_generator import generate_video
from video_uploader import upload_video


TEMPLATE_PATH = "templates/bhagavad_gita_bg.png"


def main():
    try:
        logger.info("═══════════════════════════════════════════════")
        logger.info("   Bhagavad Gita Automation — Starting Run")
        logger.info("═══════════════════════════════════════════════")

        Config.validate()

        # 1. Read current chapter & verse
        chapter, verse = get_current_verse()
        logger.info(f"📖 Posting: Chapter {chapter}, Verse {verse}")

        # 2. Build prompt and generate content
        prompt = get_gita_prompt(chapter, verse)
        post = generate_gita_post(chapter, verse, prompt)

        # 3. Select CTA in a loop based on verse number
        CTAS = [
            "ఈ శ్లోకంలోని ఏ వాక్యం మీకు ఎక్కువగా నచ్చింది?",
            "ఈ శ్లోకం మీకు ఏమి నేర్పింది? కామెంట్లో చెప్పండి.",
            "ఈ బోధను మీరు మీ జీవితంలో ఎలా అనుసరిస్తారు?",
            "ఈ శ్లోకం మీ మనసును తాకిందా? మీ అభిప్రాయాన్ని పంచుకోండి.",
            "ఈ శ్లోకాన్ని వినాల్సిన వ్యక్తి ఎవరు? వారిని ట్యాగ్ చేయండి.",
            "ఈ శ్లోకం గురించి మీ అర్థం ఏమిటి? కామెంట్ చేయండి."
        ]
        # (verse - 1) makes sure verse 1 gets index 0, etc.
        selected_cta = CTAS[(verse - 1) % len(CTAS)]

        # 4. Render image
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        image_path = os.path.join(Config.OUTPUT_DIR, f"gita_ch{chapter}_v{verse}_{timestamp}.png")
        render_gita_image(post, selected_cta, TEMPLATE_PATH, image_path)

        # 5. Select music and generate video
        audio_path = get_current_music()
        video_path = os.path.join(Config.OUTPUT_DIR, f"gita_ch{chapter}_v{verse}_{timestamp}.mp4")

        if os.path.exists(audio_path):
            generate_video(image_path, audio_path, video_path, duration=15)
            logger.info(f"🎬 Video generated: {video_path}")
        else:
            logger.warning(f"Audio file not found: {audio_path}. Skipping video.")
            sys.exit(1)

        # 5. Upload video to GitHub Pages for public URL
        video_url = upload_video(video_path)
        logger.info(f"🌐 Video URL: {video_url}")

        # 6. Save metadata for publish_instagram.py
        caption_full = f"{post.caption}\n\n{selected_cta}\n\n{post.hashtags}"
        metadata = {
            "video_url": video_url,
            "caption": caption_full,
        }
        metadata_path = os.path.join(Config.OUTPUT_DIR, "post_metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        logger.info(f"📋 Metadata saved: {metadata_path}")

        # 7. Advance state to next verse ONLY after successful completion
        advance_state()

        logger.info(f"✅ Successfully completed: Chapter {chapter}, Verse {verse}")
        logger.info("═══════════════════════════════════════════════")

    except Exception as e:
        logger.error(f"Application run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
