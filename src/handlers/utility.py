"""
Utility Commands Handlers
Commands: /help, /start, /about, /ping, /time
"""
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart

from src.core.decorators import require_user, rate_limit, handle_errors

router = Router()


@router.message(CommandStart())
@require_user(create_if_missing=True)
@handle_errors()
async def start_command(message: types.Message, db_user=None):
    """Start command"""
    text = f"🌳 <b>Welcome to Fam Tree Bot!</b>\n\n"
    text += f"Hello {message.from_user.first_name}!\n\n"
    
    text += "<b>Quick Start:</b>\n"
    text += "• /account - View your profile\n"
    text += "• /tree - View family tree\n"
    text += "• /garden - Manage your garden\n"
    text += "• /daily - Claim daily reward\n\n"
    
    text += "<b>Main Features:</b>\n"
    text += "🏠 Family System - Build your family tree\n"
    text += "👥 Friends - Connect with others\n"
    text += "💰 Economy - Earn and spend money\n"
    text += "⚔️ Combat - Rob and fight\n"
    text += "🌱 Garden - Grow crops\n"
    text += "🎮 Games - Play mini-games\n\n"
    
    text += "Use /help for all commands!"
    
    await message.reply(text)


@router.message(Command("help"))
@require_user()
@rate_limit("help", 5, 60)
@handle_errors()
async def help_command(message: types.Message, db_user=None):
    """Show help"""
    text = f"📚 <b>Fam Tree Bot Commands</b>\n\n"
    
    text += "<b>👤 Account:</b>\n"
    text += "• /account - View profile\n"
    text += "• /bank - Bank balance\n"
    text += "• /deposit [amount] - Deposit money\n"
    text += "• /withdraw [amount] - Withdraw money\n"
    text += "• /pay [amount] - Send money (reply)\n\n"
    
    text += "<b>🏠 Family:</b>\n"
    text += "• /tree - View family tree\n"
    text += "• /adopt - Adopt a user (reply)\n"
    text += "• /marry - Propose marriage (reply)\n"
    text += "• /divorce - Divorce spouse\n"
    text += "• /relations - View relationships\n\n"
    
    text += "<b>👥 Friends:</b>\n"
    text += "• /circle - Friend circle\n"
    text += "• /friend - Add friend (reply)\n"
    text += "• /unfriend - Remove friend (reply)\n\n"
    
    text += "<b>⚔️ Combat:</b>\n"
    text += "• /rob - Rob a user (reply)\n"
    text += "• /kill - Kill a user (reply)\n"
    text += "• /weapon - Weapon shop\n"
    text += "• /medical - Revive yourself\n\n"
    
    text += "<b>🌱 Garden:</b>\n"
    text += "• /garden - View garden\n"
    text += "• /add [qty] [crop] - Buy seeds\n"
    text += "• /plant [plot] [crop] - Plant seeds\n"
    text += "• /harvest - Harvest crops\n"
    text += "• /barn - View barn\n\n"
    
    text += "<b>💰 Rewards:</b>\n"
    text += "• /daily - Daily reward\n"
    text += "• /fuse - Fuse gemstones (reply)\n\n"
    
    text += "<b>🎮 Games:</b>\n"
    text += "• /4p - 4 Pics 1 Word\n"
    text += "• /ripple - Ripple betting\n"
    text += "• /lottery - Lottery\n\n"
    
    text += "<b>📊 Stats:</b>\n"
    text += "• /rich - Leaderboard\n"
    text += "• /graph - Balance graph\n"
    text += "• /stats - Your stats\n\n"
    
    text += "Use /help2 for more commands!"
    
    await message.reply(text)


@router.message(Command("help2"))
@require_user()
@rate_limit("help", 5, 60)
@handle_errors()
async def help2_command(message: types.Message, db_user=None):
    """Show more help"""
    text = f"📚 <b>More Commands</b>\n\n"
    
    text += "<b>🏭 Factory:</b>\n"
    text += "• /factory - View factory\n"
    text += "• /hire - Hire worker (reply)\n"
    text += "• /work - Start work cycle\n\n"
    
    text += "<b>🛒 Trading:</b>\n"
    text += "• /market - Global market\n"
    text += "• /stand - Create stand\n"
    text += "• /buy [crop] [qty] - Buy crops\n\n"
    
    text += "<b>🍳 Cooking:</b>\n"
    text += "• /cook - Start cooking\n"
    text += "• /recipes - View recipes\n\n"
    
    text += "<b>🛡️ Insurance:</b>\n"
    text += "• /insure - Buy insurance (reply)\n"
    text += "• /myinsurance - View insurances\n\n"
    
    text += "<b>⚙️ Settings:</b>\n"
    text += "• /language - Change language\n"
    text += "• /notifications - Toggle notifications\n\n"
    
    text += "<b>ℹ️ Info:</b>\n"
    text += "• /about - About bot\n"
    text += "• /ping - Check latency\n"
    text += "• /time - Current time"
    
    await message.reply(text)


@router.message(Command("about"))
@require_user()
@handle_errors()
async def about_command(message: types.Message, db_user=None):
    """About the bot"""
    text = f"🌳 <b>Fam Tree Bot</b>\n\n"
    text += "The Ultimate Family Simulation & Gardening RPG\n\n"
    
    text += "<b>Version:</b> 1.0.0\n"
    text += "<b>Developer:</b> Fam Tree Bot Team\n"
    text += "<b>License:</b> MIT\n\n"
    
    text += "<b>Features:</b>\n"
    text += "• Family Tree System\n"
    text += "• Friend Circle\n"
    text += "• Economy & Combat\n"
    text += "• Garden & Factory\n"
    text += "• Mini Games\n"
    text += "• Trading System\n\n"
    
    text += "🤖 Alpha: @fam_tree_bot\n"
    text += "🤖 Beta: @famtreebbot"
    
    await message.reply(text)


@router.message(Command("ping"))
@require_user()
@handle_errors()
async def ping_command(message: types.Message, db_user=None):
    """Check bot latency"""
    import time
    
    start = time.time()
    msg = await message.reply("🏓 Pong!")
    end = time.time()
    
    latency = (end - start) * 1000
    
    await msg.edit_text(f"🏓 <b>Pong!</b>\n\nLatency: {latency:.1f}ms")


@router.message(Command("time"))
@require_user()
@handle_errors()
async def time_command(message: types.Message, db_user=None):
    """Show current time"""
    now = datetime.utcnow()
    
    text = f"🕐 <b>Current Time</b>\n\n"
    text += f"UTC: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += f"Date: {now.strftime('%A, %B %d, %Y')}"
    
    await message.reply(text)
