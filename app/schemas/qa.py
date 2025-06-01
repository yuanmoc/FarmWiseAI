from typing import Optional, Dict, List
from pydantic import BaseModel

class QuestionCreate(BaseModel):
    question: str
    context: Optional[Dict] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: Optional[List] = None
    context: Optional[Dict] = None
    error: Optional[str] = None 