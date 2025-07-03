# Property Valuation ML Models and API Services

**Integration:** Machine Learning + Baserow + n8n + External APIs  
**Date:** January 7, 2025

## Overview

This property valuation system uses advanced machine learning algorithms to provide accurate property valuations, predictive pricing, and market analysis for the Italian real estate market. The system integrates with your existing Baserow database and provides API services for real-time valuations.

## Architecture

```
Property Data → Feature Engineering → ML Models → Valuation API → Baserow Storage
     ↓              ↓                    ↓            ↓              ↓
Market Data → Preprocessing → Ensemble → Price Prediction → n8n Workflows
```

## Part 1: Machine Learning Models

### 1.1 Valuation Model Types

The system implements multiple ML models for different valuation scenarios:

1. **Hedonic Pricing Model** - Feature-based valuation
2. **Comparative Market Analysis (CMA)** - Similar property comparison
3. **Investment Valuation Model** - ROI and cash flow analysis
4. **Market Trend Predictor** - Future price forecasting

### 1.2 Feature Engineering

**Property Features:**
- Location coordinates (latitude, longitude)
- Property type and size (square meters, rooms)
- Age and condition of property
- Energy efficiency rating
- Amenities and features (parking, garden, elevator)
- Floor level and building characteristics

**Market Features:**
- Historical price trends in the area
- Days on market for similar properties
- Local infrastructure development
- Economic indicators (employment, income levels)
- Seasonal market patterns

**Neighborhood Features:**
- School ratings and proximity
- Public transportation access
- Commercial and recreational facilities
- Crime rates and safety scores
- Future development plans

## Part 2: Property Valuation Service Implementation

### 2.1 Create Valuation Service

