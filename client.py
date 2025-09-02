import os
import time
import argparse
import asyncio
import aiohttp
import statistics
import glob

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
    
    # Correctly determine the folder (e.g., "Docker" or "Kubernetes")
    folder_path = os.path.join("outputs", test_name.split('_')[0].capitalize())
    os.makedirs(folder_path, exist_ok=True)
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
    """
    Scans all generated txt files in the outputs directory, calculates averages,
    and creates a cumulative Output.txt file.
    """
    print("\n--- Processing all results and generating cumulative Output.txt ---")
    
    final_results = []
    # Use glob to find all response files in both Docker and Kubernetes folders
    search_pattern = os.path.join("outputs", "**", "*_response_*.txt")
    result_files = glob.glob(search_pattern, recursive=True)

    for file_path in result_files:
        try:
            # Extract info from filename, e.g., "Docker" and "10"
            filename = os.path.basename(file_path)
            parts = filename.replace('.txt', '').split('_')
            env = parts[0].capitalize()
            rate = int(parts[2])

            with open(file_path, "r") as f:
                lines = f.readlines()
            
            valid_times = [float(line.strip()) for line in lines if line.strip().replace('.', '', 1).isdigit()]
            
            if valid_times:
                average = statistics.mean(valid_times)
                avg_response_time = f"{average:.4f}"
            else:
                avg_response_time = "N/A (No successful requests)"

            # Store rate as an integer for proper sorting later
            final_results.append({"env": env, "rate": rate, "avg": avg_response_time})
        except (IndexError, ValueError) as e:
            print(f"Warning: Could not parse file {filename}. Skipping. Error: {e}")
            continue

    if not final_results:
        print("No result files found to process.")
        return

    # Sort by environment, then by request rate
    final_results_sorted = sorted(final_results, key=lambda x: (x['env'], x['rate']))

    with open("Output.txt", "w") as f:
        for result in final_results_sorted:
            f.write(f"<{result['env']} @ {result['rate']} RPS, {result['avg']}>\n")
        
    print("--- Output.txt has been generated/updated successfully! ---")


async def main():
    """Main function to orchestrate a single, user-defined experiment."""
    parser = argparse.ArgumentParser(description="Cloud Computing Assignment 1 - Flexible Client")
    parser.add_argument("server_ip", help="The IP address of the server.")
    parser.add_argument("--port", type=int, required=True, help="The port of the server.")
    parser.add_argument(
        "--environment", 
        type=str, 
        required=True, 
        choices=['docker', 'kubernetes'], 
        help="The target environment to test ('docker' or 'kubernetes')."
    )
    parser.add_argument(
        "--rps",
        type=int,
        required=True,
        help="The number of requests per second (RPS) to send."
    )
    args = parser.parse_args()

    # Dynamically create the test name based on user input
    # e.g., "Docker_response_500" or "kubernetes_response_10000"
    test_name = f"{args.environment.capitalize()}_response_{args.rps}"
    # The script now runs only ONE test per execution.
    await run_experiment(test_name, args.server_ip, args.port, args.rps, TEST_DURATION_SECONDS)

    # After the test, process ALL available results to create a cumulative report.
    process_results()
    print(f"\nExperiment for {args.environment.upper()} at {args.rps} RPS is complete!")

if __name__ == "__main__":
    asyncio.run(main())
