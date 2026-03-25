"""
Notification Settings Handlers
Commands: /notifications, /setnotify, /notifytest
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors

router = Router()

# User notification settings
user_notifications = {}


@router.message(Command("notifications"))
@router.message(Command("notify"))
@require_user()
@rate_limit("notifications", 10, 60)
@handle_errors()
async def notifications_command(message: types.Message, db_user=None):
    """Show notification settings"""
    user_id = db_user.id
    
    if user_id not in user_notifications:
        user_notifications[user_id] = {
            "daily": True,
            "crop_ready": True,
            "friend_activity": True,
            "combat": True,
            "events": True
        }
    
    settings = user_notifications[user_id]
    
    text = "🔔 <b>Notification Settings</b>\n\n"
    
    for setting, enabled in settings.items():
        status = "✅ On" if enabled else "❌ Off"
        text += f"{setting.replace('_', ' ').title()}: {status}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Daily Rewards", callback_data="notify_daily")],
        [InlineKeyboardButton(text="Crop Ready", callback_data="notify_crop")],
        [InlineKeyboardButton(text="Friend Activity", callback_data="notify_friend")],
        [InlineKeyboardButton(text="Combat", callback_data="notify_combat")],
        [InlineKeyboardButton(text="Events", callback_data="notify_events")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("notify_"))
@handle_errors()
async def notify_callback(callback: types.CallbackQuery):
    """Toggle notification setting"""
    setting = callback.data.replace("notify_", "")
    user_id = callback.from_user.id
    
    if user_id not in user_notifications:
        user_notifications[user_id] = {
            "daily": True,
            "crop_ready": True,
            "friend_activity": True,
            "combat": True,
            "events": True
        }
    
    # Toggle setting
    if setting == "crop":
        setting = "crop_ready"
    elif setting == "friend":
        setting = "friend_activity"
    
    if setting in user_notifications[user_id]:
        user_notifications[user_id][setting] = not user_notifications[user_id][setting]
        status = "enabled" if user_notifications[user_id][setting] else "disabled"
        await callback.answer(f"{setting.replace('_', ' ').title()} notifications {status}!")
    
    # Update display
    settings = user_notifications[user_id]
    text = "🔔 <b>Notification Settings</b>\n\n"
    
    for s, enabled in settings.items():
        status = "✅ On" if enabled else "❌ Off"
        text += f"{s.replace('_', ' ').title()}: {status}\n"
    
    await callback.message.edit_text(text)


@router.message(Command("setnotify"))
@require_user()
@handle_errors()
async def setnotify_command(message: types.Message, db_user=None):
    """Set notification preference"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/setnotify [type] [on/off]</code>\n"
            "Types: daily, crop, friend, combat, events\n"
            "Example: <code>/setnotify daily on</code>"
        )
    
    notify_type = args[1].lower()
    state = args[2].lower()
    
    if notify_type not in ["daily", "crop", "friend", "combat", "events"]:
        return await message.reply("❌ Invalid notification type!")
    
    if state not in ["on", "off"]:
        return await message.reply("❌ Use 'on' or 'off'!")
    
    user_id = db_user.id
    
    if user_id not in user_notifications:
        user_notifications[user_id] = {
            "daily": True,
            "crop_ready": True,
            "friend_activity": True,
            "combat": True,
            "events": True
        }
    
    # Map type
    type_map = {
        "crop": "crop_ready",
        "friend": "friend_activity"
    }
    notify_type = type_map.get(notify_type, notify_type)
    
    user_notifications[user_id][notify_type] = (state == "on")
    
    await message.reply(
        f"🔔 <b>Notification Updated</b>\n\n"
        f"{notify_type.replace('_', ' ').title()}: {state.upper()}"
    )


@router.message(Command("notifytest"))
@require_user()
@handle_errors()
async def notifytest_command(message: types.Message, db_user=None):
    """Test notifications"""
    await message.reply(
        "🔔 <b>Test Notification</b>\n\n"
        "This is a test notification!\n\n"
        "If you see this, notifications are working! ✅"
    )
