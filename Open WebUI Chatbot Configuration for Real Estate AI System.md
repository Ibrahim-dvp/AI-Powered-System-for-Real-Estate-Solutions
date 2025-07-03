# Open WebUI Chatbot Configuration for Real Estate AI System

**Open WebUI Instance:** ai.intelligentb2b.com  
**Date:** January 7, 2025

## Overview

This guide configures your existing Open WebUI instance to serve as an intelligent real estate chatbot capable of lead qualification, property recommendations, appointment scheduling, and seamless integration with your Baserow database and n8n workflows.

## Architecture

```
User Message → Open WebUI → Custom Model → Intent Processing → Action Execution → Response Generation
                    ↓
            n8n Webhook → Baserow Update → Lead Scoring
```

## Part 1: Model Configuration

### 1.1 Create Custom Real Estate Model

In your Open WebUI admin panel, create a new model with these specifications:

**Model Name:** `real-estate-assistant`  
**Base Model:** `gpt-4o-mini` (OpenAI)  
**Model Type:** Chat Completion

**System Prompt:**
```
You are an expert real estate assistant for an Italian real estate agency. Your primary goals are:

1. LEAD QUALIFICATION: Gather essential information about prospects
2. PROPERTY MATCHING: Recommend suitable properties based on preferences
3. APPOINTMENT SCHEDULING: Book property viewings and consultations
4. MARKET INSIGHTS: Provide accurate market information and trends

## CORE CAPABILITIES:

### Lead Qualification Questions:
- Budget range (minimum and maximum)
- Preferred locations/neighborhoods
- Property type (apartment, house, villa, commercial)
- Number of bedrooms/bathrooms needed
- Timeline for purchase/rental
- Financing requirements
- Investment vs. primary residence
- Family size and composition

### Property Information:
- Detailed property descriptions
- Market comparisons
- Neighborhood insights
- Investment potential
- Financing options
- Legal requirements

### Conversation Guidelines:
- Always be professional, helpful, and knowledgeable
- Ask one question at a time to avoid overwhelming users
- Confirm understanding before moving to next topic
- Provide specific, actionable information
- Use Italian real estate terminology when appropriate
- Maintain conversation context throughout the interaction

### Data Collection:
For each conversation, extract and structure:
- Contact information (name, email, phone)
- Budget preferences (min/max price)
- Location preferences (cities, neighborhoods)
- Property requirements (type, size, features)
- Timeline and urgency level
- Financing needs and pre-approval status

### Response Format:
- Provide clear, concise answers
- Use bullet points for multiple options
- Include relevant property suggestions when appropriate
- Always end with a follow-up question to continue engagement
- Offer to schedule viewings or consultations when relevant

### Integration Actions:
When appropriate, trigger these actions:
- SAVE_LEAD: Save qualified lead information
- SCHEDULE_VIEWING: Book property viewing appointment
- SEND_PROPERTIES: Send matching property recommendations
- REQUEST_CALLBACK: Schedule phone consultation
- ESCALATE_TO_AGENT: Transfer to human agent

Remember: You represent a premium real estate service. Maintain high standards of professionalism while being approachable and helpful.
```

### 1.2 Model Parameters

Configure these parameters for optimal performance:

```json
{
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 0.9,
  "frequency_penalty": 0.1,
  "presence_penalty": 0.1,
  "stop_sequences": ["[END_CONVERSATION]"]
}
```

### 1.3 Function Definitions

Add these function definitions to enable structured actions:

