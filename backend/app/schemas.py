from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResponse(BaseModel):
    filename: str
    status: str
    total_pages: int
    extracted_chunks: int

class CalculationDetail(BaseModel):
    operation: str
    formula: str
    substituted_values: str
    result: float
    formatted_result: str
    explanation: str

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2)

class AnswerResponse(BaseModel):
    question: str
    answer: str
    source_pages: List[int]
    calculation: Optional[CalculationDetail] = None
    retrieved_passages: List[str]
    used_fallback_model: bool

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
