# Setup Checklist ✅

Follow these steps to get your bot running:

## ✅ Done

- [x] Project structure created
- [x] All Python dependencies installed (upgraded for Python 3.14)
- [x] Virtual environment set up
- [x] Helper scripts created
- [x] Python 3.14 compatibility fixed

## 🔧 To Do

### Step 1: Get Telegram Bot Token

1. Open Telegram and find **@BotFather**
2. Send `/newbot`
3. Follow instructions to create your bot
4. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Yandex Cloud Credentials (Optional but Recommended)

See detailed instructions in `YANDEX_SETUP.md`, or quick version:

1. Go to https://console.cloud.yandex.ru/
2. Create/select a folder → copy **Folder ID**
3. Create service account with `ai.languageModels.user` role
4. Create API key → copy **API Key**

### Step 3: Configure .env File

Create a `.env` file (copy from template):

```bash
cp config_template.txt .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_BOT_TOKEN=your_actual_telegram_token
YANDEX_API_KEY=your_actual_yandex_key
YANDEX_FOLDER_ID=your_actual_folder_id
```

### Step 4: Run the Bot

Easy way:
```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python bot.py
```

You should see: `INFO - Bot started!`

### Step 5: Test the Bot

1. Open Telegram
2. Find your bot by username
3. Send `/start`
4. Follow the interactive menu!

## 📁 Project Structure

```
mch_helper/
├── bot.py                    # Main bot code ✅
├── requirements.txt          # Dependencies ✅
├── config_template.txt       # Config template ✅
├── run.sh                    # Helper script ✅
├── .env                      # Your credentials (YOU CREATE)
├── .gitignore               # Git ignore rules ✅
├── venv/                    # Virtual environment ✅
├── README.md                # Full documentation ✅
├── QUICKSTART.md            # Quick start guide ✅
├── YANDEX_SETUP.md          # Yandex setup guide ✅
└── SETUP_CHECKLIST.md       # This file ✅
```

## 🎯 Quick Start Commands

```bash
# 1. Configure credentials
nano .env   # or use any text editor

# 2. Run the bot
./run.sh

# 3. Stop the bot
# Press Ctrl+C in the terminal
```

## 💡 Tips

- **Without Yandex API**: Bot will still work with simple template filling
- **Keep terminal open**: Bot needs to run continuously
- **Update template**: You can change your template anytime in Telegram
- **Check logs**: Terminal shows all bot activity

## 🆘 Troubleshooting

### "TELEGRAM_BOT_TOKEN not found"
→ Make sure you created `.env` file and added your token

### "Module not found" error
→ Activate venv: `source venv/bin/activate`

### Bot doesn't respond in Telegram
→ Check that bot is running (you should see "Bot started!" message)

### Yandex API errors
→ See `YANDEX_SETUP.md` for detailed troubleshooting

## 📚 Next Steps

Once the bot is running:

1. **Set your template** - Click "Set/Update Template" in bot
2. **Send a vacancy** - Paste vacancy text or link
3. **Get formatted message** - Bot returns ready-to-use message

Need more help? Check:
- `README.md` - Complete documentation
- `QUICKSTART.md` - Detailed setup guide
- `YANDEX_SETUP.md` - Yandex Cloud setup

---

**Current Status**: Dependencies installed ✅ Python 3.14 compatible ✅  
**Next Step**: Configure `.env` file with your credentials

## ⚠️ Important Note

If you're using Python 3.14, the bot now uses `python-telegram-bot==22.5` which is fully compatible.
The initial AttributeError issue has been resolved! ✅

Good luck! 🚀

