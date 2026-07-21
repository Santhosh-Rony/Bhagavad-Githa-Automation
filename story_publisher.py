import os
import sys
import json
import time
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from logger import logger
from config import Config
from instagram_publisher import wait_for_processing, publish_post

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def create_story_image_container(image_url: str, business_id: str, access_token: str) -> str:
    """
    Create a media container for a STORY from an image URL.
    Stories cannot have captions via the API.
    """
    logger.info("Instagram Story Image upload started (Creating Media Container)")
    url = f"https://graph.instagram.com/v25.0/{business_id}/media"
    
    params = {
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": access_token
    }
    
    response: Optional[requests.Response] = None
    try:
        response = requests.post(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to create story media container. Error: {e}")
        if response is not None:
            logger.error(f"Instagram API Response: {response.text}")
        raise

def publish_story_image(image_url: str) -> str:
    """
    Orchestrates the Instagram publishing process for a STORY image.
    """
    access_token = Config.INSTAGRAM_ACCESS_TOKEN
    business_id = Config.INSTAGRAM_BUSINESS_ID
    
    if not access_token or not business_id:
        raise ValueError("Instagram credentials missing. Cannot publish story.")
        
    container_id = create_story_image_container(image_url, business_id, access_token)
    if not container_id:
        raise RuntimeError("Failed to retrieve a valid container_id for Story from Instagram API")
        
    logger.info(f"Created story media container with ID: {container_id}")
    
    # Images usually process instantly, but wait just in case
    success = wait_for_processing(container_id, access_token)
    if not success:
        raise RuntimeError("Failed to process story image on Instagram servers.")
    
    post_id = publish_post(container_id, business_id, access_token)
    logger.info("Instagram Story Image publish completed")
    return post_id

def main():
    try:
        logger.info("Starting Epic Image Story Publishing Pipeline...")
        
        Config.validate()
        
        metadata_path = os.path.join("output", "story_metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file {metadata_path} not found. Did story_generator.py run successfully?")
            
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        image_url = metadata.get("image_url")
        if not image_url:
            raise ValueError("Invalid metadata. Missing image_url.")
            
        logger.info(f"Loaded public URL: {image_url}")
        
        story_id = publish_story_image(image_url)
        logger.info(f"Successfully published Epic Story with ID: {story_id}")
        
    except Exception as e:
        logger.error(f"Story Publishing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
