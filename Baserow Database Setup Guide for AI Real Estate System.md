# Baserow Database Setup Guide for AI Real Estate System

**Baserow Instance:** dayta.intelligentb2b.com  
**Date:** January 7, 2025

## Database Schema Implementation

### Step 1: Create Core Tables in Baserow

#### 1.1 Users Table

Navigate to your Baserow instance and create a new table called "Users" with the following fields:

**Basic Information:**

- `user_id` (Auto Number) - Primary key
- `email` (Email) - Unique identifier
- `phone` (Phone Number) - Contact information
- `first_name` (Text, 50 chars)
- `last_name` (Text, 50 chars)
- `registration_date` (Date) - Auto-populated
- `user_status` (Single Select: Active, Inactive, Suspended)

**Demographics:**

- `date_of_birth` (Date)
- `gender` (Single Select: Male, Female, Other, Prefer not to say)
- `marital_status` (Single Select: Single, Married, Divorced, Widowed)
- `household_size` (Number, 1-20)
- `annual_income` (Number)
- `employment_status` (Single Select: Employed, Self-employed, Unemployed, Retired, Student)

**Lead Scoring:**

- `lead_score` (Number, 0-100) - Auto-calculated
- `lead_grade` (Single Select: A, B, C, D, Unqualified)
- `source` (Single Select: Website, Social Media, Referral, Advertisement)

**Marketing:**

- `utm_source` (Text, 100 chars)
- `utm_medium` (Text, 100 chars)
- `utm_campaign` (Text, 100 chars)
- `privacy_consent` (Checkbox) - GDPR compliance
- `marketing_consent` (Checkbox)

**Timestamps:**

- `created_at` (Date and Time) - Auto-populated
- `updated_at` (Date and Time) - Auto-updated

#### 1.2 Properties Table

Create "Properties" table with these fields:

**Basic Information:**

- `property_id` (Auto Number) - Primary key
- `external_id` (Text, 100 chars) - For portal integration
- `property_type` (Single Select: Apartment, House, Villa, Commercial, Land)
- `listing_type` (Single Select: Sale, Rent, Both)
- `title` (Text, 200 chars)
- `description` (Long Text)

**Location:**

- `address` (Text, 300 chars)
- `city` (Text, 100 chars)
- `region` (Text, 100 chars)
- `postal_code` (Text, 20 chars)
- `latitude` (Number, decimal)
- `longitude` (Number, decimal)
- `neighborhood` (Text, 100 chars)

**Property Details:**

- `square_meters` (Number)
- `lot_size` (Number)
- `bedrooms` (Number, 0-20)
- `bathrooms` (Number, 0-20)
- `floors` (Number, 1-50)
- `floor_number` (Number, -5 to 50)
- `building_year` (Number, 1800-2025)
- `condition` (Single Select: Excellent, Good, Fair, Poor, Needs Renovation)

**Features:**

- `heating_type` (Single Select: Central, Autonomous, Heat Pump, None)
- `energy_class` (Single Select: A4, A3, A2, A1, B, C, D, E, F, G)
- `parking_spaces` (Number, 0-20)
- `garage` (Checkbox)
- `garden` (Checkbox)
- `balcony` (Checkbox)
- `terrace` (Checkbox)
- `elevator` (Checkbox)
- `furnished` (Single Select: Furnished, Semi-furnished, Unfurnished)

**Pricing:**

- `current_price` (Number)
- `original_price` (Number)
- `price_per_sqm` (Number) - Auto-calculated
- `monthly_expenses` (Number)
- `property_taxes` (Number)

**Status:**

- `listing_date` (Date)
- `status` (Single Select: Active, Pending, Sold, Rented, Withdrawn)
- `days_on_market` (Number) - Auto-calculated
- `view_count` (Number)
- `inquiry_count` (Number)

**Relationships:**

- `agent_id` (Link to Users table)
- `owner_id` (Link to Users table)

**External:**

