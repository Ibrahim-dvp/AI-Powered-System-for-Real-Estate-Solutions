"""
Lead Scoring Service
====================

This service handles intelligent lead scoring using machine learning models.
It processes user interactions, behavioral data, and demographic information
to assign quality scores to leads.

Features:
- Real-time lead scoring
- ML-based qualification
- Behavioral tracking
- Integration with Baserow CRM
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = os.getenv("BASEROW_API_URL", "https://dayta.intelligentb2b.com/api")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")
BASEROW_USERS_TABLE_ID = os.getenv("BASEROW_USERS_TABLE_ID")
BASEROW_LEADS_TABLE_ID = os.getenv("BASEROW_LEADS_TABLE_ID")
BASEROW_INTERACTIONS_TABLE_ID = os.getenv("BASEROW_INTERACTIONS_TABLE_ID")

class LeadScoringEngine:
    """Main lead scoring engine with ML models"""
    
    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'page_views', 'session_duration', 'bounce_rate',
            'email_opens', 'email_clicks', 'property_views',
            'search_queries', 'contact_forms', 'phone_calls',
            'budget_range', 'location_preference', 'property_type_preference',
            'days_since_registration', 'recency_score', 'frequency_score'
        ]
        self.load_models()
    
    def load_models(self):
        """Load pre-trained ML models or train new ones"""
        try:
            self.rf_model = joblib.load('models/rf_lead_scoring.pkl')
            self.gb_model = joblib.load('models/gb_lead_scoring.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            logger.info("Models loaded successfully")
        except FileNotFoundError:
            logger.info("No pre-trained models found. Training new models...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with sample data"""
        # Generate sample training data
        np.random.seed(42)
        n_samples = 1000
        
        # Create synthetic features
        data = {
            'page_views': np.random.poisson(5, n_samples),
            'session_duration': np.random.exponential(180, n_samples),
            'bounce_rate': np.random.beta(2, 3, n_samples),
            'email_opens': np.random.poisson(3, n_samples),
            'email_clicks': np.random.poisson(1, n_samples),
            'property_views': np.random.poisson(4, n_samples),
            'search_queries': np.random.poisson(2, n_samples),
            'contact_forms': np.random.poisson(0.5, n_samples),
            'phone_calls': np.random.poisson(0.3, n_samples),
            'budget_range': np.random.uniform(0, 1, n_samples),
            'location_preference': np.random.uniform(0, 1, n_samples),
            'property_type_preference': np.random.uniform(0, 1, n_samples),
            'days_since_registration': np.random.exponential(30, n_samples),
            'recency_score': np.random.uniform(0, 1, n_samples),
            'frequency_score': np.random.uniform(0, 1, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create target variable (high-quality leads)
        df['lead_quality'] = (
            (df['contact_forms'] > 0) | 
            (df['phone_calls'] > 0) | 
            (df['email_clicks'] > 2) |
            (df['property_views'] > 5)
        ).astype(int)
        
        # Prepare features
        X = df[self.feature_columns]
        y = df['lead_quality']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train models
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        self.rf_model.fit(X_train, y_train)
        self.gb_model.fit(X_train, y_train)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.rf_model, 'models/rf_lead_scoring.pkl')
        joblib.dump(self.gb_model, 'models/gb_lead_scoring.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        logger.info("Models trained and saved successfully")
    
    def calculate_lead_score(self, lead_data):
        """Calculate lead score using ML models"""
        try:
            # Extract features
            features = []
            for col in self.feature_columns:
                features.append(lead_data.get(col, 0))
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get predictions
            rf_prob = self.rf_model.predict_proba(features_scaled)[0][1]
            gb_prob = self.gb_model.predict_proba(features_scaled)[0][1]
            
            # Ensemble prediction
            final_score = (rf_prob + gb_prob) / 2
            
            # Convert to 0-100 scale
            score = int(final_score * 100)
            
            # Determine grade
            if score >= 80:
                grade = 'A'
            elif score >= 60:
                grade = 'B'
            elif score >= 40:
                grade = 'C'
            elif score >= 20:
                grade = 'D'
            else:
                grade = 'F'
            
            return {
                'score': score,
                'grade': grade,
                'probability': final_score,
                'confidence': abs(rf_prob - gb_prob) < 0.1
            }
            
        except Exception as e:
            logger.error(f"Error calculating lead score: {str(e)}")
            return {'score': 0, 'grade': 'F', 'probability': 0.0, 'confidence': False}

# Initialize lead scoring engine
lead_engine = LeadScoringEngine()

class BaserowAPI:
    """Baserow API integration"""
    
    def __init__(self):
        self.base_url = BASEROW_API_URL
        self.token = BASEROW_TOKEN
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_data(self, user_id):
        """Get user data from Baserow"""
        try:
            url = f"{self.base_url}/database/rows/table/{BASEROW_USERS_TABLE_ID}/{user_id}/"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            return None
    
    def get_user_interactions(self, user_id):
        """Get user interactions from Baserow"""
        try:
            url = f"{self.base_url}/database/rows/table/{BASEROW_INTERACTIONS_TABLE_ID}/"
            params = {'filters': f'user_id={user_id}'}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('results', [])
            return []
        except Exception as e:
            logger.error(f"Error fetching interactions: {str(e)}")
            return []
    
    def update_lead_score(self, user_id, score_data):
        """Update lead score in Baserow"""
        try:
            url = f"{self.base_url}/database/rows/table/{BASEROW_USERS_TABLE_ID}/{user_id}/"
            data = {
                'lead_score': score_data['score'],
                'lead_grade': score_data['grade'],
                'score_updated_at': datetime.now().isoformat()
            }
            response = requests.patch(url, headers=self.headers, json=data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating lead score: {str(e)}")
            return False

# Initialize Baserow API
baserow_api = BaserowAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'lead-scoring-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/score-lead', methods=['POST'])
def score_lead():
    """Score a lead based on provided data"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get user data from Baserow
        user_data = baserow_api.get_user_data(user_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user interactions
        interactions = baserow_api.get_user_interactions(user_id)
        
        # Prepare lead data for scoring
        lead_data = prepare_lead_data(user_data, interactions)
        
        # Calculate score
        score_result = lead_engine.calculate_lead_score(lead_data)
        
        # Update score in Baserow
        baserow_api.update_lead_score(user_id, score_result)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'score': score_result['score'],
            'grade': score_result['grade'],
            'probability': score_result['probability'],
            'confidence': score_result['confidence']
        })
        
    except Exception as e:
        logger.error(f"Error scoring lead: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk-score', methods=['POST'])
def bulk_score_leads():
    """Score multiple leads at once"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify({'error': 'user_ids array is required'}), 400
        
        results = []
        for user_id in user_ids:
            try:
                # Get user data
                user_data = baserow_api.get_user_data(user_id)
                if not user_data:
                    continue
                
                # Get interactions
                interactions = baserow_api.get_user_interactions(user_id)
                
                # Prepare and score
                lead_data = prepare_lead_data(user_data, interactions)
                score_result = lead_engine.calculate_lead_score(lead_data)
                
                # Update in Baserow
                baserow_api.update_lead_score(user_id, score_result)
                
                results.append({
                    'user_id': user_id,
                    'score': score_result['score'],
                    'grade': score_result['grade']
                })
                
            except Exception as e:
                logger.error(f"Error scoring user {user_id}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in bulk scoring: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/track-interaction', methods=['POST'])
def track_interaction():
    """Track user interaction and update lead score"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        interaction_type = data.get('type')
        
        if not user_id or not interaction_type:
            return jsonify({'error': 'user_id and type are required'}), 400
        
        # Record interaction in Baserow
        interaction_data = {
            'user_id': user_id,
            'interaction_type': interaction_type,
            'timestamp': datetime.now().isoformat(),
            'page_url': data.get('page_url'),
            'session_id': data.get('session_id'),
            'duration': data.get('duration', 0),
            'details': data.get('details', {})
        }
        
        # Store interaction
        url = f"{BASEROW_API_URL}/database/rows/table/{BASEROW_INTERACTIONS_TABLE_ID}/"
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        requests.post(url, headers=headers, json=interaction_data)
        
        # Recalculate lead score
        user_data = baserow_api.get_user_data(user_id)
        if user_data:
            interactions = baserow_api.get_user_interactions(user_id)
            lead_data = prepare_lead_data(user_data, interactions)
            score_result = lead_engine.calculate_lead_score(lead_data)
            baserow_api.update_lead_score(user_id, score_result)
        
        return jsonify({
            'success': True,
            'message': 'Interaction tracked and score updated'
        })
        
    except Exception as e:
        logger.error(f"Error tracking interaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

def prepare_lead_data(user_data, interactions):
    """Prepare lead data for scoring"""
    # Calculate interaction metrics
    page_views = len([i for i in interactions if i.get('interaction_type') == 'page_view'])
    email_opens = len([i for i in interactions if i.get('interaction_type') == 'email_open'])
    email_clicks = len([i for i in interactions if i.get('interaction_type') == 'email_click'])
    property_views = len([i for i in interactions if i.get('interaction_type') == 'property_view'])
    search_queries = len([i for i in interactions if i.get('interaction_type') == 'search'])
    contact_forms = len([i for i in interactions if i.get('interaction_type') == 'contact_form'])
    phone_calls = len([i for i in interactions if i.get('interaction_type') == 'phone_call'])
    
    # Calculate session metrics
    session_durations = [i.get('duration', 0) for i in interactions if i.get('duration')]
    avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
    
    # Calculate recency and frequency
    if interactions:
        latest_interaction = max(interactions, key=lambda x: x.get('timestamp', ''))
        latest_time = datetime.fromisoformat(latest_interaction.get('timestamp', '').replace('Z', ''))
        recency_score = max(0, 1 - (datetime.now() - latest_time).days / 30)
        frequency_score = min(1, len(interactions) / 10)
    else:
        recency_score = 0
        frequency_score = 0
    
    # Calculate days since registration
    reg_date = user_data.get('created_at', datetime.now().isoformat())
    reg_time = datetime.fromisoformat(reg_date.replace('Z', ''))
    days_since_registration = (datetime.now() - reg_time).days
    
    return {
        'page_views': page_views,
        'session_duration': avg_session_duration,
        'bounce_rate': 0.5,  # Default value
        'email_opens': email_opens,
        'email_clicks': email_clicks,
        'property_views': property_views,
        'search_queries': search_queries,
        'contact_forms': contact_forms,
        'phone_calls': phone_calls,
        'budget_range': 0.5,  # Default value
        'location_preference': 0.5,  # Default value
        'property_type_preference': 0.5,  # Default value
        'days_since_registration': days_since_registration,
        'recency_score': recency_score,
        'frequency_score': frequency_score
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
