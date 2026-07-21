import os
import shutil
from logger import logger

def upload_video(video_path: str) -> str:
    """
    Returns the raw.githubusercontent.com URL for the video in the output/ folder.
    This bypasses GitHub Pages entirely and is available instantly after git push.
    """
    filename = os.path.basename(video_path)
    
    # Expected public URL based on GitHub Raw Content convention
    github_user = os.environ.get("GITHUB_USERNAME", "Santhosh-Rony")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "mahabharata_chronicles").split("/")[-1]
    
    public_url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/output/{filename}"
    
    logger.info(f"Generated raw public URL: {public_url}")
    return public_url
