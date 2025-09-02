# CS6847: Cloud Computing - Assignment 1

This project demonstrates and evaluates the performance of a client-server application deployed in two distinct environments: a fixed-scale service on **Docker Swarm** and an auto-scaling service on **Kubernetes**.

The client script is designed to be flexible, allowing the user to specify any request rate for testing. The entire server-side setup is fully automated with a single script for a seamless evaluation experience.

**GitHub Repository:**
https://github.com/Gamikant/CS6847-A1/tree/master

## Project Structure
```text
.
├── Dockerfile              \# Instructions to build the server container
├── README.md               \# This file
├── client.py               \# Automated client side script to run performance tests
├── deployment.yaml         \# Kubernetes Deployment configuration
├── hpa.yaml                \# Kubernetes Horizontal Pod Autoscaler configuration
├── requirements.txt        \# Python dependencies for the server
├── server.py               \# The Flask server application
├── service.yaml            \# Kubernetes Service configuration
├── start_servers.ps1       \# Automation script to deploy both environments
├── stop_servers.ps1        \# Automation script to deploy both environments
├── Output.txt              \# Average response time with different rates for both environments
└── outputs/                \# Results of both clusters with different request rates from client
    ├── Docker/             \# Results for server container in docker swarm
    └── kubernetes/         \# Results for server container in kubernetes
```

## Prerequisites

### Server Host Machine (Student's Machine)
* Windows OS with PowerShell
* Docker Desktop
* Minikube & `kubectl`

### Evaluator Machine (Evaluator's Machine)
* Python 3.9.13
* The `aiohttp` library (`pip install aiohttp`)
* Network access to the Server Host machine (e.g., connected to the same Wi-Fi)

---

## Execution Guide for Live Evaluation

This guide is split into two parts: the setup steps for the **Server Host** and the testing steps for the **Evaluator**.

### Part 1: Server Host Setup (Student Steps)

The server setup is a simple two-step process.

1.  **Build the Docker Image**
    Open PowerShell and run the following command in the project's root directory:
    ```bash
    docker build -t cpu-loader-server:v1 .
    ```

2.  **Run the Automation Script**
    Run the setup script in an **Administrator PowerShell** window. This single command will deploy both the Docker Swarm and Kubernetes services.
    ```powershell
    # Allow script execution for the current session (if needed)
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    
    # Run the main setup script
    .\start_servers.ps1
    ```
    The script will open a **second PowerShell window** for the Kubernetes network connection. When the script finishes, it will print the final URLs for both services. **Keep both PowerShell windows open** throughout the evaluation.

### Part 2: Evaluator's Steps (Evaluator's Steps)

The evaluator can run the `client.py` script for any desired request rate using the `--rps` flag.

**To run a test, specify the server IP, port, environment, and the desired requests per second (RPS).**

#### Example Commands:

* **To test Docker Swarm at 10 RPS:**
    ```bash
    python client.py <DOCKER_IP> --port 5001 --environment docker --rps 10
    ```

* **To test Kubernetes at 10,000 RPS:**
    ```bash
    python client.py <KUBERNETES_IP> --port 5002 --environment kubernetes --rps 10000
    ```

* **To run a custom test (e.g., Kubernetes at 500 RPS):**
    ```bash
    python client.py <KUBERNETES_IP> --port 5002 --environment kubernetes --rps 500
    ```

* **The `DOCKER_IP` and `KUBERNETES_IP` are the Wi-Fi network's IPv4 addresses, and they both are same**
    - The evaluator (client) and the student's laptop (server) should be connected to the same Wi-Fi network otherwise the requests can't be sent.
    - For the experiment to run, please connect both client and server to the the same Wi-Fi network.
---

## Expected Output

After each run, the client script will:
1.  Create a specific response file for that test (e.g., `outputs/Docker/Docker_response_10.txt`).
2.  Scan **all** existing response files in the `outputs` directory.
3.  Generate a new, updated `Output.txt` file containing a sorted list of the average response times for every experiment run so far.

## Cleanup (Server Host)

After the evaluation is complete, run the cleanup script on the server host machine in an **Administrator PowerShell** to stop all services and clusters.
```powershell
.\stop_servers.ps1
```
You will also need to manually close the second PowerShell window that was opened for the Kubernetes connection.