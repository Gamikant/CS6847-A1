# stop_servers.ps1

Write-Host "🧹 Cleaning up all services and clusters..." -ForegroundColor Yellow

# Stop Docker Swarm
Write-Host "  - Removing Docker Swarm service..."
docker service rm cpu-loader-service | Out-Null
docker swarm leave --force | Out-Null

# Stop Minikube
Write-Host "  - Stopping Minikube cluster..."
minikube stop | Out-Null

Write-Host "`n❗ Please manually close the 'kubectl port-forward' PowerShell window." -ForegroundColor Cyan
Write-Host "✅ Cleanup complete." -ForegroundColor Green