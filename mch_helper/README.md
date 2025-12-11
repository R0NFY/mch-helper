# Telegram Vacancy Message Generator Bot

A Telegram bot that helps you generate formatted vacancy messages based on customizable templates.

## Features

- 📝 **Custom Templates**: Create and update your own message templates
- 🤖 **AI-Powered Generation**: Uses Yandex GPT to intelligently format vacancy information
- 📋 **Flexible Input**: Accept vacancy links or text descriptions
- 📞 **Contact Management**: Automatically detect and include contact information
- 💾 **Persistent Storage**: Your templates are saved between sessions

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- Yandex Cloud API Key (optional, for AI-powered generation)
- Yandex Cloud Folder ID (optional, for AI-powered generation)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/maximkolomiets/bots/mch_helper
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the project directory:
   ```bash
   cp config_template.txt .env
   ```
   
   Then edit the `.env` file and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   YANDEX_API_KEY=your_yandex_api_key_here
   YANDEX_FOLDER_ID=your_yandex_folder_id_here
   ```

   **Getting your Telegram Bot Token:**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow the instructions
   - Copy the token provided

   **Getting your Yandex Cloud credentials (optional):**
   - Go to [Yandex Cloud Console](https://console.cloud.yandex.ru/)
   - Sign in or create an account
   - Create or select a folder, copy the Folder ID
   - Go to Service accounts → Create service account
   - Assign the `ai.languageModels.user` role
   - Create an API key and copy it
   - Note: If you don't provide Yandex credentials, the bot will use simple template filling

5. **Run the bot:**
   
   Option 1 - Using the helper script:
   ```bash
   ./run.sh
   ```
   
   Option 2 - Manual activation:
   ```bash
   source venv/bin/activate
   python bot.py
   ```

## Usage

### 1. Start the Bot

Open Telegram and search for your bot, then send:
```
/start
```

### 2. Set Up Your Template

Click the "📝 Set/Update Template" button and send your template. For example:

```
🎯 Position: [Job Title]
🏢 Company: [Company Name]
📍 Location: [Location]
💰 Salary: [Salary Range]
📝 Description: [Brief Description]
🔗 Apply: [Application Link]
```

Then provide a description like: "Template for IT job positions"

### 3. Generate Messages

Simply send the bot a vacancy link or paste the vacancy text. The bot will:
- Extract key information from the vacancy
- Format it according to your template
- Include contact information if available
- Return the ready-to-use message

### 4. Commands

- `/start` - Show the main menu
- `/generate` - Start generating a new message
- `/cancel` - Cancel the current operation

## Example Workflow

1. **Set Template:**
   ```
   🎯 Job: [Position]
   🏢 Company: [Company]
   💰 Salary: [Salary]
   📍 Location: [Location]
   ```

2. **Send Vacancy:**
   ```
   Senior Python Developer
   Tech Company Inc.
   Remote work, $80k-$120k
   Contact: hr@techcompany.com
   ```

3. **Receive Formatted Message:**
   ```
   🎯 Job: Senior Python Developer
   🏢 Company: Tech Company Inc.
   💰 Salary: $80k-$120k
   📍 Location: Remote
   📧 Contact: hr@techcompany.com
   ```

## File Structure

```
mch_helper/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── templates.json     # Stored templates (auto-generated)
├── user_data.json     # User data (auto-generated)
└── README.md          # This file
```

## Troubleshooting

### Bot doesn't start
- Check that your `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### AI generation not working
- Verify your `YANDEX_API_KEY` and `YANDEX_FOLDER_ID` are correct
- Check your Yandex Cloud account has sufficient credits
- Ensure the service account has `ai.languageModels.user` role
- The bot will fall back to simple formatting if AI fails

### Template not saving
- Check file permissions in the project directory
- Ensure `templates.json` is writable

## Advanced Usage

### Custom Template Variables

You can use any placeholders in your template. The AI will try to match them with the vacancy information:
- `[Position]`, `[Job Title]`, `[Role]`
- `[Company]`, `[Company Name]`
- `[Location]`, `[City]`, `[Country]`
- `[Salary]`, `[Compensation]`, `[Pay]`
- `[Requirements]`, `[Skills]`
- `[Contact]`, `[Email]`, `[Phone]`

### Multiple Templates

Currently, each user has one template. To switch templates:
1. Click "Set/Update Template"
2. Send your new template

Your old template will be replaced.

## Support

For issues or questions, please check:
- Bot logs in the terminal where it's running
- Telegram Bot API documentation
- Yandex Cloud API documentation
- Yandex Cloud status page

## License

This project is provided as-is for personal use.

