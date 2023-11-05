"""
@brief Class for thread-safe dictionary operations. Uses mutex locking.
"""
from threading import Lock
class ThreadSafeDictionary:
    def __init__(self, numOfMutexes):
        self.data = {}
        self.mutexes = []
        for i in range(numOfMutexes):
            self.mutexes.append(Lock())
    def insertMany(self, kvPairs):
        mutexes = []
        for k, v in kvPairs:
            mutexes.append(self.getMutex(k))
            mutexes[-1].acquire(blocking=True)
        for key, value in kvPairs:
            self.data[key] = value
        for mutex in mutexes:
            mutex.release()

    def getMutex(self, key):
        mutexIdx = hash(key) % len(self.mutexes)
        return self.mutexes[mutexIdx]

    def insert(self, key, value):
        mutex = self.getMutex(key)
        mutex.acquire(blocking=True)
        self.data[key] = value
        mutex.release()

    def get(self, key):
        if key not in self.data:
            return None
        return self.data[key]
    
    def retrieve(self):
        return self.data
    def insertFromDB(self, db_query_results):
        for mutex in self.mutexes:
            mutex.acquire(blocking=True)
        for db_row in db_query_results:
            key, value = db_row["post_key"], db_row["post_data"]
            self.data[key] = value
        for mutex in self.mutexes:
            mutex.release()
    
    def delete(self, key):
        updated = False
        mutex = self.getMutex(key)
        mutex.acquire(blocking=True)
        if key in self.data:
            updated = True
            self.data.pop(key)
        mutex.release()
        return updated
        
