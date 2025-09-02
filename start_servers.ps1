# start_servers.ps1 (Final Version)

# This script must be run as an Administrator.

Write-Host "🚀 Starting setup for cloud assignment..." -ForegroundColor Green

# --- Part 1: Docker Swarm Setup ---
Write-Host "`n[1/2] Setting up Docker Swarm environment..." -ForegroundColor Yellow

$env:LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi* | Select-Object -First 1).IPAddress
if (-not $env:LOCAL_IP) {
    Write-Host "⚠️ Could not auto-detect Wi-Fi IP. You may need to find it manually with 'ipconfig'." -ForegroundColor Yellow
}

docker swarm init
if (-not $?) { Write-Host "❌ FATAL: 'docker swarm init' failed." -ForegroundColor Red; exit 1 }

docker service create --name cpu-loader-service --replicas 3 --publish published=5001,target=5000 cpu-loader-server:v1
if (-not $?) {
    Write-Host "❌ FATAL: 'docker service create' failed." -ForegroundColor Red
    docker swarm leave --force | Out-Null; exit 1
}
Write-Host "  - Docker Swarm service is LIVE."


# --- Part 2: Kubernetes (Minikube) Preparation ---
Write-Host "`n[2/2] Preparing Kubernetes environment..." -ForegroundColor Yellow
Write-Host "  - Starting Minikube..."
minikube start
if (-not $?) { Write-Host "❌ FATAL: 'minikube start' failed." -ForegroundColor Red; exit 1 }

Write-Host "  - Loading Docker image into Minikube..."
minikube image load cpu-loader-server:v1
if (-not $?) { Write-Host "❌ FATAL: 'minikube image load' failed." -ForegroundColor Red; exit 1 }

Write-Host "  - Applying Kubernetes configurations..."
kubectl apply -f deployment.yaml,service.yaml,hpa.yaml
if (-not $?) { Write-Host "❌ FATAL: 'kubectl apply' failed." -ForegroundColor Red; exit 1 }


# --- Part 3: Final Instructions ---
Write-Host "`n✅✅✅ Setup Complete! Ready for Final Step. ✅✅✅" -ForegroundColor Green
Write-Host "------------------------------------------------------------------"
Write-Host "[Docker Swarm] is LIVE at: http://$($env:LOCAL_IP):5001"
Write-Host "------------------------------------------------------------------"
Write-Host -ForegroundColor Cyan "`n➡️ To activate the Kubernetes service, open a NEW PowerShell terminal and run this command:"
Write-Host -ForegroundColor White "   kubectl port-forward service/cpu-loader-service --address 0.0.0.0 5002:5000"
Write-Host -ForegroundColor Cyan "Your Kubernetes service will then be available at http://$($env:LOCAL_IP):5002"