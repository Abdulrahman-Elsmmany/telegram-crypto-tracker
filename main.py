#!/usr/bin/env python3
# --------------------
# Imports
# --------------------
import asyncio
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InputFile, ReplyKeyboardRemove, ForceReply
from aiogram.utils.markdown import hbold, hitalic, hcode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError, TelegramServerError, TelegramRetryAfter
from aiogram.types import FSInputFile


from helper import parse_telegram_message, generat_user_agents, web_scraping, send_to_GoogleSheet

# --------------------
# Logger Setup
# --------------------
logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --------------------
# Load environment variables
# --------------------
load_dotenv()

# --------------------
# Bot Initialization
# --------------------
session = AiohttpSession()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
My_Account = os.getenv('My_Account')
default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(TOKEN, session=session, default=default_properties)
router = Router()

current_time = datetime.now().strftime("  %Y-%m-%d %I:%M:%S %p ")

#---------------------
# Commands
#---------------------
@router.message(CommandStart()) # Handler for /start command
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.reply("Hi! I am Mems Sheet Bot. I can help you to track the price of your favorite token on different blockchains. Just send me the contract address of your token and I will fetch the price of the token from the blockchain and update it in your Google Sheet. To start, send me the contract address of your token.")

#---------------------
# Channel Post Handler
#---------------------
@router.channel_post()
async def handle_channel_post(message: types.Message):
    text = message.text
    message_type = "channel"

    try:
        data = parse_telegram_message(text)
    except Exception as e:
        await bot.send_message(chat_id=My_Account, text=f'parse_telegram_message Failed for "\n\n" {text}')
        return
    
    coin_name, coin_symbol, blockchain, contract_address = (data.get(key, None) for key in ['coin_name', 'coin_symbol', 'blockchain', 'contract_address'])
    
    logging.info('Working on sending data')
    logging.info(data)
    logging.info(f"The address is: {contract_address}")
    logging.info(f"The Chain name is: {blockchain}")

    pair = f"({coin_symbol}/WSOL)"
    link = f"https://gmgn.ai/sol/token/{contract_address}"
    user_agents = generat_user_agents(10)
    
    try:
        price = await web_scraping(link, user_agents)
    except Exception as e:
        logging.error(f"Error during web scraping: {e}")
        price = None

    updated_places = send_to_GoogleSheet(blockchain, contract_address, coin_name, pair, price)

    try:
        statement = ("Working on sending data\n"
                     f"The name is: {coin_name}\n\n"
                     f"The address is: {contract_address}\n\n"
                     f"The Chain name is: {blockchain}\n\n")
        
        # Handle price formatting properly
        if price is not None:
            try:
                # Convert price to float only if it's not already a float
                price_float = float(price) if isinstance(price, str) else price
                statement += f"The price is: ${price_float:.8f}\n\n"
            except ValueError:
                # If conversion fails, just display the raw price
                statement += f"The price is: ${price}\n\n"
        else:
            statement += "Unable to fetch price\n\n"
            
        statement += f"Data updated in Google Sheet at: {updated_places}"
        await bot.send_message(chat_id=My_Account, text=statement)
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        # Fallback message in case of formatting error
        await bot.send_message(
            chat_id=My_Account, 
            text=f"Data processed but encountered error in message formatting: {str(e)}\n"
                 f"Raw price value: {price}"
        )

    try:
        photo = FSInputFile("last.jpg")
        await bot.send_photo(chat_id=My_Account, photo=photo)
    except Exception as e:
        logging.error(f"Error sending photo: {e}")

#---------------------
# Error Handler
#---------------------
@router.errors()
async def error_handler(update: types.Update, exception: Exception):
    try:
        if update.message and update.message.chat:
            logging.error(f'Update {update} caused error {exception} in user chat {update.message.chat.id}')
        elif update.channel_post:
            logging.error(f'Update {update} caused error {exception} in channel chat {update.channel_post.chat.id}')
        else:
            logging.error(f'Update {update} caused error {exception}')
    except Exception as e:
        logging.error(f'Error handling update {update}: {e}')
    return True

# --------------------
# Main Function
# --------------------
async def main() -> None:
    # Initialize Dispatcher
    dp = Dispatcher()

    # Include the router in the dispatcher
    dp.include_router(router)

    # Start polling
    await dp.start_polling(bot)

# --------------------
# Entry Point
# --------------------
if __name__ == "__main__":
    asyncio.run(main())