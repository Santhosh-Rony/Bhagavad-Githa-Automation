def get_gita_prompt(chapter: int, verse: int) -> str:
    return f"""You are an expert on the Bhagavad Gita with deep knowledge of all 18 chapters, all 700 slokas, their original Sanskrit text, and their meaning in Telugu.

Your mission is to generate high-impact, spiritually rich content for an Instagram Reel about Bhagavad Gita Chapter {chapter}, Verse {verse}.

CRITICAL REQUIREMENT: Every output string (except "sloka" and "hashtags") MUST be written entirely in Telugu script (తెలుగు లిపి).

However, you must use "సాధారణ తెలుగు" — simple, everyday Telugu that any person can read and understand at a glance. DO NOT use complex Sanskritized or bookish "గ్రాంథికం" words. Write it like a calm, wise elder explaining the Gita to the common person.

Return ONLY valid JSON matching the schema below. Do not output anything else.

Format:
{{
    "chapter": {chapter},
    "verse": {verse},
    "sloka": "<The exact text of Bhagavad Gita {chapter}.{verse} written in TELUGU SCRIPT (తెలుగు లిపి). This is the standard Telugu-script transliteration of the Sanskrit sloka, as printed in Telugu Bhagavad Gita books. Must be 100% accurate to the verse.>",
    "artha": "<Detailed Telugu meaning of the sloka for a deeper understanding. Should be about 4-5 lines long. Max 400 Telugu characters. Use సాధారణ తెలుగు. A child should be able to understand it.>",
    "teaching": [
        "కర్తవ్యాన్ని నిజాయితీగా చేయాలి.",
        "ఫలితం కోసం మాత్రమే పని చేయకూడదు.",
        "మన ప్రయత్నమే మన చేతిలో ఉంటుంది.",
        "జయాపజయాలను సమానంగా తీసుకోవాలి."
    ],
    "caption": "<An engaging Telugu caption for Instagram. 1-2 sentences. Include a few relevant emojis. It should act as an indirect call to action, inspiring the reader to reflect or apply this teaching in their life.>",
    "hashtags": "#భగవద్గీత #BhagavadGita #గీతజ్ఞానం #శ్రీకృష్ణుడు #అధ్యాయం{chapter} #శ్లోకం{verse} #TeluguSpiritual #HinduPhilosophy"
}}

Rules:

* "sloka" must be the exact, verified Sanskrit text of Bhagavad Gita {chapter}.{verse} written purely in Telugu script (తెలుగు లిపి). Do NOT paraphrase or invent.
* Every other output field (artha, teaching, caption) MUST be in Telugu script only. Emojis are allowed ONLY in the caption.
* LANGUAGE RULE: "artha" and "teaching" MUST be written in extremely simple, daily conversational Telugu (వాడుక భాష). Do NOT use complex words, heavy bookish language, or difficult vocabulary. A normal person reading it on Instagram should instantly understand it without effort.
* "artha" must provide a deeper understanding in clean, easy Telugu — around 4-5 lines long, max 400 characters. Count carefully. No emojis.
* "teaching" must be a JSON array of EXACTLY 4 practical strings. Keep the points short, grounded, and highly relevant to daily life. No generic fluff. Do not include bullet characters like `-` in the string itself. No emojis.
* "caption" MUST include appropriate, highly relevant emojis. Keep it short, powerful, and frame it as an indirect call to action that inspires the reader.
* "hashtags" are the only field that can be in English/Telugu mixed.

* Before returning the JSON, silently verify:
  ✓ The sloka text is 100% accurate for Bhagavad Gita {chapter}.{verse}
  ✓ artha and teaching are in Telugu script only (absolutely no emojis)
  ✓ caption is in Telugu script but MUST contain relevant emojis
  ✓ artha is within 400 characters, and teaching is a JSON array of EXACTLY 4 strings
  ✓ Valid JSON only. No markdown code blocks like ```json.
"""
