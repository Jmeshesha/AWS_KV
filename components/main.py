from flask import Flask, request, Response
from logging.config import dictConfig
from threadsafedictionary import ThreadSafeDictionary
from persistance import AsyncPersistance
import json
import socket
from flask_apscheduler import APScheduler
from kvstore import KeyValueStore

#keyValueStore = KeyValueStore(1)
keyValueStore = ThreadSafeDictionary(10)

HOST, PORT = '0.0.0.0', 5000
server_startup_finished = False

app = Flask(__name__)
scheduler = APScheduler()
persistantDb = AsyncPersistance(app)

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

@app.put("/put")
def insert():
    if not server_startup_finished:
        return "<p>Server is still starting up plase wait</p>", 500
    key = request.args.get("key")
    value = request.args.get("value")
    if key is None:
        return "<p>Key was not provided in query parameters</p>", 400
    if value is None:
        return "<p>Value was not provided in query parameters</p>", 400
    keyValueStore.insert(key, value)
    persistantDb.saveInsert(key, value)
    app.logger.info(f'{key} set to {value}')
    return "<p>Successfully inserted key value pair./p>", 200

@app.get("/get")
def get():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    key = request.args.get("key")
    if key is None:
        return "<p>Key was not provided in query parameters</p>", 400

    value = keyValueStore.get(key)
    
    return f"<p>Value for key {key} is {value}.</p>"

@app.delete("/del")
def delete():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    key = request.args.get("key")
    if key is None:
        return "<p>Key was not provided in query parameters</p>", 400

    wasDeleted = keyValueStore.delete(key)
    if(not wasDeleted):
        return f"<p>No entry found for key {key}.</p>", 400
    persistantDb.saveDelete(key)
    app.logger.info(f'{key} deleted')
    return f"<p>Successfully deleted entry for key {key}.</p>"

@app.route('/api/data', methods=['GET'])
def data_dump():
    if not server_startup_finished:
        return "<p>Server is still starting up please wait</p>", 500
    temp = {}
    for kv in persistantDb.runReadQuery('SELECT post_key, post_data FROM post'):
        temp[kv[0]] = kv[1]
    return Response(json.dumps(temp), mimetype="application/json")


with app.app_context():
    previousRecords = persistantDb.getPreviousRecords()
    keyValueStore.insertFromDB(db_query_results=previousRecords)
    server_startup_finished = True
    print("Finished loading from db")

@scheduler.task('interval', id='persistanceJob', seconds=1)
def persistanceRunner():
    persistantDb.queryRunnerJob()


if __name__== "__main__":
    scheduler.init_app(app)
    scheduler.start()
    app.run(HOST, PORT, threaded=True, debug=False)
    