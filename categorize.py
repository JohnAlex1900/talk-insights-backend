import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

def categorize_text(summary):
    if not summary or summary.strip() == "":
        raise ValueError("Summary cannot be null or empty.")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract key complaints, insights, categories, and sentiment from the summary. Also, categorize complaints into severity levels (minor, major, critical). Return a JSON object like this: {\"categories\": [...], \"sentiments\": {\"positive\": 0, \"neutral\": 0, \"negative\": 0}, \"complaint_severity\": {\"minor\": [], \"major\": [], \"critical\": []}}."},
                {"role": "user", "content": summary}
            ]
        )

        print(f"New Raw response: {response}")

        # Parse the response into JSON
        response_text = response.choices[0].message.content
        structured_data = json.loads(response_text)  # Convert string to JSON object

        return structured_data
    except json.JSONDecodeError:
        print("Error: Could not parse response into JSON")
        return {"categories": [], "sentiments": {}, "complaint_severity": {"minor": [], "major": [], "critical": []}, "summary": ""}
    except Exception as e:
        print(f"Error during categorization: {e}")
        return {"categories": [], "sentiments": {}, "complaint_severity": {"minor": [], "major": [], "critical": []}, "summary": ""}
