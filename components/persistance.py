import asyncio
from flask import g
from queue import Queue, Empty
import psycopg2
import os
from threading import Thread
from flask_apscheduler import APScheduler
class AsyncPersistance:
    def __init__(self, app):
        self.batchQueries = Queue()
        self.app = app
        self.dbUsername = os.environ["DB_USERNAME"]
        self.dbPassword = os.environ["DB_PASSWORD"]

    def queryRunnerJob(self):
        queries = []
        notEmpty = True
        while notEmpty:
            try:
                queries.append(self.batchQueries.get_nowait())
                self.batchQueries.task_done()
            except Empty:
                notEmpty = False
        self.runWriteQueries(queries)
            

    def saveInsert(self, key, value):
        query = "INSERT INTO post (post_key, post_data) VALUES (%s, %s)"
        args = (key, value)
        self.batchQueries.put_nowait((query, args))    

    def saveDelete(self, key):
        query = "DELETE FROM post WHERE post_key=%s"
        args = (key,)
        self.batchQueries.put_nowait((query, args))

    def runWriteQuery(self, query, args=()):
        db = self.connectToDatabase()
        cursor = db.cursor()
        cursor.execute(query, args)
        cursor.close()
        self.closeDatabase()

    def runWriteQueries(self, queries):
        db = self.connectToDatabase()
        cursor = db.cursor()
        for query, args in queries:
            cursor.execute(query, args)
        cursor.close()
        self.closeDatabase()

    def runReadQuery(self, query, args=()):
        db = self.connectToDatabase()
        cursor = db.cursor()
        cursor.execute(query, args)
        data = cursor.fetchall()
        cursor.close()
        self.closeDatabase()
        return data
    
    def init_db(self):
        db = self.connectToDatabase()
        print("initializing")
        with self.app.open_resource('schema.sql') as f:
            cursor = db.cursor()
            cursor.execute(f.read().decode('utf8'))
            db.commit()
        self.closeDatabase()

    def getPreviousRecords(self):
        query = f"SELECT post_key, post_data FROM post"
        return self.runReadQuery(query)

    def connectToDatabase(self):
        with self.app.app_context():
            
            if 'db' not in g:
                g.db = psycopg2.connect(
                    host='dpg-ckonvi41tcps73ba1mkg-a.ohio-postgres.render.com',
                    database='kvdb',
                    user=self.dbUsername,
                    password=self.dbPassword
                )

            return g.db
    
    def closeDatabase(self):
        with self.app.app_context():
            db = g.pop('db', None)
            if db is not None:
                db.close()
        
