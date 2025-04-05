# custom_app.py
import threading
import time
import requests
from kubernetes import client, config

# CONFIGURABLE
MULTIPLIER_SERVICE_URL = "http://matrix-multiplier-service:7000/multiply"
DEPLOYMENT_NAME = "matrix-multiplier"
NAMESPACE = "default"
MIN_REPLICAS = 1
MAX_REPLICAS = 10
USER_INCREMENT = 100
ROUND_INTERVAL = 5  # in seconds

# Initialize K8s client
config.load_incluster_config()
apps_v1 = client.AppsV1Api()

# Shared state
active_users = 0
active_users_lock = threading.Lock()

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
    global active_users
    try:
        response = requests.get(MULTIPLIER_SERVICE_URL, timeout=10)
        data = response.json()
        print(f"[User {user_id}] Processing time: {data['processing_time_ms']} ms")
    except Exception as e:
        print(f"[User {user_id}] Request failed: {e}")
    finally:
        with active_users_lock:
            active_users -= 1

def scale_loop():
    while True:
        with active_users_lock:
            current_users = active_users
        scale_deployment(current_users)
        time.sleep(ROUND_INTERVAL)

def user_generator():
    global active_users
    user_id_counter = 0
    while True:
        threads = []
        print(f"\n[User Generator] Spawning {USER_INCREMENT} new users...")
        with active_users_lock:
            active_users += USER_INCREMENT
        for _ in range(USER_INCREMENT):
            t = threading.Thread(target=simulate_user, args=(user_id_counter,))
            t.start()
            threads.append(t)
            user_id_counter += 1
        time.sleep(ROUND_INTERVAL)

if __name__ == "__main__":
    scaler_thread = threading.Thread(target=scale_loop, daemon=True)
    scaler_thread.start()

    user_generator()
