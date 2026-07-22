from pydantic import BaseModel, Field

class GitaPost(BaseModel):
    chapter: int = Field(..., description="Chapter number (1-18)")
    verse: int = Field(..., description="Verse number within the chapter")
    sloka: str = Field(..., description="The original Sanskrit sloka transliterated in Telugu script (తెలుగు లిపి)")
    artha: str = Field(..., description="Detailed Telugu meaning of the sloka for a deeper understanding, approx 4-5 lines (max 400 chars). Must use very simple, daily conversational Telugu.")
    teaching: list[str] = Field(..., description="What this sloka teaches us, formatted as a list of EXACTLY 4 short practical points in simple daily conversational Telugu.")
    caption: str = Field(..., description="Engaging Telugu Instagram caption, no emojis")
    hashtags: str = Field(..., description="Relevant hashtags")
