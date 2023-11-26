"""
@brief Class for thread-safe dictionary operations. Uses mutex locking.
"""
from threading import Lock
class ThreadSafeDictionary:
    def __init__(self):
        self.data = {}
        self.mutex = Lock()
        
    def insertMany(self, kvPairs):
        self.mutex.acquire(blocking=True)
        for key, value in kvPairs:
            self.data[key] = value
        self.mutex.release()

    def insert(self, key, value):
        self.mutex.acquire(blocking=True)
        self.data[key] = value
        self.mutex.release()

    def get(self, key):
        if key not in self.data:
            return None
        return self.data[key]
    
    def retrieve(self):
        return self.data
    def insertFromDB(self, db_query_results):
        self.mutex.acquire(blocking=True)
        for db_row in db_query_results:
            key, value = db_row["post_key"], db_row["post_data"]
            self.data[key] = value

        self.mutex.release()
    
    def delete(self, key):
        updated = False
        self.mutex.acquire(blocking=True)
        if key in self.data:
            updated = True
            self.data.pop(key)
        self.mutex.release()
        return updated
        
