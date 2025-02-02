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
                {"role": "system", "content": "Extract key complaints, leads, positive feedback, general information, and sentiment from the summary. Categorize complaints into severity levels (minor, major, critical). Return a JSON object like this: {\"summary\": \"\", \"categories\": [...], \"sentiments\": {\"positive\": 0, \"neutral\": 0, \"negative\": 0}, \"complaint_severity\": {\"minor\": [...], \"major\": [...], \"critical\": [...]}}. Ensure the response includes a 'summary' field."},
                {"role": "user", "content": summary}
            ]
        )

        print(f"New Raw response: {response}")

        response_text = response.choices[0].message.content.strip()

        # Ensure JSON parsing is successful
        try:
            structured_data = json.loads(response_text)
        except json.JSONDecodeError:
            print("Error: OpenAI response is not valid JSON. Raw response:", response_text)
            structured_data = {"summary": summary, "categories": [], "sentiments": {}, "complaint_severity": {"minor": [], "major": [], "critical": []}}

        return structured_data
    except Exception as e:
        print(f"Error during categorization: {e}")
        return {"summary": summary, "categories": [], "sentiments": {}, "complaint_severity": {"minor": [], "major": [], "critical": []}}
