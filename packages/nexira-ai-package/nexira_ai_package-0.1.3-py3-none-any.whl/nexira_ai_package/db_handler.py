import pymongo
import numpy as np
import os
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
import logging
import hashlib
import threading
from datetime import datetime, UTC
from flashrank import Ranker, RerankRequest


class DocumentDBHandler:
    def __init__(self, connection_string: str, username: str, password: str, db_name: str, collection_name: str):
        self.client = None
        self.db = None
        self.collection = None
        self.connection_string = connection_string
        self.username = username
        self.password = password
        self.db_name = db_name
        self.collection_name = collection_name
        self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        self.lock = threading.Lock()
        self.vector_dim = 768  # or 384 depending on model
        self.reranker = Ranker(max_length=128)

    def connect_to_database(self):
        try:
            self.client = pymongo.MongoClient(
                self.connection_string + "/?directConnection=true",
                username=self.username,
                password=self.password,
                retryWrites=False,
                #tls=True,
                #tlsCAFile="global-bundle.pem",
                tlsAllowInvalidHostnames=True
            )
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            print(f"✅ Connected to database: {self.db_name}")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")

    def get_embedding(self, text: str) -> List[float]:
        with self.lock:
            return self.model.encode(text).tolist()

    def generate_doc_id(self, identifier: str) -> str:
        return hashlib.md5(identifier.encode()).hexdigest()

    def insert_document(self, key: Dict[str, Any], messages_as_dicts: List[Dict[str, Any]]):
        try:
            set_on_insert = key.copy()
            set_on_insert["created_at"] = datetime.now(UTC)

            update = {
                "$setOnInsert": set_on_insert,
                "$push": {
                    "messages": {
                        "$each": messages_as_dicts,
                    }
                }
            }

            self.collection.update_one(
                key,
                update,
                upsert=True,
            )
            print(f"✅ Document successfully inserted: {key}")
        except Exception as e:
            print(f"❌ Error inserting document: {e}")

    def insert_vector_document(self, text: str, metadata: Dict[str, any]):
        try:
            doc_id = self.generate_doc_id(text)
            vector = self.get_embedding(text)
            document = {
                "_id": doc_id,
                "text": text,
                "embedding": vector,
                "metadata": metadata
            }
            self.collection.replace_one({"_id": doc_id}, document, upsert=True)
            print(f"✅ Document successfully inserted: {doc_id}")
            return True
        except Exception as e:
            print(f"❌ Error inserting document: {e}")
            return False

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        v1_np = np.array(v1)
        v2_np = np.array(v2)
        if np.linalg.norm(v1_np) == 0 or np.linalg.norm(v2_np) == 0:
            return 0.0
        return float(np.dot(v1_np, v2_np) / (np.linalg.norm(v1_np) * np.linalg.norm(v2_np)))

    def search_similar(self, query: str, limit: int = 5, search_filter: str = "") -> List[Dict]:
        query_vector = self.get_embedding(query)
        query_filter = {"embedding": {"$exists": True}}
        if search_filter:
            query_filter["metadata.tags"] = search_filter

        all_docs = self.collection.find(query_filter, {"text": 1, "embedding": 1, "metadata": 1})

        passages = [
            {
                "id": str(doc["_id"]),
                "text": doc["text"],
                "meta": {k: v for k, v in doc["metadata"].items() if k != "text"}
            }
            for doc in all_docs
        ]

        rerank_request = RerankRequest(query=query, passages=passages)
        reranked = self.reranker.rerank(rerank_request)
        reranked = reranked[0:limit]

        final_results = [
            {
                "score": item.get("score"),
                "id": item.get("id"),
                "text": item.get("text"),
                "payload": item.get("meta", {})
            }
            for item in reranked
        ]
        return final_results

    def delete_document(self, doc_id: str):
        self.collection.delete_one({"_id": doc_id})

    def clear_collection(self):
        self.collection.delete_many({})
        print(f"Collection '{self.collection_name}' cleared.")

    def close_connection(self):
        self.client.close()