```json
{
  "functions": [
    {
      "name": "save_lead_information",
      "description": "Save qualified lead information to the CRM system",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Full name of the lead"
          },
          "email": {
            "type": "string",
            "description": "Email address"
          },
          "phone": {
            "type": "string",
            "description": "Phone number"
          },
          "budget_min": {
            "type": "number",
            "description": "Minimum budget in EUR"
          },
          "budget_max": {
            "type": "number",
            "description": "Maximum budget in EUR"
          },
          "property_type": {
            "type": "string",
            "enum": ["apartment", "house", "villa", "commercial", "land"],
            "description": "Preferred property type"
          },
          "locations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Preferred locations or neighborhoods"
          },
          "bedrooms": {
            "type": "number",
            "description": "Number of bedrooms needed"
          },
          "timeline": {
            "type": "string",
            "enum": ["immediate", "1-3 months", "3-6 months", "6-12 months", "1+ years"],
            "description": "Purchase timeline"
          },
          "financing_needed": {
            "type": "boolean",
            "description": "Whether financing is required"
          },
          "investment_purpose": {
            "type": "boolean",
            "description": "Whether this is an investment property"
          }
        },
        "required": ["name", "email", "budget_min", "budget_max", "property_type"]
      }
    },
    {
      "name": "schedule_property_viewing",
      "description": "Schedule a property viewing appointment",
      "parameters": {
        "type": "object",
        "properties": {
          "property_id": {
            "type": "string",
            "description": "ID of the property to view"
          },
          "contact_name": {
            "type": "string",
            "description": "Name of the person scheduling"
          },
          "contact_email": {
            "type": "string",
            "description": "Email for confirmation"
          },
          "contact_phone": {
            "type": "string",
            "description": "Phone number for contact"
          },
          "preferred_date": {
            "type": "string",
            "description": "Preferred viewing date (YYYY-MM-DD)"
          },
          "preferred_time": {
            "type": "string",
            "description": "Preferred viewing time (HH:MM)"
          },
          "notes": {
            "type": "string",
            "description": "Additional notes or requirements"
          }
        },
        "required": ["property_id", "contact_name", "contact_email", "preferred_date"]
      }
    },
    {
      "name": "search_properties",
      "description": "Search for properties matching user criteria",
      "parameters": {
        "type": "object",
        "properties": {
          "budget_min": {
            "type": "number",
            "description": "Minimum budget in EUR"
          },
          "budget_max": {
            "type": "number",
            "description": "Maximum budget in EUR"
          },
          "property_type": {
            "type": "string",
            "enum": ["apartment", "house", "villa", "commercial", "land"],
            "description": "Property type"
          },
          "location": {
            "type": "string",
            "description": "City or neighborhood"
          },
          "bedrooms": {
            "type": "number",
            "description": "Number of bedrooms"
          },
          "bathrooms": {
            "type": "number",
            "description": "Number of bathrooms"
          },
          "min_sqm": {
            "type": "number",
            "description": "Minimum square meters"
          },
          "max_sqm": {
            "type": "number",
            "description": "Maximum square meters"
          }
        },
        "required": ["budget_min", "budget_max", "property_type"]
      }
    },
    {
      "name": "request_agent_callback",
      "description": "Request a callback from a human agent",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the person requesting callback"
          },
          "phone": {
            "type": "string",
            "description": "Phone number for callback"
          },
          "email": {
            "type": "string",
            "description": "Email address"
          },
          "preferred_time": {
            "type": "string",
            "description": "Preferred callback time"
          },
          "reason": {
            "type": "string",
            "description": "Reason for callback request"
          },
          "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Urgency level"
          }
        },
        "required": ["name", "phone", "reason"]
      }
    }
  ]
}
```

## Part 2: Webhook Integration Setup

### 2.1 Create Webhook Endpoint in n8n

Create this n8n workflow to handle Open WebUI function calls:

