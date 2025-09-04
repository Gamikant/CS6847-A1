# This script must be run with Administrator privileges.

Write-Host "🚀 Starting deployment for the string reversal service..." -ForegroundColor Green

# --- Part 0: Network Setup ---
Write-Host "`n[0/3] Detecting Local Network IP Address..." -ForegroundColor Yellow
$env:LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi* | Select-Object -First 1).IPAddress
if (-not $env:LOCAL_IP) {
    Write-Host "⚠️ Could not auto-detect Wi-Fi/Ethernet IP. The script will use 'localhost'." -ForegroundColor Yellow
    Write-Host "⚠️ You will need to find your IP manually using 'ipconfig' for the evaluator." -ForegroundColor Yellow
    $env:LOCAL_IP = "localhost"
}
Write-Host "  - Server will be accessible at: $($env:LOCAL_IP)"


# --- Part 1: Docker Swarm Setup ---
Write-Host "`n[1/3] Setting up Docker Swarm environment..." -ForegroundColor Yellow
docker swarm leave --force | Out-Null
docker swarm init
if (-not $?) { Write-Host "❌ FATAL: 'docker swarm init' failed." -ForegroundColor Red; exit 1 }

docker service create --name string-reverser-swarm-service --replicas 3 --publish published=5001,target=5000 string-reverser:v1
if (-not $?) {
    Write-Host "❌ FATAL: 'docker service create' failed." -ForegroundColor Red
    docker swarm leave --force | Out-Null; exit 1
}
Write-Host "  - Docker Swarm service is now LIVE."


# --- Part 2: Kubernetes (Docker Desktop) Setup ---
Write-Host "`n[2/3] Preparing Kubernetes on Docker Desktop..." -ForegroundColor Yellow
Write-Host "  - Ensuring kubectl context is set to 'docker-desktop'..."
kubectl config use-context docker-desktop

Write-Host "  - Applying Kubernetes configurations (deployment, service, hpa)..."
kubectl apply -f deployment.yaml,service.yaml,hpa.yaml
if (-not $?) { Write-Host "❌ FATAL: 'kubectl apply' failed." -ForegroundColor Red; exit 1 }

# --- NEW: Wait for the deployment to be ready before port-forwarding ---
Write-Host "  - Waiting for Kubernetes pods to become ready... (This may take a minute)"
kubectl wait --for=condition=available deployment/string-reverser-deployment --timeout=120s
if (-not $?) { 
    Write-Host "❌ FATAL: Timed out waiting for Kubernetes deployment to be ready." -ForegroundColor Red
    Write-Host "  - Run 'kubectl get pods' to check the status of your pods for errors." -ForegroundColor Cyan
    exit 1 
}
Write-Host "  - Pods are running!"

Write-Host "  - Starting Kubernetes port-forward in a new window... (Please keep this new window open)"
$portForwardCommand = "kubectl port-forward service/string-reverser-service --address 0.0.0.0 5002:5000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$portForwardCommand"
Write-Host "  - Kubernetes service is now LIVE."


# --- Part 3: Final Summary ---
Write-Host "`n[3/3] ✅ All Services Deployed Successfully! ✅" -ForegroundColor Green
Write-Host "The services are now running and accessible on your local network."
Write-Host "------------------------------------------------------------------"
Write-Host "[Docker Swarm]:   http://$($env:LOCAL_IP):5001/reverse"
Write-Host "[Kubernetes]:     http://$($env:LOCAL_IP):5002/reverse"
Write-Host "------------------------------------------------------------------"
Write-Host "Provide these URLs and the IP Address to your evaluator."
Write-Host "Keep this terminal AND the new 'kubectl port-forward' window open."

