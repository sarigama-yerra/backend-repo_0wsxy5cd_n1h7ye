import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document
from schemas import Survey, SurveyResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a real app, questions could be stored in DB. For now, serve a curated set of
# "major topics" that users typically expect in a survey site.
PRESET_SURVEY: Survey = Survey(
    survey_id="major-topics-001",
    title="General Interests & Lifestyle Survey",
    description="A quick survey covering technology, health, finance, education, travel and entertainment.",
    questions=[
        {"id": "q1", "topic": "technology", "text": "How comfortable are you with new technology?", "type": "scale"},
        {"id": "q2", "topic": "technology", "text": "Which platform do you use the most?", "type": "single", "options": ["iOS", "Android", "Windows", "macOS", "Linux"]},
        {"id": "q3", "topic": "health", "text": "How many days a week do you exercise?", "type": "single", "options": ["0", "1-2", "3-4", "5+"]},
        {"id": "q4", "topic": "finance", "text": "How do you primarily budget your expenses?", "type": "single", "options": ["App", "Spreadsheet", "Pen & Paper", "I don't budget"]},
        {"id": "q5", "topic": "education", "text": "Highest level of education completed?", "type": "single", "options": ["High School", "Associate", "Bachelor's", "Master's", "Doctorate"]},
        {"id": "q6", "topic": "travel", "text": "How often do you travel for leisure?", "type": "single", "options": ["Rarely", "1-2x/yr", "3-4x/yr", "5+ / yr"]},
        {"id": "q7", "topic": "entertainment", "text": "Favorite entertainment format?", "type": "single", "options": ["Movies", "Series", "Books", "Gaming", "Music Concerts"]},
        {"id": "q8", "topic": "technology", "text": "What tech topic are you most curious about right now?", "type": "text"},
    ],
)

@app.get("/")
def read_root():
    return {"message": "Survey backend running"}

@app.get("/api/survey", response_model=Survey)
async def get_survey():
    return PRESET_SURVEY

class SubmitPayload(BaseModel):
    survey_id: str
    answers: List[dict]

@app.post("/api/survey/submit")
async def submit_survey(payload: SubmitPayload, request: Request):
    if payload.survey_id != PRESET_SURVEY.survey_id:
        raise HTTPException(status_code=400, detail="Invalid survey id")

    # Collect metadata
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None

    # Persist to DB
    try:
        doc_id = create_document(
            "surveyresponse",
            {
                "survey_id": payload.survey_id,
                "answers": payload.answers,
                "user_agent": ua,
                "ip": ip,
            },
        )
    except Exception as e:
        # Persisting is best-effort; if DB not configured, surface error clearly
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"status": "ok", "id": doc_id}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