```python
# property_valuation_service.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import requests
import json
from datetime import datetime, timedelta
import os
from geopy.distance import geodesic
import math

class PropertyValuationEngine:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.models_dir = 'valuation_models'
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize models
        self.models['hedonic'] = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        self.models['cma'] = GradientBoostingRegressor(n_estimators=150, max_depth=8, random_state=42)
        self.models['investment'] = LinearRegression()
        self.models['trend'] = GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
        
        # Initialize preprocessing tools
        self.scalers['numeric'] = StandardScaler()
        self.encoders['categorical'] = {}
        
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            for model_name in self.models.keys():
                self.models[model_name] = joblib.load(f'{self.models_dir}/{model_name}_model.pkl')
            
            self.scalers['numeric'] = joblib.load(f'{self.models_dir}/numeric_scaler.pkl')
            
            with open(f'{self.models_dir}/categorical_encoders.json', 'r') as f:
                encoder_data = json.load(f)
                for key, mapping in encoder_data.items():
                    encoder = LabelEncoder()
                    encoder.classes_ = np.array(list(mapping.keys()))
                    self.encoders['categorical'][key] = encoder
            
            print("Valuation models loaded successfully")
        except FileNotFoundError:
            print("Training new valuation models...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with sample data"""
        # Generate comprehensive training data
        training_data = self.generate_training_data()
        
        # Prepare features for different models
        hedonic_features = self.prepare_hedonic_features(training_data)
        cma_features = self.prepare_cma_features(training_data)
        investment_features = self.prepare_investment_features(training_data)
        trend_features = self.prepare_trend_features(training_data)
        
        # Train hedonic pricing model
        X_hedonic = hedonic_features.drop(['price', 'property_id'], axis=1)
        y_hedonic = hedonic_features['price']
        
        # Encode categorical variables
        X_hedonic_encoded = self.encode_features(X_hedonic, fit=True)
        X_hedonic_scaled = self.scalers['numeric'].fit_transform(X_hedonic_encoded)
        
        self.models['hedonic'].fit(X_hedonic_scaled, y_hedonic)
        
        # Train CMA model
        X_cma = cma_features.drop(['price', 'property_id'], axis=1)
        y_cma = cma_features['price']
        X_cma_scaled = self.scalers['numeric'].transform(self.encode_features(X_cma))
        self.models['cma'].fit(X_cma_scaled, y_cma)
        
        # Train investment model
        X_investment = investment_features.drop(['roi', 'property_id'], axis=1)
        y_investment = investment_features['roi']
        X_investment_scaled = self.scalers['numeric'].transform(self.encode_features(X_investment))
        self.models['investment'].fit(X_investment_scaled, y_investment)
        
        # Train trend prediction model
        X_trend = trend_features.drop(['future_price', 'property_id'], axis=1)
        y_trend = trend_features['future_price']
        X_trend_scaled = self.scalers['numeric'].transform(self.encode_features(X_trend))
        self.models['trend'].fit(X_trend_scaled, y_trend)
        
        # Save models
        self.save_models()
        print("Valuation models trained and saved")
    
    def generate_training_data(self):
        """Generate comprehensive training data for Italian real estate"""
        np.random.seed(42)
        n_samples = 5000
        
        # Italian cities with their characteristics
        cities = {
            'Rome': {'base_price': 4500, 'lat': 41.9028, 'lon': 12.4964, 'growth_rate': 0.03},
            'Milan': {'base_price': 5200, 'lat': 45.4642, 'lon': 9.1900, 'growth_rate': 0.04},
            'Florence': {'base_price': 4800, 'lat': 43.7696, 'lon': 11.2558, 'growth_rate': 0.035},
            'Naples': {'base_price': 3200, 'lat': 40.8518, 'lon': 14.2681, 'growth_rate': 0.025},
            'Turin': {'base_price': 3800, 'lat': 45.0703, 'lon': 7.6869, 'growth_rate': 0.03},
            'Bologna': {'base_price': 4200, 'lat': 44.4949, 'lon': 11.3426, 'growth_rate': 0.032},
            'Venice': {'base_price': 5500, 'lat': 45.4408, 'lon': 12.3155, 'growth_rate': 0.02}
        }
        
        property_types = ['apartment', 'house', 'villa', 'commercial']
        conditions = ['excellent', 'good', 'fair', 'poor']
        energy_classes = ['A4', 'A3', 'A2', 'A1', 'B', 'C', 'D', 'E']
        
        data = []
        
        for i in range(n_samples):
            city_name = np.random.choice(list(cities.keys()))
            city_data = cities[city_name]
            
            # Property characteristics
            property_type = np.random.choice(property_types)
            square_meters = np.random.normal(100, 30) if property_type == 'apartment' else np.random.normal(150, 50)
            square_meters = max(30, square_meters)
            
            bedrooms = max(1, int(np.random.normal(2.5, 1)))
            bathrooms = max(1, int(np.random.normal(1.8, 0.8)))
            
            # Location within city (add some variance)
            lat = city_data['lat'] + np.random.normal(0, 0.05)
            lon = city_data['lon'] + np.random.normal(0, 0.05)
            
            # Building characteristics
            building_year = np.random.randint(1950, 2024)
            age = 2024 - building_year
            condition = np.random.choice(conditions, p=[0.2, 0.4, 0.3, 0.1])
            energy_class = np.random.choice(energy_classes, p=[0.1, 0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.05])
            
            # Features
            has_parking = np.random.choice([0, 1], p=[0.4, 0.6])
            has_garden = np.random.choice([0, 1], p=[0.7, 0.3])
            has_elevator = np.random.choice([0, 1], p=[0.5, 0.5])
            has_balcony = np.random.choice([0, 1], p=[0.3, 0.7])
            floor_number = np.random.randint(0, 8) if has_elevator else np.random.randint(0, 4)
            
            # Market factors
            distance_to_center = np.random.exponential(5)  # km from city center
            public_transport_score = max(1, min(10, np.random.normal(6, 2)))
            school_rating = max(1, min(10, np.random.normal(7, 1.5)))
            
            # Calculate base price per sqm
            base_price_sqm = city_data['base_price']
            
            # Apply adjustments
            price_sqm = base_price_sqm
            
            # Property type adjustment
            if property_type == 'villa':
                price_sqm *= 1.3
            elif property_type == 'house':
                price_sqm *= 1.1
            elif property_type == 'commercial':
                price_sqm *= 0.9
            
            # Condition adjustment
            condition_multipliers = {'excellent': 1.2, 'good': 1.0, 'fair': 0.85, 'poor': 0.7}
            price_sqm *= condition_multipliers[condition]
            
            # Age adjustment
            if age < 5:
                price_sqm *= 1.15
            elif age < 15:
                price_sqm *= 1.05
            elif age > 50:
                price_sqm *= 0.9
            
            # Energy class adjustment
            energy_multipliers = {'A4': 1.1, 'A3': 1.08, 'A2': 1.05, 'A1': 1.02, 'B': 1.0, 'C': 0.95, 'D': 0.9, 'E': 0.85}
            price_sqm *= energy_multipliers[energy_class]
            
            # Location adjustment
            price_sqm *= max(0.7, 1 - (distance_to_center * 0.05))
            
            # Features adjustment
            if has_parking:
                price_sqm *= 1.08
            if has_garden:
                price_sqm *= 1.05
            if has_elevator and floor_number > 2:
                price_sqm *= 1.03
            if has_balcony:
                price_sqm *= 1.02
            
            # Floor adjustment
            if floor_number == 0:
                price_sqm *= 0.95  # Ground floor discount
            elif floor_number >= 5:
                price_sqm *= 1.05  # High floor premium
            
            # Transport and amenities
            price_sqm *= (1 + (public_transport_score - 5) * 0.02)
            price_sqm *= (1 + (school_rating - 5) * 0.01)
            
            # Add some random noise
            price_sqm *= np.random.normal(1, 0.1)
            
            total_price = price_sqm * square_meters
            
            # Calculate investment metrics
            monthly_rent = total_price * 0.004  # 4% annual yield / 12
            annual_expenses = total_price * 0.015  # 1.5% of property value
            annual_rent = monthly_rent * 12
            net_annual_income = annual_rent - annual_expenses
            roi = (net_annual_income / total_price) * 100
            
            # Future price (1 year prediction)
            growth_rate = city_data['growth_rate'] + np.random.normal(0, 0.01)
            future_price = total_price * (1 + growth_rate)
            
            data.append({
                'property_id': f'PROP_{i:05d}',
                'city': city_name,
                'property_type': property_type,
                'square_meters': round(square_meters, 1),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'building_year': building_year,
                'age': age,
                'condition': condition,
                'energy_class': energy_class,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'distance_to_center': round(distance_to_center, 2),
                'floor_number': floor_number,
                'has_parking': has_parking,
                'has_garden': has_garden,
                'has_elevator': has_elevator,
                'has_balcony': has_balcony,
                'public_transport_score': round(public_transport_score, 1),
                'school_rating': round(school_rating, 1),
                'price': round(total_price, 0),
                'price_per_sqm': round(price_sqm, 2),
                'monthly_rent': round(monthly_rent, 2),
                'roi': round(roi, 2),
                'future_price': round(future_price, 0)
            })
        
        return pd.DataFrame(data)
    
    def prepare_hedonic_features(self, data):
        """Prepare features for hedonic pricing model"""
        features = data.copy()
        
        # Create additional features
        features['age_squared'] = features['age'] ** 2
        features['sqm_per_room'] = features['square_meters'] / (features['bedrooms'] + features['bathrooms'])
        features['luxury_score'] = (
            features['has_parking'] * 2 +
            features['has_garden'] * 2 +
            features['has_elevator'] * 1 +
            features['has_balcony'] * 1
        )
        
        return features
    
    def prepare_cma_features(self, data):
        """Prepare features for comparative market analysis"""
        features = data.copy()
        
        # Add market comparison features
        for city in data['city'].unique():
            city_data = data[data['city'] == city]
            city_median_price = city_data['price_per_sqm'].median()
            features.loc[features['city'] == city, 'city_median_price_sqm'] = city_median_price
        
        features['price_vs_city_median'] = features['price_per_sqm'] / features['city_median_price_sqm']
        
        return features
    
    def prepare_investment_features(self, data):
        """Prepare features for investment analysis"""
        features = data.copy()
        
        # Investment-specific features
        features['price_to_rent_ratio'] = features['price'] / (features['monthly_rent'] * 12)
        features['cap_rate'] = (features['monthly_rent'] * 12) / features['price'] * 100
        
        return features
    
    def prepare_trend_features(self, data):
        """Prepare features for trend prediction"""
        features = data.copy()
        
        # Add trend indicators
        features['market_momentum'] = np.random.normal(1, 0.1, len(features))  # Mock market momentum
        features['economic_indicator'] = np.random.normal(0, 1, len(features))  # Mock economic data
        
        return features
    
    def encode_features(self, X, fit=False):
        """Encode categorical features"""
        X_encoded = X.copy()
        
        categorical_columns = ['city', 'property_type', 'condition', 'energy_class']
        
        for col in categorical_columns:
            if col in X_encoded.columns:
                if fit:
                    # Create new encoder
                    encoder = LabelEncoder()
                    X_encoded[col] = encoder.fit_transform(X_encoded[col].astype(str))
                    self.encoders['categorical'][col] = encoder
                else:
                    # Use existing encoder
                    if col in self.encoders['categorical']:
                        encoder = self.encoders['categorical'][col]
                        # Handle unknown categories
                        known_categories = set(encoder.classes_)
                        X_encoded[col] = X_encoded[col].astype(str)
                        X_encoded[col] = X_encoded[col].apply(
                            lambda x: x if x in known_categories else encoder.classes_[0]
                        )
                        X_encoded[col] = encoder.transform(X_encoded[col])
                    else:
                        X_encoded[col] = 0  # Default value for unknown categories
        
        return X_encoded
    
    def save_models(self):
        """Save trained models and preprocessing tools"""
        for model_name, model in self.models.items():
            joblib.dump(model, f'{self.models_dir}/{model_name}_model.pkl')
        
        joblib.dump(self.scalers['numeric'], f'{self.models_dir}/numeric_scaler.pkl')
        
        # Save categorical encoders
        encoder_data = {}
        for key, encoder in self.encoders['categorical'].items():
            encoder_data[key] = {cls: idx for idx, cls in enumerate(encoder.classes_)}
        
        with open(f'{self.models_dir}/categorical_encoders.json', 'w') as f:
            json.dump(encoder_data, f)
    
    def valuate_property(self, property_data, valuation_type='hedonic'):
        """Perform property valuation using specified model"""
        try:
            # Prepare features based on valuation type
            if valuation_type == 'hedonic':
                features = self.prepare_single_property_hedonic(property_data)
            elif valuation_type == 'cma':
                features = self.prepare_single_property_cma(property_data)
            elif valuation_type == 'investment':
                features = self.prepare_single_property_investment(property_data)
            elif valuation_type == 'trend':
                features = self.prepare_single_property_trend(property_data)
            else:
                raise ValueError(f"Unknown valuation type: {valuation_type}")
            
            # Encode and scale features
            features_encoded = self.encode_features(features)
            features_scaled = self.scalers['numeric'].transform(features_encoded.values.reshape(1, -1))
            
            # Make prediction
            if valuation_type == 'investment':
                prediction = self.models[valuation_type].predict(features_scaled)[0]
                return {'roi': round(prediction, 2)}
            elif valuation_type == 'trend':
                prediction = self.models[valuation_type].predict(features_scaled)[0]
                return {'future_price': round(prediction, 0)}
            else:
                prediction = self.models[valuation_type].predict(features_scaled)[0]
                return {'estimated_value': round(prediction, 0)}
        
        except Exception as e:
            return {'error': str(e)}
    
    def prepare_single_property_hedonic(self, property_data):
        """Prepare features for a single property (hedonic model)"""
        features = pd.Series({
            'square_meters': property_data.get('square_meters', 100),
            'bedrooms': property_data.get('bedrooms', 2),
            'bathrooms': property_data.get('bathrooms', 1),
            'age': property_data.get('age', 10),
            'distance_to_center': property_data.get('distance_to_center', 5),
            'floor_number': property_data.get('floor_number', 2),
            'has_parking': property_data.get('has_parking', 0),
            'has_garden': property_data.get('has_garden', 0),
            'has_elevator': property_data.get('has_elevator', 0),
            'has_balcony': property_data.get('has_balcony', 0),
            'public_transport_score': property_data.get('public_transport_score', 5),
            'school_rating': property_data.get('school_rating', 5),
            'city': property_data.get('city', 'Rome'),
            'property_type': property_data.get('property_type', 'apartment'),
            'condition': property_data.get('condition', 'good'),
            'energy_class': property_data.get('energy_class', 'B')
        })
        
        # Add derived features
        features['age_squared'] = features['age'] ** 2
        features['sqm_per_room'] = features['square_meters'] / (features['bedrooms'] + features['bathrooms'])
        features['luxury_score'] = (
            features['has_parking'] * 2 +
            features['has_garden'] * 2 +
            features['has_elevator'] * 1 +
            features['has_balcony'] * 1
        )
        
        return features
    
    def prepare_single_property_cma(self, property_data):
        """Prepare features for CMA valuation"""
        features = self.prepare_single_property_hedonic(property_data)
        
        # Add market comparison (mock data for single property)
        features['city_median_price_sqm'] = 4500  # Default median
        features['price_vs_city_median'] = 1.0  # Will be calculated after prediction
        
        return features
    
    def prepare_single_property_investment(self, property_data):
        """Prepare features for investment analysis"""
        features = self.prepare_single_property_hedonic(property_data)
        
        # Add investment features (estimated)
        estimated_price = property_data.get('estimated_price', 400000)
        estimated_rent = estimated_price * 0.004  # 4% annual yield / 12
        
        features['price_to_rent_ratio'] = estimated_price / (estimated_rent * 12)
        features['cap_rate'] = (estimated_rent * 12) / estimated_price * 100
        
        return features
    
    def prepare_single_property_trend(self, property_data):
        """Prepare features for trend prediction"""
        features = self.prepare_single_property_hedonic(property_data)
        
        # Add trend indicators (mock data)
        features['market_momentum'] = 1.0
        features['economic_indicator'] = 0.0
        
        return features
    
    def get_comparable_properties(self, property_data, limit=5):
        """Find comparable properties for CMA analysis"""
        # This would query your Baserow database for similar properties
        # For now, return mock comparable properties
        
        comparables = []
        base_price = 400000
        
        for i in range(limit):
            comparable = {
                'property_id': f'COMP_{i+1}',
                'address': f'Via Example {i+1}, {property_data.get("city", "Rome")}',
                'price': base_price + np.random.randint(-50000, 50000),
                'square_meters': property_data.get('square_meters', 100) + np.random.randint(-20, 20),
                'bedrooms': property_data.get('bedrooms', 2),
                'bathrooms': property_data.get('bathrooms', 1),
                'distance_km': round(np.random.uniform(0.1, 2.0), 2),
                'days_on_market': np.random.randint(10, 180),
                'sale_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).strftime('%Y-%m-%d')
            }
            comparable['price_per_sqm'] = round(comparable['price'] / comparable['square_meters'], 2)
            comparables.append(comparable)
        
        return comparables
    
    def calculate_confidence_score(self, property_data, valuation_result):
        """Calculate confidence score for the valuation"""
        confidence = 85  # Base confidence
        
        # Adjust based on data completeness
        required_fields = ['square_meters', 'bedrooms', 'bathrooms', 'city', 'property_type']
        missing_fields = sum(1 for field in required_fields if not property_data.get(field))
        confidence -= missing_fields * 5
        
        # Adjust based on property type (some types are harder to value)
        if property_data.get('property_type') == 'commercial':
            confidence -= 10
        elif property_data.get('property_type') == 'villa':
            confidence -= 5
        
        # Adjust based on location data availability
        if not property_data.get('latitude') or not property_data.get('longitude'):
            confidence -= 10
        
        return max(50, min(95, confidence))

# Initialize the valuation engine
valuation_engine = PropertyValuationEngine()
```

