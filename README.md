# CS6847: Cloud Computing - Assignment 1
## A Comparative Study of Fixed-Scale vs. Auto-Scaling Systems

### 1. Project Objective

The primary objective of this assignment is to implement, deploy, and evaluate a client-server application to demonstrate the performance differences between a fixed-scale system (Docker Swarm) and an auto-scaling system (Kubernetes).

The evaluation focuses on observing the server's average response time under varying client request loads (requests per second) and analyzing the behavior of each orchestration platform, particularly the auto-scaling feature of Kubernetes based on CPU utilization.

### 2. System Design and Implementation

#### 2.1. Server (`server.py`)
- **Technology:** Python with the Flask framework.
- **Functionality:** The server exposes a single endpoint (`/`). Upon receiving a request, it performs a computationally expensive, CPU-bound task—calculating all prime numbers up to 15,000. This is designed to simulate a realistic CPU load that can be used to trigger CPU-based auto-scaling.
- **Networking:** The server is configured to listen on `0.0.0.0`, making it accessible on all network interfaces of the host machine, which is crucial for the live evaluation.

#### 2.2. Client (`client.py`)
- **Technology:** Python with `asyncio` and the `aiohttp` library.
- **Functionality:** The client is a powerful command-line tool capable of generating a high volume of concurrent requests to the server.
    - **Flexible Load:** It accepts a command-line argument (`--rps`) to specify the exact number of requests per second to send.
    - **Circuit Breaker:** To prevent infinite loops during server overload, the client implements a circuit breaker. If it detects 100 consecutive connection errors or timeouts, it aborts the current test, writes a clear message to the output file, and allows the evaluation to proceed.
    - **Automated File Generation:** The client automatically creates the required output files in the correct directory structure (`outputs/Docker/` or `outputs/Kubernetes/`).

#### 2.3. Containerization (`Dockerfile`)
- The server application is containerized using a multi-stage `Dockerfile` based on a lightweight Python slim image (`python:3.9-slim`). This ensures a small, efficient, and portable image that contains all necessary code and dependencies.

#### 2.4. Orchestration Environments

**A. Docker Swarm (Fixed-Scale System)**
- **Configuration:** Deployed as a Docker Swarm service with a fixed replica count of **3**.
- **Purpose:** This environment serves as the baseline for a "statically provisioned" system without auto-scaling. Its performance under high load demonstrates the limitations of a fixed-capacity architecture.

**B. Kubernetes (Auto-Scaling System)**
- **Configuration:** Deployed using three manifest files:
    - `deployment.yaml`: Defines the application deployment, initially starting with **3 replicas**. It critically includes CPU resource requests (`200m`) and limits (`500m`), which are necessary for the auto-scaler to function.
    - `hpa.yaml`: The Horizontal Pod Autoscaler is configured to monitor the CPU utilization of the pods. It will trigger a scale-up event if the average CPU utilization exceeds **50%**. The number of replicas will automatically scale between a minimum of **3** and a maximum of **10**.
    - `service.yaml`: Exposes the deployment to the network.

### 3. Prerequisites

#### 3.1. Server Host Machine (Your Machine)
- Windows OS with PowerShell
- Docker Desktop
- Minikube & `kubectl`

#### 3.2. Evaluator Machine (Professor's Machine)
- Python 3.8+
- The `aiohttp` library (`pip install aiohttp`)
- Network access to the Server Host machine (e.g., connected to the same Wi-Fi)

---

### 4. Execution Guide for Live Evaluation

This guide provides the complete, end-to-end process for setting up the servers and running the performance tests.

#### 4.1. Server Host Setup (Your Steps)

The entire server-side deployment is automated with a single script.

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

#### 4.2. Evaluator's Steps (Professor's Steps)

The evaluator will run the `client.py` script to conduct the required tests.

**To run a test, specify the server IP, port, environment, and the requests per second (RPS).**

**A. Test Docker Swarm at 10 RPS:**
```bash
python client.py <DOCKER_IP> --port 5001 --environment docker --rps 10
````

**B. Test Docker Swarm at 10,000 RPS:**

```bash
python client.py <DOCKER_IP> --port 5001 --environment docker --rps 10000
```

**C. Test Kubernetes at 10 RPS:**

```bash
python client.py <KUBERNETES_IP> --port 5002 --environment kubernetes --rps 10
```

**D. Test Kubernetes at 10,000 RPS:**

```bash
python client.py <KUBERNETES_IP> --port 5002 --environment kubernetes --rps 10000
```

-----

### 5\. Output Files

The client script generates two types of output files as required by the submission guidelines:

1.  **Raw Response Time Logs:** These files contain the response time for every single request (or an error message). They are placed in separate folders for each environment.

      - `outputs/Docker/Docker_response_10.txt`
      - `outputs/Docker/Docker_response_10000.txt`
      - `outputs/Kubernetes/kubernetes_response_10.txt`
      - `outputs/Kubernetes/kubernetes_response_10000.txt`

2.  **Summary File (`Output.txt`):** After each test run, this file is regenerated. It contains a cumulative and sorted list of the average response times for every experiment conducted so far.

      - **Format:** `<Environment @ Rate RPS, Average Response Time>`
      - **Example:**
        ```
        <Docker @ 10 RPS, 0.0550>
        <Docker @ 10000 RPS, 5.6580>
        <Kubernetes @ 10 RPS, 0.1891>
        <Kubernetes @ 10000 RPS, 6.8424>
        ```

### 6\. Cleanup (Server Host)

After the evaluation is complete, run the cleanup script on the server host machine in an **Administrator PowerShell** to stop all services, containers, and clusters.

```powershell
.\stop_servers.ps1
```

You will also need to manually close the second PowerShell window that was opened for the Kubernetes connection.