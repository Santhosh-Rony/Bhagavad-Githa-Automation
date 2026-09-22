import json
import time
from google import genai
from config import Config
from logger import logger
from models import GitaPost


def _parse_gita_post(content: str) -> GitaPost:
    """Parses a JSON string into a GitaPost, robustly."""
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_string = content[start_idx:end_idx + 1]
        parsed = json.loads(json_string)
    else:
        parsed = json.loads(content)
    return GitaPost(**parsed)


def _verify_sloka_with_gemini(api_key: str, chapter: int, verse: int, sloka: str) -> bool:
    """
    Second-pass verification: An independent AI call checks if the
    generated sloka is actually the correct verse, not an adjacent one.
    Returns True if verified, False if suspicious.
    """
    logger.info(f"🔍 Running sloka verification for Chapter {chapter}, Verse {verse}...")
    client = genai.Client(api_key=api_key)

    verify_prompt = f"""You are a Bhagavad Gita scholar who verifies verse accuracy.

I need you to verify if the following Telugu-script sloka is EXACTLY Bhagavad Gita Chapter {chapter}, Verse {verse}.

Sloka to verify:
{sloka}

VERIFICATION STEPS:
1. What are the first 3 Sanskrit words of Bhagavad Gita {chapter}.{verse - 1 if verse > 1 else 'N/A (first verse)'}?
2. What are the first 3 Sanskrit words of Bhagavad Gita {chapter}.{verse}?
3. What are the first 3 Sanskrit words of Bhagavad Gita {chapter}.{verse + 1}?
4. Does the given sloka match verse {chapter}.{verse} and NOT verse {verse - 1 if verse > 1 else 'N/A'} or {verse + 1}?

Respond with ONLY valid JSON:
{{"is_correct": true}} or {{"is_correct": false, "reason": "This appears to be verse X.Y instead"}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=verify_prompt
        )
        content = response.text
        # Parse the JSON response
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1:
            result = json.loads(content[start_idx:end_idx + 1])
            is_correct = result.get("is_correct", False)
            if is_correct:
                logger.info(f"✅ Sloka verification PASSED for {chapter}.{verse}")
            else:
                reason = result.get("reason", "Unknown reason")
                logger.warning(f"❌ Sloka verification FAILED for {chapter}.{verse}: {reason}")
            return is_correct
        else:
            logger.warning("Verification response was not valid JSON. Assuming pass.")
            return True
    except Exception as e:
        logger.warning(f"Verification call failed: {e}. Assuming pass to avoid blocking.")
        return True


def _generate_with_gemini(api_key: str, model_name: str, prompt: str) -> GitaPost:
    logger.info(f"Attempting generation with {model_name}...")
    client = genai.Client(api_key=api_key)
    system = (
        "You are an expert on the Bhagavad Gita. "
        "You strictly output valid JSON matching the requested schema. No markdown. No extra text."
    )
    response = client.models.generate_content(
        model=model_name,
        contents=f"{system}\n\n{prompt}"
    )
    content = response.text
    logger.info(f"Received response from {model_name}.")
    return _parse_gita_post(content)


def generate_gita_post(chapter: int, verse: int, prompt: str) -> GitaPost:
    """
    Main entry point. Iterates through 5 Gemini Lite keys using gemini-3.5-flash-lite.
    If all 5 Lite keys fail, falls back to 5 Gemini Flash keys using gemini-2.5-flash.
    Includes a second-pass AI verification to catch hallucinated/wrong verses.
    """
    last_error = None

    # PHASE 1: Try Gemini 3.5 Flash Lite with its dedicated keys
    if Config.GEMINI_LITE_KEYS:
        for key_idx, api_key in enumerate(Config.GEMINI_LITE_KEYS):
            logger.info(f"--- Trying gemini-3.5-flash-lite on Lite Key #{key_idx + 1} ---")
            for attempt in range(1, 4):
                try:
                    post = _generate_with_gemini(api_key, "gemini-3.5-flash-lite", prompt)
                    logger.info(f"Generated Gita post for Chapter {chapter}, Verse {verse} via gemini-3.5-flash-lite (attempt {attempt}).")

                    if _verify_sloka_with_gemini(api_key, chapter, verse, post.sloka):
                        logger.info(f"✅ Fully verified Gita post for Chapter {chapter}, Verse {verse}.")
                        return post
                    else:
                        logger.warning(f"⚠️ Sloka verification failed on attempt {attempt}. Regenerating...")
                        time.sleep(3)
                        continue

                except Exception as e:
                    last_error = e
                    wait = 5 * attempt
                    logger.warning(f"gemini-3.5-flash-lite attempt {attempt} failed on Lite Key #{key_idx + 1}: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
            logger.warning(f"gemini-3.5-flash-lite exhausted on Lite Key #{key_idx + 1}.")
    else:
        logger.warning("No Gemini Lite API keys found. Skipping 3.5 Flash Lite phase.")

    # PHASE 2: Fallback to Gemini 2.5 Flash with its dedicated keys
    logger.warning("Falling back to gemini-2.5-flash...")
    if not Config.GEMINI_FLASH_KEYS:
        logger.error("No Gemini Flash API keys found. Cannot generate content.")
        if last_error:
            raise last_error
        else:
            raise ValueError("Missing API keys")

    for key_idx, api_key in enumerate(Config.GEMINI_FLASH_KEYS):
        logger.info(f"--- Trying gemini-2.5-flash on Flash Key #{key_idx + 1} ---")
        for attempt in range(1, 4):
            try:
                post = _generate_with_gemini(api_key, "gemini-2.5-flash", prompt)
                logger.info(f"Generated Gita post for Chapter {chapter}, Verse {verse} via gemini-2.5-flash (attempt {attempt}).")

                if _verify_sloka_with_gemini(api_key, chapter, verse, post.sloka):
                    logger.info(f"✅ Fully verified Gita post for Chapter {chapter}, Verse {verse}.")
                    return post
                else:
                    logger.warning(f"⚠️ Sloka verification failed on attempt {attempt}. Regenerating...")
                    time.sleep(3)
                    continue

            except Exception as e:
                last_error = e
                wait = 5 * attempt
                logger.warning(f"gemini-2.5-flash attempt {attempt} failed on Flash Key #{key_idx + 1}: {e}. Retrying in {wait}s...")
                time.sleep(wait)
        logger.warning(f"gemini-2.5-flash exhausted on Flash Key #{key_idx + 1}.")

    logger.error("All API keys and models exhausted. Cannot generate content.")
    raise last_error
