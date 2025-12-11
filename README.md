# Vacancy Template Bot

A simple Telegram bot that applies your saved template to any vacancy text or link using Yandex Qwen via the Foundation Models API.

## Setup

1) Install dependencies:
```bash
pip install -r requirements.txt
```

2) Create `env.example` into a real env file or export the variables:
- `TELEGRAM_BOT_TOKEN` – the Telegram bot token you provided.
- `YANDEX_API_KEY` – Yandex Cloud API key with access to Foundation Models.
- `YANDEX_MODEL_URI` – optional; defaults to `gpt://b1gransh9mb37bnvtl9u/qwen3-4b/latest`.
- `TEMPLATE_STORE_PATH` – optional path for storing templates (defaults to `templates.json`).

3) Run the bot:
```bash
python main.py
```

## How it works
- `/start` shows buttons: **Update template** and **Show current template**.
- **Update template** prompts for the template text and a short description/context; both are saved per user.
- Send any vacancy link or text; the bot calls Yandex Qwen to adapt your template and replies with a ready-to-send message.

Templates are stored in `templates.json` (or the path you set) so they persist across restarts.

