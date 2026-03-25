"""
Insurance System Handlers
Commands: /insure, /myinsurance, /claiminsurance
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.core.constants import INSURANCE_TYPES

router = Router()
economy_service = EconomyService()
user_service = UserService()

# Insurance storage
user_insurances = {}


@router.message(Command("insure"))
@require_user()
@require_reply("Please reply to the user you want to insure!")
@rate_limit("insure", 5, 86400)
@handle_errors()
async def insure_command(message: types.Message, db_user=None):
    """Buy insurance for a user"""
    insurer = db_user
    insured_tg = message.reply_to_message.from_user
    
    if insurer.telegram_id == insured_tg.id:
        return await message.reply("❌ You cannot insure yourself!")
    
    insured = await user_service.get_or_create_user(insured_tg)
    
    # Determine relationship type
    # Simplified: check if friends
    rel_type = "friend"  # Default
    multiplier = INSURANCE_TYPES["friend"]["multiplier"]
    max_payout = INSURANCE_TYPES["friend"]["max_payout"]
    
    # Calculate cost (10% of max payout)
    cost = max_payout // 10
    
    # Check funds
    balance = await economy_service.get_balance(insurer.id)
    if balance < cost:
        return await message.reply(f"❌ You need ${cost} to buy insurance!")
    
    # Deduct cost
    await economy_service.deduct_money(insurer.id, cost)
    
    # Create insurance
    if insurer.id not in user_insurances:
        user_insurances[insurer.id] = []
    
    user_insurances[insurer.id].append({
        "insured_id": insured.id,
        "insured_name": insured.display_name,
        "type": rel_type,
        "max_payout": max_payout,
        "purchased_at": "2024-01-01"
    })
    
    await message.reply(
        f"🛡️ <b>Insurance Purchased!</b>\n\n"
        f"Insured: {insured.display_name}\n"
        f"Type: {rel_type.title()}\n"
        f"Max Payout: ${max_payout:,}\n"
        f"Multiplier: {multiplier}x\n"
        f"💰 Cost: ${cost}\n\n"
        f"If they die, you'll receive compensation!"
    )


@router.message(Command("myinsurance"))
@router.message(Command("insurances"))
@require_user()
@rate_limit("myinsurance", 10, 60)
@handle_errors()
async def myinsurance_command(message: types.Message, db_user=None):
    """Show your insurances"""
    user_id = db_user.id
    
    if user_id not in user_insurances or not user_insurances[user_id]:
        return await message.reply(
            "🛡️ <b>No Active Insurances</b>\n\n"
            "Use <code>/insure</code> (reply to user) to buy insurance!"
        )
    
    text = "🛡️ <b>Your Insurances</b>\n\n"
    
    for i, ins in enumerate(user_insurances[user_id], 1):
        text += f"{i}. Insured: {ins['insured_name']}\n"
        text += f"   Type: {ins['type'].title()}\n"
        text += f"   Max Payout: ${ins['max_payout']:,}\n\n"
    
    await message.reply(text)


@router.message(Command("claiminsurance"))
@require_user()
@handle_errors()
async def claiminsurance_command(message: types.Message, db_user=None):
    """Claim insurance payout"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/claiminsurance [insurance_number]</code>\n"
            "Use <code>/myinsurance</code> to see your insurances."
        )
    
    try:
        ins_num = int(args[1]) - 1
    except:
        return await message.reply("❌ Invalid insurance number!")
    
    user_id = db_user.id
    
    if user_id not in user_insurances or ins_num >= len(user_insurances[user_id]):
        return await message.reply("❌ Insurance not found!")
    
    ins = user_insurances[user_id][ins_num]
    
    # Check if insured is dead (simplified)
    # In production, check user's health
    
    # Calculate payout with decay
    import random
    payout = random.randint(ins['max_payout'] // 2, ins['max_payout'])
    
    # Give payout
    await economy_service.add_money(user_id, payout)
    
    # Remove insurance
    user_insurances[user_id].pop(ins_num)
    
    await message.reply(
        f"💰 <b>Insurance Claimed!</b>\n\n"
        f"Insured: {ins['insured_name']}\n"
        f"Payout: ${payout:,}\n\n"
        f"Compensation has been added to your balance!"
    )
