# Start Minikube
minikube start

# Enable metrics server (optional)
minikube addons enable metrics-server

# Build Docker images
docker build -t custom-app:latest -f Dockerfile.app .
docker build -t matrix-multiplier:latest -f Dockerfile.scaler .

# Load into Minikube
minikube image load custom-app:latest
minikube image load matrix-multiplier:latest

# Apply K8s manifests
kubectl apply -f k8s-manifests.yaml

# View logs
kubectl logs -f deployment/custom-app
