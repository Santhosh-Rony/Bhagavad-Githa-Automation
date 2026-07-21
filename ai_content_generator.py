import os
import json
import time
from openai import OpenAI
from google import genai
from config import Config
from logger import logger
from models import CharacterPost

def _generate_with_key(api_key: str, dynamic_prompt: str) -> CharacterPost:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    try:
        models_to_try = [
            "openai/gpt-oss-120b:free",
            "qwen/qwen3-next-80b-a3b-instruct:free"
        ]
        
        last_exception = None
        for model_name in models_to_try:
            logger.info(f"Attempting content generation using model: {model_name}")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that strictly outputs valid JSON data matching the requested schema. You are an expert at clear, concise writing. Return ONLY JSON."
                        },
                        {
                            "role": "user",
                            "content": dynamic_prompt
                        }
                    ],
                    temperature=0.7,
                )

                content = response.choices[0].message.content
                logger.info("Successfully received response from AI")
                
                # Parse JSON
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_string = content[start_idx:end_idx+1]
                    parsed_json = json.loads(json_string)
                else:
                    parsed_json = json.loads(content)
                
                # Validate against Pydantic Model
                post = CharacterPost(**parsed_json)
                return post
            
            except Exception as e:
                logger.warning(f"Failed to generate with {model_name}: {e}")
                last_exception = e
                continue
                
        logger.error("All models failed.")
        raise last_exception
        
    except Exception as e:
        logger.error(f"Failed to generate AI content: {e}")
        raise

def _generate_with_gemini(api_key: str, dynamic_prompt: str) -> CharacterPost:
    logger.info("Attempting content generation using model: gemini-2.5-flash")
    client = genai.Client(api_key=api_key)
    
    # We use a system-like instruction prefix in the contents for Gemini
    system_instruction = "You are a helpful assistant that strictly outputs valid JSON data matching the requested schema. You are an expert at clear, concise writing. Return ONLY JSON.\n\n"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_instruction + dynamic_prompt
        )
        
        content = response.text
        logger.info("Successfully received response from Gemini API")
        
        # Parse JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_string = content[start_idx:end_idx+1]
            parsed_json = json.loads(json_string)
        else:
            parsed_json = json.loads(content)
        
        # Validate against Pydantic Model
        post = CharacterPost(**parsed_json)
        return post
        
    except Exception as e:
        logger.error(f"Failed to generate AI content with Gemini: {e}")
        raise

def generate_character_post(dynamic_prompt: str) -> CharacterPost:
    last_error = None
    
    # 1. Try Gemini first (Primary)
    if Config.GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY found. Attempting generation with Gemini...")
        max_retries = 5
        for attempt in range(max_retries + 1):
            try:
                return _generate_with_gemini(Config.GEMINI_API_KEY, dynamic_prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"Gemini attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"Gemini failed after {max_retries} retries. Falling back to OpenRouter...")
    else:
        logger.warning("GEMINI_API_KEY not found. Skipping Gemini and using OpenRouter...")

    # 2. Fallback to OpenRouter keys
    api_keys = Config.OPENROUTER_API_KEYS
    valid_keys = [k for k in api_keys if k and k.strip()]
    
    if not valid_keys:
        logger.error("No valid OpenRouter fallback keys found!")
        if last_error:
            raise last_error
        raise ValueError("No API keys configured.")
        
    for idx, key in enumerate(valid_keys):
        logger.info(f"Attempting fallback generation using OpenRouter Key #{idx+1}...")
        try:
            return _generate_with_key(key, dynamic_prompt)
        except Exception as e:
            logger.warning(f"OpenRouter Key #{idx+1} failed: {e}")
            last_error = e
            continue
            
    logger.error("All available API keys (Gemini and OpenRouter) exhausted.")
    raise last_error
