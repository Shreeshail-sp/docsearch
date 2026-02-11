import requests
import msgpack
from typing import List, Dict
from config import config

class EndeeClient:
    def __init__(self):
        self.base_url = config.ENDEE_BASE_URL
        self.headers = {"Content-Type": "application/json"}
        if config.ENDEE_AUTH_TOKEN:
            self.headers["Authorization"] = config.ENDEE_AUTH_TOKEN
        print(f"Connecting to Endee at {self.base_url}")

    def create_index(self, index_name: str, dimension: int, metric: str = "cosine") -> Dict:
        url = f"{self.base_url}/api/v1/index/create"
        payload = {
            "index_name": index_name,
            "dim": dimension,
            "space_type": metric
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            print(f"Create index response: {response.status_code} - {response.text[:300]}")
            if response.status_code == 200:
                print(f"Index '{index_name}' created successfully")
                return {"status": "created"}
            else:
                print(f"Error creating index: {response.text}")
                return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def list_indices(self) -> List[str]:
        url = f"{self.base_url}/api/v1/index/list"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                indexes = data.get("indexes", [])
                return [idx["name"] for idx in indexes]
        except Exception as e:
            print(f"Error: {e}")
        return []

    def index_exists(self, index_name: str) -> bool:
        names = self.list_indices()
        print(f"Existing indexes: {names}")
        return index_name in names

    def insert_vectors(self, index_name: str, vectors: List[Dict]) -> Dict:
        """Insert vectors - sends as JSON list directly"""
        url = f"{self.base_url}/api/v1/index/{index_name}/vector/insert"

        # API expects a JSON list of objects: [{"id": ..., "vector": [...]}, ...]
        payload = []
        for v in vectors:
            item = {
                "id": str(v["id"]),
                "vector": v["vector"]
            }
            payload.append(item)

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            print(f"Insert response: {response.status_code}")
            if response.status_code == 200:
                print(f"Inserted {len(vectors)} vectors successfully")
                return {"status": "inserted", "count": len(vectors)}
            else:
                print(f"Insert error: {response.status_code} - {response.text[:300]}")
                return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def search(self, index_name: str, query_vector: List[float], top_k: int = 5) -> Dict:
        """Search - returns msgpack decoded results"""
        url = f"{self.base_url}/api/v1/index/{index_name}/search"
        payload = {
            "vector": query_vector,
            "k": top_k
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            print(f"Search response: {response.status_code}")

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')

                if 'msgpack' in content_type:
                    data = msgpack.unpackb(response.content, raw=False)
                    print(f"Search returned {len(data)} results")
                    return {"results": data}
                else:
                    return response.json()
            else:
                print(f"Search error: {response.text[:300]}")
                return {"results": []}
        except Exception as e:
            print(f"Error: {e}")
            return {"results": []}
