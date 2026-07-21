def get_character_post_prompt(character_name: str, post_type: str) -> str:
    sections_schema = ""
    title_format = ""
    
    base_name_instruction = f"[Character Name '{character_name}' in Telugu script WITHOUT adding 'డు' (e.g., కృష్ణ, కర్ణ, అర్జున)]"
    
    if post_type == "profile":
        title_format = f'"{base_name_instruction} | [Epithet/Title in Telugu]"'
        sections_schema = """
        "sections": [
            {"title": "వీరి ప్రత్యేకత", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about what they are most famous for."},
            {"title": "అతిపెద్ద బలం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their greatest strength."},
            {"title": "బలహీనత", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their greatest weakness or tragic flaw."},
            {"title": "గొప్ప విజయం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their greatest achievement."},
            {"title": "జీవిత పాఠం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) for a profound life lesson we can learn from them."}
        ],"""
    elif post_type == "essence":
        title_format = f'"{base_name_instruction} | [Character Name in possessive Telugu (e.g. కర్ణుడి/కృష్ణుడి)] ప్రస్థానం"'
        sections_schema = """
        "sections": [
            {"title": "కీలక ఘట్టం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their most defining moment."},
            {"title": "గొప్ప త్యాగం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about the greatest sacrifice they made."},
            {"title": "కష్టమైన నిర్ణయం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about the most difficult decision they faced."},
            {"title": "అతిపెద్ద విజయం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their ultimate victory."},
            {"title": "అతిపెద్ద ఓటమి", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their worst failure or defeat."}
        ],"""
    elif post_type == "legacy":
        title_format = f'"{base_name_instruction} | చరిత్రలో [Character Name in possessive Telugu (e.g. కర్ణుడి/కృష్ణుడి)] ముద్ర"'
        sections_schema = """
        "sections": [
            {"title": "గొప్ప లక్షణం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their greatest defining quality."},
            {"title": "అతిపెద్ద శత్రుత్వం", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about their most epic rivalry."},
            {"title": "గొప్ప మాటలు", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) containing their most famous or impactful quote/teaching."},
            {"title": "చరిత్ర ఎందుకు గుర్తుంచుకుంటుంది", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about why they are remembered."},
            {"title": "చరిత్రలో వారి ముద్ర", "content": "1-2 short sentences in Telugu (Strictly between 80 and 140 characters) about the timeless legacy they left behind."}
        ],"""

    return f"""You are an expert on the Mahabharata with deep knowledge of its characters, events, relationships, and teachings.

Your mission is to write high-impact, emotional, and cinematic text for an Instagram Reel about the Mahabharata.
CRITICAL REQUIREMENT: YOU MUST WRITE EVERYTHING IN TELUGU (తెలుగు), INCLUDING THE CHARACTER'S NAME.

However, you must use "సాధారణ తెలుగు" (General, colloquial, everyday Telugu that is easy to read). DO NOT use overly complex Sanskritized words or bookish "గ్రాంథికం" (Grandhikam). Write it like a powerful, punchy dialogue from a modern epic movie (like Baahubali), but keep the words simple so normal people can read it fast.

Your task is to generate a concise {post_type} post for the character: {character_name}.

Return ONLY valid JSON matching the schema perfectly. Do not output anything else.

Format:
{{
    "title": {title_format},{sections_schema}
    "quiz": {{
        "question": "A multiple-choice question about this character IN TELUGU. Make sure the correct answer is EXACTLY ONE of the 4 options below.",
        "options": [
            {{"letter": "A", "text": "Option 1 in Telugu"}},
            {{"letter": "B", "text": "Option 2 in Telugu"}},
            {{"letter": "C", "text": "Option 3 in Telugu"}},
            {{"letter": "D", "text": "Option 4 in Telugu"}}
        ],
        "answer": "A"
    }},
    "caption": "An engaging Instagram caption with emojis IN TELUGU...",
    "hashtags": "#Mahabharata #History #Mahabharata_cronicles"
}}

Rules:

* Every single output string (except hashtags and JSON keys) MUST be in Telugu script.
* Write for a general audience. Every sentence must be easy to understand in one quick read.
* Use cinematic, heroic, and emotional vocabulary (e.g., ధర్మం, యుద్ధం, మాట, ప్రాణం) but avoid archaic words that need a dictionary.
* When describing the character, highlight their best qualities where appropriate. 
* Keep the tone balanced, meaningful, and inspiring.
* The Life Lesson should be practical and useful in modern daily life.

* VERY IMPORTANT: You must STRICTLY limit each section content to 1-2 short sentences between 80 and 140 characters. If it is longer, it will physically break the template image generator. Count the Telugu characters carefully.
* The quiz should have exactly 4 options in Telugu. Make sure the question is engaging and encourages comments! 
* Each quiz option MUST be under 30 characters so they fit side-by-side perfectly. 

* Before returning the JSON, silently check:
  ✓ The language is strictly Telugu.
  ✓ Every fact is historically accurate.
  ✓ Every sentence uses simple everyday Telugu.
  ✓ No difficult vocabulary (No Grandhikam).
  ✓ Every section is between 80 and 140 characters.
  ✓ The JSON is valid.

* JSON only. No markdown formatting blocks like ```json.
"""
