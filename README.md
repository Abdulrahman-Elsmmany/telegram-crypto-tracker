# MemSheet Bot 🤖

A Telegram bot that automatically tracks cryptocurrency token prices and updates them to Google Sheets, focusing on Solana blockchain tokens. 📊

## Features ⭐

- 📈 Real-time token price tracking across blockchains
- 📑 Automated Google Sheets integration
- 💬 Telegram channel post monitoring
- 🕷️ Web scraping with Cloudflare CAPTCHA handling
- 📸 Screenshot capture of price data
- 🤖 Human-like behavior simulation
- 📝 Comprehensive logging

## Prerequisites 📋

- 🐍 Python 3.7+
- 🤖 Telegram Bot Token
- ☁️ Google Cloud Project with Sheets API enabled
- 🔑 Google Service Account credentials

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/Abdulrahman-Elsmmany/memsheet-bot.git
cd memsheet-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
My_Account=your_telegram_account_id
GOOGLE_SHEETS_SCOPES=https://www.googleapis.com/auth/spreadsheets
SPREADSHEET_ID=your_google_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_KEY=path/to/your/service-account-key.json
SHEET_NAME=General
```

## Usage 💡

1. Start the bot:
```bash
python3 main.py
```

2. Send messages to your Telegram channel:
```
🪙 Token Name ($SYMBOL)
🔗 BLOCKCHAIN
CA: CONTRACT_ADDRESS
```

The bot will:
- 🔍 Parse the message
- 💰 Fetch token price
- 📝 Update Google Sheet
- 📸 Capture price screenshot
- ✉️ Send confirmation messages

## Project Structure 📂

```
memsheet-bot/
├── main.py              # 🤖 Bot logic and Telegram handlers
├── helper.py            # 🔧 Helper functions
├── requirements.txt     # 📦 Dependencies
├── .env                # 🔐 Environment variables
└── logging.log         # 📝 Logs
```

## Environment Variables 🔐

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | 🤖 Telegram bot token |
| My_Account | 👤 Telegram account ID |
| GOOGLE_SHEETS_SCOPES | 📊 Google Sheets API scope |
| SPREADSHEET_ID | 📑 Google Sheet ID |
| GOOGLE_SERVICE_ACCOUNT_KEY | 🔑 Service account key path |
| SHEET_NAME | 📝 Sheet name (default: 'General') |

## Contributing 🤝

1. 🍴 Fork repository
2. 🌿 Create feature branch (`git checkout -b feature/Feature`)
3. ✍️ Commit changes (`git commit -m 'Add Feature'`)
4. ⬆️ Push branch (`git push origin feature/Feature`)
5. 🎯 Open Pull Request

## License 📜

MIT License

## Acknowledgments 🙏

- 🤖 aiogram for Telegram bot framework
- 🕷️ Playwright for web scraping
- 📊 Google Sheets API for spreadsheet integration

## Support 💬

Open an issue in the GitHub repository or contact maintainers.

---
Made with ❤️ by Abdulrahman