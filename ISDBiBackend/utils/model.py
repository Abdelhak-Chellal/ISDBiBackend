# ISDBiBackend/utils/model.py

class LLMHandler:
    def __init__(self):
        # Setup API key, model config, etc.
        pass

    def answer(self, question: str, topic: str) -> str:
        # Here you'll later add RAG or direct LLM call logic
        return f"Answer to '{question}' in the context of '{topic}'"
