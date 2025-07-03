from flask import Blueprint, request, jsonify
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
import os
from datetime import datetime, timedelta
import math

valuation_bp = Blueprint('valuation', __name__)

class PropertyValuationEngine:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'valuation_models')
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
        
        # Train hedonic pricing model
        X_hedonic = hedonic_features.drop(['price', 'property_id'], axis=1)
        y_hedonic = hedonic_features['price']
        
        # Encode categorical variables
        X_hedonic_encoded = self.encode_features(X_hedonic, fit=True)
        X_hedonic_scaled = self.scalers['numeric'].fit_transform(X_hedonic_encoded)
        
        self.models['hedonic'].fit(X_hedonic_scaled, y_hedonic)
        
        # Train other models with same preprocessing
        self.models['cma'].fit(X_hedonic_scaled, y_hedonic)
        
        # Train investment model (ROI prediction)
        y_investment = hedonic_features['roi']
        self.models['investment'].fit(X_hedonic_scaled, y_investment)
        
        # Train trend prediction model
        y_trend = hedonic_features['future_price']
        self.models['trend'].fit(X_hedonic_scaled, y_trend)
        
        # Save models
        self.save_models()
        print("Valuation models trained and saved")
    
    def generate_training_data(self):
        """Generate comprehensive training data for Italian real estate"""
        np.random.seed(42)
        n_samples = 5000
        
        # Italian cities with their characteristics
        cities = {
            'Rome': {'base_price': 4500, 'growth_rate': 0.03},
            'Milan': {'base_price': 5200, 'growth_rate': 0.04},
            'Florence': {'base_price': 4800, 'growth_rate': 0.035},
            'Naples': {'base_price': 3200, 'growth_rate': 0.025},
            'Turin': {'base_price': 3800, 'growth_rate': 0.03},
            'Bologna': {'base_price': 4200, 'growth_rate': 0.032},
            'Venice': {'base_price': 5500, 'growth_rate': 0.02}
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
            # Prepare features
            features = self.prepare_single_property_features(property_data)
            
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
    
    def prepare_single_property_features(self, property_data):
        """Prepare features for a single property"""
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
    
    def get_comparable_properties(self, property_data, limit=5):
        """Find comparable properties for CMA analysis"""
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
        
        # Adjust based on property type
        if property_data.get('property_type') == 'commercial':
            confidence -= 10
        elif property_data.get('property_type') == 'villa':
            confidence -= 5
        
        return max(50, min(95, confidence))

# Initialize the valuation engine
valuation_engine = PropertyValuationEngine()

@valuation_bp.route('/valuate-property', methods=['POST'])
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
        
        # Calculate ensemble valuation
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
        
        return jsonify({
            'success': True,
            'property_data': property_data,
            'valuations': results,
            'comparable_properties': comparables,
            'confidence_score': confidence_score,
            'valuation_date': datetime.now().isoformat(),
            'methodology': 'Ensemble ML models with hedonic pricing and comparative market analysis'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@valuation_bp.route('/market-analysis', methods=['POST'])
def market_analysis():
    """Perform market analysis for a specific area"""
    try:
        criteria = request.json
        location = criteria.get('location', 'Rome')
        property_type = criteria.get('property_type', 'apartment')
        
        # Mock market analysis
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

@valuation_bp.route('/investment-analysis', methods=['POST'])
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
        property_taxes = property_value * 0.01
        insurance = property_value * 0.003
        maintenance = property_value * 0.01
        management = annual_rent * 0.08
        
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
            }
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

