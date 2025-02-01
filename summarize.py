from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

def summarize_text(text):
    # Validate that the 'text' is not null or empty
    if not text or text.strip() == "":
        raise ValueError("Text cannot be null or empty.")

    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Summarize the following call transcript."},
                  {"role": "user", "content": text}]
        )
        print(f"Raw response: {response}")
    
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