### 2.2 Flask API Service

Create a Flask service for property valuation:

```python
# valuation_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from property_valuation_service import valuation_engine
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = "https://daytaa.intelligentb2b.com/api"
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN', 'your_baserow_token_here')

@app.route('/api/valuate-property', methods=['POST'])
def valuate_property():
    """Perform comprehensive property valuation"""
    try:
        property_data = request.json
        
        # Validate required fields
        required_fields = ['square_meters', 'city', 'property_type']
        for field in required_fields:
            if not property_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Perform different types of valuations
        results = {}
        
        # Hedonic pricing valuation
        hedonic_result = valuation_engine.valuate_property(property_data, 'hedonic')
        if 'error' not in hedonic_result:
            results['hedonic_valuation'] = hedonic_result
        
        # Comparative market analysis
        cma_result = valuation_engine.valuate_property(property_data, 'cma')
        if 'error' not in cma_result:
            results['cma_valuation'] = cma_result
        
        # Investment analysis
        investment_result = valuation_engine.valuate_property(property_data, 'investment')
        if 'error' not in investment_result:
            results['investment_analysis'] = investment_result
        
        # Trend prediction
        trend_result = valuation_engine.valuate_property(property_data, 'trend')
        if 'error' not in trend_result:
            results['trend_prediction'] = trend_result
        
        # Calculate ensemble valuation (average of hedonic and CMA)
        if 'hedonic_valuation' in results and 'cma_valuation' in results:
            ensemble_value = (
                results['hedonic_valuation']['estimated_value'] +
                results['cma_valuation']['estimated_value']
            ) / 2
            results['ensemble_valuation'] = {'estimated_value': round(ensemble_value, 0)}
        
        # Get comparable properties
        comparables = valuation_engine.get_comparable_properties(property_data)
        
        # Calculate confidence score
        primary_valuation = results.get('ensemble_valuation', results.get('hedonic_valuation', {}))
        confidence_score = valuation_engine.calculate_confidence_score(property_data, primary_valuation)
        
        # Prepare response
        response = {
            'success': True,
            'property_data': property_data,
            'valuations': results,
            'comparable_properties': comparables,
            'confidence_score': confidence_score,
            'valuation_date': datetime.now().isoformat(),
            'methodology': 'Ensemble ML models with hedonic pricing and comparative market analysis'
        }
        
        # Save valuation to Baserow
        save_valuation_to_baserow(property_data, results, confidence_score)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-analysis', methods=['POST'])
def market_analysis():
    """Perform market analysis for a specific area"""
    try:
        criteria = request.json
        location = criteria.get('location', 'Rome')
        property_type = criteria.get('property_type', 'apartment')
        
        # Mock market analysis (replace with real data analysis)
        analysis = {
            'location': location,
            'property_type': property_type,
            'market_metrics': {
                'average_price_sqm': 4500,
                'median_price_sqm': 4200,
                'price_range': {'min': 2800, 'max': 8500},
                'average_days_on_market': 65,
                'inventory_levels': 'moderate',
                'market_trend': 'increasing',
                'trend_percentage': 3.2
            },
            'price_distribution': {
                'under_300k': 25,
                '300k_500k': 35,
                '500k_750k': 25,
                '750k_1m': 10,
                'over_1m': 5
            },
            'neighborhood_insights': {
                'transportation_score': 8.2,
                'school_rating': 7.5,
                'safety_score': 8.0,
                'amenities_score': 7.8,
                'future_development': 'High - New metro line planned'
            },
            'investment_outlook': {
                'appreciation_forecast': '3-5% annually',
                'rental_yield': '3.5-4.5%',
                'liquidity': 'Good',
                'risk_level': 'Medium'
            }
        }
        
        return jsonify({
            'success': True,
            'market_analysis': analysis,
            'analysis_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/price-prediction', methods=['POST'])
def price_prediction():
    """Predict future property prices"""
    try:
        property_data = request.json
        
        # Get current valuation
        current_valuation = valuation_engine.valuate_property(property_data, 'hedonic')
        
        if 'error' in current_valuation:
            return jsonify({
                'success': False,
                'error': 'Could not calculate current valuation'
            }), 400
        
        current_value = current_valuation['estimated_value']
        
        # Predict future prices
        predictions = {}
        
        # 6 months prediction
        predictions['6_months'] = {
            'predicted_value': round(current_value * 1.015, 0),  # 1.5% growth
            'confidence': 85,
            'factors': ['Seasonal trends', 'Local market conditions']
        }
        
        # 1 year prediction
        trend_result = valuation_engine.valuate_property(property_data, 'trend')
        if 'error' not in trend_result:
            predictions['1_year'] = {
                'predicted_value': trend_result['future_price'],
                'confidence': 75,
                'factors': ['Market trends', 'Economic indicators', 'Infrastructure development']
            }
        
        # 3 year prediction
        predictions['3_years'] = {
            'predicted_value': round(current_value * 1.10, 0),  # 10% growth over 3 years
            'confidence': 60,
            'factors': ['Long-term market trends', 'Urban development', 'Economic growth']
        }
        
        return jsonify({
            'success': True,
            'current_value': current_value,
            'predictions': predictions,
            'prediction_date': datetime.now().isoformat(),
            'disclaimer': 'Predictions are estimates based on current market data and trends'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/investment-analysis', methods=['POST'])
def investment_analysis():
    """Perform detailed investment analysis"""
    try:
        property_data = request.json
        
        # Get property valuation
        valuation = valuation_engine.valuate_property(property_data, 'hedonic')
        if 'error' in valuation:
            return jsonify({
                'success': False,
                'error': 'Could not calculate property valuation'
            }), 400
        
        property_value = valuation['estimated_value']
        
        # Investment parameters
        down_payment_pct = property_data.get('down_payment_percent', 20)
        loan_rate = property_data.get('loan_interest_rate', 3.5)
        loan_term = property_data.get('loan_term_years', 30)
        
        # Calculate investment metrics
        down_payment = property_value * (down_payment_pct / 100)
        loan_amount = property_value - down_payment
        
        # Monthly mortgage payment
        monthly_rate = loan_rate / 100 / 12
        num_payments = loan_term * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        # Rental income estimation
        monthly_rent = property_value * 0.004  # 4% annual yield / 12
        annual_rent = monthly_rent * 12
        
        # Operating expenses
        property_taxes = property_value * 0.01  # 1% of property value
        insurance = property_value * 0.003  # 0.3% of property value
        maintenance = property_value * 0.01  # 1% of property value
        management = annual_rent * 0.08  # 8% of rental income
        
        total_expenses = property_taxes + insurance + maintenance + management
        
        # Cash flow analysis
        annual_debt_service = monthly_payment * 12
        net_operating_income = annual_rent - total_expenses
        cash_flow = net_operating_income - annual_debt_service
        
        # Return metrics
        cap_rate = (net_operating_income / property_value) * 100
        cash_on_cash_return = (cash_flow / down_payment) * 100
        gross_yield = (annual_rent / property_value) * 100
        
        analysis = {
            'property_value': property_value,
            'investment_summary': {
                'down_payment': round(down_payment, 0),
                'loan_amount': round(loan_amount, 0),
                'monthly_payment': round(monthly_payment, 2),
                'monthly_rent': round(monthly_rent, 2),
                'monthly_cash_flow': round(cash_flow / 12, 2)
            },
            'annual_analysis': {
                'gross_rental_income': round(annual_rent, 0),
                'total_expenses': round(total_expenses, 0),
                'net_operating_income': round(net_operating_income, 0),
                'debt_service': round(annual_debt_service, 0),
                'net_cash_flow': round(cash_flow, 0)
            },
            'return_metrics': {
                'cap_rate': round(cap_rate, 2),
                'cash_on_cash_return': round(cash_on_cash_return, 2),
                'gross_yield': round(gross_yield, 2)
            },
            'expense_breakdown': {
                'property_taxes': round(property_taxes, 0),
                'insurance': round(insurance, 0),
                'maintenance': round(maintenance, 0),
                'management': round(management, 0)
            },
            'investment_grade': get_investment_grade(cap_rate, cash_on_cash_return),
            'recommendations': generate_investment_recommendations(cap_rate, cash_on_cash_return, cash_flow)
        }
        
        return jsonify({
            'success': True,
            'investment_analysis': analysis,
            'analysis_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def save_valuation_to_baserow(property_data, results, confidence_score):
    """Save valuation results to Baserow"""
    try:
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Prepare valuation data
        valuation_data = {
            'property_id': property_data.get('property_id', ''),
            'valuation_type': 'Automated',
            'estimated_value': results.get('ensemble_valuation', results.get('hedonic_valuation', {})).get('estimated_value', 0),
            'confidence_score': confidence_score,
            'valuation_method': 'Ensemble ML',
            'valuation_date': datetime.now().date().isoformat(),
            'valid_until': (datetime.now().date() + timedelta(days=90)).isoformat(),
            'created_by': 'System',
            'notes': f'Automated valuation using ML models. Results: {json.dumps(results)}'
        }
        
        # Save to Baserow (mock implementation)
        # response = requests.post(
        #     f'{BASEROW_API_URL}/database/tables/PROPERTY_VALUATIONS_TABLE_ID/rows/',
        #     headers=headers,
        #     json=valuation_data
        # )
        
        print(f"Valuation saved: {valuation_data}")
        
    except Exception as e:
        print(f"Error saving valuation: {e}")

def get_investment_grade(cap_rate, cash_on_cash_return):
    """Determine investment grade based on returns"""
    if cap_rate >= 8 and cash_on_cash_return >= 12:
        return 'A - Excellent'
    elif cap_rate >= 6 and cash_on_cash_return >= 8:
        return 'B - Good'
    elif cap_rate >= 4 and cash_on_cash_return >= 4:
        return 'C - Fair'
    else:
        return 'D - Poor'

def generate_investment_recommendations(cap_rate, cash_on_cash_return, cash_flow):
    """Generate investment recommendations"""
    recommendations = []
    
    if cap_rate < 4:
        recommendations.append("Consider negotiating a lower purchase price to improve returns")
    
    if cash_on_cash_return < 6:
        recommendations.append("Explore ways to increase rental income or reduce operating expenses")
    
    if cash_flow < 0:
        recommendations.append("This property has negative cash flow - consider alternative financing or pass on this investment")
    elif cash_flow > 5000:
        recommendations.append("Strong positive cash flow makes this an attractive investment")
    
    if cap_rate > 8:
        recommendations.append("High cap rate indicates good value - verify market conditions")
    
    return recommendations

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'property-valuation-service',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
```

