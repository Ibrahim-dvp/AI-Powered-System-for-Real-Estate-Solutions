"""
Property Valuation Service
=========================

This service provides AI-powered property valuation and market analysis.
It uses machine learning models to estimate property values based on
location, features, market conditions, and comparable sales.

Features:
- Automated property valuation
- Market trend analysis
- Comparable property analysis
- Investment metrics calculation
- Confidence scoring
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = os.getenv("BASEROW_API_URL", "https://dayta.intelligentb2b.com/api")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")
BASEROW_PROPERTIES_TABLE_ID = os.getenv("BASEROW_PROPERTIES_TABLE_ID")
BASEROW_MARKET_DATA_TABLE_ID = os.getenv("BASEROW_MARKET_DATA_TABLE_ID")

class PropertyValuationEngine:
    """Main property valuation engine with ML models"""
    
    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'square_meters', 'bedrooms', 'bathrooms', 'floors', 'floor_number',
            'building_year', 'condition_score', 'location_score', 'neighborhood_score',
            'energy_class_score', 'parking_spaces', 'garden', 'balcony', 'terrace',
            'elevator', 'market_trend', 'days_on_market', 'price_per_sqm_area'
        ]
        self.property_cache = {}
        self.market_data_cache = {}
        self.load_models()
    
    def load_models(self):
        """Load pre-trained ML models or train new ones"""
        try:
            self.rf_model = joblib.load('models/rf_valuation.pkl')
            self.gb_model = joblib.load('models/gb_valuation.pkl')
            self.scaler = joblib.load('models/valuation_scaler.pkl')
            logger.info("Valuation models loaded successfully")
        except FileNotFoundError:
            logger.info("No pre-trained models found. Training new models...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with sample data"""
        # Generate sample training data
        np.random.seed(42)
        n_samples = 5000
        
        # Create synthetic property data
        data = {
            'square_meters': np.random.normal(80, 30, n_samples),
            'bedrooms': np.random.poisson(2.5, n_samples),
            'bathrooms': np.random.poisson(1.5, n_samples),
            'floors': np.random.poisson(3, n_samples),
            'floor_number': np.random.randint(0, 10, n_samples),
            'building_year': np.random.randint(1950, 2024, n_samples),
            'condition_score': np.random.uniform(1, 5, n_samples),
            'location_score': np.random.uniform(1, 10, n_samples),
            'neighborhood_score': np.random.uniform(1, 10, n_samples),
            'energy_class_score': np.random.uniform(1, 10, n_samples),
            'parking_spaces': np.random.poisson(1, n_samples),
            'garden': np.random.binomial(1, 0.3, n_samples),
            'balcony': np.random.binomial(1, 0.7, n_samples),
            'terrace': np.random.binomial(1, 0.4, n_samples),
            'elevator': np.random.binomial(1, 0.6, n_samples),
            'market_trend': np.random.normal(1, 0.1, n_samples),
            'days_on_market': np.random.exponential(45, n_samples),
            'price_per_sqm_area': np.random.normal(3000, 1000, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create target variable (property price)
        df['price'] = (
            df['square_meters'] * df['price_per_sqm_area'] *
            (1 + df['location_score'] / 20) *
            (1 + df['condition_score'] / 10) *
            (1 + (df['bedrooms'] - 1) * 0.1) *
            (1 + df['garden'] * 0.05) *
            (1 + df['balcony'] * 0.03) *
            (1 + df['terrace'] * 0.04) *
            (1 + df['elevator'] * 0.02) *
            df['market_trend']
        )
        
        # Add some noise
        df['price'] += np.random.normal(0, df['price'] * 0.1)
        df['price'] = np.maximum(df['price'], 50000)  # Minimum price
        
        # Prepare features
        X = df[self.feature_columns]
        y = df['price']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        self.rf_model.fit(X_scaled, y)
        self.gb_model.fit(X_scaled, y)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.rf_model, 'models/rf_valuation.pkl')
        joblib.dump(self.gb_model, 'models/gb_valuation.pkl')
        joblib.dump(self.scaler, 'models/valuation_scaler.pkl')
        
        logger.info("Valuation models trained and saved successfully")
    
    def get_property_valuation(self, property_data):
        """Get property valuation using ML models"""
        try:
            # Prepare features
            features = self.prepare_features(property_data)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get predictions
            rf_prediction = self.rf_model.predict(features_scaled)[0]
            gb_prediction = self.gb_model.predict(features_scaled)[0]
            
            # Ensemble prediction
            estimated_value = (rf_prediction + gb_prediction) / 2
            
            # Calculate confidence (inverse of prediction difference)
            confidence = max(0.1, 1 - abs(rf_prediction - gb_prediction) / estimated_value)
            
            # Get comparable properties
            comparables = self.get_comparable_properties(property_data)
            
            # Calculate market metrics
            market_metrics = self.calculate_market_metrics(property_data)
            
            return {
                'estimated_value': round(estimated_value, 2),
                'confidence_score': round(confidence, 2),
                'value_range': {
                    'min': round(estimated_value * 0.9, 2),
                    'max': round(estimated_value * 1.1, 2)
                },
                'price_per_sqm': round(estimated_value / property_data.get('square_meters', 1), 2),
                'comparables': comparables,
                'market_metrics': market_metrics,
                'valuation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in property valuation: {str(e)}")
            return None
    
    def prepare_features(self, property_data):
        """Prepare features for ML model"""
        features = []
        
        for col in self.feature_columns:
            if col == 'condition_score':
                # Convert condition to numeric score
                condition = property_data.get('condition', 'fair').lower()
                score_map = {'excellent': 5, 'good': 4, 'fair': 3, 'poor': 2, 'needs_renovation': 1}
                features.append(score_map.get(condition, 3))
            elif col == 'location_score':
                # Calculate location score based on city/region
                features.append(self.calculate_location_score(property_data))
            elif col == 'neighborhood_score':
                # Calculate neighborhood score
                features.append(self.calculate_neighborhood_score(property_data))
            elif col == 'energy_class_score':
                # Convert energy class to score
                energy_class = property_data.get('energy_class', 'E')
                class_map = {'A4': 10, 'A3': 9, 'A2': 8, 'A1': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'F': 2, 'G': 1}
                features.append(class_map.get(energy_class, 3))
            elif col == 'market_trend':
                # Get market trend for area
                features.append(self.get_market_trend(property_data))
            elif col == 'price_per_sqm_area':
                # Get average price per sqm for area
                features.append(self.get_area_price_per_sqm(property_data))
            elif col in ['garden', 'balcony', 'terrace', 'elevator']:
                # Boolean features
                features.append(1 if property_data.get(col, False) else 0)
            else:
                # Numeric features
                features.append(property_data.get(col, 0))
        
        return features
    
    def calculate_location_score(self, property_data):
        """Calculate location score based on city/region"""
        # Major cities scoring
        city_scores = {
            'milano': 10, 'roma': 9, 'firenze': 8, 'venezia': 8,
            'napoli': 7, 'torino': 7, 'bologna': 7, 'genova': 6,
            'bari': 5, 'catania': 5, 'palermo': 5
        }
        
        city = property_data.get('city', '').lower()
        return city_scores.get(city, 5)  # Default score
    
    def calculate_neighborhood_score(self, property_data):
        """Calculate neighborhood score"""
        # This would typically use more sophisticated data
        # For now, return a random score between 3-8
        return np.random.uniform(3, 8)
    
    def get_market_trend(self, property_data):
        """Get market trend for the area"""
        # This would query market data
        # For now, return a slight positive trend
        return 1.02
    
    def get_area_price_per_sqm(self, property_data):
        """Get average price per sqm for the area"""
        # This would query market data
        # For now, return a default based on city
        city_prices = {
            'milano': 4500, 'roma': 3800, 'firenze': 3500, 'venezia': 3200,
            'napoli': 2200, 'torino': 2800, 'bologna': 3000, 'genova': 2600
        }
        
        city = property_data.get('city', '').lower()
        return city_prices.get(city, 2500)  # Default price
    
    def get_comparable_properties(self, property_data):
        """Get comparable properties for valuation"""
        # This would query the database for similar properties
        # For now, return mock data
        return [
            {
                'id': 'comp1',
                'address': 'Via Example 1',
                'price': 250000,
                'square_meters': 75,
                'similarity_score': 0.85
            },
            {
                'id': 'comp2',
                'address': 'Via Example 2',
                'price': 280000,
                'square_meters': 82,
                'similarity_score': 0.78
            },
            {
                'id': 'comp3',
                'address': 'Via Example 3',
                'price': 265000,
                'square_meters': 78,
                'similarity_score': 0.82
            }
        ]
    
    def calculate_market_metrics(self, property_data):
        """Calculate market metrics for the area"""
        return {
            'avg_price_per_sqm': self.get_area_price_per_sqm(property_data),
            'market_velocity': 45,  # days on market
            'price_trend_12m': 0.05,  # 5% increase
            'inventory_level': 'moderate',
            'demand_index': 7.2
        }
    
    def get_investment_analysis(self, property_data, rental_income=None):
        """Calculate investment metrics"""
        valuation = self.get_property_valuation(property_data)
        if not valuation:
            return None
        
        property_value = valuation['estimated_value']
        
        # Calculate rental yield if rental income provided
        if rental_income:
            annual_rental = rental_income * 12
            gross_yield = (annual_rental / property_value) * 100
            net_yield = gross_yield * 0.85  # Assuming 15% expenses
        else:
            # Estimate rental income based on property value
            estimated_monthly_rent = property_value * 0.005  # 0.5% of value
            gross_yield = (estimated_monthly_rent * 12 / property_value) * 100
            net_yield = gross_yield * 0.85
        
        return {
            'property_value': property_value,
            'estimated_monthly_rent': estimated_monthly_rent if not rental_income else rental_income,
            'gross_yield': round(gross_yield, 2),
            'net_yield': round(net_yield, 2),
            'investment_grade': 'A' if net_yield > 6 else 'B' if net_yield > 4 else 'C',
            'roi_projection_5y': round(net_yield * 5 + 20, 2),  # Including capital appreciation
            'cash_flow_monthly': round((rental_income or estimated_monthly_rent) * 0.85, 2)
        }

# Initialize valuation engine
valuation_engine = PropertyValuationEngine()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'property-valuation-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/valuate', methods=['POST'])
def valuate_property():
    """Get property valuation"""
    try:
        data = request.get_json()
        property_data = data.get('property_data')
        
        if not property_data:
            return jsonify({'error': 'property_data is required'}), 400
        
        # Get valuation
        valuation = valuation_engine.get_property_valuation(property_data)
        
        if not valuation:
            return jsonify({'error': 'Failed to calculate valuation'}), 500
        
        return jsonify({
            'success': True,
            'valuation': valuation
        })
        
    except Exception as e:
        logger.error(f"Error in property valuation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/investment-analysis', methods=['POST'])
def investment_analysis():
    """Get investment analysis for a property"""
    try:
        data = request.get_json()
        property_data = data.get('property_data')
        rental_income = data.get('rental_income')
        
        if not property_data:
            return jsonify({'error': 'property_data is required'}), 400
        
        # Get investment analysis
        analysis = valuation_engine.get_investment_analysis(property_data, rental_income)
        
        if not analysis:
            return jsonify({'error': 'Failed to calculate investment analysis'}), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error in investment analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-analysis', methods=['POST'])
def market_analysis():
    """Get market analysis for an area"""
    try:
        data = request.get_json()
        location = data.get('location')
        
        if not location:
            return jsonify({'error': 'location is required'}), 400
        
        # Mock market analysis data
        analysis = {
            'location': location,
            'avg_price_per_sqm': valuation_engine.get_area_price_per_sqm({'city': location}),
            'market_trend': 'positive',
            'price_change_12m': 5.2,
            'inventory_level': 'moderate',
            'days_on_market_avg': 45,
            'demand_index': 7.2,
            'investment_attractiveness': 'high',
            'growth_forecast': {
                '1_year': 3.5,
                '3_year': 12.0,
                '5_year': 22.5
            }
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparables', methods=['POST'])
def get_comparables():
    """Get comparable properties"""
    try:
        data = request.get_json()
        property_data = data.get('property_data')
        
        if not property_data:
            return jsonify({'error': 'property_data is required'}), 400
        
        # Get comparable properties
        comparables = valuation_engine.get_comparable_properties(property_data)
        
        return jsonify({
            'success': True,
            'comparables': comparables
        })
        
    except Exception as e:
        logger.error(f"Error getting comparables: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
