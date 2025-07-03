"""
Web Interface Service
====================

This service provides a simple web server for the dashboard interface.
It serves the HTML, CSS, and JavaScript files for the real estate dashboard.
"""

import os
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('.', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'web-interface',
        'timestamp': '2025-01-07T10:00:00Z'
    })

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
