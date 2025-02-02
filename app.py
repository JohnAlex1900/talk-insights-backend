import shutil
import os
import json
import csv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
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
        return {"summary": "", "categories": [], "sentiments": {}, "complaint_severity": {}}
    return latest_analysis

@app.get("/export")
async def export_data():
    if not latest_analysis:
        return JSONResponse(content={"error": "No data available to export."}, status_code=400)

    export_filename = "call_summary.csv"
    
    # Prepare the data for CSV export
    data_to_export = []
    for key, value in latest_analysis.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    data_to_export.append([key, sub_key, ", ".join(sub_value)])
                else:
                    data_to_export.append([key, sub_key, sub_value])
        elif isinstance(value, list):
            data_to_export.append([key, ", ".join(value)])
        else:
            data_to_export.append([key, value])

    # Write to CSV
    with open(export_filename, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Category", "Value"])
        for row in data_to_export:
            writer.writerow(row)
    
    return FileResponse(export_filename, media_type='text/csv', filename=export_filename)
