from flask import Flask, jsonify, request
import time

# Create a Flask web server
app = Flask(__name__)

def is_prime(n):
    """A simple function to check if a number is prime."""
    if n <= 1:
        return False
    # Check for factors from 2 up to the square root of n
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

@app.route('/', methods=['GET'])
def process_request():
    """
    Endpoint to handle client requests. It performs a CPU-intensive task.
    """
    start_time = time.time()
    
    # Simulate a CPU-intensive task by finding prime numbers
    # The upper limit can be adjusted to increase/decrease the load
    limit = 15000 
    primes = [num for num in range(limit) if is_prime(num)]
    
    end_time = time.time()
    
    # Return a success message along with some data
    return jsonify({
        "message": "Processed successfully",
        "primes_found": len(primes),
        "processing_time_seconds": round(end_time - start_time, 4)
    })

if __name__ == '__main__':
    # The server will be accessible on your local network
    # Port 5000 is used here, but can be changed
    app.run(host='0.0.0.0', port=5000)