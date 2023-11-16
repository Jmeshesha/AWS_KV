import socket
import time
import threading
import http.client
import requests
import matplotlib.pyplot as plt
import numpy as np

HOST, PORT = '127.0.0.1', 80
NUM_REQUESTS = 100  # Number of requests to send per client
NUM_CLIENTS = 5     # Number of concurrent clients

latencies = []  # To store latencies for each request
throughputs = []

def client_thread(client_id):
    connection = http.client.HTTPConnection(HOST, PORT)

    start_time_all = time.time()  # Record start time for each client

    for i in range(NUM_REQUESTS):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"
        
        # PUT request
        start_time = time.time()
        connection.request("PUT", f"/put?key={key}&value={value}")
        response = connection.getresponse()
        response.read()
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)

        # GET request
        start_time = time.time()
        connection.request("GET", f"/get?key={key}")
        response = connection.getresponse()
        response.read()
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)

        # DEL request
        start_time = time.time()
        connection.request("DELETE", f"/del?key={key}")
        response = connection.getresponse()
        response.read()
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)

    end_time_all = time.time()  # Record end time for each client

    total_requests = NUM_REQUESTS
    total_time = end_time_all - start_time_all

    throughput = total_requests / total_time
    throughputs.append(throughput)

    connection.close()

if __name__ == "__main__":
    clients = []
    start_time_all = time.time()  # Record start time for all clients

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    end_time_all = time.time()  # Record end time for all clients

    total_requests = NUM_CLIENTS * NUM_REQUESTS
    total_time = end_time_all - start_time_all

    throughput = total_requests / total_time
    print(f"Throughput: {throughput} requests per second")
    x = np.linspace(0, throughput, len(latencies))
    # Print average latency
    avg_latency = np.mean(latencies)
    print(f"Average Latency: {avg_latency} seconds")
    #print(max(throughputs))
    latencies.sort()
    # Plot latencies over throughput
    plt.plot(x, latencies)
    plt.title('Latencies Over Throughput With 3 Nodes')
    plt.xlabel('Throughput (requests per second)')
    plt.ylabel('Latency (seconds)')
    plt.show()

    print("Testing completed.")
