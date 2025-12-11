#!/usr/bin/env python3
"""
Telegram Bot for generating vacancy messages based on templates.
"""

import os
import json
import logging
import re
import html
from typing import Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
TEMPLATE_INPUT, DESCRIPTION_INPUT, DESCRIPTION_EDIT_INPUT, VACANCY_INPUT = range(4)

# File paths
TEMPLATES_FILE = 'templates.json'
USER_DATA_FILE = 'user_data.json'


class TemplateManager:
    """Manages message examples for users."""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self) -> dict:
        """Load examples from file."""
        if os.path.exists(TEMPLATES_FILE):
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_templates(self):
        """Save examples to file."""
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def set_template(self, user_id: int, example: str, description: str):
        """Set example for a user."""
        self.templates[str(user_id)] = {
            'example': example,
            'description': description
        }
        self.save_templates()

    def update_description(self, user_id: int, description: str):
        """Update only description for an existing example."""
        if str(user_id) in self.templates:
            self.templates[str(user_id)]['description'] = description
            self.save_templates()
    
    def get_template(self, user_id: int) -> Optional[dict]:
        """Get example for a user."""
        return self.templates.get(str(user_id))


class VacancyProcessor:
    """Processes vacancy information and generates messages."""
    
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def format_contact_links(self, text: str) -> str:
        """Wrap bare contact URLs into anchor tags for Telegram HTML."""
        # 1) Стать частью команды + @username
        text = re.sub(
            r"(Стать частью команды:?\\s*)(@\\w+)",
            lambda m: f"{m.group(1)}{m.group(2)}",
            text,
            flags=re.IGNORECASE,
        )
        # 2) Стать частью команды + URL -> сделать текст гиперссылкой
        text = re.sub(
            r"(Стать частью команды:?\\s*)(https?://\\S+)",
            lambda m: f'<a href="{m.group(2)}">Стать частью команды</a>',
            text,
            flags=re.IGNORECASE,
        )
        # 3) Общий случай: оборачиваем любые голые URL в <a>, якорь "ссылка"
        text = re.sub(
            r"(?<!href=\")(?<!\">)(https?://\\S+)",
            lambda m: f'<a href="{m.group(1)}">ссылка</a>',
            text,
        )
        return text
    
    def clean_html_for_telegram(self, text: str) -> str:
        """Clean HTML to only include Telegram-supported tags."""
        # Strip accidental code fences/backticks
        text = re.sub(r'^`{3,}\s*', '', text)
        text = re.sub(r'\s*`{3,}$', '', text)

        # Remove unsupported tags
        text = re.sub(r'<br\s*/?>', '\n', text)  # <br> → newline
        text = re.sub(r'<p[^>]*>', '\n', text)  # <p> → newline
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<div[^>]*>', '\n', text)  # <div> → newline
        text = re.sub(r'</div>', '\n', text)
        text = re.sub(r'</?span[^>]*>', '', text)  # Remove span
        text = re.sub(r'<strong>', '<b>', text)  # <strong> → <b>
        text = re.sub(r'</strong>', '</b>', text)
        text = re.sub(r'<em>', '<i>', text)  # <em> → <i>
        text = re.sub(r'</em>', '</i>', text)

        # Remove any other unsupported tags but keep content; allow blockquote
        text = re.sub(r'<(?!/?[biusa]|/?code|/?pre|/?blockquote|a\s)[^>]+>', '', text)

        # Удаляем упоминания агрегаторов (не компания)
        text = re.sub(r'https?://\S*vseti\.app\S*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vseti\.app', '', text, flags=re.IGNORECASE)

        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove accidental leading service words like "html", "body"
        text = re.sub(r'^\s*(html|body)\s*[:>\-]?\s*', '', text, flags=re.IGNORECASE)

        return text.strip()
    
    def extract_url_content(self, text: str) -> Tuple[str, Optional[str]]:
        """Extract and parse content from URL if present in text."""
        # Find URLs in text
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        if not urls:
            return text, None
        
        # Try to fetch content from the first URL
        url = urls[0]
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Clean up extra whitespace
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            logger.info(f"Successfully parsed content from URL: {url}")
            return clean_text, url
            
        except Exception as e:
            logger.error(f"Error fetching URL content: {e}")
            return text, url
        
        return text, None
    
    async def generate_message(
        self,
        vacancy_text: str,
        example: str,
        description: str,
        contact_info: Optional[str] = None
    ) -> str:
        """Generate a message based on vacancy and example."""
        
        if not self.api_key or not self.folder_id:
            return self._generate_simple_message(vacancy_text, example, contact_info)
        
        try:
            prompt = f"""Ты генератор сообщений для Telegram. Используй HTML-форматирование. НИЧЕГО лишнего в начале (не пиши "html", "body" и т.п.).

=== ПРИМЕР (твой ШАБЛОН) ===
{example}

=== ОБЪЯСНЕНИЕ СТРУКТУРЫ ===
{description}

=== НОВЫЕ ДАННЫЕ (вакансия для форматирования) ===
{vacancy_text}

{"=== ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ ===\n" + contact_info if contact_info else ""}

ВАЖНО ПРО ИЗВЛЕЧЕНИЕ ДАННЫХ:
1. Название КОМПАНИИ - это бренд/организация (например: "VSETI.APP", "Яндекс", "Google")
   НЕ путай с доменом сайта!
2. КОНТАКТ - это email, телефон, telegram username
   НЕ путай с названием компании!
3. Если видишь "Стать частью команды: email@company.com" - email это КОНТАКТ, не компания
4. Описание компании и роли делай объёмным: 2–3 коротких абзаца внутри <blockquote>…</blockquote>. Больше конкретики про компанию и чем заниматься.
5. НИКОГДА не используй домен/URL в качестве названия компании. Компания = текстовое имя бренда (например: "Яндекс", "HR Creative"). Игнорируй агрегаторы/сайты (vseti.app, hh.ru, career.habr.com и т.п.).
6. Контакт оформляй как часть текста с якорной ссылкой: например, "Стать частью команды: <a href=\"URL\">откликнуться</a>". Не оставляй голые URL.

АЛГОРИТМ:

Шаг 1. Разбери ПРИМЕР:
- Где жирный текст - там используй <b>текст</b>
- Где курсив - там <i>текст</i>
- Где ссылка - там <a href="url">текст</a>
- Где смайлики - запомни какие

Шаг 2. Извлеки из НОВЫХ ДАННЫХ:
- Должность (например: "Продуктовый дизайнер")
- Компания (например: "VSETI.APP" - это бренд, НЕ домен!)
- Формат работы (офис/удаленка/гибрид)
- Опыт (junior/middle/senior)
- Описание компании (кратко о чем она)
- Контакт (email, телефон или telegram)

Шаг 3. СКОПИРУЙ структуру примера:
- Если в примере: <b>должность</b> → используй <b>новая должность</b>
- Если в примере: 💚 <b>компания ищут</b> 💚 → используй 💚 <b>новая компания ищут</b> 💚
- Если в примере: <b>Формат:</b> текст → используй <b>Формат:</b> новый текст
- Сохрани ВСЕ пустые строки из примера
- Описание/quote: 2–3 коротких абзаца, оберни в <blockquote>…</blockquote>. Больше деталей про компанию и роль.

TELEGRAM ПОДДЕРЖИВАЕТ ТОЛЬКО ЭТИ HTML ТЕГИ:
- <b>жирный</b> или <strong>жирный</strong>
- <i>курсив</i> или <em>курсив</em>
- <u>подчеркнутый</u>
- <s>зачеркнутый</s>
- <blockquote>текст</blockquote> — для цитаты
- <a href="url">ссылка</a>

НЕ ИСПОЛЬЗУЙ:
- <br> - используй просто перенос строки (Enter)
- <p>, <div>, <span> - не нужны
- Любые другие теги

КОНВЕРТАЦИЯ MARKDOWN → HTML:
- **текст** → <b>текст</b>
- *текст* → <i>текст</i>
- [текст](url) → <a href="url">текст</a>
- Цитата/описание → оберни в <blockquote>…</blockquote>, 2–3 коротких абзаца
- Пустая строка остается пустой строкой (НЕ <br>!)

ПРАВИЛА:
1. ТОЧНО копируй структуру примера
2. НЕ меняй смайлики (💚 остается 💚)
3. НЕ меняй слова типа "ищут"
4. Пустые строки на тех же местах
5. HTML теги для форматирования
6. Компания - это БРЕНД, не домен!
7. В начале сообщения не добавляй "html", "body" или другие служебные слова
8. Описание: 2–3 коротких абзаца внутри <blockquote>…</blockquote>
9. Название компании пиши как текст (без ссылки). Контакт/ссылку ставь внизу, как в примере, с якорной ссылкой в тексте.

ВЕРНИ:
Только готовое сообщение в HTML. Без комментариев."""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}"
            }
            
            data = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-32k/latest",  # YandexGPT 32k - most powerful
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 2000
                },
                "messages": [
                    {
                        "role": "system",
                        "text": "Ты профессиональный помощник по форматированию сообщений о вакансиях."
                    },
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result['result']['alternatives'][0]['message']['text'].strip()
                # Format links and clean HTML
                generated_text = self.format_contact_links(generated_text)
                # Clean HTML for Telegram
                return self.clean_html_for_telegram(generated_text)
            else:
                logger.error(f"Yandex API error: {response.status_code} - {response.text}")
                return self._generate_simple_message(vacancy_text, example, contact_info)
        
        except Exception as e:
            logger.error(f"Error generating message with AI: {e}")
            return self._generate_simple_message(vacancy_text, example, contact_info)
    
    def _generate_simple_message(
        self,
        vacancy_text: str,
        example: str,
        contact_info: Optional[str]
    ) -> str:
        """Generate a simple message without AI."""
        message = f"⚠️ AI генерация недоступна. Показываю пример:\n\n"
        message += f"**Ваш пример:**\n{example}\n\n"
        message += f"**Новая вакансия:**\n{vacancy_text}\n\n"
        message += f"💡 Настройте Yandex API для автоматической генерации в стиле примера."
        return message


# Initialize managers
template_manager = TemplateManager()
vacancy_processor = VacancyProcessor(
    os.getenv('YANDEX_API_KEY'),
    os.getenv('YANDEX_FOLDER_ID')
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("📝 Загрузить пример", callback_data='set_template')],
        [InlineKeyboardButton("📋 Посмотреть пример", callback_data='view_template')],
        [InlineKeyboardButton("✏️ Обновить описание", callback_data='set_description')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""👋 Привет, {user.first_name}!

Я бот для генерации сообщений о вакансиях с помощью AI. 

**Как работаю:**
1. Ты показываешь мне ПРИМЕР готовой вакансии (как образец)
2. Я анализирую его стиль и структуру
3. Потом применяю этот стиль к новым вакансиям

**Гибкость:**
При каждой новой вакансии можешь добавлять инструкции:
"Заголовок сделай таким", "ссылку добавь эту" и т.д.

Выбери действие ниже:"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'set_template':
        await query.edit_message_text(
            "📝 **Загрузка примера вакансии**\n\n"
            "Отправьте мне ПРИМЕР готовой вакансии - такой, как вы хотите видеть результат.\n\n"
            "Нейронка проанализирует:\n"
            "• Структуру вашего сообщения\n"
            "• Форматирование (жирный, цитаты, ссылки)\n"
            "• Стиль и расположение элементов\n"
            "• Использование смайликов\n\n"
            "**Пример того, что отправить:**\n"
            "```\n"
            "**Толковые middle/senior дизайнеры**\n\n"
            "💚 **Relate ищут** 💚\n\n"
            "**Формат:** удаленка\n"
            "**Опыт:** middle/senior\n\n"
            "> Relate – международная web3 студия. \n"
            "> Стратегический дизайн-партнер для фаундеров\n\n"
            "[Стать частью команды](https://t.me/relate)\n"
            "```\n\n"
            "Просто скопируйте ваше готовое сообщение!\n\n"
            "Отправьте /cancel для отмены.",
            parse_mode='Markdown'
        )
        return TEMPLATE_INPUT
    
    elif query.data == 'view_template':
        template_data = template_manager.get_template(query.from_user.id)
        if template_data:
            text = f"**Ваш пример вакансии:**\n\n"
            text += f"**Описание структуры:**\n{template_data['description']}\n\n"
            text += f"**Пример:**\n{template_data['example']}"
        else:
            text = "❌ У вас еще нет примера. Используйте кнопку 'Загрузить пример' для создания."
        
        keyboard = [[InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'help':
        help_text = """**📖 Как использовать бота**

**Концепция:**
Бот использует AI для гибкой генерации. Вы показываете ПРИМЕР готовой вакансии, и AI применяет его стиль к новым вакансиям.

**Шаг 1: Загрузите пример**
Нажмите "Загрузить пример" и отправьте:
1. Готовое сообщение о вакансии (как вы хотите видеть результат)
2. Описание структуры (подсказки для AI)

**Шаг 2: Генерируйте сообщения**
Отправьте мне:
- Текст новой вакансии
- Можете добавить инструкции: "заголовок сделай таким", "ссылку добавь эту"

**Шаг 3: Получите результат**
AI проанализирует вашу вакансию и применит стиль примера!

**Гибкость:**
При каждой вакансии можете указывать изменения в тексте сообщения.

**Команды:**
/start - Главное меню
/cancel - Отменить операцию
/generate - Начать генерацию

**Преимущества:**
- Максимальная гибкость через AI
- Можете влиять на каждое сообщение
- Не жесткий шаблон, а умное применение стиля"""
        
        keyboard = [[InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]]
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("📝 Загрузить пример", callback_data='set_template')],
            [InlineKeyboardButton("📋 Посмотреть пример", callback_data='view_template')],
            [InlineKeyboardButton("✏️ Обновить описание", callback_data='set_description')],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
        ]
        await query.edit_message_text(
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data == 'generate_now':
        user_id = query.from_user.id
        template_data = template_manager.get_template(user_id)
        
        if template_data:
            await query.edit_message_text(
                "📋 **Готов к генерации!**\n\n"
                "Отправьте мне текст новой вакансии.\n\n"
                "**💡 Гибкость:**\n"
                "Можете добавить инструкции прямо в сообщении:\n"
                "• \"Заголовок сделай 'Senior React Developer'\"\n"
                "• \"Ссылку добавь https://...\"\n"
                "• \"Компанию укажи как 'TechCorp'\"\n\n"
                "AI применит стиль вашего примера + учтет ваши инструкции!",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Что-то пошло не так. Пожалуйста, загрузите пример заново через /start"
            )

    elif query.data == 'set_description':
        template_data = template_manager.get_template(query.from_user.id)
        if not template_data:
            keyboard = [[InlineKeyboardButton("📝 Загрузить пример", callback_data='set_template')]]
            await query.edit_message_text(
                "Сначала загрузите пример вакансии, затем можно обновить описание.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        await query.edit_message_text(
            "✏️ Обновление описания структуры\n\n"
            "Отправьте новое описание структуры вашего примера.\n\n"
            "Подскажите нейросети, как понимать блоки и форматирование. Например:\n"
            "«Первая строка — должность жирным, вторая — компания между 💚, далее Формат/Опыт, "
            "описание в <blockquote>, ссылка внизу»\n\n"
            "Отправьте /cancel для отмены."
        )
        return DESCRIPTION_EDIT_INPUT


async def receive_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the example from user."""
    context.user_data['template'] = update.message.text
    
    await update.message.reply_text(
        "✅ Пример получен!\n\n"
        "Теперь отправьте описание структуры этого примера.\n\n"
        "**Это важно!** Опишите структуру, чтобы нейронка понимала:\n"
        "• Где заголовок и как он оформлен\n"
        "• Где компания и как выделена\n"
        "• Какие блоки есть (формат, опыт, описание)\n"
        "• Как используются смайлики и форматирование\n\n"
        "**Например:**\n"
        "\"Первая строка - название должности жирным. Вторая - компания между 💚. "
        "Потом формат и опыт. Описание компании цитатой. Ссылка с текстом 'Стать частью команды'\"\n\n"
        "Отправьте /cancel для отмены."
    )
    return DESCRIPTION_INPUT


async def receive_template_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the template description and save."""
    description = update.message.text
    template = context.user_data.get('template')
    
    if template:
        template_manager.set_template(update.effective_user.id, template, description)
        
        keyboard = [
            [InlineKeyboardButton("🚀 Сгенерировать сообщение", callback_data='generate_now')],
            [InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]
        ]
        
        await update.message.reply_text(
            "✅ **Пример успешно сохранен!**\n\n"
            f"**Описание структуры:** {description}\n\n"
            "Теперь можете отправлять мне информацию о вакансиях!\n\n"
            "**Как использовать:**\n"
            "• Просто отправьте текст новой вакансии\n"
            "• Можете добавить инструкции: \"заголовок сделай таким\", \"ссылку добавь эту\" и т.д.\n"
            "• Нейронка применит стиль вашего примера к новой вакансии\n\n"
            "💡 **Гибкость:** В любом сообщении можете указать, что изменить!\n\n"
            "Используйте /start для возврата в главное меню.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    context.user_data.clear()
    return ConversationHandler.END


async def receive_description_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive updated description for existing example."""
    description = update.message.text
    user_id = update.effective_user.id
    template_data = template_manager.get_template(user_id)

    if not template_data:
        await update.message.reply_text(
            "❌ Нет сохраненного примера. Сначала загрузите пример через /start."
        )
        return ConversationHandler.END

    template_manager.update_description(user_id, description)

    keyboard = [
        [InlineKeyboardButton("🚀 Сгенерировать сообщение", callback_data='generate_now')],
        [InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]
    ]

    await update.message.reply_text(
        "✅ Описание обновлено!\n\n"
        f"**Новое описание:** {description}\n\n"
        "Теперь можете генерировать сообщения с обновленными подсказками.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


async def handle_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle vacancy input and generate message."""
    user_id = update.effective_user.id
    vacancy_text = update.message.text
    
    # Check if user has an example
    template_data = template_manager.get_template(user_id)
    if not template_data:
        keyboard = [[InlineKeyboardButton("📝 Загрузить пример", callback_data='set_template')]]
        await update.message.reply_text(
            "⚠️ Сначала нужно загрузить пример вакансии!\n"
            "Нажмите кнопку ниже, чтобы показать мне образец.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🔄 Обрабатываю вакансию...")
    
    try:
        # Check if text contains URL and extract content
        parsed_content, found_url = vacancy_processor.extract_url_content(vacancy_text)
        
        if found_url:
            await processing_msg.edit_text("🔄 Извлекаю контент со страницы...\n🌐 Парсинг вакансии...")
        
        # Update processing message
        await processing_msg.edit_text("🔄 Генерирую сообщение с помощью AI...")
        
        # Generate message
        generated_message = await vacancy_processor.generate_message(
            parsed_content,
            template_data['example'],
            template_data['description'],
            None  # User instructions are in vacancy_text itself
        )
        
        # Delete the processing message
        await processing_msg.delete()
        
        # Send the clean message ready for forwarding
        await update.message.reply_text(
            generated_message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
        # Send a separate informational message
        await update.message.reply_text(
            "✅ Сообщение готово! Можете пересылать в канал.\n\n"
            "💡 **Отправьте следующую вакансию.**\n"
            "Можете добавить инструкции прямо в тексте:\n"
            "• \"Заголовок сделай таким\"\n"
            "• \"Ссылку используй эту\"\n"
            "• \"Формат укажи офис\" и т.д.\n\n"
            "AI учтет ваши указания!"
        )
    
    except Exception as e:
        logger.error(f"Error processing vacancy: {e}")
        await processing_msg.edit_text(
            "❌ Извините, произошла ошибка при обработке запроса. Попробуйте еще раз."
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current operation."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Операция отменена.\n\nИспользуйте /start для возврата в главное меню."
    )
    return ConversationHandler.END


async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate command to start vacancy input."""
    user_id = update.effective_user.id
    template_data = template_manager.get_template(user_id)
    
    if not template_data:
        keyboard = [[InlineKeyboardButton("📝 Загрузить пример", callback_data='set_template')]]
        await update.message.reply_text(
            "⚠️ Сначала нужно загрузить пример!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    await update.message.reply_text(
        "📋 **Готов к генерации!**\n\n"
        "Отправьте мне текст новой вакансии.\n\n"
        "**Можете добавить инструкции:**\n"
        "Например: \"Заголовок сделай 'Senior Developer'\"\n"
        "Или: \"Ссылку добавь https://company.com/jobs\"\n\n"
        "Я применю стиль вашего примера к новой вакансии!",
        parse_mode='Markdown'
    )


def main():
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Conversation handler for template setup
    template_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern='^set_template$')],
        states={
            TEMPLATE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_template),
            ],
            DESCRIPTION_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_template_description),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,
    )

    # Conversation handler for description edit
    description_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern='^set_description$')],
        states={
            DESCRIPTION_EDIT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description_update),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('generate', generate_command))
    application.add_handler(CommandHandler('cancel', cancel))
    application.add_handler(template_conv_handler)
    application.add_handler(description_conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vacancy))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