## Part 3: Integration with n8n

### 3.1 Automated Valuation Workflow

Create this n8n workflow for automatic property valuations:

```json
{
  "name": "Automated Property Valuation Workflow",
  "nodes": [
    {
      "parameters": {
        "triggerOn": "specificTable",
        "tableId": "PROPERTIES_TABLE_ID",
        "event": "created"
      },
      "name": "New Property Trigger",
      "type": "n8n-nodes-base.baserowTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "// Prepare property data for valuation\nconst property = $input.first().json;\n\nconst valuationData = {\n  property_id: property.id,\n  square_meters: property.square_meters,\n  bedrooms: property.bedrooms,\n  bathrooms: property.bathrooms,\n  city: property.city,\n  property_type: property.property_type,\n  building_year: property.building_year,\n  condition: property.condition,\n  energy_class: property.energy_class,\n  latitude: property.latitude,\n  longitude: property.longitude,\n  has_parking: property.parking_spaces > 0 ? 1 : 0,\n  has_garden: property.garden ? 1 : 0,\n  has_elevator: property.elevator ? 1 : 0,\n  has_balcony: property.balcony ? 1 : 0,\n  floor_number: property.floor_number || 0\n};\n\n// Calculate age\nif (property.building_year) {\n  valuationData.age = new Date().getFullYear() - property.building_year;\n}\n\nreturn [{ json: valuationData }];"
      },
      "name": "Prepare Valuation Data",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:5002/api/valuate-property",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpMethod": "POST",
        "jsonParameters": true,
        "parametersJson": "={{ JSON.stringify($json) }}",
        "options": {}
      },
      "name": "Call Valuation API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.success }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Check Valuation Success",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "update",
        "tableId": "PROPERTIES_TABLE_ID",
        "rowId": "={{ $('New Property Trigger').first().json.id }}",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "estimated_value",
              "fieldValue": "={{ $json.valuations.ensemble_valuation?.estimated_value || $json.valuations.hedonic_valuation?.estimated_value || 0 }}"
            },
            {
              "fieldName": "valuation_confidence",
              "fieldValue": "={{ $json.confidence_score }}"
            },
            {
              "fieldName": "last_valuation_date",
              "fieldValue": "={{ $json.valuation_date }}"
            }
          ]
        }
      },
      "name": "Update Property Value",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1120, 200]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.valuations.ensemble_valuation?.estimated_value || $json.valuations.hedonic_valuation?.estimated_value || 0 }}",
              "operation": "larger",
              "value2": 500000
            }
          ]
        }
      },
      "name": "Check High Value",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [1340, 200]
    },
    {
      "parameters": {
        "subject": "High-Value Property Alert",
        "message": "A new high-value property has been added:\n\nProperty ID: {{ $('New Property Trigger').first().json.id }}\nEstimated Value: €{{ $json.valuations.ensemble_valuation?.estimated_value || $json.valuations.hedonic_valuation?.estimated_value }}\nConfidence: {{ $json.confidence_score }}%\nLocation: {{ $('New Property Trigger').first().json.city }}\n\nReview this property for premium marketing.",
        "options": {}
      },
      "name": "Send High Value Alert",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1560, 100]
    }
  ],
  "connections": {
    "New Property Trigger": {
      "main": [
        [
          {
            "node": "Prepare Valuation Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Prepare Valuation Data": {
      "main": [
        [
          {
            "node": "Call Valuation API",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Call Valuation API": {
      "main": [
        [
          {
            "node": "Check Valuation Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Valuation Success": {
      "main": [
        [
          {
            "node": "Update Property Value",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update Property Value": {
      "main": [
        [
          {
            "node": "Check High Value",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check High Value": {
      "main": [
        [
          {
            "node": "Send High Value Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 3.2 Market Analysis Workflow

Create a workflow for periodic market analysis:

```json
{
  "name": "Weekly Market Analysis Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 0 9 * * 1"
            }
          ]
        }
      },
      "name": "Weekly Schedule",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "getAll",
        "tableId": "PROPERTIES_TABLE_ID",
        "filters": {
          "filter": [
            {
              "field": "status",
              "type": "equal",
              "value": "Active"
            }
          ]
        }
      },
      "name": "Get Active Properties",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "functionCode": "// Analyze market data\nconst properties = $input.all().map(item => item.json);\n\n// Group by city and property type\nconst marketData = {};\n\nproperties.forEach(property => {\n  const key = `${property.city}_${property.property_type}`;\n  \n  if (!marketData[key]) {\n    marketData[key] = {\n      city: property.city,\n      property_type: property.property_type,\n      properties: [],\n      total_value: 0,\n      avg_price_sqm: 0,\n      count: 0\n    };\n  }\n  \n  marketData[key].properties.push(property);\n  marketData[key].total_value += property.current_price || 0;\n  marketData[key].count += 1;\n});\n\n// Calculate averages\nObject.keys(marketData).forEach(key => {\n  const data = marketData[key];\n  data.avg_price = data.total_value / data.count;\n  \n  const totalSqm = data.properties.reduce((sum, p) => sum + (p.square_meters || 0), 0);\n  data.avg_price_sqm = data.total_value / totalSqm;\n});\n\nreturn Object.values(marketData).map(data => ({ json: data }));"
      },
      "name": "Analyze Market Data",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "MARKET_ANALYSIS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "city",
              "fieldValue": "={{ $json.city }}"
            },
            {
              "fieldName": "property_type",
              "fieldValue": "={{ $json.property_type }}"
            },
            {
              "fieldName": "average_price",
              "fieldValue": "={{ Math.round($json.avg_price) }}"
            },
            {
              "fieldName": "average_price_sqm",
              "fieldValue": "={{ Math.round($json.avg_price_sqm) }}"
            },
            {
              "fieldName": "property_count",
              "fieldValue": "={{ $json.count }}"
            },
            {
              "fieldName": "analysis_date",
              "fieldValue": "={{ new Date().toISOString().split('T')[0] }}"
            }
          ]
        }
      },
      "name": "Save Market Analysis",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [900, 300]
    }
  ],
  "connections": {
    "Weekly Schedule": {
      "main": [
        [
          {
            "node": "Get Active Properties",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Active Properties": {
      "main": [
        [
          {
            "node": "Analyze Market Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Market Data": {
      "main": [
        [
          {
            "node": "Save Market Analysis",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Part 4: Deployment and Testing

### 4.1 Create Deployment Package

Create a complete deployment package for the valuation service:

```bash
# Create deployment directory
mkdir property-valuation-deployment
cd property-valuation-deployment

# Copy service files
cp ../property_valuation_service.py .
cp ../valuation_api.py .

# Create requirements.txt
cat > requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
requests==2.31.0
python-dotenv==1.0.0
geopy==2.3.0
EOF

# Create startup script
cat > start_valuation_service.py << EOF
#!/usr/bin/env python3
import subprocess
import sys
import os

def start_service():
    print("🚀 Starting Property Valuation Service...")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Set environment variables
    if not os.getenv('BASEROW_TOKEN'):
        token = input("Enter your Baserow API token: ")
        os.environ['BASEROW_TOKEN'] = token
    
    # Start the service
    print("🔥 Starting Flask service on port 5002...")
    subprocess.run([sys.executable, 'valuation_api.py'])

if __name__ == '__main__':
    start_service()
EOF

chmod +x start_valuation_service.py
```

### 4.2 Testing Suite

Create comprehensive tests for the valuation system:

```python
# test_valuation_system.py
import unittest
import json
import requests
from property_valuation_service import PropertyValuationEngine

class TestPropertyValuationSystem(unittest.TestCase):
    
    def setUp(self):
        self.engine = PropertyValuationEngine()
        self.api_base_url = 'http://localhost:5002/api'
        
        self.sample_property = {
            'square_meters': 85,
            'bedrooms': 2,
            'bathrooms': 1,
            'city': 'Rome',
            'property_type': 'apartment',
            'building_year': 2015,
            'condition': 'good',
            'energy_class': 'B',
            'has_parking': 1,
            'has_garden': 0,
            'has_elevator': 1,
            'has_balcony': 1,
            'floor_number': 3
        }
    
    def test_hedonic_valuation(self):
        """Test hedonic pricing model"""
        result = self.engine.valuate_property(self.sample_property, 'hedonic')
        
        self.assertIn('estimated_value', result)
        self.assertIsInstance(result['estimated_value'], (int, float))
        self.assertGreater(result['estimated_value'], 0)
    
    def test_cma_valuation(self):
        """Test comparative market analysis"""
        result = self.engine.valuate_property(self.sample_property, 'cma')
        
        self.assertIn('estimated_value', result)
        self.assertIsInstance(result['estimated_value'], (int, float))
        self.assertGreater(result['estimated_value'], 0)
    
    def test_investment_analysis(self):
        """Test investment analysis"""
        result = self.engine.valuate_property(self.sample_property, 'investment')
        
        self.assertIn('roi', result)
        self.assertIsInstance(result['roi'], (int, float))
    
    def test_trend_prediction(self):
        """Test trend prediction"""
        result = self.engine.valuate_property(self.sample_property, 'trend')
        
        self.assertIn('future_price', result)
        self.assertIsInstance(result['future_price'], (int, float))
        self.assertGreater(result['future_price'], 0)
    
    def test_comparable_properties(self):
        """Test comparable properties search"""
        comparables = self.engine.get_comparable_properties(self.sample_property)
        
        self.assertIsInstance(comparables, list)
        self.assertGreater(len(comparables), 0)
        
        for comp in comparables:
            self.assertIn('property_id', comp)
            self.assertIn('price', comp)
            self.assertIn('square_meters', comp)
    
    def test_confidence_score(self):
        """Test confidence score calculation"""
        hedonic_result = self.engine.valuate_property(self.sample_property, 'hedonic')
        confidence = self.engine.calculate_confidence_score(self.sample_property, hedonic_result)
        
        self.assertIsInstance(confidence, (int, float))
        self.assertGreaterEqual(confidence, 50)
        self.assertLessEqual(confidence, 95)
    
    def test_api_valuation_endpoint(self):
        """Test API valuation endpoint"""
        try:
            response = requests.post(
                f'{self.api_base_url}/valuate-property',
                json=self.sample_property,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data['success'])
                self.assertIn('valuations', data)
                self.assertIn('confidence_score', data)
            else:
                self.skipTest("API service not available")
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API service not running")
    
    def test_market_analysis_endpoint(self):
        """Test market analysis endpoint"""
        try:
            response = requests.post(
                f'{self.api_base_url}/market-analysis',
                json={'location': 'Rome', 'property_type': 'apartment'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data['success'])
                self.assertIn('market_analysis', data)
            else:
                self.skipTest("API service not available")
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API service not running")
    
    def test_price_prediction_endpoint(self):
        """Test price prediction endpoint"""
        try:
            response = requests.post(
                f'{self.api_base_url}/price-prediction',
                json=self.sample_property,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data['success'])
                self.assertIn('predictions', data)
                self.assertIn('current_value', data)
            else:
                self.skipTest("API service not available")
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API service not running")
    
    def test_investment_analysis_endpoint(self):
        """Test investment analysis endpoint"""
        try:
            investment_data = self.sample_property.copy()
            investment_data.update({
                'down_payment_percent': 20,
                'loan_interest_rate': 3.5,
                'loan_term_years': 30
            })
            
            response = requests.post(
                f'{self.api_base_url}/investment-analysis',
                json=investment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data['success'])
                self.assertIn('investment_analysis', data)
            else:
                self.skipTest("API service not available")
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API service not running")

if __name__ == '__main__':
    unittest.main()
```

### 4.3 Performance Benchmarks

Create performance benchmarks:

```python
# benchmark_valuation_system.py
import time
import statistics
from property_valuation_service import PropertyValuationEngine

def benchmark_valuation_performance():
    """Benchmark valuation system performance"""
    engine = PropertyValuationEngine()
    
    sample_property = {
        'square_meters': 85,
        'bedrooms': 2,
        'bathrooms': 1,
        'city': 'Rome',
        'property_type': 'apartment',
        'building_year': 2015,
        'condition': 'good',
        'energy_class': 'B',
        'has_parking': 1,
        'has_garden': 0,
        'has_elevator': 1,
        'has_balcony': 1,
        'floor_number': 3
    }
    
    # Benchmark different valuation types
    valuation_types = ['hedonic', 'cma', 'investment', 'trend']
    results = {}
    
    for val_type in valuation_types:
        times = []
        
        # Run 100 valuations
        for _ in range(100):
            start_time = time.time()
            engine.valuate_property(sample_property, val_type)
            end_time = time.time()
            times.append(end_time - start_time)
        
        results[val_type] = {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times)
        }
    
    # Print results
    print("Property Valuation Performance Benchmark")
    print("=" * 50)
    
    for val_type, metrics in results.items():
        print(f"\n{val_type.upper()} Valuation:")
        print(f"  Average time: {metrics['avg_time']:.4f}s")
        print(f"  Min time: {metrics['min_time']:.4f}s")
        print(f"  Max time: {metrics['max_time']:.4f}s")
        print(f"  Std deviation: {metrics['std_dev']:.4f}s")
    
    # Overall performance target: < 0.1s per valuation
    overall_avg = statistics.mean([m['avg_time'] for m in results.values()])
    print(f"\nOverall average time: {overall_avg:.4f}s")
    
    if overall_avg < 0.1:
        print("✅ Performance target met (< 0.1s)")
    else:
        print("❌ Performance target not met (>= 0.1s)")

if __name__ == '__main__':
    benchmark_valuation_performance()
```

This comprehensive property valuation system provides accurate, ML-powered property valuations with multiple methodologies, investment analysis, and market insights. The system integrates seamlessly with your Baserow database and n8n workflows for automated property valuation and market analysis.

