from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from elasticsearch_service import init_elasticsearch, index_ad, delete_ad
from search_intent_logic import SearchIntentParser

app = FastAPI(title="Search Engine Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_elasticsearch()

# Minimal City model to accept cities payload for intent parsing
# Normally, we'd fetch this from the DB, but since this service shouldn't connect
# to PostgreSQL to keep it decoupled, the client can pass cities or we can just 
# rely on a static list or rely on the main backend. Wait! 
# The main backend used to query PostgreSQL for cities_db and pass it to the parser!
# Since this service shouldn't connect to postgres, the easiest way is to let the 
# mobile app or the backend pass the list of cities, OR we hardcode the major cities,
# OR we do a quick HTTP call to the main backend?
# Given the user wants high performance, hardcoding or fetching via background task is best.
# Let's add a static list of cities for now.

# We will just use a generic dictionary for ads
class AdPayload(BaseModel):
    ad: Dict[str, Any]

@app.post("/api/internal/index")
async def api_index_ad(payload: AdPayload):
    try:
        await index_ad(payload.ad)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/internal/index/{ad_id}")
async def api_delete_ad(ad_id: int):
    try:
        await delete_ad(ad_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IntentRequest(BaseModel):
    q: str
    # In a fully decoupled system, the cities list could be fetched from cache.
    # We will let the query pass it, or we use a basic static fallback.

@app.get("/api/search/intent")
async def get_search_intent(q: str = ""):
    # A basic list of cities for Jordan as a fallback. 
    # For a production system, you'd periodically sync this from the main DB or Redis.
    static_cities = [
        {"name_ar": "عمان", "regions": []},
        {"name_ar": "اربد", "regions": []},
        {"name_ar": "الزرقاء", "regions": []},
        {"name_ar": "العقبة", "regions": []},
        {"name_ar": "السلط", "regions": []},
        {"name_ar": "المفرق", "regions": []},
        {"name_ar": "جرش", "regions": []},
        {"name_ar": "عجلون", "regions": []},
        {"name_ar": "مادبا", "regions": []},
        {"name_ar": "الكرك", "regions": []},
        {"name_ar": "الطفيلة", "regions": []},
        {"name_ar": "معان", "regions": []},
    ]
    
    intent = SearchIntentParser.parse(q, static_cities)
    return intent.model_dump()
