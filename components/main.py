from flask import Flask, abort, request, g, Response, current_app
from logging.config import dictConfig
from threadsafedictionary import ThreadSafeDictionary
import os
import sqlite3
import json
import socket
import psycopg2
keyValueStore = ThreadSafeDictionary()

HOST, PORT = '0.0.0.0', 5000
server_startup_finished = False

app = Flask(__name__)
# app.config.from_mapping(
#     SECRET_KEY='dev',
#     DATABASE=os.path.join(os.getcwd(), 'flaskr.sqlite'),
# )

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "flask.log",
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["file"]},
    }
)

@app.errorhandler(404)
def invalid_url_handler(error):
    return """
    <!doctype html>
    <html lang=en>
        <h1>404 Not Found</h1>
        <p>Invalid url. Use the endpoints: </p>
        <ul>
            <li>/put to insert a value into the key-value store</li>
            <li>/get to get a value from key-value store</li>
            <li>/del to delete a value from the key-value store/li>
        </ul>
    </html>
    """, 404

@app.get("/")
def home():
    d = socket.gethostname()
    return f"""
        <h1>Simple key value store - {d}</h1>
        <p>Welcome to the simple key value store. You can use the endpoints:</p>
        <ul>
            <li>/put with a PUT request to insert the given key-value pair</li>
            <li>/get with a GET request to get the value associated with the given key</li>
            <li>/del with a DELETE request to delete the value associated with the given key</li>
        </ul>

        <p>For each endpoint, you can specify a key and value using url query parameters with separate parameters for the key and the value.</p>
    """
def batch_insert():
    print("BAtch_insert")
    db = get_db()
    cur = db.cursor()
    kv = keyValueStore.retrieve()
    # args_str = ','.join(cur.mogrify("(%s,%s)", i) for i in kv)
    args_str = ','.join(['%s'] * len(kv))
    query = "INSERT INTO post (post_key, post_data) VALUES {}".format(args_str)
    cur.execute(query, list(kv.items()))
    db.commit()
# Concat keys into one delete query
def batch_delete():
    print("Batch Delete")
    db = get_db()
    cur = db.cursor()
    keys = keyValueStore.retrieve_del_batch()
    args_str = ','.join(['%s'] * len(keys))
    query = "DELETE FROM post WHERE post_key IN ({})".format(args_str)
    cur.execute(query, list(kv.keys()))
    db.commit
    keyValueStore.clear_del_batch()
    

@app.put("/put")
def insert():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    key = request.args.get("key")
    value = request.args.get("value")
    # db = get_db()
    # cursor = db.cursor()
    if key is None:
        return "<p>Key was not provided in query parameters</p>", 400
    if value is None:
        return "<p>Value was not provided in query parameters</p>", 400
    keyValueStore.insert(key, value)

    if(keyValueStore.get_cur_batch() >= 50):
        batch_insert()
    # cursor.execute(
    #     "INSERT INTO post (post_key, post_data) VALUES (%s, %s)",
    #     (key, value)
    # )
    # db.commit()
    # cursor.close()
    # db.close()
    app.logger.info(f'{key} set to {value}')
    return "<p>Successfully inserted key value pair./p>"

@app.get("/get")
def get():
    d = socket.gethostname()
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    key = request.args.get("key")
    if key is None:
        return f"<p>Key was not provided in query parameters</p> {d}", 400

    value = keyValueStore.get(key)
    # if value is None:
    #     db = get_db()
    #     cur = db.cursor()
    #     cur.execute('SELECT post_data FROM post WHERE post_key = %s' , (key,))
    #     response = cur.fetchall()
    #     cur.close()
    #     db.close()
    #     if response:
    #         keyValueStore.insert(key, response[0][0])
    #         return f"<p>Value for key {key} is {response[0][0]}.</p>"
    #     return f"<p>No entry found for key {key}</p>", 400
    
    return f"<p>Value for key {key} is {value}. - {d}</p>"

@app.delete("/del")
def delete():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    key = request.args.get("key")
    db = get_db()
    if key is None:
        return "<p>Key was not provided in query parameters</p>", 400

    wasDeleted = keyValueStore.delete(key)
    # if(not wasDeleted):
    #     return f"<p>No entry found for key {key}.</p>", 400
    
    # if(len(keyValueStore.retrieve_del_batch()) >= 50):
    #     batch_delete()
    if(not wasDeleted):
        query = 'DELETE FROM post WHERE post_key=%s'
        cur = db.cursor()
        cur.execute(query, (key,))
        cur.close()
        db.close()
        
        return f"<p>No entry found for key {key}.</p>", 400
    query = 'DELETE FROM post WHERE post_key=%s'
    cur = db.cursor()
    cur.execute(query, (key,))
    db.commit()
    cur.close()
    db.close()
    app.logger.info(f'{key} deleted')
    return f"<p>Successfully deleted entry for key {key}.</p>"

@app.route('/api/data', methods=['GET'])
def data_dump():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    temp = {}
    for kv in query_db('SELECT post_key, post_data FROM post'):
        temp[kv[0]] = kv[1]
    return Response(json.dumps(temp), mimetype="application/json")

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host='dpg-ckonvi41tcps73ba1mkg-a.ohio-postgres.render.com',
            database='kvdb',
            user=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD']
        )
    
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    print("initializing")
    with current_app.open_resource('schema.sql') as f:
        cursor = db.cursor()
        cursor.execute(f.read().decode('utf8'))
        db.commit()

with app.app_context():
 
    server_startup_finished = True
    print("Server Startup finished")

if __name__== "__main__":
    app.run(HOST, PORT, threaded=True, debug=False)