from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import json
from fastapi.responses import JSONResponse
from speech_to_text import transcribe_audio
from summarize import summarize_text
from categorize import categorize_text

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://talk-insights.vercel.app"],
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
        "sentiments": insights.get("sentiments", {}),
        "complaint_severity": insights.get("complaint_severity", {})
    }

    return {"transcript": transcript, "summary": summary, "insights": insights}

@app.get("/analysis")
async def get_analysis():
    if not latest_analysis:
        return {"error": "No analysis data available. Please upload an audio file first."}
    
    return latest_analysis

@app.get("/export")
async def export_data():
    if not latest_analysis:
        return JSONResponse(content={"error": "No data available to export."}, status_code=400)
    
    export_filename = "call_summary.json"
    with open(export_filename, "w") as file:
        json.dump(latest_analysis, file, indent=2)
    
    return JSONResponse(content={"message": "Data exported successfully.", "filename": export_filename})
