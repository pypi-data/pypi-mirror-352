from groq import Groq # Import Groq API
from constants import DEFAULT_API_KEY, DEFAULT_MODEL

def get_api_key_model():
    """
    Prompt the user for API key and model selection.
    Defaults to values in constants if the user presses Enter.
    """
    print("\n🔑 API & Model Selection")
    print("--------------------------------------------------")

    # Prompt for API key
    user_api_key = input(f"Enter your API key (or press Enter to use default): ").strip()
    api_key = user_api_key if user_api_key else DEFAULT_API_KEY

    # Prompt for model selection
    print("\nChoose a model (or press Enter to use the default):")
    print("  1. mistral-saba-24b")
    print("  2. llama3-8b-8192")
    model = DEFAULT_MODEL

    user_model_input = input("Enter your choice [1 or 2]: ").strip()

    if user_model_input == '1':
        model = "mistral-saba-24b"
    elif user_model_input == '2':
        model = "llama3-8b-8192"
    elif user_model_input == '':
        print(f"✨ Using default model: {DEFAULT_MODEL}")
    else:
        print("⚠️  Invalid input. Using default model.")

    print("✅ Configuration complete.\n")
    return api_key, model


def generate_text_from_llm(prompt, api_key, model):

    # Initialize Groq client
    client = Groq(api_key=api_key)  # Replace with your API key

    """Generate text using Groq's Mixtral model."""
    messages = [{"role": "user", "content": prompt}]
    
    # Call Groq API for text generation
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        max_tokens=6000,
        top_p=1,
        stream=True
    )

    # Capture streamed output
    response_text = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text.strip()
