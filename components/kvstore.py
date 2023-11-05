from threadsafedictionary import ThreadSafeDictionary
class KeyValueStore:
    def __init__(self, numOfBuckets: int) -> None:
        self.buckets = []
    #     for i in range(numOfBuckets):
    #         self.buckets.append(ThreadSafeDictionary())

    # def getBucket(self, key) -> ThreadSafeDictionary:
    #     return self.buckets[self.getBucketIdx(key)]
    
    # def getBucketIdx(self, key):
    #     return hash(key) % len(self.buckets)
    
    # def insert(self, key, value):
    #     bucket = self.getBucket(key)
    #     bucket.insert(key, value)

    # def delete(self, key):
    #     bucket = self.getBucket(key)
    #     return bucket.delete(key)
    # def get(self, key):
    #     bucket = self.getBucket(key)
    #     return bucket.get(bucket)
    # def insertFromDB(self, db_query_results):
    #     kvPairs = {}
    #     for db_row in db_query_results:
    #         key, value = db_row["post_key"], db_row["post_data"]
    #         bucketIdx = self.getBucketIdx(key)
    #         kvPairs[bucketIdx] = kvPairs.get(bucketIdx, []) + [(key, value)]
    #     for bucketIdx in kvPairs:
    #         self.buckets[bucketIdx].insertMany(kvPairs[bucketIdx])
        


