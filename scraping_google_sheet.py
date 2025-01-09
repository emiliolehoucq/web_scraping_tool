# Script to get URLs from a Google Sheet and scrape those URLs
# Emilio Lehoucq

# TODO: this is a copy paste of several scripts. standardize (e.g., be more consistent with re-tries and error handling)

####################################### Loading libraries #######################################
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from scraper import get_selenium_response
import os
import json
from datetime import datetime
import logging
from time import sleep
from text_extractor import extract_text

##################################### Setting parameters #####################################

# Timestamp
TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Number of retries
RETRIES = 5

##################################### Configure the logging settings #####################################
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Logging configured. Current timestamp: {TS}")

##################################### Define functions for this script #####################################
def upload_file(element_id, file_suffix, content, folder_id, service, logger):
    """
    Function to upload a file to Google Drive.

    Inputs:
    - element_id: ID of the job post
    - file_suffix: suffix of the file name
    - content: content of the file
    - folder_id: ID of the folder in Google Drive
    - service: service for Google Drive
    - logger: logger

    Outputs: None

    Dependencies: from googleapiclient.http import MediaFileUpload, os
    """
    
    logger.info(f"Inside upload_file: uploading ID {element_id} to Google Drive.")

    try:
        # Prepare the file name
        file_name = f"{element_id}_{file_suffix}.txt"
        logger.info(f"Inside upload_file: prepared the name of the file for the {file_suffix}")

        # Write the content to a temporary file
        with open(file_name, 'w') as temp_file:
            temp_file.write(content)
        logger.info(f"Inside upload_file: wrote the {file_suffix} string to a temporary file")

        # Prepare the file metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        logger.info(f"Inside upload_file: prepared the file metadata for the {file_suffix}")

        # Prepare the file media
        media = MediaFileUpload(file_name, mimetype='text/plain')
        logger.info(f"Inside upload_file: prepared the file media for the {file_suffix}")

        # Upload the file to the Drive folder
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Inside upload_file: uploaded the file to the shared folder for the {file_suffix}")

        # Remove the temporary file after uploading
        os.remove(file_name)
        logger.info(f"Inside upload_file: removed the temporary file after uploading for the {file_suffix}")
    
    except Exception as e:
        logger.info(f"Inside upload_file: something went wrong. Error: {e}")

    return None

logger.info("Functions defined.")

####################################### Get URLs from Google Sheet #######################################

# Retrieve the environment variable with the credentials
credentials_info = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
logger.info("Got credentials.")

# Parse credentials as JSON
credentials_dict = json.loads(credentials_info)
logger.info("Parsed credentials JSON.")

# Use the parsed dictionary to create the credentials object
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
logger.info("Created credentials object.")

# Build the service
service = build("sheets", "v4", credentials=credentials)
logger.info("Built service.")

# Get the values from the Google Sheet
result = service.spreadsheets().values().get(spreadsheetId="18HONqO0zv0SvM9_BCqa259Jvo12d6CXgmJQHhzGE2Jg", range="A1:C1000000").execute()
rows = result.get("values", []) # Example output: [['url', 'id', 'ts'], ['url', 'id', 'ts'], ['url']] 
logger.info("Got values from Google Sheets.")

####################################### Get the URLs that I haven't scraped #######################################

# Define variable for number of postings already scraped
num_postings_scraped = 0
logger.info("Defined variable for number of postings already scraped.")

# Define variable for missing URLs
missing_urls = []
logger.info("Defined variable for missing URLS.")

logger.info("About to iterate over rows of the Google spreadsheet.")
# Iterate over rows of the Google spreadsheet
for row in rows:
    # If there's url, id, and ts
    if len(row) == 3:
        num_postings_scraped += 1
        logger.info(f"Updated number of postings already scraped: {num_postings_scraped}.")
        
    # If there's only the URL -- not id or ts
    if len(row) == 1:
        # Append to list of missing URLs
        missing_urls.append(row[0])
        logger.info(f"Appended url to missing_urls: {row[0]}.")

####################################### Scrape new URLs #######################################

# Define variable for new data
new_data = []
logger.info("Defined variable for new data.")

# Define id
id = num_postings_scraped + 1
logger.info(f"Defined id: {id}.")

