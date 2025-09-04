"""
Basic text generation example using OpenAGI.

This example demonstrates how to:
1. Initialize the OpenAGI platform
2. Load a large language model
3. Generate text from prompts
4. Use different generation parameters
"""

from openagi import OpenAGI

def main():
    print("🚀 OpenAGI Text Generation Example")
    
    # Initialize OpenAGI platform
    agi = OpenAGI()
    
    # Show available LLM models
    llm_models = agi.models.list(category="llm")
    print(f"\n📋 Found {len(llm_models)} LLM models")
    
    # Show some popular models
    popular_models = ["llama2-7b-chat", "mistral-7b-instruct", "vicuna-7b"]
    available_popular = [m for m in popular_models if agi.models.get(m)]
    
    if available_popular:
        model_id = available_popular[0]
        print(f"🤖 Using model: {model_id}")
        
        # Load the model
        print("⏳ Loading model...")
        llm = agi.models.load(model_id)
        print("✅ Model loaded successfully")
        
        # Generate text with different prompts
        prompts = [
            "Explain quantum computing in simple terms:",
            "Write a haiku about artificial intelligence:",
            "What are the benefits of open source AI?",
            "Describe the future of AGI in 100 words:"
        ]
        
        print("\n" + "="*60)
        print("TEXT GENERATION EXAMPLES")
        print("="*60)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n🔹 Example {i}: {prompt}")
            print("-" * 50)
            
            try:
                # Generate response
                response = llm.generate(
                    prompt=prompt,
                    max_length=200,
                    temperature=0.7,
                    do_sample=True
                )
                
                print(f"Response: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Demonstrate chat interface
        print("\n" + "="*60)
        print("CHAT INTERFACE EXAMPLE")
        print("="*60)
        
        conversation = [
            {"role": "user", "content": "Hello! Can you help me understand AI?"},
            {"role": "assistant", "content": "Hello! I'd be happy to help you understand AI. What specific aspect would you like to know about?"},
            {"role": "user", "content": "What's the difference between AI and AGI?"}
        ]
        
        try:
            response = llm.chat(conversation)
            print(f"\n🤖 AI Response: {response}")
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            
    else:
        print("❌ No popular LLM models available")
        print("Available models:")
        for model in llm_models[:5]:
            print(f"  - {model.id}: {model.name}")
    
    print("\n✨ Example completed!")

if __name__ == "__main__":
    main()