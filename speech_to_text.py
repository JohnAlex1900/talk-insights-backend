import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

def transcribe_audio(audio_file):
    try:
        # Open the audio file
        with open(audio_file, "rb") as audio:
            # Make API request to OpenAI Whisper model
            response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio, 
                response_format="text"
            )

        # Check if the response is a string (direct transcription text)
        if isinstance(response, str):
            transcript = response  # Directly assign if response is a string
        else:
            # Otherwise, assume the response is a dictionary and access 'text' field
            transcript = response.get('text', None)

        if transcript is None:
            print("Error: No transcription text returned.")
            return None

        print(f"Transcription successful: {transcript}")
        return transcript

    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


