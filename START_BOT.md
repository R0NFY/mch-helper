# 🚀 Start Your Bot - Quick Reference

## Prerequisites Checklist

Before starting the bot, make sure you have:

- [x] ✅ Virtual environment created (`venv/`)
- [x] ✅ Dependencies installed (`pip install -r requirements.txt`)
- [ ] ⚠️ `.env` file configured with your credentials

## Step 1: Configure .env File

If you haven't already, create and edit your `.env` file:

```bash
# Copy the template
cp config_template.txt .env

# Edit with your credentials
nano .env  # or use any text editor
```

Your `.env` should look like this:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
YANDEX_API_KEY=AQVNabcdefGHIjklMNOpqrsTUVwxyz  # Optional
YANDEX_FOLDER_ID=b1g2abc3def4ghi5jklm  # Optional
```

### Where to Get These:

- **TELEGRAM_BOT_TOKEN**: Talk to [@BotFather](https://t.me/botfather) → `/newbot`
- **YANDEX_API_KEY & FOLDER_ID**: See `YANDEX_SETUP.md` (optional for AI features)

## Step 2: Start the Bot

### Option A: Using the Helper Script (Recommended)

```bash
./run.sh
```

### Option B: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python bot.py
```

## Expected Output

When the bot starts successfully, you should see:

```
2024-XX-XX XX:XX:XX - __main__ - INFO - Bot started!
```

**✅ Success!** Your bot is now running and ready to receive messages.

## Step 3: Test Your Bot

1. Open Telegram
2. Search for your bot by username (the one you set with BotFather)
3. Send `/start`
4. You should see a welcome message with buttons!

## Managing the Bot

### Stop the Bot

Press `Ctrl+C` in the terminal where the bot is running.

### Run in Background (Optional)

To run the bot in the background:

```bash
# Start in background
nohup ./run.sh > bot.log 2>&1 &

# Check if running
ps aux | grep bot.py

# View logs
tail -f bot.log

# Stop it
pkill -f bot.py
```

### Auto-restart on Crash

For production use, consider using `systemd`, `supervisor`, or `pm2`:

**Using screen (simple solution):**
```bash
# Start a screen session
screen -S telegram_bot

# Run the bot
./run.sh

# Detach: Press Ctrl+A, then D
# Reattach: screen -r telegram_bot
```

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not found"

**Problem**: `.env` file is missing or not configured

**Solution**:
```bash
# Check if .env exists
ls -la .env

# If not, create it
cp config_template.txt .env
nano .env
```

### "Module not found" errors

**Problem**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Bot starts but doesn't respond in Telegram

**Possible causes**:
1. Wrong bot token → Check `.env` file
2. Bot not started → Make sure you see "Bot started!" message
3. Wrong bot username → Check with BotFather

**Test**:
```bash
# Check bot.py logs in terminal
# You should see activity when sending messages
```

### "AttributeError" with Python 3.14

**Solution**: Already fixed! We upgraded to `python-telegram-bot==22.5`

### Permission denied on `./run.sh`

**Solution**:
```bash
chmod +x run.sh
```

## Testing Checklist

After starting the bot, test these features:

1. [ ] `/start` command shows welcome menu
2. [ ] "Set/Update Template" button works
3. [ ] Can save a template with description
4. [ ] "View Current Template" shows your template
5. [ ] Sending vacancy text generates a message
6. [ ] Help button shows instructions

## Quick Commands Reference

```bash
# Start bot (recommended)
./run.sh

# Start bot (manual)
source venv/bin/activate && python bot.py

# View bot logs (if running in background)
tail -f bot.log

# Check if bot is running
ps aux | grep bot.py

# Stop bot (if in background)
pkill -f bot.py

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Run in screen session
screen -S telegram_bot
./run.sh
# Press Ctrl+A then D to detach
```

## What's Next?

Once your bot is running:

1. **Set up your template** - Use the bot menu to create your message template
2. **Test with a vacancy** - Send a job vacancy text
3. **Customize** - Edit `bot.py` to add more features
4. **Deploy** - Consider hosting on a VPS for 24/7 operation

## Need Help?

- Check `README.md` for full documentation
- See `YANDEX_SETUP.md` for AI features setup
- Review `QUICKSTART.md` for detailed setup guide

---

**Status**: Dependencies upgraded ✅ Python 3.14 compatible ✅  
**Next**: Configure `.env` and run `./run.sh`

Good luck! 🤖

