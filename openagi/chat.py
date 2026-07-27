import logging
from typing import List, Dict, Any, Optional

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

logger = logging.getLogger(__name__)

class AGIChat:
    """
    AGI Chat implementation designed to mimic cognitive abilities of the human brain,
    including generalization (transferring knowledge across domains) and
    common sense knowledge (reasoning based on worldly facts and norms).
    """

    SYSTEM_PROMPT = (
        "You are an AGI (Artificial General Intelligence) system. "
        "You possess the cognitive abilities of the human brain. "
        "1. Generalization: You can transfer knowledge and skills learned in one domain "
        "to another, adapting to new and unseen situations effectively. "
        "2. Common Sense: You have a vast repository of knowledge about the world, "
        "including facts, relationships, and social norms, allowing you to reason "
        "and make decisions based on this common understanding. "
        "Answer the user's queries by explicitly utilizing these capabilities."
    )

    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize the AGI Chat with a language model.
        """
        self.model_name = model_name
        self.memory: List[Dict[str, str]] = []

        if pipeline is None:
            logger.warning("transformers library not found. Running in mock mode.")
            self.generator = None
        else:
            try:
                # Using text-generation pipeline.
                # For a real AGI, a more capable model (like a large instruct model) would be used.
                self.generator = pipeline("text-generation", model=model_name)
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                self.generator = None

    def add_to_memory(self, role: str, content: str) -> None:
        """
        Store interaction in short-term memory to support contextual reasoning.
        """
        self.memory.append({"role": role, "content": content})

    def _build_prompt(self, user_input: str) -> str:
        """
        Build a prompt combining system instructions, memory, and current input.
        """
        prompt = self.SYSTEM_PROMPT + "\n\n"

        # Include a summary of recent memory (simulating context/generalization)
        if self.memory:
            prompt += "Previous conversation:\n"
            for msg in self.memory[-5:]: # Keep last 5 interactions for context
                role = "AGI" if msg['role'].lower() == "agi" else msg['role'].capitalize()
                prompt += f"{role}: {msg['content']}\n"

        prompt += f"\nUser: {user_input}\nAGI:"
        return prompt

    def generate_response(self, user_input: str, max_length: int = 150) -> str:
        """
        Generate a response that demonstrates generalization and common sense.
        """
        # Build prompt BEFORE adding current input to memory to avoid duplicating it
        prompt = self._build_prompt(user_input)

        self.add_to_memory("user", user_input)

        if not self.generator:
            # Fallback mock response for testing/demonstration without model weights
            response = (
                "As an AGI, I recognize the context of your query. Applying my common sense "
                "knowledge and generalizing from related domains, here is my insight: "
                "[Mock Response: Please install transformers and download a model for actual text generation]."
            )
            self.add_to_memory("agi", response)
            return response

        try:
            # Generate response
            outputs = self.generator(
                prompt,
                max_new_tokens=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256 # Default pad token for GPT-2
            )

            # Extract generated text
            full_text = outputs[0]["generated_text"]
            # Extract just the AGI's response part
            response = full_text[len(prompt):].strip()

            # Simple cleanup if the model hallucinates a User follow-up
            if "\nUser:" in response:
                response = response.split("\nUser:")[0].strip()

            self.add_to_memory("agi", response)
            return response

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "I apologize, my cognitive processes encountered an error."

    def clear_memory(self) -> None:
        """
        Clear the short-term memory.
        """
        self.memory = []
