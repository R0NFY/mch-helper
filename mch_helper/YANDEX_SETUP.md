# Yandex Cloud Setup Guide

Detailed instructions for setting up Yandex Cloud credentials for the bot.

## Step 1: Create Yandex Cloud Account

1. Go to [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Click "Sign in" or create a new Yandex account
3. Complete the registration process

## Step 2: Create or Select a Folder

1. In the Yandex Cloud console, you'll see your cloud
2. Either use the default folder or create a new one:
   - Click "Create folder"
   - Give it a name (e.g., "telegram-bot")
3. **Important**: Copy the **Folder ID** (it looks like: `b1g2abc3def4ghi5jklm`)
   - You can find it in the folder details or in the URL

## Step 3: Create a Service Account

1. In the left menu, go to **"Service accounts"**
2. Click **"Create service account"**
3. Fill in the details:
   - **Name**: e.g., "vacancy-bot-service"
   - **Description**: Optional description
4. Click **"Create"**

## Step 4: Assign the Required Role

1. Find your newly created service account in the list
2. Click on it to open details
3. Go to the **"Access bindings"** tab
4. Click **"Assign roles"**
5. Select the folder where you want to use the bot
6. Add the role: **`ai.languageModels.user`**
7. Click **"Save"**

## Step 5: Create an API Key

1. Still in the service account details, go to the **"API keys"** tab
2. Click **"Create API key"**
3. **Important**: Copy the API key immediately!
   - It looks like: `AQVNabcdefGHIjklMNOpqrsTUVwxyz123456789`
   - You won't be able to see it again after closing the dialog
4. Save it securely

## Step 6: Add Credentials to .env

Edit your `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
YANDEX_API_KEY=AQVNabcdefGHIjklMNOpqrsTUVwxyz123456789
YANDEX_FOLDER_ID=b1g2abc3def4ghi5jklm
```

## Troubleshooting

### "Access denied" error

Make sure your service account has the `ai.languageModels.user` role:
1. Go to the folder settings
2. Click "Access bindings"
3. Find your service account
4. Check if the role is assigned

### "Invalid folder_id" error

Double-check your folder ID:
1. Go to your folder
2. The ID is in the URL: `https://console.cloud.yandex.ru/folders/YOUR_FOLDER_ID`
3. Or find it in folder details

### API key not working

- Make sure you copied the full key
- Check there are no extra spaces
- The key should start with `AQVN` or similar

### Billing issues

Yandex Cloud requires:
1. A payment method to be added (even for free tier)
2. The free tier includes some free usage
3. Check your billing account status in the console

## Yandex Cloud Pricing

YandexGPT Lite (used by the bot):
- **Free tier**: First requests each month are free
- **Paid usage**: Very affordable per 1000 tokens
- Check current pricing: [Yandex Cloud Pricing](https://cloud.yandex.com/en/docs/yandexgpt/pricing)

## API Models Used

The bot uses **YandexGPT Lite** which is:
- ✅ Fast response time
- ✅ Good quality for text formatting
- ✅ Cost-effective
- ✅ Suitable for message generation

You can modify `bot.py` to use **YandexGPT** (full version) for better quality:

```python
"modelUri": f"gpt://{self.folder_id}/yandexgpt",  # instead of yandexgpt-lite
```

## Useful Links

- [Yandex Cloud Console](https://console.cloud.yandex.ru/)
- [YandexGPT Documentation](https://cloud.yandex.com/en/docs/yandexgpt/)
- [Service Accounts Guide](https://cloud.yandex.com/en/docs/iam/concepts/users/service-accounts)
- [API Keys Documentation](https://cloud.yandex.com/en/docs/iam/concepts/authorization/api-key)

## Security Tips

1. **Never share your API key** publicly
2. Keep your `.env` file private (it's in `.gitignore`)
3. Rotate API keys periodically
4. Use separate service accounts for different projects
5. Monitor your usage in the Yandex Cloud console

## Testing Your Setup

After setup, test if it works:

```bash
# Run the bot
python bot.py

# In Telegram:
# 1. Send /start to your bot
# 2. Set up a template
# 3. Send a test vacancy
# 4. Check if AI-generated message works
```

If you see a formatted message, everything works! 🎉

If it falls back to simple formatting, check the bot logs for error messages.

