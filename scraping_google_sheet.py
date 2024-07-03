# Script to get URLs from a Google Sheet and scrape those URLs
# Emilio Lehoucq

# Loading libraries
import google.auth
from googleapiclient.discovery import build
import pandas as pd
from scrapers import get_selenium_response

# Get URLs from the Google Sheet

# In the local machine, run: export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
# In GitHub, add to secrets
# Get the credentials from the environment variable
creds, _ = google.auth.default()

# Build the service
service = build("sheets", "v4", credentials=creds)

# Get the values from the Google Sheet
result = service.spreadsheets().values().get(spreadsheetId="18HONqO0zv0SvM9_BCqa259Jvo12d6CXgmJQHhzGE2Jg", range="A1:A500").execute()
rows = result.get("values", [])
# print(rows)

# Check if the URLs have already been scraped

# Open data.csv
df = pd.read_csv('data.csv')

# Get existing URLs
existing_urls = df['url'].tolist()
# print(existing_urls)

# Iterate over the URLs in the Google Sheet
for row in rows:
    # Check if the given URL is already in the CSV
    if row[0] not in existing_urls:
        # If it's not in the CSV, scrape it
        # print(f"Scraping {row[0]}")
        response = get_selenium_response(row[0])
        # If the response is not None, add it to the CSV
        if response is not None:
            # print(f"Scraped {row[0]} successfully")
            # print(response)
            df = pd.concat([df, pd.DataFrame({'url': row[0], 'html': response}, index=[len(df)])], ignore_index=True)
    # If it's already in the CSV, skip it
    else:
        # print(f"Skipping {row[0]} as it's already in the CSV")
        continue

# Save the updated CSV
df.to_csv('data.csv', index=False)