logger.info("About to iterate over missing urls.")
# Iterate over new/missing URLs
for missing_url in missing_urls:

    # Define variable to store data for given posting
    new_posting = []
    logger.info("Defined variable for new posting.")
    
    # Append id to new data
    new_posting.append(id)
    logger.info(f"Appended id: {id}.")
    # Increment id by 1
    id += 1
    logger.info(f"Incremented id by 1: {id}.")
    
    # Get current timestamp
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Append ts to new data
    new_posting.append(ts)
    logger.info(f"Got and appended current ts: {ts}.")
    
    # Scrape URL
    source_code = get_selenium_response(missing_url)
    # Append source code to new data
    new_posting.append(source_code)
    logger.info("Got and appended source code.")
    
    # Get text
    text = extract_text(source_code)
    # Append text to new data
    new_posting.append(text)
    logger.info("Got and appended text.")

    # Append given posting to new data
    new_data.append(new_posting)
    logger.info("Appended new_posting to new_data.")

####################################### WRITE NEW DATA TO GOOGLE SHEETS #######################################

# Data for the postings

# Spreadsheet id
# https://docs.google.com/spreadsheets/d/18HONqO0zv0SvM9_BCqa259Jvo12d6CXgmJQHhzGE2Jg/edit?gid=0#gid=0
spreadsheet_id = "18HONqO0zv0SvM9_BCqa259Jvo12d6CXgmJQHhzGE2Jg"

# Retry block in case of failure
logger.info("Re-try block for data for postings (Google Sheets) about to start.")

# Iterate over the number of retries
for attempt in range(RETRIES):

    try:
        logger.info(f"Re-try block for data for postings (Google Sheets). Attempt {attempt + 1}.")

        # Range to write the data
        range_sheet="B"+str(num_postings_scraped+1)+":C10000000"
        logger.info(f"Prepared range to write the data for the postings, starting at row str(num_postings_scraped+1): {str(num_postings_scraped+1)}.")

        # Body of the request
        # id, ts
        body={"values": [element[0:2] for element in new_data]} 
        logger.info(f"Prepared body of the request for the postings: {element[0:2]}.")

        # Execute the request
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_sheet,
            valueInputOption="USER_ENTERED",
            body=body
            ).execute()
        logger.info("Wrote new data to Google Sheets for the postings.")

        # Break the loop if successful
        logger.info("Re-try block for data for postings successful. About to break the loop.")
        break
    
    except Exception as e:
        logger.info(f"Re-try block for data for postings. Attempt {attempt + 1} failed. Error: {e}")

        if attempt < RETRIES - 1:
            logger.info("Re-try block for data for postings. Sleeping before retry.")
            sleep(5)
        else:
            logger.info("Re-try block for data for postings. All retries exhausted.")
            raise

logger.info("Wrote new data to Google Sheets for the postings.")

####################################### WRITE NEW DATA TO GOOGLE DRIVE #######################################

# Note: if there's already a file with the same name in the folder, this code will add another with the same name

# Data for the postings

# Folder ID
# https://drive.google.com/drive/u/3/folders/1sOO4FZa4T1FhDcdVkgMu1E-cPQgSqe6p
folder_id = "1sOO4FZa4T1FhDcdVkgMu1E-cPQgSqe6p" 

logger.info("About to send data to Google Drive.")
# Retry block in case of failure
for attempt in range(RETRIES):

    try:
        logger.info(f"Re-try block for data for the postings (Google Drive). Attempt {attempt + 1}.")

        # Authenticate using the service account (for Google Drive, not Sheets)
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Created service for Google Drive.")
                    
        # Iterate over each of the new data
        for element in new_data:
            logger.info("Iterating over the new data.")

            # Get the source code of the job post
            source_code = element[-2]
            logger.info("Got the source code of the post.")
            # Upload the source code to Google Drive
            upload_file(element[0], "source_code", source_code, folder_id, service, logger)
            
            # Get the text of the job post
            text = element[-1]
            logger.info("Got the text of the post.")
            # Upload the text to Google Drive
            upload_file(element[0], "text", text, folder_id, service, logger)
            
        logger.info("Wrote new data for the postings (if available) to Google Drive.")

        # Break the loop if successful
        logger.info("Re-try block for data for the postings successful. About to break the loop.")
        break

    except Exception as e:
        logger.info(f"Re-try block for data for the postings. Attempt {attempt + 1} failed. Error: {e}.")

        if attempt < RETRIES - 1:
            logger.info("Re-try block for data for the postings. Sleeping before retry.")
            sleep(5)
        else:
            logger.info("Re-try block for data for the postings. All retries exhausted.")
            raise

logger.info("Script run until the end.")
