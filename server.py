from flask import Flask, request, jsonify

# Create a Flask web server
app = Flask(__name__)

@app.route('/reverse', methods=['POST'])
def reverse_string():
    """
    Endpoint to handle client requests.
    It accepts a JSON payload with a "string" key,
    reverses the string, and returns it in the response.
    """
    # Check if the request has a JSON body and if 'string' key exists
    if not request.json or 'string' not in request.json:
        return jsonify({"error": "Invalid request: Missing 'string' in JSON body"}), 400

    original_string = request.json['string']
    
    # Reverse the string using slicing
    reversed_string = original_string[::-1]
    
    return jsonify({"reversed_string": reversed_string})

if __name__ == '__main__':
    # The server will be accessible on port 5000 inside the container
    app.run(host='0.0.0.0', port=5000)