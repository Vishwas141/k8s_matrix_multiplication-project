# custom_scaler.py
from flask import Flask, jsonify
import numpy as np
import time

app = Flask(__name__)

@app.route('/multiply', methods=['GET'])
def multiply():
    matrix_size = 100

    # Generate random matrices
    A = np.random.rand(matrix_size, matrix_size)
    B = np.random.rand(matrix_size, matrix_size)

    # Measure processing time
    start_time = time.time()
    result = np.dot(A, B)
    end_time = time.time()

    processing_time_ms = (end_time - start_time) * 1000

    return jsonify({
        'processing_time_ms': round(processing_time_ms, 3)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
