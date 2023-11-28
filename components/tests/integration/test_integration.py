
import os
from unittest import mock
import unittest

os.environ["DB_USERNAME"] = "test"
os.environ["DB_PASSWORD"] = "test"

import main

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
    
class TestIntegration:
    def test_getNoKey(self):
        main.server_startup_finished = True
        with main.app.test_client() as client:
            response = client.get('/get')
            assert response.status_code == 400 
    
    def test_getEmptyDictionary(self):
        main.server_startup_finished = True
        with main.app.test_client() as client:
            response = client.get('/get', headers={"key": "abc"})
            assert b"Value for key abc is None." in response.data
            assert response.status_code == 200
    
    def test_insertEmptyBody(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.post('/post', json={})
            assert response.status_code == 400

            main.persistantDb.queryRunnerJob()

            assert len(mockDb.getExecutedQueries()) == 0
            

    def test_insertNoKey(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.post('/post', json={
                "value": "def"
            })
            assert response.status_code == 400

            main.persistantDb.queryRunnerJob()

            assert len(mockDb.getExecutedQueries()) == 0

    def test_insertNoValue(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.post('/post', json={
                "key": "abc"
            })
            assert response.status_code == 400

            main.persistantDb.queryRunnerJob()

            assert len(mockDb.getExecutedQueries()) == 0

    
    def test_insertSingle(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.post('/post', json={
                "key": "abc",
                "value": "def"
            })
            assert response.status_code == 200
            assert main.keyValueStore.get("abc") == "def"
            main.persistantDb.queryRunnerJob()

            assert len(mockDb.getExecutedQueries()) == 1
            

            query, args = mockDb.getExecutedQueries()[0]

            assert query == "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
            assert args == ("abc", "def")
    
    def test_getInsertedValue(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        main.keyValueStore.data = {}
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.post('/post', json={
                "key": "efg",
                "value": "hij"
            })
            assert response.status_code == 200
            assert main.keyValueStore.get("efg") == "hij"
            main.persistantDb.queryRunnerJob()
            response = client.get('/get', headers={
                "key": "efg"
            })
            assert response.status_code == 200
            assert b"Value for key efg is hij." in response.data

    
    def test_deleteEmpty(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            response = client.delete('/del')
            assert response.status_code == 400

    def test_deleteDoesNotExist(self):
        mockDb = MockDb()
        main.server_startup_finished = True
        with main.app.test_client() as client, mock.patch('persistance.psycopg2.connect', return_value=mockDb):
            assert main.keyValueStore.get("hij") == None
            response = client.delete('/del', headers={"key": "hij"})
            assert response.status_code == 400
            assert b"No entry found for key hij." in response.data
            assert main.keyValueStore.get("hij") == None

            main.persistantDb.queryRunnerJob()

            assert len(mockDb.getExecutedQueries()) == 0
    
    # def test_delete