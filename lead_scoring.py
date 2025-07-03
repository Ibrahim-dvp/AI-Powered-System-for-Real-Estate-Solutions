from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import requests
import json
from datetime import datetime, timedelta
import os

lead_scoring_bp = Blueprint('lead_scoring', __name__)

# Configuration
BASEROW_API_URL = "https://dayta.intelligentb2b.com/api"
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN', 'your_baserow_token_here')

class LeadScoringModel:
    def __init__(self):
        self.behavioral_model = None
        self.demographic_model = None
        self.scaler = StandardScaler()
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'ml_models')
        os.makedirs(self.models_dir, exist_ok=True)
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            self.behavioral_model = joblib.load(os.path.join(self.models_dir, 'behavioral_model.pkl'))
            self.demographic_model = joblib.load(os.path.join(self.models_dir, 'demographic_model.pkl'))
            self.scaler = joblib.load(os.path.join(self.models_dir, 'scaler.pkl'))
            print("Models loaded successfully")
        except FileNotFoundError:
            print("Training new models...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with sample data"""
        # Behavioral model (Random Forest)
        self.behavioral_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Demographic model (Gradient Boosting)
        self.demographic_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        
        # Create sample training data
        sample_data = self.generate_sample_data()
        
        # Train behavioral model
        behavioral_features = ['page_views', 'property_views', 'time_spent', 
                             'search_frequency', 'contact_forms', 'email_opens']
        X_behavioral = sample_data[behavioral_features]
        y_behavioral = sample_data['converted']
        
        self.behavioral_model.fit(X_behavioral, y_behavioral)
        
        # Train demographic model
        demographic_features = ['age', 'income_bracket', 'family_size', 
                              'employment_status_encoded', 'location_score']
        X_demographic = sample_data[demographic_features]
        y_demographic = sample_data['conversion_value']
        
        X_demographic_scaled = self.scaler.fit_transform(X_demographic)
        self.demographic_model.fit(X_demographic_scaled, y_demographic)
        
        # Save models
        joblib.dump(self.behavioral_model, os.path.join(self.models_dir, 'behavioral_model.pkl'))
        joblib.dump(self.demographic_model, os.path.join(self.models_dir, 'demographic_model.pkl'))
        joblib.dump(self.scaler, os.path.join(self.models_dir, 'scaler.pkl'))
        
        print("Models trained and saved")
    
    def generate_sample_data(self):
        """Generate sample training data"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'page_views': np.random.poisson(10, n_samples),
            'property_views': np.random.poisson(5, n_samples),
            'time_spent': np.random.exponential(300, n_samples),
            'search_frequency': np.random.poisson(3, n_samples),
            'contact_forms': np.random.poisson(1, n_samples),
            'email_opens': np.random.poisson(2, n_samples),
            'age': np.random.normal(40, 12, n_samples),
            'income_bracket': np.random.choice([1, 2, 3, 4, 5], n_samples),
            'family_size': np.random.choice([1, 2, 3, 4, 5], n_samples),
            'employment_status_encoded': np.random.choice([1, 2, 3, 4], n_samples),
            'location_score': np.random.uniform(0, 1, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create target variables
        df['conversion_probability'] = (
            0.3 * (df['contact_forms'] > 0) +
            0.2 * (df['property_views'] > 3) +
            0.2 * (df['time_spent'] > 600) +
            0.15 * (df['income_bracket'] >= 3) +
            0.15 * (df['email_opens'] > 1)
        )
        
        df['converted'] = (df['conversion_probability'] > 0.5).astype(int)
        df['conversion_value'] = df['income_bracket'] * 100000 * df['converted']
        
        return df
    
    def calculate_behavioral_score(self, user_data):
        """Calculate behavioral score using ML model"""
        features = [
            user_data.get('page_views', 0),
            user_data.get('property_views', 0),
            user_data.get('time_spent', 0),
            user_data.get('search_frequency', 0),
            user_data.get('contact_forms', 0),
            user_data.get('email_opens', 0)
        ]
        
        # Get probability of conversion
        probability = self.behavioral_model.predict_proba([features])[0][1]
        return min(int(probability * 100), 100)
    
    def calculate_demographic_score(self, user_data):
        """Calculate demographic score using ML model"""
        features = [
            user_data.get('age', 35),
            user_data.get('income_bracket', 3),
            user_data.get('family_size', 2),
            user_data.get('employment_status_encoded', 1),
            user_data.get('location_score', 0.5)
        ]
        
        features_scaled = self.scaler.transform([features])
        score = self.demographic_model.predict(features_scaled)[0]
        
        # Normalize to 0-100 scale
        return min(max(int(score / 1000), 0), 100)

# Initialize model
scoring_model = LeadScoringModel()

@lead_scoring_bp.route('/calculate-lead-score', methods=['POST'])
def calculate_lead_score():
    """Calculate comprehensive lead score"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get user data from Baserow (mock data for now)
        user_data = get_user_data(user_id)
        if not user_data:
            # Use default data if user not found
            user_data = {
                'age': 35,
                'income_bracket': 3,
                'family_size': 2,
                'employment_status_encoded': 1,
                'location_score': 0.5
            }
        
        # Get user interactions (mock data for now)
        interactions = get_user_interactions(user_id)
        
        # Process interaction data
        behavioral_data = process_interactions(interactions)
        
        # Calculate scores
        behavioral_score = scoring_model.calculate_behavioral_score(behavioral_data)
        demographic_score = scoring_model.calculate_demographic_score(user_data)
        
        # Calculate intent score based on recent activity
        intent_score = calculate_intent_score(interactions)
        
        # Weighted total score
        total_score = int(
            0.4 * behavioral_score +
            0.3 * demographic_score +
            0.3 * intent_score
        )
        
        # Determine lead grade
        if total_score >= 80:
            lead_grade = 'A'
        elif total_score >= 60:
            lead_grade = 'B'
        elif total_score >= 40:
            lead_grade = 'C'
        else:
            lead_grade = 'D'
        
        return jsonify({
            'user_id': user_id,
            'total_score': total_score,
            'behavioral_score': behavioral_score,
            'demographic_score': demographic_score,
            'intent_score': intent_score,
            'lead_grade': lead_grade,
            'calculated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_scoring_bp.route('/batch-score-leads', methods=['POST'])
def batch_score_leads():
    """Calculate scores for multiple leads"""
    try:
        data = request.json
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify({'error': 'User IDs required'}), 400
        
        results = []
        for user_id in user_ids:
            # Calculate score for each user
            score_data = calculate_single_lead_score(user_id)
            results.append(score_data)
        
        return jsonify({
            'results': results,
            'processed_count': len(results),
            'processed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_scoring_bp.route('/lead-insights/<user_id>', methods=['GET'])
def get_lead_insights(user_id):
    """Get detailed insights for a specific lead"""
    try:
        # Get user interactions
        interactions = get_user_interactions(user_id)
        behavioral_data = process_interactions(interactions)
        
        # Calculate various metrics
        insights = {
            'user_id': user_id,
            'total_interactions': len(interactions),
            'property_views': behavioral_data.get('property_views', 0),
            'search_frequency': behavioral_data.get('search_frequency', 0),
            'engagement_level': calculate_engagement_level(behavioral_data),
            'last_activity': get_last_activity_date(interactions),
            'preferred_property_types': get_preferred_property_types(interactions),
            'price_range_interest': get_price_range_interest(interactions),
            'location_preferences': get_location_preferences(interactions),
            'conversion_probability': calculate_conversion_probability(behavioral_data)
        }
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_single_lead_score(user_id):
    """Calculate score for a single lead"""
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            user_data = {
                'age': 35,
                'income_bracket': 3,
                'family_size': 2,
                'employment_status_encoded': 1,
                'location_score': 0.5
            }
        
        interactions = get_user_interactions(user_id)
        behavioral_data = process_interactions(interactions)
        
        behavioral_score = scoring_model.calculate_behavioral_score(behavioral_data)
        demographic_score = scoring_model.calculate_demographic_score(user_data)
        intent_score = calculate_intent_score(interactions)
        
        total_score = int(
            0.4 * behavioral_score +
            0.3 * demographic_score +
            0.3 * intent_score
        )
        
        if total_score >= 80:
            lead_grade = 'A'
        elif total_score >= 60:
            lead_grade = 'B'
        elif total_score >= 40:
            lead_grade = 'C'
        else:
            lead_grade = 'D'
        
        return {
            'user_id': user_id,
            'total_score': total_score,
            'behavioral_score': behavioral_score,
            'demographic_score': demographic_score,
            'intent_score': intent_score,
            'lead_grade': lead_grade
        }
        
    except Exception as e:
        return {
            'user_id': user_id,
            'error': str(e),
            'total_score': 0,
            'lead_grade': 'D'
        }

def get_user_data(user_id):
    """Fetch user data from Baserow"""
    # Mock implementation - replace with actual Baserow API call
    return {
        'age': 35,
        'income_bracket': 3,
        'family_size': 2,
        'employment_status_encoded': 1,
        'location_score': 0.5
    }

def get_user_interactions(user_id):
    """Fetch user interactions from Baserow"""
    # Mock implementation - replace with actual Baserow API call
    return [
        {
            'interaction_type': 'property_view',
            'created_at': datetime.now().isoformat(),
            'time_spent': 300
        },
        {
            'interaction_type': 'property_search',
            'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'search_query': 'apartment rome'
        }
    ]

def process_interactions(interactions):
    """Process interactions into behavioral features"""
    page_views = len([i for i in interactions if i.get('interaction_type') == 'page_view'])
    property_views = len([i for i in interactions if i.get('interaction_type') == 'property_view'])
    contact_forms = len([i for i in interactions if i.get('interaction_type') == 'contact_form'])
    
    # Calculate total time spent
    time_spent = sum([
        i.get('time_spent', 0) for i in interactions 
        if i.get('time_spent')
    ])
    
    # Calculate search frequency
    search_frequency = len([i for i in interactions if i.get('interaction_type') == 'property_search'])
    
    return {
        'page_views': page_views,
        'property_views': property_views,
        'time_spent': time_spent,
        'search_frequency': search_frequency,
        'contact_forms': contact_forms,
        'email_opens': 0  # Would be fetched from email campaign data
    }

def calculate_intent_score(interactions):
    """Calculate intent score based on recent activity patterns"""
    if not interactions:
        return 0
    
    # Recent activity (last 7 days gets higher weight)
    recent_cutoff = datetime.now() - timedelta(days=7)
    recent_interactions = [
        i for i in interactions 
        if datetime.fromisoformat(i.get('created_at', '').replace('Z', '+00:00')) > recent_cutoff
    ]
    
    score = 0
    
    # High-intent actions
    for interaction in recent_interactions:
        interaction_type = interaction.get('interaction_type')
        
        if interaction_type == 'contact_form':
            score += 30
        elif interaction_type == 'property_view':
            score += 10
        elif interaction_type == 'property_search':
            score += 8
        elif interaction_type == 'time_on_property' and interaction.get('time_spent', 0) > 300:
            score += 15
    
    # Frequency bonus
    if len(recent_interactions) > 10:
        score += 20
    
    return min(score, 100)

def calculate_engagement_level(behavioral_data):
    """Calculate engagement level"""
    total_engagement = (
        behavioral_data.get('property_views', 0) * 2 +
        behavioral_data.get('search_frequency', 0) * 1.5 +
        behavioral_data.get('contact_forms', 0) * 5 +
        min(behavioral_data.get('time_spent', 0) / 300, 10)
    )
    
    if total_engagement >= 20:
        return 'High'
    elif total_engagement >= 10:
        return 'Medium'
    else:
        return 'Low'

def get_last_activity_date(interactions):
    """Get the date of last activity"""
    if not interactions:
        return None
    
    latest_date = max([
        datetime.fromisoformat(i.get('created_at', '').replace('Z', '+00:00'))
        for i in interactions
    ])
    
    return latest_date.isoformat()

def get_preferred_property_types(interactions):
    """Extract preferred property types from interactions"""
    # Mock implementation
    return ['Apartment', 'House']

def get_price_range_interest(interactions):
    """Extract price range interest from search patterns"""
    # Mock implementation
    return {'min': 200000, 'max': 500000}

def get_location_preferences(interactions):
    """Extract location preferences from search patterns"""
    # Mock implementation
    return ['Rome', 'Milan']

def calculate_conversion_probability(behavioral_data):
    """Calculate probability of conversion"""
    score = scoring_model.calculate_behavioral_score(behavioral_data)
    return min(score / 100, 1.0)

