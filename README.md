# CS6847: Cloud Computing - Assignment 1

This project demonstrates and evaluates the performance of a client-server application deployed in two distinct environments: a fixed-scale service on **Docker Swarm** and an auto-scaling service on **Kubernetes**. The goal is to observe the difference in server response time under both low (10 requests/sec) and high (10,000 requests/sec) loads.

The entire process is streamlined with automation scripts for easy setup and a smart client for clear, separate testing of each environment.

## Project Structure

```text
.
├── Dockerfile              \# Instructions to build the server container
├── README.md               \# This file
├── client.py               \# Automated script to run performance tests
├── deployment.yaml         \# Kubernetes Deployment configuration
├── hpa.yaml                \# Kubernetes Horizontal Pod Autoscaler configuration
├── requirements.txt        \# Python dependencies for the server
├── server.py               \# The Flask server application
├── service.yaml            \# Kubernetes Service configuration
├── start_servers.ps1       \# Automation script to deploy both environments
└── stop_servers.ps1        \# Automation script to clean up all resources
```

## Prerequisites

### Server Host Machine (Your Machine)
* Windows OS with PowerShell
* Docker Desktop
* Minikube & `kubectl`

### Evaluator Machine (Professor's Machine)
* Python 3.9.13
* The `aiohttp` library (`pip install aiohttp`)
* Network access to the Server Host machine (e.g., connected to the same Wi-Fi)

---

## Execution Guide for Live Evaluation

This guide is split into two parts: the setup steps for the **Server Host** and the testing steps for the **Evaluator**.

### Part 1: Server Host Setup (Your Steps)

Follow these steps on your machine to start both server environments.

1. **Build the Docker Image**
   Open PowerShell and run the following command in the project's root directory to build the container image for the server:
```bash
   docker build -t cpu-loader-server:v1 .
```

2.  **Run the Automation Script**
    This script will start the Docker Swarm service and prepare the Kubernetes environment. Run it in an **Administrator PowerShell** window. You may need to set the execution policy first.

```powershell
# Allow script execution for the current session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Run the main setup script
.\start_servers.ps1
```

    The script will provide the **final Docker Swarm URL** when it finishes.

3.  **Activate the Kubernetes Service**
    As instructed by the script's output, open a **new, separate PowerShell terminal** and run the `kubectl port-forward` command. This creates a network bridge to the Kubernetes cluster.

```powershell
kubectl port-forward service/cpu-loader-service --address 0.0.0.0 5002:5000
```

    This command will provide you with the **final Kubernetes URL**.

4.  **Provide URLs**
    You will now have two distinct URLs, both accessible on your local network. Provide both to the evaluator. **Keep both of your PowerShell windows open** throughout the entire test.

### Part 2: Evaluator's Steps (Professor's Steps)

The evaluator will run the `client.py` script twice from their machine to test each environment.

1.  **Test the Docker Swarm Environment**
    Run the client script with the `--environment docker` flag and the Docker Swarm URL providedy the host.

```bash
# Replace <DOCKER_IP> with the host's Wi-Fi IP
python client.py <DOCKER_IP> --port 5001 --environment docker
```

2.  **Test the Kubernetes Environment**
    Next, run the script again with the `--environment kubernetes` flag and the Kubernetes URL.

```bash
# Replace <KUBERNETES_IP> with the host's Wi-Fi IP
python client.py <KUBERNETES_IP> --port 5002 --environment kubernetes
```

## Expected Output

After the evaluator runs both commands, the following files and folders will be generated on their machine:

  * `outputs/Docker/`: Contains `Docker_response_10.txt` and `Docker_response_10000.txt`.
  * `outputs/Kubernetes/`: Contains `kubernetes_response_10.txt` and `kubernetes_response_10000.txt`.
  * `Output.txt`: A summary file with the average response time for all four experiments, formatted as `<Environment @ Rate RPS, Average Response Time>`.

## Cleanup (Server Host)

After the evaluation is complete, run the cleanup script on the server host machine in an **Administrator PowerShell** to stop all services and clusters.

```powershell
.\stop_servers.ps1
```

You will also need to manually close the `kubectl port-forward` window.