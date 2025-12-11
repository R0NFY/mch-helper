#!/bin/bash
# Script to run the Telegram bot with the virtual environment

cd "$(dirname "$0")"
source venv/bin/activate
python bot.py

