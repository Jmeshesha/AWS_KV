import socket
import time
import threading
import http.client
import requests
import matplotlib.pyplot as plt
import numpy as np
HOST, PORT = '127.0.0.1', 80
NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10     # Number of concurrent clients

# Arrays to store throughput and latency
throughput_ = []
latency_ = []
elastiput_ = []
time_ = []
def client_thread(client_id):
    connection = http.client.HTTPConnection(HOST, PORT)
    print("Connection made")
    div = NUM_REQUESTS * 3
    # Start time
    start_time = time.time()
    
    for i in range(NUM_REQUESTS):
        if(i % 100 == 0):
            loop_time = time.time()
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"
        
        # PUT request
        #r = requests.put(f"http://127.0.0.1/put?key={key}&value={value}")
        connection.request("PUT", f"/put?key={key}&value={value}")
        response = connection.getresponse()
        response.read()

        # GET request
        #r = requests.get(f"http://127.0.0.1/get?key={key}")
        connection.request("GET", f"/get?key={key}")
        response = connection.getresponse()
        response.read()

        # DEL request
        #r = requests.delete(f"http://127.0.0.1/del?key={key}")
        connection.request("DELETE", f"/del?key={key}")
        response = connection.getresponse()
        response.read()
        if(i % 100 == 0):
            time_elapsed = time.time() - loop_time
            time_.append(time.time() - start_time)
            throughput_.append(div / time_elapsed)
            latency_.append(time_elapsed / div)
    # End time
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    throughput = NUM_REQUESTS * 3 / elapsed_time  # Multiply by 3 for PUT, GET, DEL
    latency = elapsed_time / (NUM_REQUESTS * 3)  # Average latency per request
    # throughput_x[client_id] = NUM_REQUESTS * 3 / elapsed_time  # Multiply by 3 for PUT, GET, DEL
    # latency_x[client_id] = elapsed_time / (NUM_REQUESTS * 3)  # Average latency per request
    # elastiput_x[client_id] = throughput_x[client_id] / latency_x[client_id]

    print(f"Client-{client_id} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds")

if __name__ == "__main__":
    clients = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    print("Testing completed.")
    # time = np.arange(NUM_CLIENTS)

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots()

    # Plot throughput
    color = 'tab:blue'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Throughput (req/s)', color=color)
    ax1.plot(time_, throughput_, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Create a second y-axis for latency
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Latency (s)', color=color)
    ax2.plot(time_, latency_, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title('Throughput and Latency over Time (3 Node)')
    # Show the plot
    plt.show()