# MemSheet Bot 🤖

A Telegram bot that automatically tracks cryptocurrency token prices and updates them to Google Sheets. The bot monitors token prices across different blockchains (with a focus on Solana) and maintains a record in a specified Google Spreadsheet.

## Features ✨

- 🔄 Real-time price tracking for cryptocurrency tokens
- 📊 Automatic Google Sheets integration
- 💬 Telegram channel post monitoring
- 🔗 Web scraping capability for price data
- 📸 Screenshot capture of price data
- 🤖 Human-like behavior simulation to avoid blocking
- 📝 Comprehensive logging system

## Prerequisites 📋

Before running the bot, make sure you have:

- Python 3.7 or higher
- A Telegram Bot Token
- Google Cloud Project with Sheets API enabled
- Google Service Account credentials

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/memsheet-bot.git
cd memsheet-bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
My_Account=your_telegram_account_id
GOOGLE_SHEETS_SCOPES=https://www.googleapis.com/auth/spreadsheets
SPREADSHEET_ID=your_google_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_KEY=path/to/your/service-account-key.json
SHEET_NAME=General
SCREENSHOT_PATH=last.jpg
```

## Usage 💡

1. Start the bot:
```bash
python3 main.py
```

2. Send messages to your Telegram channel in the following format:
```
🪙 Token Name ($SYMBOL)
🔗 BLOCKCHAIN
CA: CONTRACT_ADDRESS
```

The bot will automatically:
- Parse the message
- Fetch the current token price
- Update the Google Sheet
- Take a screenshot of the price data
- Send confirmation messages to the specified account

## Project Structure 📁

```
memsheet-bot/
├── main.py              # Main bot logic and Telegram handlers
├── helper.py            # Helper functions for parsing, scraping, and sheets
├── requirements.txt     # Project dependencies
├── .env                # Environment variables
└── logging.log         # Log file
```

## Environment Variables 🔐

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Your Telegram bot token from BotFather |
| My_Account | Your Telegram account ID for notifications |
| GOOGLE_SHEETS_SCOPES | Google Sheets API scope |
| SPREADSHEET_ID | ID of your Google Sheet |
| GOOGLE_SERVICE_ACCOUNT_KEY | Path to your Google service account key file |
| SHEET_NAME | Name of the sheet to update (default: 'General') |
| SCREENSHOT_PATH | Path where screenshots will be saved |

## Error Handling 🔧

The bot includes comprehensive error handling for:
- Telegram API errors
- Web scraping failures
- Google Sheets API errors
- Message parsing issues

All errors are logged in `logging.log` for debugging purposes.

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- [aiogram](https://github.com/aiogram/aiogram) for the Telegram bot framework
- [Playwright](https://playwright.dev/) for web scraping capabilities
- [Google Sheets API](https://developers.google.com/sheets/api) for spreadsheet integration

## Support 📫

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by [Abdulrahman]
