import json
import time
from google import genai
from openai import OpenAI
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


def _verify_sloka_with_gemini(chapter: int, verse: int, sloka: str) -> bool:
    """
    Second-pass verification: An independent AI call checks if the
    generated sloka is actually the correct verse, not an adjacent one.
    Returns True if verified, False if suspicious.
    """
    logger.info(f"🔍 Running sloka verification for Chapter {chapter}, Verse {verse}...")
    client = genai.Client(api_key=Config.GEMINI_API_KEY)

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


def _generate_with_gemini(prompt: str) -> GitaPost:
    logger.info("Attempting generation with Gemini (gemini-2.5-flash)...")
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    system = (
        "You are an expert on the Bhagavad Gita. "
        "You strictly output valid JSON matching the requested schema. No markdown. No extra text."
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system}\n\n{prompt}"
    )
    content = response.text
    logger.info("Received response from Gemini.")
    return _parse_gita_post(content)


def _generate_with_openrouter(api_key: str, prompt: str) -> GitaPost:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    models_to_try = [
        "openai/gpt-oss-120b:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "google/gemma-4-31b-it:free",
    ]
    last_exc = None
    for model_name in models_to_try:
        logger.info(f"Trying OpenRouter model: {model_name}")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert on the Bhagavad Gita. Output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return _parse_gita_post(content)
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            last_exc = e
            continue
    raise last_exc


def generate_gita_post(chapter: int, verse: int, prompt: str) -> GitaPost:
    """
    Main entry point. Tries Gemini first with retries, then falls back to OpenRouter keys.
    Includes a second-pass AI verification to catch hallucinated/wrong verses.
    """
    last_error = None

    # 1. Try Gemini (with verification loop)
    if Config.GEMINI_API_KEY:
        for attempt in range(1, 4):
            try:
                post = _generate_with_gemini(prompt)
                logger.info(f"Generated Gita post for Chapter {chapter}, Verse {verse} via Gemini (attempt {attempt}).")

                # ── SECOND-PASS VERIFICATION ──
                if _verify_sloka_with_gemini(chapter, verse, post.sloka):
                    logger.info(f"✅ Fully verified Gita post for Chapter {chapter}, Verse {verse}.")
                    return post
                else:
                    logger.warning(f"⚠️ Sloka verification failed on attempt {attempt}. Regenerating...")
                    time.sleep(3)
                    continue

            except Exception as e:
                last_error = e
                wait = 5 * attempt
                logger.warning(f"Gemini attempt {attempt} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
        logger.warning("Gemini exhausted. Falling back to OpenRouter...")
    else:
        logger.warning("GEMINI_API_KEY not set. Using OpenRouter...")

    # 2. Fallback to OpenRouter keys (no verification available for free models)
    for idx, key in enumerate(Config.OPENROUTER_API_KEYS):
        logger.info(f"Trying OpenRouter key #{idx + 1}...")
        try:
            post = _generate_with_openrouter(key, prompt)
            logger.info(f"✅ Generated Gita post via OpenRouter key #{idx + 1}.")
            return post
        except Exception as e:
            logger.warning(f"OpenRouter key #{idx + 1} failed: {e}")
            last_error = e
            continue

    logger.error("All API keys exhausted. Cannot generate content.")
    raise last_error
