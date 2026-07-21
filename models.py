from pydantic import BaseModel, Field
from typing import List

class QuizOption(BaseModel):
    letter: str = Field(..., description="A, B, C, or D")
    text: str = Field(..., description="The option text")

class Quiz(BaseModel):
    question: str = Field(..., description="A thought-provoking question about the character")
    options: List[QuizOption] = Field(..., description="Exactly 4 options (A, B, C, D)")
    answer: str = Field(..., description="The correct letter (A, B, C, or D)")

class PostSection(BaseModel):
    title: str = Field(..., description="The title of the section in ALL CAPS")
    content: str = Field(..., description="The content of the section")

class CharacterPost(BaseModel):
    title: str = Field(..., description="Character name and epithet, e.g., 'ARJUNA | The Greatest Archer'")
    sections: List[PostSection] = Field(..., description="The sections of the post")
    quiz: Quiz = Field(..., description="A quiz about the character")
    caption: str = Field(..., description="An engaging Instagram caption asking followers to answer the quiz")
    hashtags: str = Field(..., description="Relevant hashtags e.g., #Mahabharata #Arjuna #HinduMythology")
