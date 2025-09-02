import os
import time
import argparse
import asyncio
import aiohttp
import statistics

# --- Configuration ---
TEST_DURATION_SECONDS = 60
FAILURE_THRESHOLD = 100 

async def send_request(session, url):
    """Sends a single async HTTP request and returns the response time."""
    start_time = time.monotonic()
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                return time.monotonic() - start_time
            else:
                return "STATUS_ERROR"
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return "CONNECTION_ERROR"

async def run_experiment(test_name, server_ip, server_port, rps, duration):
    """Runs a single load test experiment for a given configuration."""
    print(f"\n--- Starting test: {test_name} at {rps} RPS for {duration}s ---")
    
    folder_path = os.path.join("outputs", test_name.split('_')[0].capitalize())
    os.makedirs(folder_path, exist_ok=True)
    # Correctly format the filename e.g., "kubernetes_response_10.txt"
    file_path = os.path.join(folder_path, f"{test_name}.txt")
    
    url = f"http://{server_ip}:{server_port}"
    response_times = []
    consecutive_failures = 0

    def write_results(aborted=False):
        with open(file_path, "w") as f:
            for res_time in response_times:
                if isinstance(res_time, float):
                    f.write(f"{res_time:.4f}\n")
                else:
                    f.write(f"{res_time}\n")
            if aborted:
                f.write("Test aborted due to server overload.\n")

    async with aiohttp.ClientSession() as session:
        start_time = time.monotonic()
        while time.monotonic() - start_time < duration:
            loop_start_time = time.monotonic()
            tasks = [send_request(session, url) for _ in range(rps)]
            results = await asyncio.gather(*tasks)
            
            for res_time in results:
                response_times.append(res_time)
                if isinstance(res_time, str):
                    consecutive_failures += 1
                else:
                    consecutive_failures = 0
            
            if consecutive_failures >= FAILURE_THRESHOLD:
                print(f"*** Circuit Breaker Tripped! {consecutive_failures} consecutive failures. Aborting test. ***")
                write_results(aborted=True)
                return

            loop_duration = time.monotonic() - loop_start_time
            if loop_duration < 1.0:
                await asyncio.sleep(1.0 - loop_duration)

    write_results(aborted=False)
    print(f"--- Test {test_name} finished. Data saved to {file_path} ---")

def process_results():
    """Reads all available results, calculates averages, and creates Output.txt."""
    print("\n--- Processing results and generating Output.txt ---")
    
    final_results = []
    output_dir = "outputs"
    # Search for all possible result files
    possible_files = [
        "Docker/Docker_response_10.txt", "Docker/Docker_response_10000.txt",
        "Kubernetes/kubernetes_response_10.txt", "Kubernetes/kubernetes_response_10000.txt"
    ]

    for file_rel_path in possible_files:
        file_path = os.path.join(output_dir, file_rel_path)
        
        # Extract info from filename, e.g., "Docker" and "10"
        parts = os.path.basename(file_path).replace('.txt', '').split('_')
        env = parts[0].capitalize()
        rate = parts[2]

        if not os.path.exists(file_path):
            continue # Skip files that don't exist yet

        with open(file_path, "r") as f:
            lines = f.readlines()
        
        valid_times = [float(line.strip()) for line in lines if line.strip().replace('.', '', 1).isdigit()]
        
        if valid_times:
            average = statistics.mean(valid_times)
            avg_response_time = f"{average:.4f}"
        else:
            avg_response_time = "N/A (No successful requests)"

        final_results.append(f"<{env} @ {rate} RPS, {avg_response_time}>")
    
    if not final_results:
        print("No result files found to process.")
        return

    with open("Output.txt", "w") as f:
        f.write("\n".join(sorted(final_results)))
        
    print("--- Output.txt has been generated/updated successfully! ---")

async def main():
    """Main function to orchestrate experiments based on environment."""
    parser = argparse.ArgumentParser(description="Cloud Computing Assignment 1 Client")
    parser.add_argument("server_ip", help="The IP address of the server.")
    parser.add_argument("--port", type=int, default=5000, help="The port of the server.")
    parser.add_argument(
        "--environment", 
        type=str, 
        required=True, 
        choices=['docker', 'kubernetes'], 
        help="The target environment to test ('docker' or 'kubernetes')."
    )
    args = parser.parse_args()

    # Define all possible experiments
    all_experiments = {
        "docker": [
            {"name": "Docker_response_10", "rps": 10},
            {"name": "Docker_response_10000", "rps": 10000},
        ],
        "kubernetes": [
            {"name": "kubernetes_response_10", "rps": 10},
            {"name": "kubernetes_response_10000", "rps": 10000},
        ]
    }

    # Select experiments to run based on the --environment argument
    experiments_to_run = all_experiments[args.environment]

    print(f"--- Preparing to run tests for the '{args.environment.upper()}' environment ---")
    for exp in experiments_to_run:
        await run_experiment(exp['name'], args.server_ip, args.port, exp['rps'], TEST_DURATION_SECONDS)

    # After tests, always process all available results
    process_results()
    print(f"\nAll tests for {args.environment.upper()} are complete!")

if __name__ == "__main__":
    asyncio.run(main())