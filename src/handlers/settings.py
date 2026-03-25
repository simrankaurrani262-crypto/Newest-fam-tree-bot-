"""
Settings Handlers
Commands: /language, /notifications
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.user_service import UserService
from src.core.constants import SUPPORTED_LANGUAGES

router = Router()
user_service = UserService()


@router.message(Command("language"))
@require_user()
@rate_limit("language", 5, 60)
@handle_errors()
async def language_command(message: types.Message, db_user=None):
    """Change language"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for lang in SUPPORTED_LANGUAGES:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=lang.upper(),
                callback_data=f"lang_{lang}"
            )
        ])
    
    await message.reply(
        "🌐 <b>Select Language</b>\n\n"
        f"Current: {db_user.language.upper()}\n\n"
        "Choose your preferred language:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("lang_"))
@handle_errors()
async def language_callback(callback: types.CallbackQuery):
    """Handle language selection"""
    lang = callback.data.split("_")[1]
    
    await user_service.set_language(callback.from_user.id, lang)
    
    await callback.message.edit_text(
        f"✅ <b>Language Updated!</b>\n\n"
        f"Language set to: {lang.upper()}"
    )
    
    await callback.answer()


@router.message(Command("notifications"))
@require_user()
@handle_errors()
async def notifications_command(message: types.Message, db_user=None):
    """Toggle notifications"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ On", callback_data="notif_on"),
            InlineKeyboardButton(text="❌ Off", callback_data="notif_off")
        ]
    ])
    
    await message.reply(
        "🔔 <b>Notifications</b>\n\n"
        "Toggle game notifications:\n"
        "• Daily reminders\n"
        "• Crop ready alerts\n"
        "• Friend activity\n\n"
        "Current: Enabled",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("notif_"))
@handle_errors()
async def notifications_callback(callback: types.CallbackQuery):
    """Handle notification toggle"""
    state = callback.data.split("_")[1]
    
    status = "Enabled" if state == "on" else "Disabled"
    
    await callback.message.edit_text(
        f"🔔 <b>Notifications</b>\n\n"
        f"Status: {status}"
    )
    
    await callback.answer()
