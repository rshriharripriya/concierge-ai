"""
Structured response models for RAG outputs.
Enforces JSON schema alongside conversational text for precise data extraction.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class TaxAdvice(BaseModel):
    """Structured tax advice response with extractable data"""
    
    answer_text: str = Field(
        ..., 
        description="The conversational answer for the user"
    )
    
    deductible_amount: Optional[float] = Field(
        None, 
        description="Estimated deduction value if applicable"
    )
    
    relevant_form: Optional[str] = Field(
        None, 
        description="IRS form number (e.g., 'Form 1040 Schedule C', '8889')"
    )
    
    deadline: Optional[str] = Field(
        None, 
        description="Important deadline if mentioned (e.g., '4/15/2024')"
    )
    
    confidence_score: int = Field(
        ..., 
        ge=1, 
        le=5,
        description="Confidence in this advice (1=low, 5=high)"
    )
    
    key_facts: List[str] = Field(
        default_factory=list,
        description="Bullet points of key takeaways"
    )
    
    requires_expert: bool = Field(
        False,
        description="Whether this should be escalated to human expert"
    )

class DisambiguationResponse(BaseModel):
    """Response when query needs clarification"""
    
    clarification_question: str = Field(
        ...,
        description="Question to ask the user"
    )
    
    missing_info: List[str] = Field(
        ...,
        description="What information is needed"
    )
    
    suggested_options: Optional[List[str]] = Field(
        None,
        description="Multiple choice options if applicable"
    )
