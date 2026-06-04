from langgraph.graph import StateGraph, END
from app.rag.agentic.state import RAGState
from app.rag.agentic.nodes import generate_node, verify_node
from functools import partial
import logging

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def should_retry(state: RAGState) -> str:
    """Conditional edge — decide whether to retry or end."""
    if state["is_grounded"]:
        logger.info("Answer is grounded — returning final answer")
        return "end"

    if state["retry_count"] >= MAX_RETRIES:
        logger.warning(f"Max retries ({MAX_RETRIES}) reached — returning best attempt")
        return "end"

    logger.info(f"Hallucination detected — retrying (attempt {state['retry_count'] + 1})")
    return "retry"


def increment_retry(state: RAGState) -> RAGState:
    """Increment retry count before regenerating."""
    return {**state, "retry_count": state["retry_count"] + 1}


def run_agentic_rag(query_text: str, retrieved_chunks: list, client, model: str) -> dict:
    """Build and run the agentic RAG verification graph."""

    # Bind client and model to nodes
    _generate = partial(generate_node, client=client, model=model)
    _verify = partial(verify_node, client=client, model=model)

    # Build graph
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("generate", _generate)
    graph.add_node("verify", _verify)
    graph.add_node("increment_retry", increment_retry)

    # Entry point
    graph.set_entry_point("generate")

    # Edges
    graph.add_edge("generate", "verify")

    # Conditional edge after verify
    graph.add_conditional_edges(
        "verify",
        should_retry,
        {
            "end": END,
            "retry": "increment_retry"
        }
    )

    # After incrementing retry → regenerate
    graph.add_edge("increment_retry", "generate")

    # Compile and run
    app = graph.compile()

    initial_state: RAGState = {
        "query_text": query_text,
        "retrieved_chunks": retrieved_chunks,
        "current_answer": "",
        "is_grounded": False,
        "hallucination_score": 1.0,
        "feedback": "",
        "missing_facts": [],
        "retry_count": 0,
        "final_answer": None
    }

    result = app.invoke(initial_state)

    # If final_answer not set — use current_answer as fallback
    if not result.get("final_answer"):
        result["final_answer"] = result.get("current_answer", "No answer generated.")

    logger.info(f"Agentic RAG complete — retries={result['retry_count']}, grounded={result['is_grounded']}")
    return result