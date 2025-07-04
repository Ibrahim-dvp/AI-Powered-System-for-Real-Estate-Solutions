import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from analytics import analytics_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
app.register_blueprint(analytics_bp)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'dashboard-analytics',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
