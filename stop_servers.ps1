# stop_servers.ps1

Write-Host "🧹 Cleaning up all deployed services..." -ForegroundColor Yellow

# --- Docker Swarm Cleanup ---
Write-Host "  - Removing Docker Swarm service..."
docker service rm string-reverser-swarm-service | Out-Null
docker swarm leave --force | Out-Null
Write-Host "  - Docker Swarm cleanup complete."

# --- Kubernetes Cleanup ---
Write-Host "  - Deleting Kubernetes resources (deployment, service, hpa)..."
kubectl delete -f deployment.yaml,service.yaml,hpa.yaml | Out-Null
Write-Host "  - Kubernetes cleanup complete."

Write-Host "`n✅ Cleanup complete." -ForegroundColor Green
