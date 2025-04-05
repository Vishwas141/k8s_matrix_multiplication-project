# custom_app_logger.py

import threading
import time
import requests
from kubernetes import client, config
import csv
from datetime import datetime

# CONFIGURABLE
USER_COUNT_INCREMENT = 100
MULTIPLIER_SERVICE_URL = "http://matrix-multiplier-service:7000/multiply"
DEPLOYMENT_NAME = "matrix-multiplier"
NAMESPACE = "default"
MIN_REPLICAS = 1
MAX_REPLICAS = 10
CSV_FILENAME = "processing_times.csv"

# Kubernetes client
config.load_incluster_config()
apps_v1 = client.AppsV1Api()

# Initialize CSV
with open(CSV_FILENAME, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "User ID", "Processing Time (ms)"])

# Thread-safe lock for writing to CSV
csv_lock = threading.Lock()

def scale_deployment(replicas):
    replicas = max(MIN_REPLICAS, min(MAX_REPLICAS, replicas))
    body = {'spec': {'replicas': replicas}}
    apps_v1.patch_namespaced_deployment_scale(
        name=DEPLOYMENT_NAME,
        namespace=NAMESPACE,
        body=body
    )
    print(f"[Scaler] Scaled to {replicas} replicas")

def simulate_user(user_id):
    try:
        response = requests.get(MULTIPLIER_SERVICE_URL, timeout=5)
        data = response.json()
        processing_time = data.get("processing_time_ms", -1)

        print(f"[User {user_id}] Processing time: {processing_time} ms")

        # Write to CSV
        with csv_lock:
            with open(CSV_FILENAME, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now(), user_id, processing_time])

    except Exception as e:
        print(f"[User {user_id}] Request failed: {e}")

def simulate_users_and_scale():
    current_users = 0
    while True:
        current_users += USER_COUNT_INCREMENT
        print(f"\n[Simulating] {current_users} users...")

        threads = []
        for i in range(current_users):
            t = threading.Thread(target=simulate_user, args=(i,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        scale_deployment(current_users)
        time.sleep(5)

if __name__ == "__main__":
    simulate_users_and_scale()
