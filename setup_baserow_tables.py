import os
import requests
import json

# Configuration from environment variables or direct input
BASEROW_API_URL = os.getenv("BASEROW_API_URL", "https://daytaa.intelligentb2b.com/api")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")

if not BASEROW_TOKEN:
    print("Error: BASEROW_TOKEN environment variable not set.")
    exit(1)

HEADERS = {
    "Authorization": f"Token {BASEROW_TOKEN}",
    "Content-Type": "application/json"
}

def create_table(database_id, table_name, fields):
    url = f"{BASEROW_API_URL}/database/tables/database/{database_id}/"
    data = {
        "name": table_name
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        table_id = response.json()["id"]
        print(f"Table \'{table_name}\' created with ID: {table_id}")
        for field in fields:
            create_field(table_id, field)
        return table_id
    elif response.status_code == 400 and "table with this name already exists" in response.text:
        print(f"Table \'{table_name}\' already exists. Skipping creation.")
        # Attempt to get existing table ID if it exists
        tables_url = f"{BASEROW_API_URL}/database/tables/database/{database_id}/"
        tables_response = requests.get(tables_url, headers=HEADERS)
        if tables_response.status_code == 200:
            for table in tables_response.json():
                if table["name"] == table_name:
                    table_id = table["id"]
                    print(f"Found existing table \'{table_name}\' with ID: {table_id}")
                    for field in fields:
                        create_field(table_id, field)
                    return table_id
        return None
    else:
        print(f"Error creating table \'{table_name}\': {response.status_code} - {response.text}")
        return None

def create_field(table_id, field_data):
    url = f"{BASEROW_API_URL}/database/fields/table/{table_id}/"
    response = requests.post(url, headers=HEADERS, json=field_data)
    if response.status_code == 200:
        print(f"  Field \'{field_data['name']}\' created.")
    elif response.status_code == 400 and "field with this name already exists" in response.text:
        print(f"  Field \'{field_data['name']}\' already exists. Skipping creation.")
    else:
        print(f"  Error creating field \'{field_data['name']}\': {response.status_code} - {response.text}")

def get_database_id(application_id, database_name):
    url = f"{BASEROW_API_URL}/applications/{application_id}/databases/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        for db in response.json():
            if db["name"] == database_name:
                return db["id"]
    print(f"Error: Database \'{database_name}\' not found in application {application_id}.")
    return None

# --- Define your Baserow Application ID and Database Name here ---
# You need to get these from your Baserow instance
# Example: If your Baserow URL is daytaa.intelligentb2b.com/dashboard/applications/1/database/2/
# then application_id might be 1, and you'd find the database name in the UI.
# You might need to manually create an application (workspace) and a database within it first.
APPLICATION_ID = os.getenv("BASEROW_APPLICATION_ID") # e.g., "1"
DATABASE_NAME = os.getenv("BASEROW_DATABASE_NAME", "Real Estate AI System") # e.g., "My Real Estate Database"

if not APPLICATION_ID:
    print("Error: BASEROW_APPLICATION_ID environment variable not set.")
    exit(1)

# Get the database ID
database_id = get_database_id(APPLICATION_ID, DATABASE_NAME)

if database_id:
    # --- Table and Field Definitions (based on baserow_setup_guide.md) ---
    tables_to_create = [
        {
            "name": "Users",
            "fields": [
                {"name": "Name", "type": "text"},
                {"name": "Email", "type": "email"},
                {"name": "Phone", "type": "text"},
                {"name": "Location", "type": "text"},
                {"name": "Property Type", "type": "single_select", "select_options": [{"value": "Apartment"}, {"value": "House"}, {"value": "Villa"}, {"value": "Commercial"}]},
                {"name": "Min Price", "type": "number"},
                {"name": "Max Price", "type": "number"},
                {"name": "Lead Score", "type": "number"},
                {"name": "Lead Stage", "type": "single_select", "select_options": [{"value": "New"}, {"value": "Qualified"}, {"value": "Contacted"}, {"value": "Nurturing"}, {"value": "Converted"}, {"value": "Lost"}]},
                {"name": "Last Interaction", "type": "date"},
                {"name": "Source", "type": "text"}
            ]
        },
        {
            "name": "Properties",
            "fields": [
                {"name": "Title", "type": "text"},
                {"name": "Description", "type": "long_text"},
                {"name": "Price", "type": "number"},
                {"name": "Size (sqm)", "type": "number"},
                {"name": "Rooms", "type": "number"},
                {"name": "Bathrooms", "type": "number"},
                {"name": "City", "type": "text"},
                {"name": "Address", "type": "text"},
                {"name": "Latitude", "type": "number"},
                {"name": "Longitude", "type": "number"},
                {"name": "Features", "type": "long_text"},
                {"name": "Portal Source", "type": "text"},
                {"name": "Portal ID", "type": "text"},
                {"name": "Contact Agency", "type": "text"},
                {"name": "Contact Agent", "type": "text"},
                {"name": "Contact Phone", "type": "text"},
                {"name": "Contact Email", "type": "email"},
                {"name": "Published Date", "type": "date"},
                {"name": "Collected At", "type": "date"}
            ]
        },
        {
            "name": "Leads",
            "fields": [
                {"name": "Lead Name", "type": "text"},
                {"name": "Lead Email", "type": "email"},
                {"name": "Lead Phone", "type": "text"},
                {"name": "Lead Source", "type": "text"},
                {"name": "Qualification Status", "type": "single_select", "select_options": [{"value": "New"}, {"value": "Qualified"}, {"value": "Unqualified"}]},
                {"name": "Lead Score", "type": "number"},
                {"name": "Property Interest", "type": "long_text"},
                {"name": "Budget", "type": "number"},
                {"name": "Location Preference", "type": "text"},
                {"name": "Assigned Agent", "type": "text"},
                {"name": "Created At", "type": "date"}
            ]
        },
        {
            "name": "Interactions",
            "fields": [
                {"name": "User", "type": "link_row", "link_row_table_id": "", "link_row_table_name": "Users"},
                {"name": "Type", "type": "single_select", "select_options": [{"value": "Website Visit"}, {"value": "Chatbot"}, {"value": "Email"}, {"value": "Phone Call"}, {"value": "Viewing"}]},
                {"name": "Timestamp", "type": "date"},
                {"name": "Details", "type": "long_text"},
                {"name": "Property", "type": "link_row", "link_row_table_id": "", "link_row_table_name": "Properties"},
                {"name": "Duration (min)", "type": "number"},
                {"name": "Sentiment", "type": "single_select", "select_options": [{"value": "Positive"}, {"value": "Neutral"}, {"value": "Negative"}]},
                {"name": "Outcome", "type": "text"}
            ]
        },
        {
            "name": "Deals",
            "fields": [
                {"name": "Deal Name", "type": "text"},
                {"name": "Lead", "type": "link_row", "link_row_table_id": "", "link_row_table_name": "Leads"},
                {"name": "Property", "type": "link_row", "link_row_table_id": "", "link_row_table_name": "Properties"},
                {"name": "Value", "type": "number"},
                {"name": "Stage", "type": "single_select", "select_options": [{"value": "Prospecting"}, {"value": "Qualification"}, {"value": "Proposal"}, {"value": "Negotiation"}, {"value": "Closed Won"}, {"value": "Closed Lost"}]},
                {"name": "Close Date", "type": "date"},
                {"name": "Probability", "type": "number"},
                {"name": "Assigned Agent", "type": "text"}
            ]
        },
        {
            "name": "Market Data",
            "fields": [
                {"name": "Location", "type": "text"},
                {"name": "Average Price", "type": "number"},
                {"name": "Price per Sqm", "type": "number"},
                {"name": "Total Listings", "type": "number"},
                {"name": "New Listings", "type": "number"},
                {"name": "Sold Properties", "type": "number"},
                {"name": "Days on Market", "type": "number"},
                {"name": "Price Trend", "type": "single_select", "select_options": [{"value": "Increasing"}, {"value": "Stable"}, {"value": "Decreasing"}]},
                {"name": "Data Source", "type": "text"},
                {"name": "Collected At", "type": "date"}
            ]
        },
        {
            "name": "Email Campaigns",
            "fields": [
                {"name": "Campaign Name", "type": "text"},
                {"name": "Subject Line", "type": "text"},
                {"name": "Audience Segment", "type": "text"},
                {"name": "Send Date", "type": "date"},
                {"name": "Open Rate", "type": "number"},
                {"name": "Click Rate", "type": "number"},
                {"name": "Conversion Rate", "type": "number"},
                {"name": "Status", "type": "single_select", "select_options": [{"value": "Draft"}, {"value": "Scheduled"}, {"value": "Sent"}, {"value": "Archived"}]},
                {"name": "Trigger", "type": "text"}
            ]
        },
        {
            "name": "Analytics",
            "fields": [
                {"name": "Metric Name", "type": "text"},
                {"name": "Value", "type": "number"},
                {"name": "Period", "type": "text"},
                {"name": "Timestamp", "type": "date"},
                {"name": "Source", "type": "text"},
                {"name": "Trend", "type": "single_select", "select_options": [{"value": "Up"}, {"value": "Stable"}, {"value": "Down"}]},
                {"name": "Forecast", "type": "number"}
            ]
        }
    ]

    # Create tables and fields
    created_table_ids = {}
    for table_data in tables_to_create:
        table_id = create_table(database_id, table_data["name"], table_data["fields"])
        if table_id:
            created_table_ids[table_data["name"]] = table_id

    # Update link_row fields with correct table IDs
    print("\nUpdating link_row fields...")
    for table_data in tables_to_create:
        table_name = table_data["name"]
        table_id = created_table_ids.get(table_name)
        if not table_id:
            continue

        for field_data in table_data["fields"]:
            if field_data["type"] == "link_row":
                linked_table_name = field_data["link_row_table_name"]
                linked_table_id = created_table_ids.get(linked_table_name)
                if linked_table_id:
                    # Baserow requires the linked_table_id to be set when creating the field
                    # If the field already exists, we can't update its type or linked table easily via API
                    # This part is mostly for demonstrating the structure. In a real scenario,
                    # you'd ensure linked tables are created before fields that link to them.
                    print(f"  Link field \'{field_data['name']}\' in \'{table_name}\' links to \'{linked_table_name}\' (ID: {linked_table_id})")
                else:
                    print(f"  Warning: Linked table \'{linked_table_name}\' not found for field \'{field_data['name']}\' in \'{table_name}\'")

    print("\nBaserow setup script finished.")
    print("Please ensure you have set BASEROW_TOKEN, BASEROW_APPLICATION_ID, and BASEROW_DATABASE_NAME environment variables.")
    print("You may need to manually adjust link_row fields in Baserow if they were not correctly created due to dependency order.")
else:
    print("Baserow setup cannot proceed without a valid database ID.")


