# AI-Powered Real Estate System - Complete Setup Guide

## 🚀 Step-by-Step Local Installation Guide

This guide will help you set up the complete AI-powered real estate system on your local machine, including Python services, n8n workflows, Baserow database, and Open WebUI integration.

### 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.11+** installed
- **Node.js 20+** installed
- **Docker and Docker Compose** installed
- **Git** installed
- Access to **Baserow** at `https://dayta.intelligentb2b.com`
- Access to **Open WebUI** at `https://ai.intelligentb2b.com`

### 🛠️ Phase 1: Environment Setup

#### 1.1 Clone and Setup Project

```bash
# Navigate to your desktop
cd ~/Desktop

# Create project directory
mkdir ai-real-estate-system
cd ai-real-estate-system

# Copy all files from your current directory
# (You already have these files)

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 1.2 Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your specific configuration
# You'll need to fill in:
# - BASEROW_TOKEN (from your Baserow account)
# - BASEROW_APPLICATION_ID (from your Baserow dashboard)
# - OPENAI_API_KEY (for AI features)
# - Email credentials for notifications
```

### 🗄️ Phase 2: Baserow Database Setup

#### 2.1 Get Baserow Credentials

1. **Login to Baserow**: Navigate to `https://dayta.intelligentb2b.com`
2. **Get API Token**: 
   - Go to Settings → API tokens
   - Create new token with full permissions
   - Copy token to `.env` file as `BASEROW_TOKEN`

3. **Get Application ID**:
   - In Baserow dashboard, note the URL: `https://dayta.intelligentb2b.com/dashboard/applications/YOUR_APP_ID/`
   - Copy the APP_ID to `.env` file as `BASEROW_APPLICATION_ID`

#### 2.2 Create Database Tables

```bash
# Run the automated table creation script
python setup_baserow_tables.py

# This will create all necessary tables:
# - Users (leads and customers)
# - Properties (listings)
# - Interactions (user behavior)
# - Deals (sales pipeline)
# - Market Data (analytics)
# - Email Campaigns (marketing)
# - Analytics (dashboard data)
```

#### 2.3 Verify Table Creation

1. **Check Baserow Dashboard**: Refresh your Baserow interface
2. **Update .env file**: The script will output table IDs - add them to your `.env` file
3. **Test API Access**: Run the connection test:

```bash
python scripts/test_baserow_connection.py
```

### 🐍 Phase 3: Python Services Deployment

#### 3.1 Start All Services with Docker

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 3.2 Manual Service Startup (Alternative)

If you prefer to run services individually:

```bash
# Terminal 1: Lead Scoring Service
cd services/lead-scoring
python app.py
# Service will run on http://localhost:5001

# Terminal 2: Property Search Service  
cd services/property-search
python app.py
# Service will run on http://localhost:5002

# Terminal 3: Property Valuation Service
cd services/property-valuation
python app.py
# Service will run on http://localhost:5003

# Terminal 4: Email Marketing Service
cd services/email-marketing
python app.py
# Service will run on http://localhost:5004

# Terminal 5: Dashboard Analytics Service
cd services/dashboard-analytics
python app.py
# Service will run on http://localhost:5005

# Terminal 6: Data Collection Service
cd services/data-collection
python app.py
# Service will run on http://localhost:5006
```

#### 3.3 Service Health Check

```bash
# Check all services are running
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
curl http://localhost:5005/health
curl http://localhost:5006/health
```

### 🤖 Phase 4: n8n Workflow Setup

#### 4.1 Start n8n

```bash
# Using Docker (recommended)
docker-compose up -d n8n

# Or install locally
npm install -g n8n
n8n start

# n8n will be available at http://localhost:5678
```

#### 4.2 Import Workflows

1. **Access n8n**: Open `http://localhost:5678`
2. **Login**: Use credentials from docker-compose.yml (admin/admin123)
3. **Import Workflows**:
   - Go to Workflows → Import
   - Import each workflow file from `n8n/workflows/`:
     - `lead_scoring_workflow.json`
     - `email_marketing_workflow.json`
     - `data_collection_workflow.json`
     - `property_valuation_workflow.json`

#### 4.3 Configure Workflow Connections

For each workflow, update the connection settings:

1. **HTTP Request Nodes**: Update URLs to point to your local services
2. **Baserow Nodes**: Configure with your Baserow credentials
3. **Email Nodes**: Configure with your SMTP settings
4. **Schedule Nodes**: Set appropriate intervals

### 🎯 Phase 5: Open WebUI Integration

#### 5.1 Access Open WebUI

1. **Navigate to**: `https://ai.intelligentb2b.com`
2. **Login**: Use your existing credentials

#### 5.2 Configure Real Estate Assistant

1. **Create New Model**:
   - Go to Admin Panel → Models
   - Click "Add Model"
   - Name: `real-estate-assistant`
   - Base Model: `gpt-4o-mini`

