# Quick Start Guide

Follow these steps to get your Telegram bot running in minutes!

## 1. Set Up Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Create Your Bot on Telegram

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Vacancy Helper")
4. Choose a username (must end with 'bot', e.g., "my_vacancy_helper_bot")
5. **Copy the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 3. Get Yandex Cloud Credentials (Optional but Recommended)

1. Go to https://console.cloud.yandex.ru/
2. Sign in or create a Yandex account
3. Create or select a folder
4. **Copy the Folder ID** (found in folder details)
5. Go to "Service accounts" → "Create service account"
6. Give it a name and assign the role `ai.languageModels.user`
7. Create an API key for this service account
8. **Copy the API key**

> **Note:** If you skip this step, the bot will still work but with simpler template filling instead of AI-powered generation.

## 4. Configure the Bot

Create a `.env` file in the project directory:

```bash
cp config_template.txt .env
```

Edit `.env` and paste your credentials:

```env
TELEGRAM_BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
YANDEX_API_KEY=YOUR_ACTUAL_KEY_HERE
YANDEX_FOLDER_ID=YOUR_ACTUAL_FOLDER_ID_HERE
```

## 5. Run the Bot

Option 1 - Easy way (using the helper script):
```bash
./run.sh
```

Option 2 - Manual way:
```bash
source venv/bin/activate
python bot.py
```

You should see:
```
INFO - Bot started!
```

**Note:** Keep the terminal window open while the bot is running. Press `Ctrl+C` to stop it.

## 6. Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Follow the interactive menu!

## Example Usage Flow

### Step 1: Set Up Template

Click "📝 Set/Update Template" and send:

```
🎯 Position: [Job Title]
🏢 Company: [Company Name]
📍 Location: [Location]
💰 Salary: [Salary]
📝 Requirements: [Requirements]
🔗 Apply: [Link]
```

Then send description: "IT job template"

### Step 2: Send Vacancy Info

Send something like:

```
Senior Python Developer at Tech Corp
Location: Remote
Salary: $100k-$150k
Looking for 5+ years experience
Apply at: jobs@techcorp.com
```

### Step 3: Get Your Formatted Message

The bot will return:

```
🎯 Position: Senior Python Developer
🏢 Company: Tech Corp
📍 Location: Remote
💰 Salary: $100k-$150k
📝 Requirements: 5+ years experience
🔗 Apply: jobs@techcorp.com
```

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not found"
- Check that `.env` file exists in the project directory
- Make sure there are no spaces around the `=` in `.env`
- Verify the token is correct (no extra quotes or spaces)

### Bot doesn't respond
- Make sure the bot is running (you should see "Bot started!" in terminal)
- Try sending `/start` again
- Check that you're messaging the correct bot

### AI generation not working
- Verify your Yandex API key and Folder ID are correct
- Check that your Yandex Cloud account has credits
- Ensure the service account has the `ai.languageModels.user` role
- The bot will still work with basic formatting if AI fails

## Tips

- Keep the terminal window open while the bot is running
- Press `Ctrl+C` to stop the bot
- You can update your template anytime
- The bot saves your template automatically

## Next Steps

Check out the full [README.md](README.md) for:
- Advanced features
- Multiple template management
- Custom placeholders
- Troubleshooting guide

Enjoy using your bot! 🚀