```json
{
  "name": "Open WebUI Integration Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "openwebui-webhook",
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
        "functionCode": "// Process Open WebUI function call\nconst data = $input.first().json;\n\nconst functionName = data.function_name;\nconst parameters = data.parameters || {};\nconst conversationId = data.conversation_id;\nconst userId = data.user_id;\n\n// Route to appropriate handler\nlet result = {};\n\nswitch(functionName) {\n  case 'save_lead_information':\n    result = {\n      action: 'save_lead',\n      data: parameters,\n      conversation_id: conversationId,\n      user_id: userId\n    };\n    break;\n    \n  case 'schedule_property_viewing':\n    result = {\n      action: 'schedule_viewing',\n      data: parameters,\n      conversation_id: conversationId,\n      user_id: userId\n    };\n    break;\n    \n  case 'search_properties':\n    result = {\n      action: 'search_properties',\n      data: parameters,\n      conversation_id: conversationId,\n      user_id: userId\n    };\n    break;\n    \n  case 'request_agent_callback':\n    result = {\n      action: 'request_callback',\n      data: parameters,\n      conversation_id: conversationId,\n      user_id: userId\n    };\n    break;\n    \n  default:\n    result = {\n      action: 'unknown',\n      error: 'Unknown function: ' + functionName\n    };\n}\n\nreturn [{ json: result }];"
      },
      "name": "Process Function Call",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.action }}",
              "value2": "save_lead"
            }
          ]
        }
      },
      "name": "Check Action Type",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "LEADS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "first_name",
              "fieldValue": "={{ $json.data.name.split(' ')[0] }}"
            },
            {
              "fieldName": "last_name",
              "fieldValue": "={{ $json.data.name.split(' ').slice(1).join(' ') }}"
            },
            {
              "fieldName": "email",
              "fieldValue": "={{ $json.data.email }}"
            },
            {
              "fieldName": "phone",
              "fieldValue": "={{ $json.data.phone }}"
            },
            {
              "fieldName": "budget_min",
              "fieldValue": "={{ $json.data.budget_min }}"
            },
            {
              "fieldName": "budget_max",
              "fieldValue": "={{ $json.data.budget_max }}"
            },
            {
              "fieldName": "property_type_interest",
              "fieldValue": "={{ $json.data.property_type }}"
            },
            {
              "fieldName": "timeline",
              "fieldValue": "={{ $json.data.timeline }}"
            },
            {
              "fieldName": "financing_needed",
              "fieldValue": "={{ $json.data.financing_needed }}"
            },
            {
              "fieldName": "investment_purpose",
              "fieldValue": "={{ $json.data.investment_purpose }}"
            },
            {
              "fieldName": "lead_source",
              "fieldValue": "Chatbot"
            },
            {
              "fieldName": "lead_status",
              "fieldValue": "New"
            }
          ]
        }
      },
      "name": "Save Lead to Baserow",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [900, 200]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "CHATBOT_CONVERSATIONS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "conversation_id",
              "fieldValue": "={{ $json.conversation_id }}"
            },
            {
              "fieldName": "platform",
              "fieldValue": "Website"
            },
            {
              "fieldName": "conversation_status",
              "fieldValue": "Active"
            },
            {
              "fieldName": "lead_qualified",
              "fieldValue": true
            },
            {
              "fieldName": "extracted_preferences",
              "fieldValue": "={{ JSON.stringify($json.data) }}"
            }
          ]
        }
      },
      "name": "Log Conversation",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1120, 200]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({status: 'success', message: 'Lead saved successfully', lead_id: $json.id}) }}"
      },
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Process Function Call",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process Function Call": {
      "main": [
        [
          {
            "node": "Check Action Type",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Action Type": {
      "main": [
        [
          {
            "node": "Save Lead to Baserow",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Save Lead to Baserow": {
      "main": [
        [
          {
            "node": "Log Conversation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Conversation": {
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

### 2.2 Configure Open WebUI Webhook

In your Open WebUI admin settings, configure the webhook:

**Webhook URL:** `https://your-n8n-instance.com/webhook/openwebui-webhook`  
**Events:** Function calls, conversation events  
**Authentication:** Bearer token (if required)

## Part 3: Property Search Integration

### 3.1 Create Property Search Service

Create a Flask service to handle property searches from the chatbot:

