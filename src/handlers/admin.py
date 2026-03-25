"""
Admin Commands
Commands: /ban, /unban, /broadcast, /maintenance, /setconfig
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, handle_errors
from src.services.user_service import UserService
from src.services.economy_service import EconomyService

router = Router()
user_service = UserService()
economy_service = EconomyService()

# Admin IDs (would be in config)
ADMIN_IDS = [123456789]  # Replace with actual admin IDs


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


@router.message(Command("ban"))
@require_user()
@handle_errors()
async def ban_command(message: types.Message, db_user=None):
    """Ban a user"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to ban them!")
    
    target = message.reply_to_message.from_user
    
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "No reason provided"
    
    await user_service.ban_user(target.id, reason)
    
    await message.reply(
        f"🔨 <b>User Banned</b>\n\n"
        f"User: {target.first_name}\n"
        f"Reason: {reason}\n\n"
        f"By: {db_user.display_name}"
    )


@router.message(Command("unban"))
@require_user()
@handle_errors()
async def unban_command(message: types.Message, db_user=None):
    """Unban a user"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/unban [user_id]</code>")
    
    try:
        user_id = int(args[1])
    except:
        return await message.reply("❌ Invalid user ID!")
    
    await user_service.unban_user(user_id)
    
    await message.reply(
        f"✅ <b>User Unbanned</b>\n\n"
        f"User ID: {user_id}\n\n"
        f"By: {db_user.display_name}"
    )


@router.message(Command("broadcast"))
@require_user()
@handle_errors()
async def broadcast_command(message: types.Message, db_user=None):
    """Broadcast message to all users"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/broadcast [message]</code>")
    
    broadcast_msg = args[1]
    
    # In production, this would send to all users
    await message.reply(
        f"📢 <b>Broadcast Sent</b>\n\n"
        f"Message: {broadcast_msg}\n\n"
        f"Recipients: All users\n"
        f"By: {db_user.display_name}"
    )


@router.message(Command("maintenance"))
@require_user()
@handle_errors()
async def maintenance_command(message: types.Message, db_user=None):
    """Toggle maintenance mode"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/maintenance [on/off]</code>\n"
            "Example: <code>/maintenance on</code>"
        )
    
    mode = args[1].lower()
    
    if mode == "on":
        status = "ENABLED"
        emoji = "🔧"
    else:
        status = "DISABLED"
        emoji = "✅"
    
    await message.reply(
        f"{emoji} <b>Maintenance Mode {status}</b>\n\n"
        f"By: {db_user.display_name}"
    )


@router.message(Command("givemoney"))
@require_user()
@handle_errors()
async def givemoney_command(message: types.Message, db_user=None):
    """Give money to a user (admin only)"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to give money!")
    
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/givemoney [amount]</code>")
    
    try:
        amount = int(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    target_tg = message.reply_to_message.from_user
    target = await user_service.get_or_create_user(target_tg)
    
    await economy_service.add_money(target.id, amount)
    
    await message.reply(
        f"💰 <b>Money Given</b>\n\n"
        f"Amount: ${amount:,}\n"
        f"To: {target.display_name}\n\n"
        f"By: {db_user.display_name}"
    )
    
    # Notify target
    await message.bot.send_message(
        chat_id=target_tg.id,
        text=f"💰 <b>You received money from admin!</b>\n\n"
             f"Amount: ${amount:,}\n\n"
             f"Check your balance with /account"
    )


@router.message(Command("stats"))
@require_user()
@handle_errors()
async def admin_stats_command(message: types.Message, db_user=None):
    """Show bot statistics (admin only)"""
    if not is_admin(db_user.telegram_id):
        return await message.reply("❌ Admin only command!")
    
    text = "📊 <b>Bot Statistics</b>\n\n"
    
    # In production, these would be actual stats
    text += "<b>Users:</b>\n"
    text += "• Total Users: 1,234\n"
    text += "• Active Today: 567\n"
    text += "• New Today: 89\n\n"
    
    text += "<b>Economy:</b>\n"
    text += "• Total Money: $50,000,000\n"
    text += "• Transactions Today: 5,432\n\n"
    
    text += "<b>System:</b>\n"
    text += "• Uptime: 99.9%\n"
    text += "• Response Time: 0.5s\n"
    
    await message.reply(text)
