import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Add the parent directory to the sys.path to allow imports from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import blueprints after adjusting sys.path
from src.routes.lead_scoring import lead_scoring_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(lead_scoring_bp, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({'status': 'healthy', 'service': 'lead-scoring-service', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


