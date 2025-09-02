# start_servers.ps1 (Final Fully Automated Version)

# This script must be run as an Administrator.

Write-Host "🚀 Starting full-stack deployment for cloud assignment..." -ForegroundColor Green

# --- Part 1: Docker Swarm Setup ---
Write-Host "`n[1/2] Setting up Docker Swarm environment..." -ForegroundColor Yellow

# Find the Wi-Fi IP for displaying the final URL.
$env:LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi* | Select-Object -First 1).IPAddress
if (-not $env:LOCAL_IP) {
    Write-Host "⚠️ Could not auto-detect Wi-Fi IP. Please find it manually with 'ipconfig' to provide to the evaluator." -ForegroundColor Yellow
}

# Run 'docker swarm init' without IP flags to let Docker auto-detect the best configuration.
docker swarm init
if (-not $?) { Write-Host "❌ FATAL: 'docker swarm init' failed. Docker is unable to configure swarm networking on this machine." -ForegroundColor Red; exit 1 }

docker service create --name cpu-loader-service --replicas 3 --publish published=5001,target=5000 cpu-loader-server:v1
if (-not $?) {
    Write-Host "❌ FATAL: 'docker service create' failed." -ForegroundColor Red
    docker swarm leave --force | Out-Null; exit 1
}
Write-Host "  - Docker Swarm service is LIVE."


# --- Part 2: Kubernetes (Minikube) Setup ---
Write-Host "`n[2/2] Preparing and activating Kubernetes environment..." -ForegroundColor Yellow
Write-Host "  - Starting Minikube..."
minikube start
if (-not $?) { Write-Host "❌ FATAL: 'minikube start' failed." -ForegroundColor Red; exit 1 }

Write-Host "  - Loading Docker image into Minikube..."
minikube image load cpu-loader-server:v1
if (-not $?) { Write-Host "❌ FATAL: 'minikube image load' failed." -ForegroundColor Red; exit 1 }

Write-Host "  - Applying Kubernetes configurations..."
kubectl apply -f deployment.yaml,service.yaml,hpa.yaml
if (-not $?) { Write-Host "❌ FATAL: 'kubectl apply' failed." -ForegroundColor Red; exit 1 }

# Automatically start the port-forward process in a new window.
Write-Host "  - Starting Kubernetes port-forward in a new window... (Please keep this new window open)"
$portForwardCommand = "kubectl port-forward service/cpu-loader-service --address 0.0.0.0 5002:5000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$portForwardCommand"
Write-Host "  - Kubernetes service is LIVE."


# --- Part 3: Final Summary ---
Write-Host "`n✅✅✅ All Services Deployed! ✅✅✅" -ForegroundColor Green
Write-Host "Both services are now running and accessible on your local network."
Write-Host "------------------------------------------------------------------"
Write-Host "[Docker Swarm]:   http://$($env:LOCAL_IP):5001"
Write-Host "[Kubernetes]:     http://$($env:LOCAL_IP):5002"
Write-Host "------------------------------------------------------------------"
Write-Host "Provide these two URLs to your professor for testing."
Write-Host "Keep this terminal AND the new 'kubectl port-forward' window open."
