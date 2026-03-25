"""
Statistics & Leaderboards Handlers
Commands: /rich, /graph, /stats, /activity
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.database.repositories.economy_repo import EconomyRepository
from src.database.connection import get_session

router = Router()
economy_service = EconomyService()
user_service = UserService()


@router.message(Command("rich"))
@router.message(Command("top"))
@router.message(Command("leaderboard"))
@require_user()
@rate_limit("rich", 10, 60)
@handle_errors()
async def rich_command(message: types.Message, db_user=None):
    """Show money leaderboard"""
    leaderboard = await economy_service.get_leaderboard(10)
    
    text = f"🏆 <b>Money Leaderboard</b>\n\n"
    
    for i, (economy, user) in enumerate(leaderboard, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        text += f"{medal} {user.display_name}: ${economy.balance:,.0f}\n"
    
    await message.reply(text)


@router.message(Command("graph"))
@require_user()
@rate_limit("graph", 5, 60)
@handle_errors()
async def graph_command(message: types.Message, db_user=None):
    """Show balance graph"""
    # TODO: Implement actual graph generation with matplotlib
    balance = await economy_service.get_balance(db_user.id)
    bank = await economy_service.get_bank_balance(db_user.id)
    net_worth = await economy_service.get_net_worth(db_user.id)
    
    # Simple ASCII bar chart
    max_val = max(balance, bank, net_worth) or 1
    
    bar_length = 20
    balance_bar = int((balance / max_val) * bar_length)
    bank_bar = int((bank / max_val) * bar_length)
    net_bar = int((net_worth / max_val) * bar_length)
    
    text = f"📊 <b>Balance Graph</b>\n\n"
    text += f"💳 Wallet: [{'█' * balance_bar}{'░' * (bar_length - balance_bar)}] ${balance:,.0f}\n"
    text += f"🏦 Bank:   [{'█' * bank_bar}{'░' * (bar_length - bank_bar)}] ${bank:,.0f}\n"
    text += f"💎 Total:  [{'█' * net_bar}{'░' * (bar_length - net_bar)}] ${net_worth:,.0f}\n"
    
    await message.reply(text)


@router.message(Command("stats"))
@require_user()
@rate_limit("stats", 10, 60)
@handle_errors()
async def stats_command(message: types.Message, db_user=None):
    """Show user statistics"""
    async for session in get_session():
        economy_repo = EconomyRepository(session)
        economy = await economy_repo.get_by_user_id(db_user.id)
        
        if not economy:
            return await message.reply("❌ No stats available!")
        
        text = f"📊 <b>Your Statistics</b>\n\n"
        
        text += f"💰 Total Earned: ${economy.total_earned:,.0f}\n"
        text += f"💸 Total Spent: ${economy.total_spent:,.0f}\n"
        text += f"⭐ Reputation: {economy.reputation}/200\n"
        text += f"❤️ Health: {economy.health}/5\n\n"
        
        text += f"📅 Daily Streak: {economy.daily_streak} days\n"
        text += f"💼 Job: {economy.current_job.title()}\n"
        text += f"🔫 Equipped Weapon: {economy.equipped_weapon or 'Punch'}\n\n"
        
        text += f"🦹 Robberies Today: {economy.robbery_count_today}/8\n"
        text += f"💀 Kills Today: {economy.kill_count_today}/5"
        
        await message.reply(text)


@router.message(Command("activity"))
@require_user()
@rate_limit("activity", 5, 60)
@handle_errors()
async def activity_command(message: types.Message, db_user=None):
    """Show activity stats"""
    # TODO: Implement activity tracking
    await message.reply(
        "📈 <b>Activity Stats</b>\n\n"
        "<i>Activity tracking coming soon!</i>\n\n"
        "Track your:\n"
        "• Commands used\n"
        "• Time spent\n"
        "• Most active hours"
    )
