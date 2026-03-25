"""
Daily Rewards & Gemstones Handlers
Commands: /daily, /fuse
"""
import random
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors, log_command

from src.services.economy_service import EconomyService
from src.services.family_service import FamilyService
from src.core.constants import GEMSTONES, GEMSTONE_FUSE_REWARD
from src.core.state_machine import state_manager

router = Router()
economy_service = EconomyService()
family_service = FamilyService()


@router.message(Command("daily"))
@require_user()
@rate_limit("daily", 1, 86400)  # Once per day
@handle_errors()
@log_command()
async def daily_command(message: types.Message, db_user=None):
    """Claim daily reward"""
    # Get family count for bonus
    tree = await family_service.get_family_tree(db_user.id)
    family_count = len(tree["children"]) + len(tree["spouses"])
    
    # Get current streak (simplified - would track in DB)
    streak = 0  # TODO: Implement streak tracking
    
    # Give reward
    result = await economy_service.get_daily_reward(db_user.id, family_count, streak)
    
    text = f"✨ <b>Daily Reward Claimed!</b>\n\n"
    text += f"💰 Base: ${result['base']}\n"
    
    if result['family_bonus'] > 0:
        text += f"👨‍👩‍👧‍👦 Family Bonus: ${result['family_bonus']}\n"
    
    if result['streak_bonus'] > 0:
        text += f"🔥 Streak Bonus: ${result['streak_bonus']}\n"
    
    text += f"\n💎 <b>Total: ${result['total']}</b>\n\n"
    
    gemstone = result['gemstone']
    gem_emoji = GEMSTONES[gemstone]['emoji']
    text += f"💎 Gemstone: {gem_emoji} {gemstone.title()}\n\n"
    text += f"💡 Find someone with the same gemstone and use <code>/fuse</code>!"
    
    await message.reply(text)


@router.message(Command("fuse"))
@require_user()
@require_reply("Please reply to the user with matching gemstone!")
@rate_limit("fuse", 5, 86400)
@handle_errors()
@log_command()
async def fuse_command(message: types.Message, db_user=None):
    """Fuse gemstones with another user"""
    user1 = db_user
    user2_tg = message.reply_to_message.from_user
    
    # Get user2
    from src.services.user_service import UserService
    user_service = UserService()
    user2 = await user_service.get_or_create_user(user2_tg)
    
    # Check if same user
    if user1.id == user2.id:
        return await message.reply("❌ You cannot fuse with yourself!")
    
    # TODO: Check if both users have the same gemstone
    # For now, simulate success
    
    # Give reward to both
    await economy_service.add_money(user1.id, GEMSTONE_FUSE_REWARD)
    await economy_service.add_money(user2.id, GEMSTONE_FUSE_REWARD)
    
    await message.reply(
        f"💎 <b>Gemstones Fused!</b>\n\n"
        f"✨ You and {user2.display_name} fused your gemstones!\n"
        f"💰 Reward: ${GEMSTONE_FUSE_REWARD} each!"
    )
    
    # Notify user2
    await message.bot.send_message(
        chat_id=user2_tg.id,
        text=f"💎 <b>Gemstones Fused!</b>\n\n"
             f"✨ You and {user1.display_name} fused your gemstones!\n"
             f"💰 Reward: ${GEMSTONE_FUSE_REWARD}!"
    )
