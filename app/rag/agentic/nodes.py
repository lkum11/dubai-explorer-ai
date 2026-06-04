from app.rag.agentic.state import RAGState
from app.rag.agentic.schemas import VerifierOutput
import logging

logger = logging.getLogger(__name__)


def generate_node(state: RAGState, client, model: str) -> RAGState:
    """Generate answer from retrieved chunks. Uses feedback if retry."""
    try:
        query_text = state["query_text"]
        chunks = state["retrieved_chunks"]
        feedback = state.get("feedback", "")
        retry_count = state.get("retry_count", 0)

        context = ""
        for index, chunk in enumerate(chunks, start=1):
            context += f"{index}. Title: {chunk['title']}\nText: {chunk['text']}\n\n"

        # On retry — inject verifier feedback into prompt
        feedback_section = ""
        if retry_count > 0 and feedback:
            feedback_section = f"""
        Previous answer was rejected. Reason: {feedback}
        Please correct these issues in your new answer.
        """

        prompt = f"""You are a helpful AI assistant specialised in Dubai travel and attractions.
        Use ONLY the information below to answer accurately and concisely.
        {feedback_section}
        Context:
        {context}

        Question: {query_text}

        Answer (based only on the context above):"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        logger.info(f"Generated answer (retry={retry_count}): {answer[:60]}")

        return {**state, "current_answer": answer}

    except Exception:
        logger.exception("generate_node failed")
        return {**state, "current_answer": "No response generated due to internal error."}


def verify_node(state: RAGState, client, model: str) -> RAGState:
    """Verify answer is grounded in retrieved context using LLM as judge."""
    try:
        answer = state["current_answer"]
        chunks = state["retrieved_chunks"]

        context = ""
        for index, chunk in enumerate(chunks, start=1):
            context += f"{index}. Title: {chunk['title']}\nText: {chunk['text']}\n\n"

        verify_prompt = f"""You are a strict fact-checker for a RAG system.

        Retrieved Context:
        {context}

        Generated Answer:
        {answer}

        Your task: Check if the answer is grounded in the retrieved context.
        Respond in JSON only with this exact structure:
        {{
            "is_grounded": true or false,
            "hallucination_score": 0.0 to 1.0,
            "feedback": "specific feedback on what is wrong",
            "missing_facts": ["fact1", "fact2"]
        }}

        Rules:
        - is_grounded = true only if ALL claims in answer exist in context
        - hallucination_score = 0.0 means perfectly grounded
        - hallucination_score = 1.0 means completely hallucinated
        - feedback = empty string if grounded
        - missing_facts = empty list if grounded"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": verify_prompt}],
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)
        verified = VerifierOutput(**result)

        logger.info(f"Verification result: grounded={verified.is_grounded}, score={verified.hallucination_score}")

        return {
            **state,
            "is_grounded": verified.is_grounded,
            "hallucination_score": verified.hallucination_score,
            "feedback": verified.feedback,
            "missing_facts": verified.missing_facts,
            "final_answer": state["current_answer"] if verified.is_grounded else None
        }

    except Exception:
        logger.exception("verify_node failed — returning current answer as final")
        return {
            **state,
            "is_grounded": True,
            "hallucination_score": 0.0,
            "feedback": "",
            "missing_facts": [],
            "final_answer": state["current_answer"]
        }