from pydantic import BaseModel, Field
from typing import List


class VerifierOutput(BaseModel):
    """Structured output from the verifier node."""
    is_grounded: bool = Field(
        description="True if answer is supported by retrieved context"
    )
    hallucination_score: float = Field(
        description="Score between 0-1. 0 = fully grounded, 1 = hallucinated",
        ge=0.0,
        le=1.0
    )
    feedback: str = Field(
        description="Specific feedback on what is wrong or missing"
    )
    missing_facts: List[str] = Field(
        default=[],
        description="Facts in the answer not found in retrieved context"
    )