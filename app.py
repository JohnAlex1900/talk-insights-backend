from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from speech_to_text import transcribe_audio
from summarize import summarize_text
from categorize import categorize_text

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://talk-insights-g961k8fbg-johnalex1900s-projects.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store the latest analysis results
latest_analysis = {}

@app.post('/upload')
async def upload_audio(file: UploadFile = File(...)):
    global latest_analysis  # Allow modifying the global variable

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the file: transcribe, summarize, categorize
    transcript = transcribe_audio(file_path)
    summary = summarize_text(transcript)
    insights = categorize_text(summary)

    # Store the latest analysis
    latest_analysis = {
        "summary": summary,
        "categories": insights.get("categories", []),  # Ensure default if key is missing
        "sentiments": insights.get("sentiments", {})
    }

    return {"transcript": transcript, "summary": summary, "insights": insights}




@app.get("/analysis")
async def get_analysis():
    if not latest_analysis:
        return {"error": "No analysis data available. Please upload an audio file first."}
    
    return latest_analysis