```python
# property_search_service.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = "https://daytaa.intelligentb2b.com/api"
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN')

@app.route('/api/search-properties', methods=['POST'])
def search_properties():
    """Search properties based on chatbot criteria"""
    try:
        criteria = request.json
        
        # Build Baserow filter query
        filters = []
        
        # Budget filters
        if criteria.get('budget_min'):
            filters.append(f"filter__current_price__gte={criteria['budget_min']}")
        if criteria.get('budget_max'):
            filters.append(f"filter__current_price__lte={criteria['budget_max']}")
        
        # Property type filter
        if criteria.get('property_type'):
            filters.append(f"filter__property_type__equal={criteria['property_type']}")
        
        # Location filter
        if criteria.get('location'):
            filters.append(f"filter__city__contains={criteria['location']}")
        
        # Bedroom filter
        if criteria.get('bedrooms'):
            filters.append(f"filter__bedrooms__equal={criteria['bedrooms']}")
        
        # Size filters
        if criteria.get('min_sqm'):
            filters.append(f"filter__square_meters__gte={criteria['min_sqm']}")
        if criteria.get('max_sqm'):
            filters.append(f"filter__square_meters__lte={criteria['max_sqm']}")
        
        # Only active listings
        filters.append("filter__status__equal=Active")
        
        # Query Baserow
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        query_params = '&'.join(filters) + '&size=10'  # Limit to 10 results
        
        response = requests.get(
            f'{BASEROW_API_URL}/database/tables/PROPERTIES_TABLE_ID/rows/?{query_params}',
            headers=headers
        )
        
        if response.status_code == 200:
            properties = response.json().get('results', [])
            
            # Format properties for chatbot response
            formatted_properties = []
            for prop in properties:
                formatted_properties.append({
                    'id': prop['id'],
                    'title': prop['title'],
                    'price': prop['current_price'],
                    'location': f"{prop['city']}, {prop['region']}",
                    'type': prop['property_type'],
                    'bedrooms': prop['bedrooms'],
                    'bathrooms': prop['bathrooms'],
                    'square_meters': prop['square_meters'],
                    'description': prop['description'][:200] + '...' if len(prop['description']) > 200 else prop['description'],
                    'url': f"https://your-website.com/property/{prop['id']}"
                })
            
            return jsonify({
                'success': True,
                'properties': formatted_properties,
                'total_found': len(formatted_properties),
                'search_criteria': criteria
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to search properties',
                'properties': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': []
        }), 500

@app.route('/api/get-property-details/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information about a specific property"""
    try:
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{BASEROW_API_URL}/database/tables/PROPERTIES_TABLE_ID/rows/{property_id}/',
            headers=headers
        )
        
        if response.status_code == 200:
            property_data = response.json()
            
            # Get property images
            images_response = requests.get(
                f'{BASEROW_API_URL}/database/tables/PROPERTY_IMAGES_TABLE_ID/rows/?filter__property_id__equal={property_id}',
                headers=headers
            )
            
            images = []
            if images_response.status_code == 200:
                images = images_response.json().get('results', [])
            
            return jsonify({
                'success': True,
                'property': property_data,
                'images': images
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## Part 4: Conversation Flow Templates

### 4.1 Lead Qualification Flow

Create these conversation templates in Open WebUI:

**Template Name:** `lead-qualification-flow`

```
Welcome! I'm here to help you find the perfect property. To provide you with the best recommendations, I'd like to learn about your preferences.

Let's start with your budget. What's your price range for this property?

[WAIT FOR RESPONSE]

Great! And what type of property are you looking for?
- Apartment
- House
- Villa
- Commercial property
- Land

[WAIT FOR RESPONSE]

Perfect! Which areas or neighborhoods are you considering?

[WAIT FOR RESPONSE]

How many bedrooms do you need?

[WAIT FOR RESPONSE]

