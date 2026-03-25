"""
Referral System Handlers
Commands: /refer, /myrefs, /refbonus
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import REFERRAL_REWARD_REFERRER, REFERRAL_REWARD_REFERRED

router = Router()
economy_service = EconomyService()

# Referral storage
referrals = {}  # referrer_id -> [referred_ids]
referral_claimed = set()  # users who claimed referral bonus


@router.message(Command("refer"))
@router.message(Command("referral"))
@require_user()
@rate_limit("refer", 10, 60)
@handle_errors()
async def refer_command(message: types.Message, db_user=None):
    """Get referral link"""
    bot_username = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{db_user.telegram_id}"
    
    # Count referrals
    ref_count = len(referrals.get(db_user.id, []))
    
    text = f"🔗 <b>Your Referral Link</b>\n\n"
    text += f"<code>{referral_link}</code>\n\n"
    text += f"📊 Referrals: {ref_count}\n\n"
    text += f"<b>Rewards:</b>\n"
    text += f"• You get: ${REFERRAL_REWARD_REFERRER:,} per referral\n"
    text += f"• Friend gets: ${REFERRAL_REWARD_REFERRED:,} bonus\n\n"
    text += "Share your link with friends and earn together!"
    
    await message.reply(text)


@router.message(Command("myrefs"))
@router.message(Command("myreferrals"))
@require_user()
@rate_limit("myrefs", 10, 60)
@handle_errors()
async def myrefs_command(message: types.Message, db_user=None):
    """Show my referrals"""
    my_referrals = referrals.get(db_user.id, [])
    
    text = f"👥 <b>Your Referrals</b>\n\n"
    text += f"Total Referrals: {len(my_referrals)}\n\n"
    
    if my_referrals:
        text += "<b>Referred Users:</b>\n"
        for i, ref_id in enumerate(my_referrals[:20], 1):
            from src.services.user_service import UserService
            user_service = UserService()
            user = await user_service.get_user_by_id(ref_id)
            name = user.display_name if user else f"User{ref_id}"
            text += f"{i}. {name}\n"
        
        # Calculate total earned
        total_earned = len(my_referrals) * REFERRAL_REWARD_REFERRER
        text += f"\n💰 Total Earned: ${total_earned:,}"
    else:
        text += "<i>No referrals yet!</i>\n\n"
        text += "Share your referral link with /refer!"
    
    await message.reply(text)


@router.message(Command("refbonus"))
@require_user()
@rate_limit("refbonus", 1, 86400)
@handle_errors()
async def refbonus_command(message: types.Message, db_user=None):
    """Claim referral bonus"""
    # Check if user was referred
    # In production, this would check the referral tracking
    
    if db_user.id in referral_claimed:
        return await message.reply("❌ You already claimed your referral bonus!")
    
    # Give bonus
    await economy_service.add_money(db_user.id, REFERRAL_REWARD_REFERRED)
    referral_claimed.add(db_user.id)
    
    await message.reply(
        f"🎉 <b>Referral Bonus Claimed!</b>\n\n"
        f"💰 You received: ${REFERRAL_REWARD_REFERRED:,}\n\n"
        f"Welcome to Fam Tree Bot! 🌳"
    )


@router.message(Command("toprefs"))
@require_user()
@handle_errors()
async def toprefs_command(message: types.Message, db_user=None):
    """Show top referrers"""
    # Sort by referral count
    sorted_refs = sorted(
        referrals.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:10]
    
    text = "🏆 <b>Top Referrers</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user_id, refs) in enumerate(sorted_refs, 1):
        from src.services.user_service import UserService
        user_service = UserService()
        user = await user_service.get_user_by_id(user_id)
        name = user.display_name if user else f"User{user_id}"
        
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {name} - {len(refs)} referrals\n"
    
    await message.reply(text)
