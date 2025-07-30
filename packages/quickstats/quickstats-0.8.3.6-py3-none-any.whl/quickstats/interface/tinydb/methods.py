from tinydb import TinyDB, Query
import numpy as np

class TinyDBSession:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = None

    def __enter__(self):
        self.db = TinyDB(self.db_path)
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

def remove_non_unique_field_values(db_path:str, field_name: str):
    with TinyDBSession(db_path) as db:
        query = Query()
        documents = db.search(query[field_name].exists())
        field_values = np.array([doc[field_name] for doc in documents])
        doc_ids = np.array([doc.doc_id for doc in documents])
        
        unique_values, counts = np.unique(field_values, return_counts=True)
        non_unique_values = unique_values[counts > 1]
        
        mask = np.isin(field_values, non_unique_values)
        ids_to_remove = doc_ids[mask]
        
        db.remove(doc_ids=ids_to_remove.tolist())