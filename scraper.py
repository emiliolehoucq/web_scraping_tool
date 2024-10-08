# Function to scrape websites
# Emilio Lehoucq
# This script uses code generated by ChatGPT and GitHub Copilot

# Importing libraries
from selenium import webdriver
from time import sleep

# Setting user agent
my_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Defining function
def get_selenium_response(url, headless=True):
    '''
    Function to scrape a website using Selenium.

    Inputs:
    - url: URL of the website to scrape.
    - headless: If True, run the browser in headless mode.

    Output:
    - response: HTML response of the website.

    Dependencies:
    - from selenium import webdriver
    - from time import sleep
    '''
    try:
        # Setting options https://www.selenium.dev/documentation/webdriver/drivers/options/
        options = webdriver.ChromeOptions()
        # Ask browser to ignore SSL errors
        # I think equivalent to options.add_argument('ignore-certificate-errors')
        options.accept_insecure_certs = True
        # Add user agent https://www.zenrows.com/blog/user-agent-web-scraping#best
        options.add_argument(f"--user-agent={my_user_agent}")
        # Add headless option
        if headless: options.add_argument('--headless')
        # Create driver
        driver = webdriver.Chrome(options = options)
        # Get URL
        driver.get(url)
        # Dealing with iframes for ICMS
        # Switch to iframe
        # https://www.selenium.dev/documentation/webdriver/interactions/frames/
        # This seems to behave differently if operating in headless mode or not!!!
        if 'icims.com' in url: driver.switch_to.frame('icims_content_iframe')
        # Since sleep() worked for Interfolio, I'll add some wait for every case. I don't care much about speed, so might as well...
        sleep(10)
        # Get response
        response = driver.page_source
        # Close driver
        driver.quit()
        # Return response
        return response
    # If it doesn't work, return None
    except Exception:
        return None

if __name__ == '__main__':
    print('Module with functions to scrape websites run successfully!')
