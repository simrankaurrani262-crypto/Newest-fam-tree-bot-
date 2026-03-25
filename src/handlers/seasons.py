"""
Seasons & Events Handlers
Commands: /season, /event, /eventinfo
"""
from aiogram import Router, types, F
from aiogram.filters import Command
import random

from src.core.decorators import require_user, rate_limit, handle_errors
from src.core.constants import SEASONS

router = Router()

# Current season
current_season = "spring"
active_events = {}


@router.message(Command("season"))
@require_user()
@rate_limit("season", 10, 60)
@handle_errors()
async def season_command(message: types.Message, db_user=None):
    """Show current season"""
    global current_season
    
    season_emoji = {
        "spring": "🌸",
        "summer": "☀️",
        "autumn": "🍂",
        "winter": "❄️",
        "cloudy": "☁️"
    }
    
    season_bonuses = {
        "spring": "Pepper crops grow 2x faster!",
        "summer": "All crops need less water!",
        "autumn": "Potato crops grow 2x faster!",
        "winter": "Carrot crops grow 2x faster!",
        "cloudy": "Eggplant crops grow 2x faster!"
    }
    
    text = f"{season_emoji.get(current_season, '🌤️')} <b>Current Season: {current_season.title()}</b>\n\n"
    text += f"🌱 <b>Season Bonus:</b>\n"
    text += f"{season_bonuses.get(current_season, 'No special bonus')}\n\n"
    text += f"📅 Seasons change every week!\n"
    text += f"Plan your farming accordingly!"
    
    await message.reply(text)


@router.message(Command("event"))
@require_user()
@rate_limit("event", 10, 60)
@handle_errors()
async def event_command(message: types.Message, db_user=None):
    """Show active events"""
    if not active_events:
        # Generate random event
        events = [
            {
                "name": "Double XP Weekend",
                "description": "Earn 2x XP from all activities!",
                "bonus": "2x XP",
                "emoji": "⭐"
            },
            {
                "name": "Harvest Festival",
                "description": "Crop prices are doubled!",
                "bonus": "2x Crop Prices",
                "emoji": "🌾"
            },
            {
                "name": "Combat Weekend",
                "description": "Robbery and kill rewards doubled!",
                "bonus": "2x Combat Rewards",
                "emoji": "⚔️"
            },
            {
                "name": "Lucky Day",
                "description": "All game win chances increased!",
                "bonus": "Better Odds",
                "emoji": "🍀"
            }
        ]
        
        import random
        event = random.choice(events)
        
        text = f"{event['emoji']} <b>Active Event: {event['name']}</b>\n\n"
        text += f"📜 {event['description']}\n"
        text += f"🎁 Bonus: {event['bonus']}\n\n"
        text += f"⏰ Event ends in 24 hours!"
    else:
        text = "📅 <b>Active Events</b>\n\n"
        for event_id, event in active_events.items():
            text += f"{event['emoji']} <b>{event['name']}</b>\n"
            text += f"{event['description']}\n\n"
    
    await message.reply(text)


@router.message(Command("eventinfo"))
@require_user()
@handle_errors()
async def eventinfo_command(message: types.Message, db_user=None):
    """Show event information"""
    text = "📅 <b>Event Schedule</b>\n\n"
    
    text += "<b>Weekly Events:</b>\n"
    text += "• Monday: Market Monday (2x trade profits)\n"
    text += "• Wednesday: Warrior Wednesday (2x combat XP)\n"
    text += "• Friday: Farming Friday (2x crop yields)\n"
    text += "• Weekend: Double XP Weekend\n\n"
    
    text += "<b>Monthly Events:</b>\n"
    text += "• First Week: Clan War Tournament\n"
    text += "• Mid-Month: Lottery Jackpot\n"
    text += "• Last Week: Season Change Celebration\n\n"
    
    text += "Stay active to catch all events!"
    
    await message.reply(text)
