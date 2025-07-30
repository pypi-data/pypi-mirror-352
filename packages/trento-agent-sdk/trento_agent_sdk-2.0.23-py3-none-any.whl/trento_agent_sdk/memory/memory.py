import os
import time
import json
import logging
from uuid import uuid4
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import List, Dict, Union
from openai import OpenAI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class LongMemory:

    def __init__(self, user_id, memory_prompt):
        self.user_id = user_id
        self.memory_prompt = memory_prompt

        self.qdrant_host = os.getenv("QDRANT_HOST")
        self.qdrant_headers = {
            "api-key": os.getenv("QDRANT_API_KEY"),
            "Content-Type": "application/json",
        }

        self.embedding_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_client = OpenAI(
            api_key=self.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.collection_name = self._get_or_create_user_collection()

    def _get_or_create_user_collection(self) -> str:
        name = f"user_long_memory_{self.user_id}"
        try:
            # get existing collections
            url_list = f"{self.qdrant_host}/collections"
            resp = requests.get(url_list, headers=self.qdrant_headers)
            resp.raise_for_status()
            collections = resp.json()["result"]["collections"]
            existing_names = {col["name"] for col in collections}

            # if note present create collection for a specific user (Cosine Distance)
            if name not in existing_names:
                logger.info(f"Creating Qdrant collection `{name}`")
                url_create = f"{self.qdrant_host}/collections/{name}"
                payload = {
                    "vectors": {
                        "size": 768,  # embedding size for text-embedding-004
                        "distance": "Cosine",
                    }
                }
                resp = requests.put(
                    url_create, headers=self.qdrant_headers, json=payload
                )
                resp.raise_for_status()

                # create index for filterings
                index_url = f"{self.qdrant_host}/collections/{name}/index"
                index_payload = {"field_name": "user_id", "field_schema": "keyword"}
                resp = requests.put(
                    index_url, headers=self.qdrant_headers, json=index_payload
                )
                resp.raise_for_status()
                logger.info(
                    f"Created payload index for `user_id` in collection `{name}`"
                )
        except Exception:
            logger.exception("Error checking or creating Qdrant collection")
            raise

        return name

    def _scroll_current_memories(self) -> list[dict]:
        """
        Fetch all existing memories for this user via the REST scroll API.
        
        Implements pagination and retry logic for better reliability and handling of large memory sets.
        """
        max_retries = 3
        retry_delay = 0.5
        memories = []
        page_size = 50
        scroll_pointer = None
        
        for attempt in range(max_retries):
            try:
                while True:
                    url = f"{self.qdrant_host}/collections/{self.collection_name}/points/scroll"
                    body = {
                        "filter": {"must": [{"key": "user_id", "match": {"value": self.user_id}}]},
                        "with_payload": True,
                        "limit": page_size,
                    }
                    
                    # Add pagination pointer if available
                    if scroll_pointer:
                        body["offset"] = scroll_pointer
                    
                    # Use timeout to prevent hanging requests
                    resp = requests.post(url, headers=self.qdrant_headers, json=body, timeout=10)
                    resp.raise_for_status()
                    
                    response_data = resp.json()["result"]
                    pts = response_data["points"]
                    
                    # Process the current page
                    batch_results = [
                        {
                            "id": pt["id"],
                            "topic": pt["payload"]["topic"],
                            "description": pt["payload"]["description"],
                        }
                        for pt in pts
                    ]
                    
                    memories.extend(batch_results)
                    
                    # Check if we need to continue pagination
                    if "next_page_offset" in response_data and response_data["next_page_offset"]:
                        scroll_pointer = response_data["next_page_offset"]
                    else:
                        break  # No more pages
                
                # Successful completion, return results
                return memories if memories else []
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Qdrant request failed: {str(e)}. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to retrieve memories after {max_retries} attempts: {str(e)}")
                    return []  # Return empty list on failure rather than raising exception
                    
        return []  # Fallback empty list

    def insert_into_long_memory_with_update(
        self, chat_history: Union[str, List[Dict[str, str]]]
    ):

        # the chat history could also be a list of dicts
        if isinstance(chat_history, list):
            chat_history_payload = json.dumps(chat_history, ensure_ascii=False)
        else:
            chat_history_payload = chat_history

        # current memories
        current_memories = self._scroll_current_memories()
        # get new memories
        new_memories = self._extract_memories(
            chat_history=chat_history_payload, existing_memories=current_memories
        )

        if new_memories == "NO_MEMORIES_TO_ADD":
            logger.info("No memories should be added or updated")
            return

        # update point in db
        points = []
        for memory in new_memories:
            topic = memory.get("topic")
            desc = memory.get("description")
            pid = memory.get("id") or uuid4().hex  # use provided id or generate new

            if not topic or not desc:
                logger.warning("Skipping malformed memory: %r", memory)
                continue

            emb = None
            try:
                emb = self._get_embedding(desc)
            except Exception:
                logger.exception("Embedding failed for: %s", desc)
                continue

            points.append(
                {
                    "id": pid,
                    "vector": emb,
                    "payload": {
                        "user_id": self.user_id,
                        "topic": topic,
                        "description": desc,
                        "ts": int(time.time()),
                    },
                }
            )

        if points:
            upsert_url = f"{self.qdrant_host}/collections/{self.collection_name}/points?wait=true"
            resp = requests.put(
                upsert_url, headers=self.qdrant_headers, json={"points": points}
            )
            resp.raise_for_status()
            logger.info("Upserted %d points (new+updated)", len(points))

    def _get_embedding(self, text):
        """
        Call Google embed_content, return the embedding vector.
        
        Implements LRU caching for improved performance and retries for reliability.
        """
        # Use a hash of the text as a cache key
        cache_key = hash(text)
        
        # Check if we have this embedding in the cache
        if hasattr(self, '_embedding_cache') and cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Create the cache if it doesn't exist (limit to 100 entries)
        if not hasattr(self, '_embedding_cache'):
            self._embedding_cache = {}
            self._embedding_cache_keys = []  # For LRU tracking
            
        # Implement retry logic
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                result = self.embedding_client.models.embed_content(
                    model="models/text-embedding-004",
                    contents=[text],
                    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
                )
                
                embedding = result.embeddings[0].values
                
                # Store in cache (implement simple LRU)
                if len(self._embedding_cache) >= 100:  # Cache size limit
                    # Remove oldest item
                    oldest_key = self._embedding_cache_keys.pop(0)
                    del self._embedding_cache[oldest_key]
                
                self._embedding_cache[cache_key] = embedding
                self._embedding_cache_keys.append(cache_key)
                
                return embedding
                
            except Exception as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited when getting embedding. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    logger.exception(f"Failed to get embedding after {attempt+1} attempts for text: {text[:50]}...")
                    raise Exception(f"Failed to get embedding: {str(e)}")

    def get_memories(
        self, query: str, top_k: int = 5, max_cosine_distance: float = 0.7, timeout: float = 10.0, use_cache: bool = True
    ):
        """
        Retrieve and filter the most relevant memories by cosine distance.
        
        Args:
            query: The query string to search for in memories
            top_k: Number of top results to retrieve
            max_cosine_distance: Maximum allowed cosine distance (lower = more similar)
            timeout: Request timeout in seconds
            use_cache: Whether to use query cache for identical recent queries
            
        Returns:
            List of relevant memories sorted by relevance
        """
        # Query cache implementation for frequently repeated identical queries
        if use_cache and hasattr(self, '_query_cache'):
            cache_key = f"{query}::{top_k}::{max_cosine_distance}"
            if cache_key in self._query_cache:
                cache_entry = self._query_cache[cache_key]
                # Cache entries expire after 30 seconds
                if time.time() - cache_entry["timestamp"] < 30:
                    logger.debug("Using cached query results")
                    return cache_entry["results"]
        
        # Initialize cache if it doesn't exist
        if use_cache and not hasattr(self, '_query_cache'):
            self._query_cache = {}
        
        # Implement retries for better reliability
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Get embedding for the query
                q_emb = self._get_embedding(query)
                
                query_url = f"{self.qdrant_host}/collections/{self.collection_name}/points/query"
                query_body = {
                    "query": q_emb,
                    "top": min(top_k * 2, 20),  # Request more for better filtering
                    "with_payload": True,  # include payload in response
                    "filter": {
                        "must": [{"key": "user_id", "match": {"value": self.user_id}}]
                    },
                }
                
                # Use timeout to prevent hanging requests
                resp = requests.post(
                    query_url, 
                    headers=self.qdrant_headers, 
                    json=query_body,
                    timeout=timeout
                )
                
                resp.raise_for_status()
                points = resp.json()["result"]["points"]
                
                # Filter and sort results
                results = []
                for pt in points:
                    if pt["score"] <= max_cosine_distance:
                        results.append(
                            {
                                "id": pt["id"],
                                "topic": pt["payload"].get("topic", ""),
                                "description": pt["payload"].get("description", ""),
                                "score": pt["score"],
                                "ts": pt["payload"].get("ts", 0)  # Include timestamp for recency
                            }
                        )
                
                # Sort by score (most relevant first)
                results.sort(key=lambda x: x["score"])
                
                # Trim to the requested number if we have more
                if len(results) > top_k:
                    results = results[:top_k]
                
                # Update cache
                if use_cache:
                    self._query_cache[f"{query}::{top_k}::{max_cosine_distance}"] = {
                        "results": results,
                        "timestamp": time.time()
                    }
                    
                    # Limit cache size to prevent memory leaks
                    if len(self._query_cache) > 50:
                        # Remove oldest entries
                        oldest = sorted(self._query_cache.items(), key=lambda x: x[1]["timestamp"])
                        for k, _ in oldest[:10]:  # Remove 10 oldest entries
                            del self._query_cache[k]
                
                logger.info("Retrieved %d memories out of %d candidates", len(results), len(points))
                return results
                
            except requests.exceptions.HTTPError as e:
                logger.error("Qdrant API error response: %s", resp.text if 'resp' in locals() else str(e))
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Qdrant query failed. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    raise
                    
            except Exception as e:
                logger.exception("Failed to query points for `%s`: %s", query, str(e))
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Query failed. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    return []  # Return empty list on final failure
        
        return []  # Fallback empty list

    def _extract_memories(self, chat_history: str, existing_memories: list[dict]):
        """Ask the LLM to merge chat hints with existing memories, tagging with 'id' when updating."""

        user_payload = {
            "existing_memories": existing_memories,
            "chat_history": chat_history,
        }

        messages = [
            {"role": "system", "content": self.memory_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ]

        try:
            response = self.openai_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            memories = data.get("memories_to_add")
            if memories == "NO_MEMORIES_TO_ADD" or not memories:
                return "NO_MEMORIES_TO_ADD"
            return memories

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
