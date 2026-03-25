from unittest.mock import MagicMock
from app.rag.generator import Generator
from app.config import GENERATION_MODEL


class TestGenerator:

    def test_empty_chunks_returns_no_info_message(self):
        mock_client = MagicMock()
        generator = Generator(client=mock_client, model=GENERATION_MODEL)

        result = generator.generate(
            query_text="What are attractions at Palm Jumeirah?",
            retrieved_chunks=[]
        )

        assert "don't have enough information" in result.lower()
        mock_client.chat.completions.create.assert_not_called()
    
    def test_valid_chunks_calls_openai(self, retrieved_chunks):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Burj Khalifa is tall."
        generator = Generator(client=mock_client, model=GENERATION_MODEL)

        result = generator.generate(
            query_text="What is Burj Khalifa?",
            retrieved_chunks=retrieved_chunks
        )

        assert result == "Burj Khalifa is tall."
        mock_client.chat.completions.create.assert_called_once()

    def test_openai_failure_returns_fallback(self, retrieved_chunks):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("OpenAI down")
        generator = Generator(client=mock_client, model=GENERATION_MODEL)

        result = generator.generate(
            query_text="What is Burj Khalifa?",
            retrieved_chunks=retrieved_chunks
        )

        assert "error" in result.lower()

    def test_prompt_contains_query_and_context(self, retrieved_chunks):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "answer"
        generator = Generator(client=mock_client, model=GENERATION_MODEL)

        generator.generate(
            query_text="What is Burj Khalifa?",
            retrieved_chunks=retrieved_chunks
        )

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        prompt = messages[0]["content"]
        assert "What is Burj Khalifa?" in prompt
        assert "Burj Khalifa" in prompt