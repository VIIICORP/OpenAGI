import pytest
from openagi.chat import AGIChat

def test_agi_chat_initialization():
    chat = AGIChat()
    assert chat.memory == []
    assert "generalization" in chat.SYSTEM_PROMPT.lower()
    assert "common sense" in chat.SYSTEM_PROMPT.lower()

def test_add_to_memory():
    chat = AGIChat()
    chat.add_to_memory("user", "Hello")
    assert len(chat.memory) == 1
    assert chat.memory[0] == {"role": "user", "content": "Hello"}

def test_clear_memory():
    chat = AGIChat()
    chat.add_to_memory("user", "Hello")
    chat.clear_memory()
    assert len(chat.memory) == 0

def test_build_prompt():
    chat = AGIChat()
    prompt = chat._build_prompt("Hi")
    assert chat.SYSTEM_PROMPT in prompt
    assert "User: Hi" in prompt
    assert "AGI:" in prompt

    # Test with memory
    chat.add_to_memory("user", "What is 2+2?")
    chat.add_to_memory("agi", "It's 4.")
    prompt_with_memory = chat._build_prompt("Thanks")
    assert "User: What is 2+2?" in prompt_with_memory
    assert "AGI: It's 4." in prompt_with_memory
    assert "User: Thanks" in prompt_with_memory
