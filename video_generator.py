import os
import subprocess
from logger import logger

def generate_video(image_path: str, audio_path: str, output_path: str, duration: int = 5):
    """
    Uses FFmpeg to combine a static image and an audio file into an MP4 video.
    """
    logger.info(f"Generating video from {image_path} and {audio_path}...")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}. Please add your music file.")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # FFmpeg command to loop the image, add the audio, and cut at 'duration'
    # Uses x264 codec for max Instagram compatibility, pixel format yuv420p
    cmd = [
        "ffmpeg",
        "-y", # Overwrite output
        "-loop", "1", # Loop the single image
        "-i", image_path,
        "-stream_loop", "-1", # Loop the audio indefinitely
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration), # Force exact duration
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Video generated successfully at {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode('utf-8')}")
        raise
