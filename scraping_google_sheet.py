# Script to get URLs from a Google Sheet and scrape those URLs
# Emilio Lehoucq

# Loading libraries
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd
from scraper import get_selenium_response
import os
import json
from datetime import datetime

# Get URLs from the Google Sheet

# Retrieve the environment variable with the credentials
credentials_info = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Parse credentials as JSON
credentials_dict = json.loads(credentials_info)

# Use the parsed dictionary to create the credentials object
creds = service_account.Credentials.from_service_account_info(credentials_dict)

# Build the service
service = build("sheets", "v4", credentials=creds)

# Get the values from the Google Sheet
result = service.spreadsheets().values().get(spreadsheetId="18HONqO0zv0SvM9_BCqa259Jvo12d6CXgmJQHhzGE2Jg", range="A1:A500").execute()
rows = result.get("values", [])

# Check if the URLs have already been scraped

# Open data.csv
df = pd.read_csv('data.csv')

# Get existing URLs
existing_urls = df['url'].tolist()

# Get current timestamp
ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Iterate over the URLs in the Google Sheet
for row in rows:
    # Check if the given URL is already in the CSV
    if row[0] not in existing_urls:
        # If it's not in the CSV, scrape it
        response = get_selenium_response(row[0])
        # If the response is not None, add it to the CSV
        if response is not None:
            df = pd.concat([df, pd.DataFrame({'ts': ts, 'url': row[0], 'html': response}, index=[len(df)])], ignore_index=True)
    # If it's already in the CSV, skip it
    else:
        continue

# Save the updated CSV
df.to_csv('data.csv', index=False)
