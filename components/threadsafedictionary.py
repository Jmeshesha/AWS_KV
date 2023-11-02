from threading import Lock
class ThreadSafeDictionary:
    def __init__(self):
        self.data = {}
        self.mutex = Lock()
        self.insert_batch_size = 0
        self.delete_batch = {}

    def insert_from_db(self, db_query_results):
        self.mutex.acquire(blocking=True)
        for db_row in db_query_results:
            key, value = db_row["post_key"], db_row["post_data"]
            self.data[key] = value
        self.mutex.release()

    def insert(self, key, value):
        self.mutex.acquire(blocking=True)
        self.data[key] = value
        self.insert_batch_size += 1
        self.mutex.release()

    def get(self, key):
        if key not in self.data:
            return None
        return self.data[key]
    
    def retrieve(self):
        self.insert_batch_size = 0
        return self.data
    
    def clear_del_batch(self):
        self.delete_batch = {}

    def retrieve_del_batch(self):
        return self.delete_batch
    
    def get_cur_batch(self):
        return self.insert_batch_size
    
    def delete(self, key):
        updated = False
        self.mutex.acquire(blocking=True)
        if key in self.data:
            updated = True
            self.data.pop(key)
            self.delete_batch[key] = 'del'
        self.mutex.release()
        return updated
        
