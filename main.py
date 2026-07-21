import os
import sys
import datetime
import argparse
from logger import logger
from config import Config
from characters import MAHABHARATA_CHARACTERS
from history import load_history, save_history, get_posting_state, update_posting_state, clear_posting_state
from prompt import get_character_post_prompt
from ai_content_generator import generate_character_post
from template_renderer import render_reel_image
from video_generator import generate_video
from video_uploader import upload_video
import json
# from instagram_publisher import publish_reel

def main():
    parser = argparse.ArgumentParser(description="Generate Mahabharata Reels.")
    parser.add_argument("type", choices=["profile", "essence", "legacy"], help="Type of post to generate")
    args = parser.parse_args()
    
    post_type = args.type

    try:
        logger.info(f"Starting Mahabharata Reels Automation for post type: {post_type.upper()}")
        Config.validate()

        # 1. Select the character based on state tracking
        state = get_posting_state()
        today_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        
        # Define Generic Music Sequence
        generic_music_files = [
            "music/music.mp3", "music/music1.mp3", "music/music2.mp3", "music/music3.mp3",
            "music/music4.mp3", "music/music5.mp3", "music/music6.mp3", "music/music7.mp3",
            "music/music8.mp3", "music/music9.mp3", "music/music10.mp3", "music/music11.mp3"
        ]
        
        # If it's a new day, we force an advance to the next character!
        if state.get("date") != today_date:
            logger.info(f"New day detected ({today_date})! Advancing to the next character.")
            if state.get("current_character"):
                # Save yesterday's character to history so we don't repeat them
                save_history(state["current_character"])
                    
            clear_posting_state()
            state = get_posting_state() # Reload clean state
            state["date"] = today_date
            
        current_character = state["current_character"]
        
        if not current_character:
            # Pick a fresh character!
            past_characters = load_history()
            available_characters = [c for c in MAHABHARATA_CHARACTERS if c not in past_characters]
            
            if not available_characters:
                logger.error("All characters have been posted! Add more to characters.py")
                sys.exit(1)
                
            current_character = available_characters[0]
            logger.info(f"Selected new daily Character: {current_character}")
            state["current_character"] = current_character
            state["date"] = today_date
            # Immediately save the state so other jobs know who today's character is
            update_posting_state(current_character, today_date, state.get("generic_music_index"))
        else:
            logger.info(f"Resuming daily Character: {current_character}")
            
        logger.info(f"--- Generating {post_type.upper()} post for {current_character} ---")
        
        # 2. Generate Content
        prompt = get_character_post_prompt(current_character, post_type)
        post = generate_character_post(prompt)
        
        # 3. Render Image
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        template_path = "templates/mahabharata_bg.png"
        image_output_path = f"output/{current_character}_{post_type}_{timestamp}.png"
        
        render_reel_image(post, template_path, image_output_path)
        
        # 4. Select Audio and Generate Video
        # Determine which background music to use
        char_lower = current_character.lower()
        next_generic_idx = state.get("generic_music_index", 0) # Keep current index by default
        
        if char_lower == "krishna":
            audio_path = "music/krishna.mp3"
        elif char_lower == "karna":
            if post_type == "profile":
                audio_path = "music/karna_1.mp3"
            elif post_type == "essence":
                audio_path = "music/karna_2.mp3"
            else: # legacy
                audio_path = "music/karna_3.mp3"
        elif char_lower == "arjuna":
            if post_type == "profile":
                audio_path = "music/arjuna_1.mp3"
            elif post_type == "essence":
                audio_path = "music/arjuna_2.mp3"
            else: # legacy
                audio_path = "music/arjuna_3.mp3"
        else:
            idx = state.get("generic_music_index", 0)
            audio_path = generic_music_files[idx]
            # Advance the generic music index for the NEXT post, looping if necessary
            next_generic_idx = (idx + 1) % len(generic_music_files)
            
        logger.info(f"Selected Audio Track: {audio_path}")
        video_output_path = f"output/{current_character}_{post_type}_{timestamp}.mp4"
        
        if os.path.exists(audio_path):
            generate_video(image_output_path, audio_path, video_output_path, duration=10)
            logger.info(f"Video ready for Instagram: {video_output_path}")
            
            # Save the generated caption to a text file for easy copy-pasting
            caption_path = f"output/{current_character}_{post_type}_{timestamp}.txt"
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(post.caption + "\n\n" + post.hashtags)
            logger.info(f"Caption and Hashtags saved to: {caption_path}")
            
            # Prepare Video for GitHub Pages
            video_url = upload_video(video_output_path)
            
            # Save metadata for publish_instagram.py
            metadata = {
                "video_url": video_url,
                "caption": f"{post_caption}\n\n{post.hashtags}" if 'post_caption' in locals() else f"{post.caption}\n\n{post.hashtags}"
            }
            metadata_path = os.path.join("output", "post_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Metadata saved to {metadata_path}. Generation complete. Awaiting GitHub Actions sync.")
        else:
            logger.warning(f"Audio file '{audio_path}' not found! Generated static image only.")
            
        # 5. Update State
        update_posting_state(current_character, today_date, next_generic_idx)
        
        logger.info("Automation completed successfully.")

    except Exception as e:
        logger.error(f"Application run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
