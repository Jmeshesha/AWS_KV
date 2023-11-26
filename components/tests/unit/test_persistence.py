from persistance import AsyncPersistance
import os
from flask import Flask, g
from unittest import mock

os.environ["DB_USERNAME"] = "test"
os.environ["DB_PASSWORD"] = "test"

class MockDb:
    def __init__(self):
        self.mockCursor = MockCursor()
    def cursor(self):
        return self.mockCursor
    def close(self):
        pass
    def getExecutedQueries(self):
        return self.mockCursor.executedQueries


class MockCursor:
    def __init__(self):
        self.executedQueries = []
    def execute(self, query, args):
        self.executedQueries.append((query, args))
    def close(self):
        pass
    def fetchall(self):
        return None

class TestPersistance:
    def test_saveSingleInsert(self):
        dbPersistance = AsyncPersistance(None)
        dbPersistance.saveInsert("abc", "def")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
        assert args == ("abc", "def")

    def test_saveMultipleInsert(self):
        dbPersistance = AsyncPersistance(None)
        dbPersistance.saveInsert("abc", "def")
        dbPersistance.saveInsert("efg", "hij")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
        assert args == ("abc", "def")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
        assert args == ("efg", "hij")

    def test_saveSingleDelete(self):
        dbPersistance = AsyncPersistance(None)
        dbPersistance.saveDelete("abc")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "DELETE FROM post WHERE post_key=%s"
        assert args == ("abc",)
    
    def test_saveInsertThenDelete(self):
        dbPersistance = AsyncPersistance(None)
        dbPersistance.saveInsert("abc", "def")
        dbPersistance.saveDelete("abc")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
        assert args == ("abc", "def")
        query, args = dbPersistance.batchQueries.get_nowait()
        assert query == "DELETE FROM post WHERE post_key=%s"
        assert args == ("abc",)
    
    
    def test_runReadQuery(self):
        app = Flask(__name__)
        mockDb = MockDb()
        data = ""
        

        with mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            dbPersistance = AsyncPersistance(app)
            data = dbPersistance.runReadQuery("query", ())

        assert data is None
        assert len(mockDb.getExecutedQueries()) == 1
        query, args = mockDb.getExecutedQueries()[0]
        assert query == "query"
        assert args == () 

    def test_runWriteQuery(self):
        app = Flask(__name__)
        mockDb = MockDb()
        data = ""
        

        with mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            dbPersistance = AsyncPersistance(app)
            data = dbPersistance.runWriteQuery("query", ())

        assert data is None
        assert len(mockDb.getExecutedQueries()) == 1
        query, args = mockDb.getExecutedQueries()[0]
        assert query == "query"
        assert args == () 

    def test_runWriteQueries(self):
        app = Flask(__name__)
        mockDb = MockDb()
        data = ""

        queries = [("query1", ()), ("query2", ("123")), ("query3", ("123", "45"))]
        

        with mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            dbPersistance = AsyncPersistance(app)
            data = dbPersistance.runWriteQueries(queries)

        assert data is None
        assert len(mockDb.getExecutedQueries()) == 3
        for i in range(len(mockDb.getExecutedQueries())) :
            assert mockDb.getExecutedQueries()[i] == queries[i]
            



