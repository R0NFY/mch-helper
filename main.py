import asyncio
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_MODEL_URI = os.getenv(
    "YANDEX_MODEL_URI", "gpt://b1gransh9mb37bnvtl9u/qwen3-4b/latest"
)
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "b1gransh9mb37bnvtl9u")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is required")


TEMPLATE_STORE_PATH = Path(os.getenv("TEMPLATE_STORE_PATH", "templates.json"))


@dataclass
class UserTemplate:
    template: str
    description: str


class TemplateStore:
    """Simple JSON-backed store for per-user templates."""

    def __init__(self, path: Path):
        self.path = path
        self._data: Dict[str, UserTemplate] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for user_id, payload in raw.items():
                self._data[user_id] = UserTemplate(
                    template=payload.get("template", ""),
                    description=payload.get("description", ""),
                )
        except Exception:
            # Start fresh if the file is unreadable
            self._data = {}

    def _save(self) -> None:
        payload = {uid: asdict(tpl) for uid, tpl in self._data.items()}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_template(self, user_id: int, template: str, description: str) -> None:
        self._data[str(user_id)] = UserTemplate(template=template, description=description)
        self._save()

    def get_template(self, user_id: int) -> Optional[UserTemplate]:
        return self._data.get(str(user_id))


class TemplateStates(StatesGroup):
    waiting_template = State()
    waiting_description = State()


class VacancyBot:
    def __init__(self) -> None:
        self.bot = Bot(
            token=TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        self.templates = TemplateStore(TEMPLATE_STORE_PATH)
        self._register_handlers()

    @staticmethod
    def _main_keyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Update template")],
                [KeyboardButton(text="Show current template")],
            ],
            resize_keyboard=True,
        )

    def _register_handlers(self) -> None:
        self.dp.message.register(self.on_start, CommandStart())
        self.dp.message.register(self.ask_template, F.text.casefold() == "update template")
        self.dp.message.register(self.show_template, F.text.casefold() == "show current template")
        self.dp.message.register(self.receive_template, TemplateStates.waiting_template)
        self.dp.message.register(self.receive_description, TemplateStates.waiting_description)
        self.dp.message.register(self.generate_response, F.text)

    async def on_start(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Hi! Send me a vacancy link or description and I will craft a response using your template.\n"
            "Use the buttons to update the template.",
            reply_markup=self._main_keyboard(),
        )

    async def ask_template(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Send me the template text I should use when crafting replies.\n\n"
            "You can include placeholders, but plain text is fine too.",
            reply_markup=self._main_keyboard(),
        )
        await state.set_state(TemplateStates.waiting_template)

    async def receive_template(self, message: types.Message, state: FSMContext) -> None:
        await state.update_data(template_text=message.text.strip())
        await message.answer(
            "Got the template. Now send a short description of when/how to use it "
            "(or context I should keep in mind).",
            reply_markup=self._main_keyboard(),
        )
        await state.set_state(TemplateStates.waiting_description)

    async def receive_description(self, message: types.Message, state: FSMContext) -> None:
        data = await state.get_data()
        template_text = data.get("template_text", "")
        description = message.text.strip()
        self.templates.set_template(user_id=message.from_user.id, template=template_text, description=description)
        await message.answer("Template saved ✅", reply_markup=self._main_keyboard())
        await state.clear()

    async def show_template(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        tpl = self.templates.get_template(message.from_user.id)
        if not tpl:
            await message.answer("No template saved yet. Tap 'Update template' to add one.", reply_markup=self._main_keyboard())
            return
        await message.answer(
            f"<b>Template</b>:\n{tpl.template}\n\n<b>Description</b>:\n{tpl.description}",
            reply_markup=self._main_keyboard(),
        )

    async def generate_response(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        tpl = self.templates.get_template(message.from_user.id)
        if not tpl:
            await message.answer("Please add a template first (tap 'Update template').", reply_markup=self._main_keyboard())
            return

        vacancy_text = message.text.strip()
        await message.answer("Working on it... ⏳", reply_markup=self._main_keyboard())

        try:
            reply_text = await self._call_yandex_llm(
                template=tpl.template,
                description=tpl.description,
                vacancy_text=vacancy_text,
            )
        except Exception as exc:
            await message.answer(f"Failed to generate text: {exc}")
            return

        await message.answer(reply_text, disable_web_page_preview=True, reply_markup=self._main_keyboard())

    async def _call_yandex_llm(self, template: str, description: str, vacancy_text: str) -> str:
        if not YANDEX_API_KEY:
            raise RuntimeError("YANDEX_API_KEY is not set")

        system_prompt = (
            "You are an assistant that crafts concise and polished application messages using a user-provided template. "
            "Respect the template wording. Insert only relevant details from the vacancy. Do not invent facts."
        )
        user_prompt = (
            f"Template:\n{template}\n\n"
            f"Template description/constraints:\n{description}\n\n"
            f"Vacancy details to adapt to the template:\n{vacancy_text}\n\n"
            "Return only the final crafted message."
        )

        payload = {
            "modelUri": YANDEX_MODEL_URI,
            "completionOptions": {
                "stream": False,
                "temperature": 0.2,
                "maxTokens": 800,
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-folder-id": YANDEX_FOLDER_ID,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        try:
            return data["result"]["alternatives"][0]["message"]["text"].strip()
        except Exception:
            raise RuntimeError(f"Unexpected response from Yandex LLM: {data}")

    async def run(self) -> None:
        await self.dp.start_polling(self.bot)


async def main() -> None:
    bot = VacancyBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

