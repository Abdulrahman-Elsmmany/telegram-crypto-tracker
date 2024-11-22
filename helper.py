#!/usr/bin/env python3
import re
import os
import logging
import random
import time
import asyncio
from datetime import datetime

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from seleniumbase import Driver
from xvfbwrapper import Xvfb
from pyvirtualdisplay import Display

from fake_useragent import UserAgent
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
    """
    Parse Telegram messages containing token information with improved pattern matching.
    Returns a dictionary with extracted information or None if parsing fails.
    """
    logging.info(f"Attempting to parse message:\n{message}")
    
    info = {}
    
    try:
        coin_match = re.search(r'🪙\s*([^(]+?)\s*\((\$\w+)\s*\)', message)
        if coin_match:
            info['coin_name'] = coin_match.group(1).strip()
            info['coin_symbol'] = coin_match.group(2).strip()
            logging.info(f"Found coin: {info['coin_name']} ({info['coin_symbol']})")
        else:
            logging.warning("Could not extract coin name and symbol")
            return None
        
        chain_match = re.search(r'🔗\s*(\w+)', message)
        if chain_match:
            info['blockchain'] = chain_match.group(1).strip()
            logging.info(f"Found blockchain: {info['blockchain']}")
        else:
            logging.warning("Could not extract blockchain")
            return None
        
        address_match = re.search(r'(?:CA:|Contract:)\s*([A-Za-z0-9]+)', message)
        if address_match:
            info['contract_address'] = address_match.group(1).strip()
            logging.info(f"Found contract address: {info['contract_address']}")
        else:
            logging.warning("Could not extract contract address")
            return None
        
        required_fields = ['coin_name', 'coin_symbol', 'blockchain', 'contract_address']
        if all(key in info for key in required_fields):
            logging.info(f"Successfully extracted all required fields: {info}")
            return info
        else:
            missing_fields = [field for field in required_fields if field not in info]
            logging.warning(f"Missing required fields: {missing_fields}")
            return None
            
    except Exception as e:
        logging.error(f"Error parsing message: {str(e)}")
        return None

def generate_user_agents(count):
    """Generate random user agents."""
    ua = UserAgent()
    return [ua.random for _ in range(count)]

def process_subscript_number(price_text):
    """
    Process a number with subscript digits by replacing them with the appropriate
    number of zeros after the decimal point.
    """
    subscript_map = {
        '₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
        '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9
    }
    
    decimal_pos = price_text.find('.')
    if decimal_pos == -1:
        return price_text
    
    before_decimal = price_text[:decimal_pos]
    after_decimal = price_text[decimal_pos + 1:]
    
    result_after_decimal = ""
    i = 0
    while i < len(after_decimal):
        if after_decimal[i] in subscript_map:
            zeros_count = subscript_map[after_decimal[i]]
            result_after_decimal += '0' * zeros_count
            result_after_decimal += after_decimal[i + 1:]
            break
        else:
            result_after_decimal += after_decimal[i]
            i += 1
    
    return f"{before_decimal}.{result_after_decimal}"

async def web_scraping(link, user_agents):
    """Perform web scraping using SeleniumBase's UC Mode with improved captcha handling."""
    price = None
    driver = None
    display = None
    
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()

        driver = Driver(uc=True, agent=user_agents)
        if not driver:
            raise Exception("Failed to initialize driver")
            
        # Use UC Mode's special open method with reconnect
        driver.uc_open_with_reconnect(link, reconnect_time=4)

        # Handle captcha using SeleniumBase's UC Mode method
        driver.uc_gui_click_captcha()
        logging.info("Waiting for captcha to be solved...")

        await asyncio.sleep(random.uniform(2, 4))
        
        # Get price with improved error handling
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                parent_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'css-1lqrh8c'))
                )
                
                if parent_element:
                    price_element = parent_element.find_element(By.CSS_SELECTOR, 'div:first-child')
                    if price_element:
                        price_text = price_element.text
                        price_text = price_text.replace('$', '')
                        price = process_subscript_number(price_text)
                        if price:
                            logging.info(f"Extracted price: {price}")
                            return price
                            
                raise Exception("Price element not found")
                
            except Exception as e:
                logging.warning(f"Retry {retry_count + 1}/{max_retries} failed: {e}")
                retry_count += 1
                await asyncio.sleep(random.uniform(2, 4))
                
        raise Exception(f"Failed to extract price after {max_retries} retries")
            
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        raise
    finally:
        if driver:
            try:
                driver.save_screenshot("last.jpg")
                driver.quit()
            except Exception as e:
                logging.error(f"Cleanup error: {e}")
        if display:
            display.stop()
    
    return None

def send_to_GoogleSheet(network_chain, token_address, token_name, pair_name, price, 
                       keyfile_path=KEYFILE_PATH, sheet_name=SHEET_NAME):
    """Send scraped data to Google Sheets."""
    try:
        creds = service_account.Credentials.from_service_account_file(keyfile_path, scopes=SCOPES)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

    service = build("sheets", "v4", credentials=creds)

    try:
        # Get all values from columns A to T
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A:T'
        ).execute()
        values = result.get('values', [])

        # Find first empty row
        next_empty_row = 1
        for i, row in enumerate(values, start=1):
            if not row or not row[0]:
                next_empty_row = i
                break
        
        if next_empty_row == 1 and values:
            next_empty_row = len(values) + 1

        logging.info(f"Adding new data at row {next_empty_row}")
        
        current_date = datetime.now().strftime("%m/%d/%Y")
        SAMPLE_RANGE_NAME = f'{sheet_name}!A{next_empty_row}:T{next_empty_row}'
        
        formatted_price = f"${price}" if price is not None else None
        empty_columns = [''] * 10
        
        values = [[
            network_chain,
            token_address,
            token_name,
            pair_name,
            '', '', '', '',
            formatted_price,
            *empty_columns,
            current_date
        ]]
        
        body = {"values": values}

        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return f'{sheet_name}!A{next_empty_row}:T{next_empty_row}'

    except HttpError as err:
        logging.error(f"API Error: {err}")
        return None