- `source_portal` (Single Select: Internal, Immobiliare.it, Idealista.it, etc.)
- `virtual_tour_url` (URL)
- `video_url` (URL)

#### 1.3 Leads Table

Create "Leads" table:

**Basic Information:**

- `lead_id` (Auto Number) - Primary key
- `user_id` (Link to Users) - Optional
- `email` (Email)
- `phone` (Phone Number)
- `first_name` (Text, 50 chars)
- `last_name` (Text, 50 chars)

**Lead Management:**

- `lead_source` (Single Select: Website, Social Media, Referral, Advertisement, Cold Call)
- `lead_status` (Single Select: New, Contacted, Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
- `lead_score` (Number, 0-100)
- `lead_grade` (Single Select: Hot, Warm, Cold, Unqualified)

**Preferences:**

- `budget_min` (Number)
- `budget_max` (Number)
- `property_type_interest` (Multiple Select: Apartment, House, Villa, Commercial, Land)
- `location_preferences` (Long Text) - JSON format
- `timeline` (Single Select: Immediate, 1-3 months, 3-6 months, 6-12 months, 1+ years)

**Qualifiers:**

- `financing_needed` (Checkbox)
- `first_time_buyer` (Checkbox)
- `investment_purpose` (Checkbox)

**Management:**

- `assigned_agent_id` (Link to Users)
- `last_contact_date` (Date)
- `next_follow_up` (Date)
- `conversion_date` (Date)
- `conversion_value` (Number)
- `notes` (Long Text)

#### 1.4 User_Interactions Table

Create "User_Interactions" table for behavioral tracking:

- `interaction_id` (Auto Number) - Primary key
- `user_id` (Link to Users)
- `session_id` (Text, 100 chars)
- `interaction_type` (Single Select: Page View, Property View, Search, Click, Download, Form Submit)
- `page_url` (URL)
- `property_id` (Link to Properties)
- `search_query` (Text, 500 chars)
- `search_filters` (Long Text) - JSON format
- `time_spent` (Number) - seconds
- `scroll_depth` (Number, 0-100) - percentage
- `device_type` (Single Select: Desktop, Mobile, Tablet)
- `browser` (Text, 100 chars)
- `ip_address` (Text, 45 chars)
- `referrer_url` (URL)
- `utm_source` (Text, 100 chars)
- `utm_medium` (Text, 100 chars)
- `utm_campaign` (Text, 100 chars)
- `created_at` (Date and Time)

#### 1.5 Property_Valuations Table

Create "Property_Valuations" table:

- `valuation_id` (Auto Number) - Primary key
- `property_id` (Link to Properties)
- `valuation_type` (Single Select: Automated, Manual, Comparative, Investment)
- `estimated_value` (Number)
- `confidence_score` (Number, 0-100)
- `value_per_sqm` (Number)
- `comparable_properties` (Long Text) - JSON format
- `market_factors` (Long Text) - JSON format
- `valuation_method` (Single Select: Hedonic, Comparative, Income, Cost)
- `valuation_date` (Date)
- `valid_until` (Date)
- `created_by` (Single Select: System, Agent, External)
- `notes` (Long Text)
- `created_at` (Date and Time)

#### 1.6 Email_Campaigns Table

Create "Email_Campaigns" table:

- `campaign_id` (Auto Number) - Primary key
- `campaign_name` (Text, 200 chars)
- `campaign_type` (Single Select: Newsletter, Property Alert, Nurture, Promotional, Transactional)
- `subject_line` (Text, 200 chars)
- `email_content` (Long Text)
- `target_segment` (Single Select: All Users, New Leads, Active Buyers, Past Clients)
- `segment_criteria` (Long Text) - JSON format
- `sender_name` (Text, 100 chars)
- `sender_email` (Email)
- `scheduled_date` (Date and Time)
- `sent_date` (Date and Time)
- `campaign_status` (Single Select: Draft, Scheduled, Sending, Sent, Cancelled)
- `total_recipients` (Number)
- `emails_sent` (Number)
- `emails_delivered` (Number)
- `emails_opened` (Number)
- `emails_clicked` (Number)
- `open_rate` (Number) - percentage
- `click_rate` (Number) - percentage
- `created_at` (Date and Time)
- `updated_at` (Date and Time)

#### 1.7 Chatbot_Conversations Table

Create "Chatbot_Conversations" table:

- `conversation_id` (Auto Number) - Primary key
- `user_id` (Link to Users)
- `platform` (Single Select: Website, WhatsApp, Facebook, Instagram, Telegram)
- `platform_user_id` (Text, 100 chars)
- `conversation_status` (Single Select: Active, Completed, Abandoned, Escalated)
- `lead_qualified` (Checkbox)
- `appointment_scheduled` (Checkbox)
- `satisfaction_rating` (Number, 1-5)
- `conversation_summary` (Long Text)
- `extracted_preferences` (Long Text) - JSON format
- `started_at` (Date and Time)
- `ended_at` (Date and Time)
- `total_messages` (Number)
- `response_time_avg` (Number) - seconds
- `created_at` (Date and Time)

### Step 2: Configure Baserow API Access

#### 2.1 Generate API Token

1. Go to Settings in your Baserow instance
2. Navigate to API tokens
3. Create a new token with full database access
4. Save the token securely for n8n integration

#### 2.2 API Endpoints

Your Baserow API will be available at:

- Base URL: `https://daytaa.intelligentb2b.com/api/`
- Database list: `GET /api/database/`
- Table data: `GET /api/database/tables/{table_id}/rows/`
- Create row: `POST /api/database/tables/{table_id}/rows/`
- Update row: `PATCH /api/database/tables/{table_id}/rows/{row_id}/`

### Step 3: Set Up Views and Filters

#### 3.1 Lead Management Views

Create these views in the Leads table:

- **Hot Leads**: Filter by lead_grade = "Hot"
- **New Leads**: Filter by lead_status = "New"
- **Follow-up Required**: Filter by next_follow_up <= today
- **High Score Leads**: Filter by lead_score >= 80

#### 3.2 Property Management Views

Create these views in the Properties table:

- **Active Listings**: Filter by status = "Active"
- **High Value Properties**: Filter by current_price >= 500000
- **New Listings**: Filter by listing_date >= 7 days ago
- **Price Reduced**: Filter where current_price < original_price

#### 3.3 Performance Dashboard Views

Create these views for analytics:

- **Monthly Conversions**: Group by conversion_date (month)
- **Agent Performance**: Group by assigned_agent_id
- **Source Analysis**: Group by lead_source
- **Property Type Performance**: Group by property_type

### Step 4: Data Validation Rules

Set up these validation rules in Baserow:

#### 4.1 Users Table

- Email must be unique
- Phone number format validation
- Annual income must be positive
- Lead score between 0-100

#### 4.2 Properties Table

- Current price must be positive
- Square meters must be positive
- Bedrooms/bathrooms must be non-negative
- Building year between 1800-2025

#### 4.3 Leads Table

- Budget max must be >= budget min
- Email required if no user_id
- Lead score between 0-100

### Step 5: Automation Setup

#### 5.1 Auto-calculations

Set up these formulas in Baserow:

- `price_per_sqm` = current_price / square_meters
- `days_on_market` = today() - listing_date
- Lead score updates based on interactions

#### 5.2 Webhooks for n8n Integration

Configure webhooks in Baserow to trigger n8n workflows:

- New user registration → Lead scoring workflow
- New property view → Interaction tracking workflow
- Lead status change → Follow-up workflow
- New property listing → Email campaign workflow

### Next Steps

1. **Test Database Structure**: Create sample records in each table
2. **Verify Relationships**: Ensure all links between tables work correctly
3. **API Testing**: Test API endpoints with sample requests
4. **Webhook Configuration**: Set up webhooks for n8n integration
5. **Data Import**: Import any existing data from current systems

This database structure will serve as the foundation for all AI-powered features including lead scoring, property valuation, and marketing automation.
