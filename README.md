# CS6847 - Cloud Computing Assignment 1: Orchestrator Performance Comparison

## Project Overview

This project aims to compare the performance and behavior of a containerized "string reverser" web application deployed on two popular orchestration platforms: **Docker Swarm** and **Kubernetes**.

The key difference in the setups is the scaling strategy:

  * **Docker Swarm**: Deployed with a **fixed** number of 3 replicas.
  * **Kubernetes**: Deployed with a **dynamic, CPU-based autoscaling** mechanism, managed by a Horizontal Pod Autoscaler (HPA). The number of replicas can scale from 3 up to 10 based on CPU load.

An automated client script (`client.py`) is used to send both low (10) and high (10,000) volumes of requests to each service to measure and compare their average response times under different loads.

-----

## Prerequisites

Before you begin, please ensure you have the following installed and configured on your Windows machine:

1.  **Docker Desktop**: Make sure it's running and you can execute `docker` commands in PowerShell.
2.  **Kubernetes**: Enable Kubernetes within Docker Desktop's settings (`Settings -> Kubernetes -> Enable Kubernetes`).
3.  **PowerShell**: The automation scripts are written for PowerShell.

-----

## One-Time Setup Instructions

These steps only need to be performed once to prepare the environment.

### 1\. Build the Docker Image

First, we need to build the container image for our Flask application.

Navigate to the project's root directory in a PowerShell terminal and run:

```powershell
docker build -t string-reverser:v1 .
```

### 2\. Install and Patch Kubernetes Metrics Server

The Kubernetes HPA requires a component called the **Metrics Server** to collect CPU and memory data from pods. For Docker Desktop, it needs a special patch to work correctly.

Open a PowerShell terminal and run the following two commands:

```powershell
# 1. Install the Metrics Server component
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 2. Patch the deployment for Docker Desktop compatibility
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

You can verify it's working by running `kubectl top pods -n kube-system`. If you see the `metrics-server` pod with CPU/Memory values, the setup was successful.

-----

## Running the Experiment

The entire process is automated with PowerShell scripts.

### 1\. Start the Servers

This step will initialize Docker Swarm, deploy the Kubernetes resources, and expose both services on your local network.

Open a new PowerShell terminal **as Administrator** in the project root directory. You may need to bypass the execution policy for this session.

```powershell
# Allow running scripts for this PowerShell session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Run the deployment script
.\start_servers.ps1
```

This script will:

  * Detect your local Wi-Fi IP address.
  * Deploy the Docker Swarm service on port `5001`.
  * Deploy the Kubernetes service, HPA, and deployment.
  * **Open a new PowerShell window** for `kubectl port-forward`. This exposes the Kubernetes service on port `5002`.

**IMPORTANT**: Keep both the original PowerShell window and the new `kubectl port-forward` window open throughout the experiment.

At the end of the script, you will see the IP and ports for both services, which the evaluator will need. For example:

```
[Docker Swarm]:   http://192.168.0.129:5001/reverse
[Kubernetes]:     http://192.168.0.129:5002/reverse
```

### 2\. Run the Client Tests

This step will be performed by the evaluator on their machine, which is connected to the same network.

#### Running the Full Evaluation Suite

To run the full suite of four tests as required by the assignment, open a new terminal in the project directory and execute:

```powershell
python client.py --ip <YOUR_SERVER_IP>
```

Replace `<YOUR_SERVER_IP>` with the IP address shown by the `start_servers.ps1` script (e.g., `192.168.0.129`). If you are running the client on the same machine as the server, you can omit the `--ip` flag.

#### Running a Custom Experiment (Optional)

The `client.py` script also allows for running a single, custom experiment. This is useful for testing with different request numbers. Use the `--environment` and `--strings` flags to specify your target.

For example, to send 500 requests to the Docker Swarm service:

```powershell
python client.py --ip <YOUR_SERVER_IP> --environment dockerswarm --strings 500
```

This will generate a single output file (e.g., `CE21B097dockerswarm500.txt`) in the `outputs/Dockerswarm/` directory.

-----

## Expected Output

When running the full suite, the client script will create an `outputs` directory with the following structure:

```
outputs/
├── Dockerswarm/
│   ├── CE21B097dockerswarm10.txt
│   └── CE21B097dockerswarm10000.txt
└── Kubernetes/
    ├── CE21B097kubernetes10.txt
    └── CE21B097kubernetes10000.txt
```

  * The `10.txt` files will contain the original and reversed strings for 10 requests, plus the average response time.
  * The `10000.txt` files will contain only the average response time for the 10,000 requests.

-----

## Cleanup

After the evaluation is complete, you can tear down all the created services and deployments by running the cleanup script in the project's root directory:

```powershell
.\stop_servers.ps1
```

This will remove the Docker Swarm service, leave the swarm, and delete all the Kubernetes resources (deployment, service, and HPA). You can then safely close the `kubectl port-forward` window.