What's your timeline for making a purchase?
- Immediate (within 1 month)
- 1-3 months
- 3-6 months
- 6-12 months
- More than a year

[WAIT FOR RESPONSE]

Will you need financing for this purchase?

[WAIT FOR RESPONSE]

Excellent! I have all the information I need. Let me search for properties that match your criteria.

[TRIGGER: search_properties]

Based on your preferences, I found several properties that might interest you. Would you like me to show you the top matches?

[TRIGGER: save_lead_information]
```

### 4.2 Property Recommendation Flow

**Template Name:** `property-recommendation-flow`

```
Here are the top properties that match your criteria:

[DISPLAY PROPERTY RESULTS]

For each property, I can provide:
- Detailed descriptions and features
- High-resolution photos
- Virtual tour links
- Neighborhood information
- Market analysis
- Financing options

Which property would you like to learn more about? Just tell me the property number or name.

[WAIT FOR RESPONSE]

Would you like to schedule a viewing for this property? I can check availability and book an appointment for you.

[TRIGGER: schedule_property_viewing]
```

### 4.3 Appointment Scheduling Flow

**Template Name:** `appointment-scheduling-flow`

```
I'd be happy to schedule a property viewing for you!

To book your appointment, I'll need:
- Your full name
- Phone number
- Email address
- Preferred date and time

What's your full name?

[WAIT FOR RESPONSE]

And your phone number?

[WAIT FOR RESPONSE]

Your email address?

[WAIT FOR RESPONSE]

When would you prefer to view the property? Please provide your preferred date and time.

[WAIT FOR RESPONSE]

Perfect! I'm scheduling your viewing for [PROPERTY] on [DATE] at [TIME].

You'll receive a confirmation email shortly with:
- Property address and directions
- Agent contact information
- What to bring to the viewing
- Parking information

Is there anything specific you'd like to know about the property before your visit?

[TRIGGER: schedule_property_viewing]
```

## Part 5: Multi-Platform Integration

### 5.1 WhatsApp Business API Integration

Configure WhatsApp integration in Open WebUI:

```javascript
// WhatsApp webhook handler
const whatsappWebhook = {
  endpoint: 'https://ai.intelligentb2b.com/api/whatsapp-webhook',
  verification_token: 'your_verification_token',
  access_token: 'your_whatsapp_access_token',
  
  handleMessage: function(message) {
    // Process incoming WhatsApp message
    const userMessage = message.text.body;
    const phoneNumber = message.from;
    
    // Send to Open WebUI for processing
    return this.sendToOpenWebUI({
      message: userMessage,
      platform: 'whatsapp',
      user_id: phoneNumber,
      conversation_id: `whatsapp_${phoneNumber}_${Date.now()}`
    });
  },
  
  sendResponse: function(response, phoneNumber) {
    // Send response back to WhatsApp
    const whatsappAPI = `https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages`;
    
    return fetch(whatsappAPI, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        to: phoneNumber,
        text: { body: response }
      })
    });
  }
};
```

### 5.2 Website Chat Widget

Create this HTML widget for your website:

```html
<!-- Real Estate Chat Widget -->
<div id="real-estate-chat-widget">
  <div id="chat-button" onclick="toggleChat()">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
      <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
    </svg>
  </div>
  
  <div id="chat-window" style="display: none;">
    <div id="chat-header">
      <h3>Real Estate Assistant</h3>
      <button onclick="toggleChat()">×</button>
    </div>
    
    <div id="chat-messages"></div>
    
    <div id="chat-input">
      <input type="text" id="message-input" placeholder="Ask about properties...">
      <button onclick="sendMessage()">Send</button>
    </div>
  </div>
</div>

<script>
function toggleChat() {
  const chatWindow = document.getElementById('chat-window');
  const chatButton = document.getElementById('chat-button');
  
  if (chatWindow.style.display === 'none') {
    chatWindow.style.display = 'block';
    chatButton.style.display = 'none';
    initializeChat();
  } else {
    chatWindow.style.display = 'none';
    chatButton.style.display = 'block';
  }
}

