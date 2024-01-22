# Devman Checker Telegram Bot

This Python script uses the Devman API to monitor the status of code submissions and sends notifications to a Telegram chat when a task is reviewed.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Pip package manager installed
- A Telegram bot token (obtainable from BotFather on Telegram)
- A Devman API token (available on the Devman website)

## Getting Started

Clone the repository:

```bash
git clone https://github.com/nucluster/devman-notifications-bot.git
```

1. Change into the project directory:

```bash

cd devman-checker-bot
```
2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

 - On Unix or MacOS:
```bash
source venv/bin/activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

5. Create a .env file in the project root and add the following information:

```env

DEVMAN_TOKEN=your_devman_api_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```
6. Run the script:

```bash
python bot.py
```

## Configuration

- DEVMAN_TOKEN: Your Devman API token.
- TELEGRAM_TOKEN: Your Telegram bot token.
- TELEGRAM_CHAT_ID: The chat ID where the bot will send notifications.

## Logging

The script uses logging to record events. You can adjust the log level in the script for debugging or production use.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
