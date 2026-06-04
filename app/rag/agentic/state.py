from typing import TypedDict, List, Optional


class RAGState(TypedDict):
    """LangGraph state passed between nodes."""
    query_text: str
    retrieved_chunks: List[dict]
    current_answer: str
    is_grounded: bool
    hallucination_score: float
    feedback: str
    missing_facts: List[str]
    retry_count: int
    final_answer: Optional[str]