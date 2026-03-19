# Signal Engine - Automated Trading Alerts System

An end-to-end automated stock signal engine that scans a universe of stocks, generates trading signals using technical indicators, tracks trade performance, updates Google Sheets, and sends alerts via Telegram.

---

## Features

- Automated signal generation based on indicator logic
- Re-entry control using a 90-day cooldown per stock
- Trade tracking with:
  - Hard Stop Loss
  - Trailing Stop Loss
  - Maximum holding period
- Forward return tracking (5D, 20D, 3M, 6M)
- Google Sheets integration for reporting
- Telegram alerts for:
  - Entry signals
  - Exit signals
- Fully automated execution using AWS scheduling

---

## Strategy Logic

### Entry
- Signal is generated using indicator conditions from the signal generator module
- A stock is eligible only if no signal has been generated in the last 90 days

### Exit Conditions
- Hard Stop Loss: 10 percent downside from entry
- Trailing Stop Loss: 20 percent from peak after 20 trading days
- Maximum Hold: 126 days from entry

---

## Project Structure

signal-engine/

data/
    price_loader.py

indicators/
    indicators.py

signals/
    signal_generator.py

sheets/
    sheet_manager.py

storage/
    universe.csv
    signals_log.csv

telegram_utils.py
main.py
requirements.txt

---

## Setup

### Clone Repository

git clone https://github.com/your-username/signal-engine.git
cd signal-engine

---

### Install Dependencies

pip install -r requirements.txt

---

### Configure Telegram

Create a bot using BotFather and update the following in telegram_utils.py:

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

Ensure the bot is started by sending a message to it before running the system.

---

### Configure Google Sheets

Set up Google Sheets API credentials and update the configuration inside sheet_manager.py accordingly.

---

## Running the Engine

python main.py

---

## Automation using AWS

The script is designed to run automatically using a scheduler such as cron on an AWS instance.

Example cron configuration:

0 9 * * * python /path/to/main.py

Ensure all dependencies are installed in the environment where the job is scheduled.

---

## Telegram Alerts

Entry alerts are triggered when a new signal is generated for a stock.

Exit alerts are triggered when any of the following conditions are met:
- Hard Stop Loss
- Trailing Stop Loss
- Maximum holding period

---

## Output

- Signals are stored in storage/signals_log.csv
- Data is synced to Google Sheets
- Alerts are sent to Telegram

---

## Workflow

AWS Scheduler
    |
    v
main.py execution
    |
    v
Signal generation
    |
    v
Update CSV and Google Sheets
    |
    v
Send Telegram alerts

---

## Notes

- Ensure Telegram bot is active and chat ID is correct
- Ensure required Python packages are installed in AWS environment
- Each stock follows a cooldown period before generating a new signal

---

## Future Enhancements

- Add chart images to Telegram alerts
- Extend system to intraday signals
- Implement signal ranking
- Build portfolio analytics dashboard

---

## Author

Abhishek

---

## License

This project is intended for educational and research purposes only.
