import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Loads GROQ_API_KEY from your .env file

# Best free model on Groq — fast + highest quality
GROQ_MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(prompt: str, system: str = "You are a helpful assistant that analyzes documents.") -> str:
    """Send a prompt to Groq and return the response."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.2,      # Low = more factual, consistent answers
            max_tokens=2048,
        )
        return response.choices[0].message.content

    except Exception as e:
        error = str(e)
        if "api_key" in error.lower():
            return "❌ Invalid or missing GROQ_API_KEY in your .env file."
        elif "rate_limit" in error.lower():
            return "❌ Groq rate limit hit. Wait a moment and try again."
        elif "model" in error.lower():
            return f"❌ Model error: {error}"
        else:
            return f"❌ Groq error: {error}"


def summarize_text(text: str) -> str:
    """Summarize a given text using the LLM."""
    prompt = f"Summarize the following text:\n\n{text}"
    return generate_response(prompt)