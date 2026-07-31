import os
from config import Config
from prompt import get_gita_prompt
from ai_content_generator import _generate_with_gemini

def main():
    Config.validate()
    print("Testing AI Sloka Generation for Chapter 1, Verses 33 to 37...\n")
    
    for verse in range(35, 36):
        print(f"--- Requesting Chapter 1, Verse {verse} ---")
        prompt = get_gita_prompt(1, verse)
        
        try:
            # We bypass the verification loop here to see what the raw AI generates
            post = _generate_with_gemini(prompt)
            print(f"Generated Sloka:\n{post.sloka}\n")
            print(f"Audit Trail used by AI:\n{post.audit_trail}\n")
        except Exception as e:
            print(f"Failed to generate for verse {verse}: {e}\n")

if __name__ == "__main__":
    main()
