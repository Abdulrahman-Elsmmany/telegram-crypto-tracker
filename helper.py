#!/usr/bin/env python3
import re
import os

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import logging
import asyncio
import random
import time
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --------------------
# Logger Setup
# --------------------
logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Load configuration from environment variables
SCOPES = os.getenv('GOOGLE_SHEETS_SCOPES', "https://www.googleapis.com/auth/spreadsheets").split(',')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
KEYFILE_PATH = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
SHEET_NAME = os.getenv('SHEET_NAME', 'General')


def parse_telegram_message(message):
    # Initialize a dictionary to store extracted information
    info = {}
    
    # Extract coin name and symbol
    coin_match = re.search(r'🪙 (.+?) \((\$\w+)\)', message)
    if coin_match:
        info['coin_name'] = coin_match.group(1)
        info['coin_symbol'] = coin_match.group(2)
    
    # Extract blockchain
    chain_match = re.search(r'🔗 (\w+)', message)
    if chain_match:
        info['blockchain'] = chain_match.group(1)
    
    # Extract contract address
    address_match = re.search(r'CA: (\w+)', message)
    if address_match:
        info['contract_address'] = address_match.group(1)
    
    return info

# Generate random count of user agents and return them in a list : user_agents
def generat_user_agents(count):
    ua = UserAgent()
    user_agents = [ua.random for _ in range(count)]
    return user_agents


async def web_scraping(link, user_agents):
    def process_subscript_number(price_text):
        """
        Process a number with subscript digits by replacing them with the appropriate
        number of zeros after the decimal point.
        Example: 0.0₅8372 becomes 0.0000008372
        """
        subscript_map = {
            '₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
            '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9
        }
        
        # Find the decimal point position
        decimal_pos = price_text.find('.')
        if decimal_pos == -1:
            return price_text
        
        # Split the number into parts before and after decimal
        before_decimal = price_text[:decimal_pos]
        after_decimal = price_text[decimal_pos + 1:]
        
        # Process the part after decimal
        result_after_decimal = ""
        i = 0
        while i < len(after_decimal):
            if after_decimal[i] in subscript_map:
                # Add the specified number of zeros
                zeros_count = subscript_map[after_decimal[i]]
                result_after_decimal += '0' * zeros_count
                # Add the rest of the number after the subscript
                result_after_decimal += after_decimal[i + 1:]
                break
            else:
                result_after_decimal += after_decimal[i]
                i += 1
        
        # Combine the parts
        return f"{before_decimal}.{result_after_decimal}"
    
    price = None  # Initialize price variable
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(user_agents))
        page = await context.new_page()

        try:
            # Emulate human-like behavior
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(link)
            await asyncio.sleep(random.uniform(2, 5))

            # Handle pop-up
            try:
                got_it_button = page.locator('text="Got it"')
                await got_it_button.click(timeout=5000)
                logging.info("Pop-up appeared and 'Got it' button was clicked.")
            except Exception as e:
                logging.info(f"Pop-up handling: {str(e)}")

            # Wait for price element with proper error handling
            try:
                parent_element = await page.wait_for_selector('.css-1lqrh8c', timeout=10000)
                if parent_element:
                    price_element = await parent_element.query_selector('div:first-child')
                    
                    if price_element:
                        price_text = await price_element.inner_text()
                        logging.info(f"Raw price text: {price_text}")
                        
                        # Remove the dollar sign and process subscript numbers
                        price_text = price_text.replace('$', '')
                        processed_price = process_subscript_number(price_text)
                        
                        # Store the exact string value without float conversion
                        price = processed_price
                        logging.info(f"Successfully extracted price: {price}")
                    else:
                        logging.error("Price element not found within parent")
                else:
                    logging.error("Parent element not found")
            except Exception as e:
                logging.error(f"Error extracting price: {e}")
                price = None

            # Take screenshot
            screenshot_path = os.getenv('SCREENSHOT_PATH', 'last.jpg')
            try:
                await page.screenshot(path=screenshot_path, full_page=True)
                logging.info(f"Screenshot saved successfully at {screenshot_path}")
            except Exception as e:
                logging.error(f"Error saving screenshot: {e}")

        except Exception as e:
            logging.error(f"General error during web scraping: {e}")
        finally:
            await browser.close()

    return price

def send_to_GoogleSheet(network_chain, token_address, token_name, pair_name, price, keyfile_path=KEYFILE_PATH, sheet_name=SHEET_NAME):
    try:
        creds = service_account.Credentials.from_service_account_file(keyfile_path, scopes=SCOPES)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

    service = build("sheets", "v4", credentials=creds)

    try:
        # Get all values from columns A to I
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A:I'
        ).execute()
        values = result.get('values', [])

        # Find the first empty row
        next_empty_row = len(values) + 1

        # Prepare the range for the new data
        SAMPLE_RANGE_NAME = f'{sheet_name}!A{next_empty_row}:I{next_empty_row}'

        # Format the price with dollar sign while maintaining full precision
        if price is not None:
            formatted_price = f"${price}"
        else:
            formatted_price = None

        # Prepare the data to be inserted
        values = [[network_chain, token_address, token_name, pair_name, '', '', '', '', formatted_price]]
        body = {"values": values}

        # Append the new data
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME,
            valueInputOption="USER_ENTERED",  # Changed from RAW to USER_ENTERED
            body=body,
        ).execute()

        updated_cells = result['updates']['updatedRange'].split('!')[1]
        return updated_cells

    except HttpError as err:
        print(f"API Error: {err}")
        return None