function initializeChat() {
  const messagesDiv = document.getElementById('chat-messages');
  messagesDiv.innerHTML = `
    <div class="bot-message">
      Hello! I'm your real estate assistant. I can help you find properties, schedule viewings, and answer questions about the market. What are you looking for today?
    </div>
  `;
}

async function sendMessage() {
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  
  if (!message) return;
  
  // Add user message to chat
  addMessage(message, 'user');
  input.value = '';
  
  // Send to Open WebUI
  try {
    const response = await fetch('https://ai.intelligentb2b.com/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        model: 'real-estate-assistant',
        conversation_id: getConversationId()
      })
    });
    
    const data = await response.json();
    addMessage(data.response, 'bot');
    
  } catch (error) {
    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
  }
}

function addMessage(message, sender) {
  const messagesDiv = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `${sender}-message`;
  messageDiv.textContent = message;
  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function getConversationId() {
  let conversationId = localStorage.getItem('chat-conversation-id');
  if (!conversationId) {
    conversationId = 'web_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('chat-conversation-id', conversationId);
  }
  return conversationId;
}

// Handle Enter key in input
document.getElementById('message-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    sendMessage();
  }
});
</script>

<style>
#real-estate-chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

#chat-button {
  width: 60px;
  height: 60px;
  background: #007bff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

#chat-window {
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
}

#chat-header {
  background: #007bff;
  color: white;
  padding: 15px;
  border-radius: 10px 10px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.user-message {
  background: #e3f2fd;
  padding: 10px;
  border-radius: 10px;
  margin: 5px 0;
  margin-left: 20px;
}

.bot-message {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 10px;
  margin: 5px 0;
  margin-right: 20px;
}

#chat-input {
  display: flex;
  padding: 15px;
  border-top: 1px solid #eee;
}

#message-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-right: 10px;
}

#chat-input button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
</style>
```

## Part 6: Testing and Optimization

### 6.1 Test Conversation Flows

Test these scenarios:

1. **Lead Qualification Test:**
   - User asks about apartments in Rome
   - Bot qualifies budget, preferences, timeline
   - Lead information is saved to Baserow

2. **Property Search Test:**
   - User provides specific criteria
   - Bot searches and displays matching properties
   - User can request more details

3. **Appointment Scheduling Test:**
   - User wants to view a property
   - Bot collects contact information
   - Appointment is scheduled in calendar

### 6.2 Performance Monitoring

Monitor these metrics:
- Response time (target: <2 seconds)
- Lead qualification rate
- Appointment booking conversion
- User satisfaction scores

### 6.3 Continuous Improvement

Implement these optimization strategies:
- A/B test different conversation flows
- Analyze conversation logs for improvement opportunities
- Update model training based on successful interactions
- Refine function calling accuracy

## Part 7: Deployment Checklist

### 7.1 Open WebUI Configuration
- [ ] Custom model created and configured
- [ ] System prompts optimized
- [ ] Function definitions added
- [ ] Webhook endpoints configured

### 7.2 n8n Workflows
- [ ] Integration workflow deployed
- [ ] Webhook URLs configured
- [ ] Baserow connections tested
- [ ] Error handling implemented

### 7.3 Property Search Service
- [ ] Flask service deployed
- [ ] Baserow API integration tested
- [ ] Search functionality verified
- [ ] CORS configured for web access

### 7.4 Multi-Platform Integration
- [ ] Website chat widget implemented
- [ ] WhatsApp Business API configured
- [ ] Social media integrations tested
- [ ] Cross-platform conversation sync

This comprehensive chatbot setup will provide intelligent, context-aware conversations that effectively qualify leads, recommend properties, and schedule appointments while seamlessly integrating with your existing Baserow database and n8n workflows.

