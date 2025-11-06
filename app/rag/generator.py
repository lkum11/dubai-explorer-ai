import logging
logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, client, model):
        self.model = model
        self.client = client

    # TODO Token efficiency
    def _build_prompt(self, query_text,  retrieved_chunks):
        """Builds the full RAG system prompt from query text and retrieved context chunks."""

        # System Role: define assistant purpose
        # Context: retrieved evidence
        # Question: user query
        # Answer (based only on the context above):
        try:
            logger.info(f"Building prompt with {len(retrieved_chunks)} retrieved chunks.")
            if not retrieved_chunks:
                logger.warning(f"No retrieved chunks provided — building minimal prompt")
            context = ""
            for index, chunk in enumerate(retrieved_chunks, start=1):
                context += f"{index}. Title: {chunk['title']} \n Text: {chunk['text']} \n\n"

            system_prompt = f"""
                You are a helpful ai assistant specialized in dubai travel and attractions.
                Use only the information below to answer accurately and concisely.

                Context:
                {context}

                Question: {query_text}

                Answer (Based on the information in the context, summarize the attractions, hotels, and notable places at Palm Jumeirah. 
                List them clearly and concisely.):   
            """
            return system_prompt.strip()
        except Exception:
            logger.exception(
                f"Failed to build system prompt for query='{query_text[:60]}' "
                f"with {len(retrieved_chunks) if retrieved_chunks else 0} chunks."
            )
    
    def _call_model(self, prompt):
        """
            Send the constructed prompt to the OpenAI model.
            Input: Prompt 
            Returns: Generated text or None if the API call fails.
        """
        try:
            logger.info(f"Calling OpenAI model: {self.model}")
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "You are a helpful ai assistant..."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            if not response.output_text:
                logger.warning("Model returned empty output.")
            return response.output_text
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
            prompt = self._build_prompt(query_text, retrieved_chunks)
            answer = self._call_model(prompt)
            if not answer:
                logger.warning("No data availbale - returning fallback response.")
                return "No data available now, please check later"

            return answer
        
        except Exception:
            logger.exception(
                f"Failed to generate response for query='{query_text[:60]}' "
                f"with {len(retrieved_chunks) if retrieved_chunks else 0} chunks."
            )
            return "No response generated due to internal error."