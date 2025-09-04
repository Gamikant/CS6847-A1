import argparse
import asyncio
import aiohttp
import time
import os
import random
import string
import statistics
import sys

# --- CONFIGURATION ---
# HARDCODE your roll number here
ROLL_NUMBER = "CE21B097"
IPv4_ADDRESS = "192.168.0.129"  # Default IP address of the server (change if needed)

# The 10 specific strings provided in the 'template output.pdf'
STRINGS_10 = [
    "5PKOHCL60uxRd0xXHQ", "JHfJtHH9", "gZFEMAS2JA", "NkmPgjT2uMwWvQ9",
    "1V0NTS", "tcmViV3cxd6J794H", "SKZpKaksPB1", "5ygFfJXEgn7ssgyus",
    "mvZ5wv7qfk", "tD58eeUOLh"
]

def generate_random_string(length=15):
    """Generates a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def send_request(session, url, input_string):
    """Sends a single POST request and returns the results."""
    payload = {'string': input_string}
    start_time = time.monotonic()
    try:
        async with session.post(url, json=payload, timeout=20) as response:
            if response.status == 200:
                data = await response.json()
                response_time = time.monotonic() - start_time
                return {
                    "time": response_time,
                    "original": input_string,
                    "reversed": data.get("reversed_string", "KEY_ERROR"),
                    "status": "SUCCESS"
                }
            else:
                return {"status": f"HTTP_{response.status}"}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return {"status": "CONNECTION_ERROR"}

async def run_experiment(server_ip, port, environment, num_strings):
    """Runs a single experiment and generates the corresponding output file."""
    
    # Capitalize environment for display and folder names
    env_name_capitalized = environment.capitalize()
    print(f"\n--- Starting Test: {env_name_capitalized} with {num_strings} strings on {server_ip}:{port} ---")
    
    # Create the correct output path (e.g., outputs/Kubernetes/)
    output_dir = os.path.join("outputs", env_name_capitalized)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename (e.g., CE21B097kubernetes10.txt)
    filename = f"{ROLL_NUMBER}{environment.lower()}{num_strings}.txt"
    file_path = os.path.join(output_dir, filename)
    
    print(f"Output will be saved to: {file_path}")
    
    url = f"http://{server_ip}:{port}/reverse"
    
    strings_to_send = STRINGS_10 if num_strings == 10 else [generate_random_string() for _ in range(num_strings)]

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, url, s) for s in strings_to_send]
        results = await asyncio.gather(*tasks)

    successful_requests = [r for r in results if r.get("status") == "SUCCESS"]
    
    if not successful_requests:
        print("❌ ERROR: No successful requests were made. Please check:")
        print("  1. Is the server running?")
        print("  2. Is the IP address and port correct?")
        print("  3. Did you 'Allow access' on the Windows Firewall prompt?")
        with open(file_path, "w") as f:
            f.write("Test failed. No successful requests.\n")
        return

    response_times = [r['time'] for r in successful_requests]
    avg_response_time = statistics.mean(response_times)

    with open(file_path, "w") as f:
        if num_strings == 10:
            for res in successful_requests:
                f.write(f"Original: {res['original']}\n")
                f.write(f"Reversed: {res['reversed']}\n\n")
            f.write(f"average_response_time={avg_response_time:.4f}\n")
        else:
            f.write(f"average_response_time={avg_response_time:.4f}\n")
    
    print(f"✅ Test finished. Average response time: {avg_response_time:.4f}s")

async def main():
    """Parses arguments and decides whether to run one experiment or all four."""
    parser = argparse.ArgumentParser(description="Cloud Computing Assignment Client. Run without arguments to execute all 4 required tests.")
    parser.add_argument("--ip", default=IPv4_ADDRESS, help="The IP address of the server (default: 192.168.0.129 - my hostel wi-fi network).")
    parser.add_argument("--environment", choices=['dockerswarm', 'kubernetes'], help="The target environment.")
    parser.add_argument("--strings", type=int, help="The number of strings to process.")
    
    args = parser.parse_args()

    # If user provides specific arguments, run only that one test
    if args.environment and args.strings:
        port = 5001 if args.environment == 'dockerswarm' else 5002
        await run_experiment(args.ip, port, args.environment, args.strings)
    
    # If no specific arguments are given, run all four standard experiments
    else:
        if len(sys.argv) > 1: # User provided some args but not all required for a single run
            print("Usage: To run a single test, provide both --environment and --strings.")
            print("Running all 4 standard tests instead...")
        
        print("🚀 No specific experiment defined. Running all 4 standard evaluation tests...")
        
        experiments = [
            {'env': 'dockerswarm', 'port': 5001, 'num': 10},
            {'env': 'kubernetes',  'port': 5002, 'num': 10},
            {'env': 'dockerswarm', 'port': 5001, 'num': 10000},
            {'env': 'kubernetes',  'port': 5002, 'num': 10000}
        ]
        
        for exp in experiments:
            await run_experiment(args.ip, exp['port'], exp['env'], exp['num'])
            
        print("\n🎉 All 4 experiments are complete.")

if __name__ == "__main__":
    asyncio.run(main())