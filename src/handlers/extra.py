"""
Extra Features Handlers
Commands: /reaction, /invite, /report, /feedback
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import REACTIONS

router = Router()
economy_service = EconomyService()


@router.message(Command("reaction"))
@require_user()
@require_reply("Please reply to a user to send a reaction!")
@rate_limit("reaction", 20, 60)
@handle_errors()
async def reaction_command(message: types.Message, db_user=None):
    """Send a reaction to a user"""
    args = message.text.split()
    
    if len(args) < 2:
        reactions_list = ", ".join(REACTIONS.keys())
        return await message.reply(
            f"❌ Usage: <code>/reaction [type]</code>\n"
            f"Available: {reactions_list}"
        )
    
    reaction_type = args[1].lower()
    
    if reaction_type not in REACTIONS:
        return await message.reply("❌ Invalid reaction type!")
    
    target = message.reply_to_message.from_user
    reaction = REACTIONS[reaction_type]
    
    await message.reply(
        f"{reaction['emoji']} {db_user.display_name} {reaction_type}s {target.first_name}!"
    )


@router.message(Command("invite"))
@require_user()
@handle_errors()
async def invite_command(message: types.Message, db_user=None):
    """Get invite link"""
    bot_username = (await message.bot.get_me()).username
    invite_link = f"https://t.me/{bot_username}?start=ref_{db_user.telegram_id}"
    
    await message.reply(
        f"🔗 <b>Invite Friends!</b>\n\n"
        f"Share this link with friends:\n"
        f"<code>{invite_link}</code>\n\n"
        f"💰 Rewards:\n"
        f"• You: $5,000 per referral\n"
        f"• Friend: $10,000 bonus"
    )


@router.message(Command("report"))
@require_user()
@handle_errors()
async def report_command(message: types.Message, db_user=None):
    """Report a bug or issue"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/report [message]</code>\n"
            "Describe the issue you're experiencing."
        )
    
    report_text = args[1]
    
    # TODO: Send report to admin channel
    
    await message.reply(
        f"✅ <b>Report Submitted!</b>\n\n"
        f"Thank you for your feedback. We'll look into it!"
    )


@router.message(Command("feedback"))
@require_user()
@handle_errors()
async def feedback_command(message: types.Message, db_user=None):
    """Send feedback"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/feedback [message]</code>\n"
            "Share your thoughts and suggestions!"
        )
    
    feedback_text = args[1]
    
    # TODO: Send feedback to admin channel
    
    await message.reply(
        f"✅ <b>Feedback Sent!</b>\n\n"
        f"Thank you for your feedback! 💚"
    )
