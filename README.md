# CS6847: Cloud Computing Assignment 1 - Report

**Name:** [Your Name Here]
**Roll Number:** [Your Roll Number Here]

---

### 1. Introduction and Objective

The primary objective of this assignment is to conduct a practical performance comparison between two distinct container orchestration models: a fixed-scale system and an auto-scaling system. This was achieved by deploying a CPU-intensive server application on both **Docker Swarm** (configured with a fixed number of 3 replicas) and **Kubernetes** (configured to auto-scale from a minimum of 3 to a maximum of 10 replicas).

A custom client was developed to subject both environments to varying request loads, from low (10 RPS) to extreme (10,000 RPS). This report analyzes the resulting server response times to understand the benefits, trade-offs, and performance characteristics of each architectural approach. A key goal is to observe the real-world implications of auto-scaling, particularly its effectiveness and limitations when faced with both steady and sudden high-stress conditions. By analyzing the collected performance data, this report identifies the parameters responsible for variations in response time and provides a detailed analysis of the underlying causes.

---
### 2. System Design and Architecture

#### 2.1. Server Application (`server.py`)
- **Technology:** Python with the Flask framework.
- **Functionality:** The server exposes a single endpoint (`/`). Upon receiving a request, it performs a computationally expensive, CPU-bound task—calculating all prime numbers up to 15,000. This is designed to simulate a realistic CPU load that can be used to trigger CPU-based auto-scaling.
- **Networking:** The server is configured to listen on `0.0.0.0`, making it accessible on all network interfaces of the host machine, which is crucial for the live evaluation.

#### 2.2. Client Application (`client.py`)
- **Technology:** Python with `asyncio` and the `aiohttp` library for efficient, high-volume request handling.
- **Functionality:** The client is a flexible command-line tool capable of generating a configurable volume of concurrent requests to the server.
    - **Variable Load:** It accepts a command-line argument (`--rps`) to specify the exact number of requests per second to send for a 60-second duration.
    - **Circuit Breaker:** To handle server unavailability under extreme load, a circuit breaker was implemented. If 100 consecutive requests fail (due to connection errors or timeouts), the client aborts the current test, writes a clear failure message to the output file, and allows the evaluation to proceed.
    - **Automated Data Logging:** For each test, the client records the response time of every individual request into a dedicated log file and generates a cumulative `Output.txt` summary file.

#### 2.3. Containerization (`Dockerfile`)
- The server application is containerized using a `Dockerfile` based on the lightweight `python:3.9-slim` image. This ensures a small, efficient, and portable image that contains all necessary code and dependencies for consistent deployment across both platforms.