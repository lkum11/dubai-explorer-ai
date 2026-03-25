import logging
logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, client, model):
        self.model = model
        self.client = client

    # TODO Token efficiency
    def _build_prompt(self, query_text,  retrieved_chunks):
        """Builds the full RAG system prompt from query text and retrieved context chunks."""
        try:
            logger.info(f"Building prompt with {len(retrieved_chunks)} retrieved chunks.")

            context = ""
            for index, chunk in enumerate(retrieved_chunks, start=1):
                context += f"{index}. Title: {chunk['title']} \n Text: {chunk['text']} \n\n"

            system_prompt = f"""
                You are a helpful ai assistant specialized in dubai travel and attractions.
                Use only the information below to answer accurately and concisely.

                Context:
                {context}

                Question: {query_text}

                Answer (Based only on the context above.):   
            """
            return system_prompt.strip()
        except Exception:
            logger.exception(
                f"Failed to build system prompt for query='{query_text[:60]}' "
                f"with {len(retrieved_chunks) if retrieved_chunks else 0} chunks."
            )
    
    def _call_model(self, prompt):
        """Send prompt to OpenAI and return generated text."""
        try:
            logger.info(f"Calling OpenAI model: {self.model}")

            # Using chat.completions — stable, standard API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            answer = response.choices[0].message.content
            if not answer:
                logger.warning("Model returned empty output.")
            return answer
        except Exception:
            logger.exception(f"OpenAI API call failed for model={self.model}")
            return ""

    def generate(self, query_text, retrieved_chunks):
        """
            Generate a RAG-based answer from retrieved context.
            Parameters:
                query_text: str - the user's natural language question.
                retrieved_chunks: list- list of retrieved context chunks.

            Returns:
                str: the generated answer text or fallback message.
        """
        try:
            logger.info(f"Starting generation for query: '{query_text[:60]}'")

            if not retrieved_chunks:
                logger.warning("No chunks retrieved — cannot generate RAG answer.")
                return "I don't have enough information to answer that question based on available data."
            
            prompt = self._build_prompt(query_text, retrieved_chunks)

            if not prompt:
                logger.error("Prompt building failed.")
                return "No response generated due to internal error."
            
            answer = self._call_model(prompt)
            if not answer:
                logger.warning("No answer returned — returning fallback response.")
                return "No response generated due to internal error."

            return answer
        
        except Exception:
            logger.exception(
                f"Failed to generate response for query='{query_text[:60]}' "
                f"with {len(retrieved_chunks) if retrieved_chunks else 0} chunks."
            )
            return "No response generated due to internal error."