2. **Set System Prompt**:
```
You are an intelligent real estate assistant for the Italian market. You help users find properties, provide market insights, and assist with real estate decisions. You have access to a comprehensive database of properties and can perform searches, valuations, and recommendations.

Your capabilities include:
- Property search and filtering
- Market analysis and valuations
- Lead qualification and scoring
- Appointment scheduling
- Investment analysis

Always be helpful, professional, and knowledgeable about the Italian real estate market.
```

3. **Configure Functions**:
   - Import function definitions from `open_webui/functions/`
   - Enable all real estate functions
   - Set endpoint URLs to your local services

#### 5.3 Test Integration

1. **Start a Chat**: Create new conversation with real estate assistant
2. **Test Property Search**: "Find me a 2-bedroom apartment in Milan under €300,000"
3. **Test Lead Scoring**: The system should automatically track interactions
4. **Test Recommendations**: Ask for personalized property recommendations

### 🖥️ Phase 6: Web Interface Setup

#### 6.1 Start Web Interface

```bash
# Navigate to web interface
cd services/web-interface

# Install dependencies
npm install

# Start development server
npm start

# Interface will be available at http://localhost:3000
```

#### 6.2 Access Dashboard

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Login**: Use admin credentials
3. **Explore Features**:
   - View property listings
   - Check analytics dashboard
   - Monitor lead scoring
   - Review email campaigns

### 🔧 Phase 7: Testing and Validation

#### 7.1 Service Integration Tests

```bash
# Run integration tests
python scripts/test_integration.py

# Test specific components
python scripts/test_lead_scoring.py
python scripts/test_property_search.py
python scripts/test_email_campaigns.py
```

#### 7.2 Manual Testing Checklist

**Lead Scoring:**
- [ ] Create test lead in Baserow
- [ ] Trigger scoring via API
- [ ] Check score updates in dashboard

**Property Search:**
- [ ] Search properties with filters
- [ ] Test recommendation engine
- [ ] Verify similar properties function

**Email Marketing:**
- [ ] Create test campaign
- [ ] Send test email
- [ ] Track open/click rates

**Data Collection:**
- [ ] Test external API connections
- [ ] Verify data import to Baserow
- [ ] Check automated workflows

### 📊 Phase 8: Monitoring and Maintenance

#### 8.1 Setup Monitoring

```bash
# Start monitoring services
docker-compose up -d grafana prometheus

# Access monitoring dashboard
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

#### 8.2 Log Management

```bash
# View service logs
docker-compose logs -f [service-name]

# Check error logs
tail -f logs/error.log

# Monitor performance
tail -f logs/performance.log
```

### 🎯 Phase 9: Production Deployment

#### 9.1 Environment Preparation

```bash
# Create production environment file
cp .env.example .env.production

# Update production settings:
# - Set FLASK_ENV=production
# - Configure production database
# - Set secure secret keys
# - Configure SSL certificates
```

#### 9.2 Deploy to Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL with Let's Encrypt
docker-compose -f docker-compose.prod.yml exec nginx certbot --nginx
```

### 🔍 Troubleshooting Guide

#### Common Issues and Solutions

**1. Baserow Connection Errors**
```bash
# Check network connectivity
curl -I https://dayta.intelligentb2b.com

# Verify API token
curl -H "Authorization: Token YOUR_TOKEN" https://dayta.intelligentb2b.com/api/applications/

# Check table IDs
python scripts/verify_baserow_tables.py
```

**2. Service Startup Failures**
```bash
# Check Docker logs
docker-compose logs [service-name]

# Verify environment variables
docker-compose exec [service-name] env

# Check port conflicts
netstat -tulpn | grep :5001
```

**3. n8n Workflow Issues**
```bash
# Check n8n logs
docker-compose logs n8n

# Verify webhook URLs
curl -X POST http://localhost:5678/webhook/test

# Test workflow execution
# Use n8n interface to manually trigger workflows
```

**4. Open WebUI Integration Problems**
```bash
# Check API connectivity
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"filters": {"property_type": "apartment"}}'

# Verify function definitions
# Check Open WebUI admin panel for function errors
```

### 📝 Next Steps

Once your system is running:

1. **Add Real Data**: Import actual property listings
2. **Configure APIs**: Set up connections to Immobiliare.it, Idealista.it
3. **Customize UI**: Modify dashboard and web interface
4. **Train Models**: Improve AI models with real data
5. **Scale Services**: Add load balancing and auto-scaling

### 🆘 Support and Documentation

- **API Documentation**: Available at `http://localhost:5001/docs`
- **System Logs**: Check `logs/` directory for detailed logs
- **Configuration**: All settings in `.env` file
- **Backups**: Regular database backups in `backups/` directory

### 🎉 Success Validation

Your system is successfully deployed when:
- [ ] All services show "healthy" status
- [ ] Baserow tables are created and populated
- [ ] n8n workflows are active
- [ ] Open WebUI responds to real estate queries
- [ ] Web dashboard displays analytics
- [ ] Email campaigns can be sent
- [ ] Property search returns results
- [ ] Lead scoring processes interactions

**Congratulations! Your AI-powered real estate system is now ready for use.**
