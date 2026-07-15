import asyncio
import urllib.request
import ssl
import json
import logging
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

cached_locations = []

def fetch_locations():
    global cached_locations
    if cached_locations:
        return cached_locations
        
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            'https://api.sooq-com.com/api/locations', 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            cached_locations = json.loads(r.read().decode('utf-8'))
            logging.info(f"Fetched {len(cached_locations)} locations from main API.")
    except Exception as e:
        logging.error(f"Failed to fetch locations: {e}")
        # Basic fallback if API fails
        cached_locations = [
            {"name_ar": "عمان", "regions": []},
            {"name_ar": "إربد", "regions": []},
            {"name_ar": "الزرقاء", "regions": []}
        ]
        
    return cached_locations

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(init_elasticsearch())
    # Prefetch locations on startup in a separate thread so we don't block
    asyncio.get_event_loop().run_in_executor(None, fetch_locations)

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

@app.get("/api/search/intent")
async def get_search_intent(q: str = ""):
    cities = fetch_locations()
    intent = SearchIntentParser.parse(q, cities)
    return intent.model_dump()
