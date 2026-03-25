"""
Achievements System Handlers
Commands: /achievements, /badges, /claimachievement
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.database.connection import get_session

router = Router()
economy_service = EconomyService()

# Achievement definitions
ACHIEVEMENTS = {
    "first_steps": {
        "name": "First Steps",
        "description": "Claim your first daily reward",
        "reward": 1000,
        "emoji": "👶",
        "requirement": 1
    },
    "family_man": {
        "name": "Family Man",
        "description": "Have 5 family members",
        "reward": 5000,
        "emoji": "👨‍👩‍👧‍👦",
        "requirement": 5
    },
    "richie_rich": {
        "name": "Richie Rich",
        "description": "Reach $100,000 balance",
        "reward": 10000,
        "emoji": "💰",
        "requirement": 100000
    },
    "master_farmer": {
        "name": "Master Farmer",
        "description": "Harvest 100 crops",
        "reward": 5000,
        "emoji": "🚜",
        "requirement": 100
    },
    "warrior": {
        "name": "Warrior",
        "description": "Win 10 combats",
        "reward": 5000,
        "emoji": "⚔️",
        "requirement": 10
    },
    "popular": {
        "name": "Popular",
        "description": "Have 20 friends",
        "reward": 3000,
        "emoji": "👥",
        "requirement": 20
    },
    "gambler": {
        "name": "Gambler",
        "description": "Play 50 games",
        "reward": 2000,
        "emoji": "🎰",
        "requirement": 50
    },
    "loyal": {
        "name": "Loyal Player",
        "description": "7 day login streak",
        "reward": 7000,
        "emoji": "🔥",
        "requirement": 7
    },
    "collector": {
        "name": "Collector",
        "description": "Own all 8 weapons",
        "reward": 10000,
        "emoji": "🔫",
        "requirement": 8
    },
    "businessman": {
        "name": "Businessman",
        "description": "Complete 50 trades",
        "reward": 5000,
        "emoji": "💼",
        "requirement": 50
    }
}

# User achievements storage
user_achievements = {}
user_stats = {}


@router.message(Command("achievements"))
@router.message(Command("ach"))
@require_user()
@rate_limit("achievements", 10, 60)
@handle_errors()
async def achievements_command(message: types.Message, db_user=None):
    """Show achievements"""
    user_id = db_user.id
    
    if user_id not in user_achievements:
        user_achievements[user_id] = set()
    
    text = "🏆 <b>Achievements</b>\n\n"
    
    # Unlocked achievements
    unlocked = user_achievements[user_id]
    if unlocked:
        text += "<b>✅ Unlocked:</b>\n"
        for ach_id in unlocked:
            ach = ACHIEVEMENTS.get(ach_id, {})
            text += f"{ach.get('emoji', '🏆')} {ach.get('name', 'Unknown')}\n"
        text += "\n"
    
    # Locked achievements
    text += "<b>🔒 Locked:</b>\n"
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id not in unlocked:
            text += f"⬜ {ach['name']} - {ach['description']}\n"
            text += f"   💰 Reward: ${ach['reward']:,}\n\n"
    
    await message.reply(text)


@router.message(Command("badges"))
@require_user()
@rate_limit("badges", 10, 60)
@handle_errors()
async def badges_command(message: types.Message, db_user=None):
    """Show earned badges"""
    user_id = db_user.id
    
    if user_id not in user_achievements:
        user_achievements[user_id] = set()
    
    unlocked = user_achievements[user_id]
    
    if not unlocked:
        return await message.reply(
            "🏅 <b>No Badges Yet!</b>\n\n"
            "Complete achievements to earn badges!\n"
            "Use <code>/achievements</code> to see available achievements."
        )
    
    text = "🏅 <b>Your Badges</b>\n\n"
    
    for ach_id in unlocked:
        ach = ACHIEVEMENTS.get(ach_id, {})
        text += f"{ach.get('emoji', '🏆')} <b>{ach['name']}</b>\n"
        text += f"   {ach['description']}\n"
        text += f"   💰 Reward: ${ach['reward']:,}\n\n"
    
    await message.reply(text)


@router.message(Command("claimachievement"))
@require_user()
@handle_errors()
async def claimachievement_command(message: types.Message, db_user=None):
    """Claim achievement reward"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/claimachievement [achievement_id]</code>\n"
            "Use <code>/achievements</code> to see available IDs."
        )
    
    ach_id = args[1].lower()
    user_id = db_user.id
    
    if ach_id not in ACHIEVEMENTS:
        return await message.reply("❌ Invalid achievement ID!")
    
    if user_id not in user_achievements:
        user_achievements[user_id] = set()
    
    if ach_id in user_achievements[user_id]:
        return await message.reply("❌ You already claimed this achievement!")
    
    # Check if user meets requirements (simplified)
    # In production, this would check actual stats
    ach = ACHIEVEMENTS[ach_id]
    
    # For demo, auto-unlock
    user_achievements[user_id].add(ach_id)
    
    # Give reward
    await economy_service.add_money(user_id, ach["reward"])
    
    await message.reply(
        f"🎉 <b>Achievement Unlocked!</b>\n\n"
        f"{ach['emoji']} <b>{ach['name']}</b>\n"
        f"{ach['description']}\n\n"
        f"💰 Reward: ${ach['reward']:,}\n"
        f"Total Achievements: {len(user_achievements[user_id])}"
    )


@router.message(Command("leaderboard"))
@require_user()
@rate_limit("leaderboard", 10, 60)
@handle_errors()
async def leaderboard_command(message: types.Message, db_user=None):
    """Show achievement leaderboard"""
    # Sort users by achievement count
    sorted_users = sorted(
        user_achievements.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:10]
    
    text = "🏆 <b>Achievement Leaderboard</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user_id, achievements) in enumerate(sorted_users, 1):
        user = await user_service.get_user_by_id(user_id)
        name = user.display_name if user else f"User{user_id}"
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {name} - {len(achievements)} achievements\n"
    
    await message.reply(text)
