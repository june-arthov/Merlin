import os
from .base import BaseTool

class VectorMemory(BaseTool):
    def __init__(self):
        self._collection = None
        self._initialized = False

    def _init_db(self):
        if self._initialized: return
        try:
            import chromadb
            # Store vector DB in ~/.merlin/chroma_db
            db_path = os.path.expanduser("~/.merlin/chroma_db")
            os.makedirs(db_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=db_path)
            self._collection = self.client.get_or_create_collection(name="merlin_long_term_memory")
            self._initialized = True
        except ImportError:
            raise ImportError("chromadb is not installed. Run 'pip install chromadb'")

    @property
    def name(self): return "vector_memory"
    
    @property
    def category(self): return "memory"
    
    @property
    def description(self): return "Persistent semantic vector memory. Use this to store or recall large amounts of information, code, or context across sessions."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["store", "recall"], "description": "Action to perform."},
                "text": {"type": "string", "description": "The text or code to store (for 'store' action)."},
                "query": {"type": "string", "description": "The question or topic to search for (for 'recall' action)."},
                "metadata": {"type": "string", "description": "Optional JSON string with metadata tags for storing."},
                "n_results": {"type": "integer", "description": "Number of results to return for recall (default 3)."}
            },
            "required": ["action"]
        }

    def execute(self, action, text=None, query=None, metadata=None, n_results=3):
        try:
            self._init_db()
            import json
            import uuid

            if action == "store":
                if not text: return {"error": "text is required for store action."}
                doc_id = str(uuid.uuid4())
                meta_dict = {}
                if metadata:
                    try: meta_dict = json.loads(metadata)
                    except: pass
                
                self._collection.add(
                    documents=[text],
                    metadatas=[meta_dict] if meta_dict else None,
                    ids=[doc_id]
                )
                return {"status": "success", "message": "Memory embedded and stored permanently.", "id": doc_id}
            
            elif action == "recall":
                if not query: return {"error": "query is required for recall action."}
                results = self._collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                if not results['documents'] or not results['documents'][0]:
                    return {"status": "No relevant memories found."}
                
                return {
                    "status": "success",
                    "memories": results['documents'][0],
                    "distances": results['distances'][0] if 'distances' in results and results['distances'] else []
                }
                
        except Exception as e:
            return {"error": f"Vector DB Error: {str(e)}"}
