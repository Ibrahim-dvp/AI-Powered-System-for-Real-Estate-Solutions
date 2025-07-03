# Lead Scoring System Implementation with n8n

**Integration:** n8n + Baserow + Python ML Models  
**Date:** January 7, 2025

## Overview

This lead scoring system automatically prioritizes leads based on behavioral data, demographics, and engagement patterns using n8n workflows and machine learning models.

## Architecture

```
User Action → JavaScript Tracking → n8n Webhook → Baserow Update → ML Scoring → Lead Priority Update
```

## Part 1: JavaScript Tracking Implementation

### 1.1 Website Tracking Script

Create this JavaScript tracking script for your website:

```javascript
// Real Estate Lead Tracking Script
class RealEstateTracker {
    constructor(config) {
        this.apiEndpoint = config.n8nWebhookUrl;
        this.sessionId = this.generateSessionId();
        this.userId = config.userId || null;
        this.startTime = Date.now();
        this.interactions = [];
        
        this.init();
    }
    
    init() {
        this.trackPageView();
        this.trackPropertyViews();
        this.trackSearchBehavior();
        this.trackFormSubmissions();
        this.trackScrollDepth();
        this.trackTimeOnPage();
        
        // Send data every 30 seconds
        setInterval(() => this.sendBatch(), 30000);
        
        // Send data before page unload
        window.addEventListener('beforeunload', () => this.sendBatch());
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    trackPageView() {
        this.addInteraction({
            type: 'page_view',
            url: window.location.href,
            referrer: document.referrer,
            timestamp: Date.now()
        });
    }
    
    trackPropertyViews() {
        // Track property detail page views
        const propertyId = this.extractPropertyId();
        if (propertyId) {
            this.addInteraction({
                type: 'property_view',
                property_id: propertyId,
                url: window.location.href,
                timestamp: Date.now()
            });
            
            // Track image interactions
            this.trackImageZoom(propertyId);
            this.trackImageGallery(propertyId);
        }
    }
    
    trackImageZoom(propertyId) {
        document.querySelectorAll('.property-image').forEach(img => {
            img.addEventListener('click', (e) => {
                this.addInteraction({
                    type: 'image_zoom',
                    property_id: propertyId,
                    image_url: e.target.src,
                    timestamp: Date.now()
                });
            });
        });
    }
    
    trackSearchBehavior() {
        // Track search form submissions
        document.querySelectorAll('form[data-search="property"]').forEach(form => {
            form.addEventListener('submit', (e) => {
                const formData = new FormData(form);
                const searchData = Object.fromEntries(formData);
                
                this.addInteraction({
                    type: 'property_search',
                    search_query: searchData.query || '',
                    filters: {
                        location: searchData.location,
                        property_type: searchData.property_type,
                        min_price: searchData.min_price,
                        max_price: searchData.max_price,
                        bedrooms: searchData.bedrooms
                    },
                    timestamp: Date.now()
                });
            });
        });
        
        // Track filter changes
        document.querySelectorAll('.search-filter').forEach(filter => {
            filter.addEventListener('change', (e) => {
                this.addInteraction({
                    type: 'filter_change',
                    filter_name: e.target.name,
                    filter_value: e.target.value,
                    timestamp: Date.now()
                });
            });
        });
    }
    
    trackFormSubmissions() {
        // Track contact forms
        document.querySelectorAll('form[data-type="contact"]').forEach(form => {
            form.addEventListener('submit', (e) => {
                const formData = new FormData(form);
                
                this.addInteraction({
                    type: 'contact_form',
                    form_data: {
                        name: formData.get('name'),
                        email: formData.get('email'),
                        phone: formData.get('phone'),
                        message: formData.get('message'),
                        property_id: formData.get('property_id')
                    },
                    timestamp: Date.now()
                });
            });
        });
        
        // Track newsletter signups
        document.querySelectorAll('form[data-type="newsletter"]').forEach(form => {
            form.addEventListener('submit', (e) => {
                const formData = new FormData(form);
                
                this.addInteraction({
                    type: 'newsletter_signup',
                    email: formData.get('email'),
                    timestamp: Date.now()
                });
            });
        });
    }
    
    trackScrollDepth() {
        let maxScroll = 0;
        
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round(
                (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                
                // Track milestone scroll depths
                if ([25, 50, 75, 90].includes(scrollPercent)) {
                    this.addInteraction({
                        type: 'scroll_depth',
                        depth_percent: scrollPercent,
                        timestamp: Date.now()
                    });
                }
            }
        });
    }
    
    trackTimeOnPage() {
        // Track time spent on property pages
        const propertyId = this.extractPropertyId();
        if (propertyId) {
            setInterval(() => {
                const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
                
                // Update time spent every 30 seconds
                this.addInteraction({
                    type: 'time_on_property',
                    property_id: propertyId,
                    time_spent: timeSpent,
                    timestamp: Date.now()
                }, true); // Replace previous time tracking
            }, 30000);
        }
    }
    
    extractPropertyId() {
        // Extract property ID from URL or data attributes
        const urlMatch = window.location.pathname.match(/\/property\/(\d+)/);
        if (urlMatch) return urlMatch[1];
        
        const dataAttr = document.querySelector('[data-property-id]');
        if (dataAttr) return dataAttr.getAttribute('data-property-id');
        
        return null;
    }
    
    addInteraction(interaction, replace = false) {
        if (replace) {
            // Replace last interaction of same type
            const lastIndex = this.interactions.findLastIndex(i => i.type === interaction.type);
            if (lastIndex !== -1) {
                this.interactions[lastIndex] = interaction;
                return;
            }
        }
        
        this.interactions.push(interaction);
    }
    
    async sendBatch() {
        if (this.interactions.length === 0) return;
        
        const payload = {
            session_id: this.sessionId,
            user_id: this.userId,
            interactions: [...this.interactions],
            page_info: {
                url: window.location.href,
                title: document.title,
                user_agent: navigator.userAgent,
                screen_resolution: `${screen.width}x${screen.height}`,
                viewport_size: `${window.innerWidth}x${window.innerHeight}`
            },
            timestamp: Date.now()
        };
        
        try {
            await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            // Clear sent interactions
            this.interactions = [];
        } catch (error) {
            console.error('Failed to send tracking data:', error);
        }
    }
}

// Initialize tracker
document.addEventListener('DOMContentLoaded', () => {
    window.realEstateTracker = new RealEstateTracker({
        n8nWebhookUrl: 'YOUR_N8N_WEBHOOK_URL',
        userId: window.currentUserId || null
    });
});
```

