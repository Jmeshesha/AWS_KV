import pytest 
from threadsafedictionary import ThreadSafeDictionary

class TestThreadSafeDictionary:
    def test_emptyDictReturnsNone(self):
        dictionary = ThreadSafeDictionary()
        assert dictionary.get("hi") is None
    
    def test_getNonExistentKey(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("hi", "hello")
        dictionary.insert("abc", "def")
        assert dictionary.get("def") is None
    
    def test_singleInsert(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("hi", "hello")
        assert dictionary.get("hi") == "hello"

    def test_multiInsertUniqueKeys(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("hi", "hello")
        dictionary.insert("abc", "def")
        assert dictionary.get("hi") == "hello"
        assert dictionary.get("abc") == "def"

    def test_multiInsertSameKeys(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("abc", "def")
        dictionary.insert("abc", "hello")
        assert dictionary.get("abc") == "hello"
    
    def test_insertMany(self):
        dictionary = ThreadSafeDictionary()
        kvPairs = [("hi", "hello"), ("abc", "def")]
        dictionary.insertMany(kvPairs)
        assert dictionary.get("hi") == "hello"
        assert dictionary.get("abc") == "def"
    
    def test_insertFromDb(self):
        dictionary = ThreadSafeDictionary()
        queryResults = [
            {
                "post_key": "hi",
                "post_data": "hello"
            },
            {
                "post_key": "abc",
                "post_data": "def"
            }  
        ]
        dictionary.insertFromDB(queryResults)
        assert dictionary.get("hi") == "hello"
        assert dictionary.get("abc") == "def"
    
    def test_deleteEmpty(self):
        dictionary = ThreadSafeDictionary()
        isUpdated = dictionary.delete("hi")
        assert not isUpdated
    
    def test_deleteSingle(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("hi", "hello")
        dictionary.insert("abc", "def")
        isUpdated = dictionary.delete("hi")
        assert isUpdated
        assert dictionary.get("hi") is None
    
    def test_deleteMany(self):
        dictionary = ThreadSafeDictionary()
        dictionary.insert("hi", "hello")
        dictionary.insert("abc", "def")
        dictionary.insert("efg", "hig")
        isUpdated = dictionary.delete("hi")
        assert isUpdated
        isUpdated = dictionary.delete("abc")
        assert dictionary.get("hi") is None

    

    