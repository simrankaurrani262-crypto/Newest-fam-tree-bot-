"""
Money Rain Event Handlers
Commands: /moneyrain, /collectrain
"""
from aiogram import Router, types, F
from aiogram.filters import Command
import random
from datetime import datetime, timedelta

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import MONEY_RAIN_INTERVAL_HOURS, MONEY_RAIN_COLLECTORS, MONEY_RAIN_REWARD

router = Router()
economy_service = EconomyService()

# Money rain state
money_rain_active = False
money_rain_collected = set()
money_rain_end_time = None


@router.message(Command("moneyrain"))
@require_user()
@handle_errors()
async def moneyrain_command(message: types.Message, db_user=None):
    """Trigger or check money rain"""
    global money_rain_active, money_rain_collected, money_rain_end_time
    
    # Check if money rain is active
    if money_rain_active:
        time_left = (money_rain_end_time - datetime.utcnow()).total_seconds()
        
        if time_left > 0:
            if db_user.id in money_rain_collected:
                return await message.reply(
                    "🌧️ <b>Money Rain Active!</b>\n\n"
                    f"⏰ Time Left: {int(time_left)} seconds\n"
                    f"✅ You already collected!\n\n"
                    f"Wait for the next rain!"
                )
            
            return await message.reply(
                "🌧️ <b>Money Rain Active!</b>\n\n"
                f"⏰ Time Left: {int(time_left)} seconds\n"
                f"💰 Reward: ${MONEY_RAIN_REWARD}\n\n"
                f"Use <code>/collectrain</code> to grab some cash!"
            )
        else:
            # Reset
            money_rain_active = False
            money_rain_collected = set()
    
    # Start new money rain (admin only or random chance)
    import random
    if random.random() < 0.1:  # 10% chance
        money_rain_active = True
        money_rain_collected = set()
        money_rain_end_time = datetime.utcnow() + timedelta(minutes=5)
        
        await message.reply(
            "🌧️ <b>MONEY RAIN STARTED!</b> 🌧️\n\n"
            f"💰 ${MONEY_RAIN_REWARD} for the first {MONEY_RAIN_COLLECTORS} collectors!\n"
            f"⏰ Ends in 5 minutes!\n\n"
            f"Use <code>/collectrain</code> NOW!"
        )
    else:
        await message.reply(
            "☀️ <b>No Money Rain</b>\n\n"
            f"Money rain occurs randomly every few hours!\n"
            f"💰 Reward: ${MONEY_RAIN_REWARD}\n"
            f"👥 {MONEY_RAIN_COLLECTORS} collectors max\n\n"
            f"Stay active and don't miss it!"
        )


@router.message(Command("collectrain"))
@require_user()
@rate_limit("collectrain", 1, 300)
@handle_errors()
async def collectrain_command(message: types.Message, db_user=None):
    """Collect money from rain"""
    global money_rain_active, money_rain_collected
    
    if not money_rain_active:
        return await message.reply(
            "☀️ <b>No Money Rain</b>\n\n"
            "There's no active money rain right now!\n"
            "Use <code>/moneyrain</code> to check for rain."
        )
    
    # Check if already collected
    if db_user.id in money_rain_collected:
        return await message.reply(
            "❌ <b>Already Collected!</b>\n\n"
            "You already collected from this money rain!"
        )
    
    # Check if max collectors reached
    if len(money_rain_collected) >= MONEY_RAIN_COLLECTORS:
        return await message.reply(
            "❌ <b>Money Rain Ended!</b>\n\n"
            "All rewards have been collected!\n"
            "Wait for the next rain!"
        )
    
    # Check time
    time_left = (money_rain_end_time - datetime.utcnow()).total_seconds()
    if time_left <= 0:
        money_rain_active = False
        return await message.reply("❌ Money rain has ended!")
    
    # Give reward
    await economy_service.add_money(db_user.id, MONEY_RAIN_REWARD)
    money_rain_collected.add(db_user.id)
    
    remaining = MONEY_RAIN_COLLECTORS - len(money_rain_collected)
    
    await message.reply(
        f"🌧️ <b>Money Collected!</b> 🌧️\n\n"
        f"💰 You got: ${MONEY_RAIN_REWARD}\n"
        f"🏃 Remaining: {remaining} spots\n\n"
        f"Quick! Tell your friends!"
    )
