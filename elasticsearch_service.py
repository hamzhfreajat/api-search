import os
import json
import asyncio
from elasticsearch import AsyncElasticsearch
from typing import Dict, Any, List

# Create the Async client using the URL from docker-compose
# Note: For production with HTTPS, verify_certs=False might be needed if using self-signed,
# but we'll try default first.
es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = AsyncElasticsearch(
    es_url,
    verify_certs=False,  # Useful for testing/local setups
)

INDEX_NAME = "classifieds_ads"

async def init_elasticsearch():
    """Initializes the ElasticSearch index with Arabic analyzer settings."""
    try:
        exists = await es.indices.exists(index=INDEX_NAME)
        if exists:
            return

        settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "arabic_custom": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "arabic_normalization",
                                "arabic_stop",
                                "arabic_stemmer"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "text", "analyzer": "arabic_custom"},
                    "description": {"type": "text", "analyzer": "arabic_custom"},
                    "category_id": {"type": "integer"},
                    "city": {"type": "keyword"},
                    "region": {"type": "keyword"},
                    "price": {"type": "double"},
                    "deal_type": {"type": "keyword"},
                    "property_type": {"type": "keyword"},
                    "bedrooms": {"type": "integer"},
                    "bathrooms": {"type": "integer"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        }
        await es.indices.create(index=INDEX_NAME, body=settings)
        print(f"Created ElasticSearch index '{INDEX_NAME}' with Arabic mappings.")
    except Exception as e:
        print(f"Error initializing ElasticSearch: {e}")

async def index_ad(ad_dict: Dict[str, Any]):
    """Indexes a single ad into ElasticSearch."""
    try:
        # Convert datetime to string for ES
        if 'created_at' in ad_dict and hasattr(ad_dict['created_at'], 'isoformat'):
            ad_dict['created_at'] = ad_dict['created_at'].isoformat()
            
        await es.index(index=INDEX_NAME, id=str(ad_dict['id']), document=ad_dict)
        print(f"Indexed ad {ad_dict['id']} into ElasticSearch.")
    except Exception as e:
        print(f"Error indexing ad {ad_dict.get('id')}: {e}")

async def delete_ad(ad_id: int):
    """Deletes an ad from ElasticSearch."""
    try:
        await es.delete(index=INDEX_NAME, id=str(ad_id), ignore=[404])
        print(f"Deleted ad {ad_id} from ElasticSearch.")
    except Exception as e:
        print(f"Error deleting ad {ad_id}: {e}")