### 1.2 Website Integration

Add this to your website's header:

```html
<!-- Real Estate Tracking -->
<script src="/js/real-estate-tracker.js"></script>
<script>
// Set user ID if logged in
window.currentUserId = {{ user.id if user.is_authenticated else 'null' }};
</script>
```

## Part 2: n8n Workflow Configurations

### 2.1 Lead Scoring Workflow

Create this workflow in n8n:

```json
{
  "name": "Lead Scoring Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "lead-tracking",
        "responseMode": "responseNode",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "// Process incoming tracking data\nconst data = $input.first().json;\n\n// Extract user interactions\nconst interactions = data.interactions || [];\nconst sessionId = data.session_id;\nconst userId = data.user_id;\n\n// Calculate behavioral scores\nlet behavioralScore = 0;\nlet engagementDepth = 0;\nlet propertyInterest = 0;\n\n// Process each interaction\ninteractions.forEach(interaction => {\n  switch(interaction.type) {\n    case 'property_view':\n      behavioralScore += 10;\n      propertyInterest += 1;\n      break;\n    case 'image_zoom':\n      behavioralScore += 5;\n      engagementDepth += 1;\n      break;\n    case 'property_search':\n      behavioralScore += 8;\n      break;\n    case 'contact_form':\n      behavioralScore += 25;\n      break;\n    case 'newsletter_signup':\n      behavioralScore += 15;\n      break;\n    case 'time_on_property':\n      if (interaction.time_spent > 120) {\n        behavioralScore += Math.min(interaction.time_spent / 30, 20);\n      }\n      break;\n    case 'scroll_depth':\n      if (interaction.depth_percent >= 75) {\n        behavioralScore += 3;\n      }\n      break;\n  }\n});\n\n// Prepare data for Baserow\nconst processedData = {\n  session_id: sessionId,\n  user_id: userId,\n  behavioral_score: Math.min(behavioralScore, 100),\n  engagement_depth: engagementDepth,\n  property_interest: propertyInterest,\n  interactions: interactions,\n  processed_at: new Date().toISOString()\n};\n\nreturn [{ json: processedData }];"
      },
      "name": "Process Tracking Data",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "USER_INTERACTIONS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "session_id",
              "fieldValue": "={{ $json.session_id }}"
            },
            {
              "fieldName": "user_id",
              "fieldValue": "={{ $json.user_id }}"
            },
            {
              "fieldName": "interaction_type",
              "fieldValue": "batch_processing"
            },
            {
              "fieldName": "behavioral_score",
              "fieldValue": "={{ $json.behavioral_score }}"
            },
            {
              "fieldName": "created_at",
              "fieldValue": "={{ $json.processed_at }}"
            }
          ]
        }
      },
      "name": "Save to Baserow",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.user_id }}",
              "operation": "isNotEmpty"
            }
          ]
        }
      },
      "name": "Check User ID",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:5000/api/calculate-lead-score",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpMethod": "POST",
        "jsonParameters": true,
        "parametersJson": "={{ JSON.stringify({\n  user_id: $json.user_id,\n  behavioral_score: $json.behavioral_score,\n  session_data: $json\n}) }}",
        "options": {}
      },
      "name": "Calculate ML Score",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [1120, 200]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "update",
        "tableId": "USERS_TABLE_ID",
        "rowId": "={{ $json.user_id }}",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "lead_score",
              "fieldValue": "={{ $json.total_score }}"
            },
            {
              "fieldName": "lead_grade",
              "fieldValue": "={{ $json.lead_grade }}"
            },
            {
              "fieldName": "updated_at",
              "fieldValue": "={{ new Date().toISOString() }}"
            }
          ]
        }
      },
      "name": "Update User Score",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1340, 200]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({status: 'success', message: 'Lead score updated'}) }}"
      },
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1560, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Process Tracking Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process Tracking Data": {
      "main": [
        [
          {
            "node": "Save to Baserow",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Save to Baserow": {
      "main": [
        [
          {
            "node": "Check User ID",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check User ID": {
      "main": [
        [
          {
            "node": "Calculate ML Score",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Calculate ML Score": {
      "main": [
        [
          {
            "node": "Update User Score",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update User Score": {
      "main": [
        [
          {
            "node": "Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2.2 Lead Qualification Workflow

Create this workflow for automatic lead qualification:

```json
{
  "name": "Lead Qualification Workflow",
  "nodes": [
    {
      "parameters": {
        "triggerOn": "specificTable",
        "tableId": "LEADS_TABLE_ID",
        "event": "created"
      },
      "name": "New Lead Trigger",
      "type": "n8n-nodes-base.baserowTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "// Qualify lead based on initial data\nconst lead = $input.first().json;\n\nlet qualificationScore = 0;\nlet qualificationReasons = [];\n\n// Budget qualification\nif (lead.budget_max && lead.budget_max >= 200000) {\n  qualificationScore += 30;\n  qualificationReasons.push('Sufficient budget');\n}\n\n// Timeline qualification\nif (['Immediate', '1-3 months'].includes(lead.timeline)) {\n  qualificationScore += 25;\n  qualificationReasons.push('Urgent timeline');\n}\n\n// Contact information completeness\nif (lead.email && lead.phone) {\n  qualificationScore += 20;\n  qualificationReasons.push('Complete contact info');\n}\n\n// Property type specificity\nif (lead.property_type_interest && lead.property_type_interest.length <= 2) {\n  qualificationScore += 15;\n  qualificationReasons.push('Specific property interest');\n}\n\n// Location specificity\nif (lead.location_preferences && lead.location_preferences.length > 10) {\n  qualificationScore += 10;\n  qualificationReasons.push('Specific location preferences');\n}\n\n// Determine lead grade\nlet leadGrade = 'Unqualified';\nif (qualificationScore >= 80) leadGrade = 'Hot';\nelse if (qualificationScore >= 60) leadGrade = 'Warm';\nelse if (qualificationScore >= 40) leadGrade = 'Cold';\n\nreturn [{\n  json: {\n    ...lead,\n    qualification_score: qualificationScore,\n    lead_grade: leadGrade,\n    qualification_reasons: qualificationReasons\n  }\n}];"
      },
      "name": "Qualify Lead",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "update",
        "tableId": "LEADS_TABLE_ID",
        "rowId": "={{ $json.id }}",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "lead_grade",
              "fieldValue": "={{ $json.lead_grade }}"
            },
            {
              "fieldName": "lead_score",
              "fieldValue": "={{ $json.qualification_score }}"
            }
          ]
        }
      },
      "name": "Update Lead Grade",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.lead_grade }}",
              "value2": "Hot"
            }
          ]
        }
      },
      "name": "Check if Hot Lead",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "subject": "🔥 New Hot Lead Alert",
        "message": "A new hot lead has been qualified:\n\nName: {{ $json.first_name }} {{ $json.last_name }}\nEmail: {{ $json.email }}\nPhone: {{ $json.phone }}\nBudget: €{{ $json.budget_min }} - €{{ $json.budget_max }}\nTimeline: {{ $json.timeline }}\nScore: {{ $json.qualification_score }}/100\n\nReasons: {{ $json.qualification_reasons.join(', ') }}",
        "options": {}
      },
      "name": "Send Alert Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1120, 200]
    }
  ],
  "connections": {
    "New Lead Trigger": {
      "main": [
        [
          {
            "node": "Qualify Lead",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Qualify Lead": {
      "main": [
        [
          {
            "node": "Update Lead Grade",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update Lead Grade": {
      "main": [
        [
          {
            "node": "Check if Hot Lead",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check if Hot Lead": {
      "main": [
        [
          {
            "node": "Send Alert Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Part 3: Machine Learning Scoring Service

### 3.1 Flask API for ML Scoring

Create a Flask application for advanced lead scoring:

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = "https://daytaa.intelligentb2b.com/api"
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN')

class LeadScoringModel:
    def __init__(self):
        self.behavioral_model = None
        self.demographic_model = None
        self.scaler = StandardScaler()
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            self.behavioral_model = joblib.load('models/behavioral_model.pkl')
            self.demographic_model = joblib.load('models/demographic_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            print("Models loaded successfully")
        except FileNotFoundError:
            print("Training new models...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with sample data"""
        # In production, this would use real historical data
        
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
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.behavioral_model, 'models/behavioral_model.pkl')
        joblib.dump(self.demographic_model, 'models/demographic_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
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

@app.route('/api/calculate-lead-score', methods=['POST'])
def calculate_lead_score():
    """Calculate comprehensive lead score"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get user data from Baserow
        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user interactions
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

def get_user_data(user_id):
    """Fetch user data from Baserow"""
    headers = {
        'Authorization': f'Token {BASEROW_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'{BASEROW_API_URL}/database/tables/USERS_TABLE_ID/rows/{user_id}/',
            headers=headers
        )
        
        if response.status_code == 200:
            user = response.json()
            
            # Process user data for ML model
            return {
                'age': calculate_age(user.get('date_of_birth')),
                'income_bracket': encode_income(user.get('annual_income')),
                'family_size': user.get('household_size', 2),
                'employment_status_encoded': encode_employment(user.get('employment_status')),
                'location_score': 0.5  # Would be calculated based on location data
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None

def get_user_interactions(user_id):
    """Fetch user interactions from Baserow"""
    headers = {
        'Authorization': f'Token {BASEROW_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get interactions from last 30 days
        response = requests.get(
            f'{BASEROW_API_URL}/database/tables/USER_INTERACTIONS_TABLE_ID/rows/',
            headers=headers,
            params={
                'filter__user_id__equal': user_id,
                'filter__created_at__date_after': (datetime.now() - timedelta(days=30)).date()
            }
        )
        
        if response.status_code == 200:
            return response.json().get('results', [])
        
        return []
        
    except Exception as e:
        print(f"Error fetching interactions: {e}")
        return []

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

def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    if not date_of_birth:
        return 35  # Default age
    
    try:
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
        age = (datetime.now() - birth_date).days // 365
        return age
    except:
        return 35

def encode_income(annual_income):
    """Encode income into brackets"""
    if not annual_income:
        return 3
    
    if annual_income < 30000:
        return 1
    elif annual_income < 50000:
        return 2
    elif annual_income < 75000:
        return 3
    elif annual_income < 100000:
        return 4
    else:
        return 5

def encode_employment(employment_status):
    """Encode employment status"""
    mapping = {
        'Employed': 1,
        'Self-employed': 2,
        'Retired': 3,
        'Unemployed': 4,
        'Student': 4
    }
    return mapping.get(employment_status, 1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 3.2 Requirements File

Create `requirements.txt`:

```
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
requests==2.31.0
python-dotenv==1.0.0
```

### 3.3 Deployment Script

Create `deploy_scoring_service.py`:

```python
#!/usr/bin/env python3
import subprocess
import sys
import os

def deploy_scoring_service():
    """Deploy the lead scoring service"""
    
    print("🚀 Deploying Lead Scoring Service...")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Set environment variables
    os.environ['BASEROW_TOKEN'] = input("Enter your Baserow API token: ")
    
    # Start the service
    print("🔥 Starting Flask service...")
    subprocess.run([sys.executable, 'app.py'])

if __name__ == '__main__':
    deploy_scoring_service()
```

## Part 4: Integration Testing

### 4.1 Test the Complete Flow

1. **Deploy the Flask service:**
   ```bash
   python deploy_scoring_service.py
   ```

2. **Test the tracking script:**
   - Add the JavaScript to your website
   - Visit property pages and perform actions
   - Check n8n workflow execution logs

3. **Verify Baserow updates:**
   - Check User_Interactions table for new records
   - Verify lead scores are being updated

4. **Test the API directly:**
   ```bash
   curl -X POST http://localhost:5000/api/calculate-lead-score \
     -H "Content-Type: application/json" \
     -d '{"user_id": "123"}'
   ```

### 4.2 Monitoring and Optimization

Set up monitoring for:
- n8n workflow execution times
- API response times
- Lead scoring accuracy
- Baserow API rate limits

This lead scoring system provides real-time, AI-powered lead prioritization that will significantly improve your sales team's efficiency and conversion rates.

