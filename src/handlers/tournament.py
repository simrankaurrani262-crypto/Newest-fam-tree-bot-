"""
Tournament System Handlers
Commands: /tournament, /jointournament, /tournamentstatus, /tournamentleaderboard
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService

router = Router()
economy_service = EconomyService()

# Tournament storage
active_tournaments = {}
tournament_participants = {}


@router.message(Command("tournament"))
@require_user()
@rate_limit("tournament", 10, 60)
@handle_errors()
async def tournament_command(message: types.Message, db_user=None):
    """Show tournament info"""
    if not active_tournaments:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Create Tournament", callback_data="tournament_create")]
        ])
        return await message.reply(
            "🏆 <b>No Active Tournaments</b>\n\n"
            "Create or join a tournament to compete for prizes!",
            reply_markup=keyboard
        )
    
    text = "🏆 <b>Active Tournaments</b>\n\n"
    
    for tour_id, tournament in active_tournaments.items():
        text += f"<b>{tournament['name']}</b>\n"
        text += f"Type: {tournament['type']}\n"
        text += f"Prize Pool: ${tournament['prize_pool']:,}\n"
        text += f"Participants: {len(tournament_participants.get(tour_id, []))}\n"
        text += f"Entry Fee: ${tournament['entry_fee']:,}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Join Tournament", callback_data="tournament_join")],
        [InlineKeyboardButton(text="📊 Leaderboard", callback_data="tournament_lb")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("createtournament"))
@require_user()
@rate_limit("createtournament", 1, 86400)
@handle_errors()
async def createtournament_command(message: types.Message, db_user=None):
    """Create a new tournament"""
    args = message.text.split(maxsplit=3)
    
    if len(args) < 4:
        return await message.reply(
            "❌ Usage: <code>/createtournament [name] [type] [prize]</code>\n"
            "Types: combat, garden, trivia\n"
            "Example: <code>/createtournament WinterWar combat 100000</code>\n\n"
            "💰 Cost: 10% of prize pool"
        )
    
    name = args[1]
    tour_type = args[2].lower()
    try:
        prize = int(args[3])
    except:
        return await message.reply("❌ Invalid prize amount!")
    
    if tour_type not in ["combat", "garden", "trivia"]:
        return await message.reply("❌ Invalid tournament type!")
    
    cost = prize // 10
    
    # Check funds
    balance = await economy_service.get_balance(db_user.id)
    if balance < cost:
        return await message.reply(f"❌ You need ${cost} to create this tournament!")
    
    # Deduct cost
    await economy_service.deduct_money(db_user.id, cost)
    
    # Create tournament
    tour_id = f"tour_{len(active_tournaments)}"
    active_tournaments[tour_id] = {
        "name": name,
        "type": tour_type,
        "prize_pool": prize,
        "entry_fee": prize // 100,
        "creator": db_user.id,
        "status": "open",
        "created_at": "2024-01-01"
    }
    tournament_participants[tour_id] = []
    
    await message.reply(
        f"🏆 <b>Tournament Created!</b>\n\n"
        f"Name: {name}\n"
        f"Type: {tour_type.title()}\n"
        f"Prize Pool: ${prize:,}\n"
        f"Entry Fee: ${prize // 100:,}\n"
        f"💰 Cost: ${cost:,}\n\n"
        f"Others can join with <code>/jointournament {tour_id}</code>!"
    )


@router.message(Command("jointournament"))
@require_user()
@rate_limit("jointournament", 5, 3600)
@handle_errors()
async def jointournament_command(message: types.Message, db_user=None):
    """Join a tournament"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/jointournament [tournament_id]</code>\n"
            "Use <code>/tournament</code> to see available tournaments."
        )
    
    tour_id = args[1]
    
    if tour_id not in active_tournaments:
        return await message.reply("❌ Tournament not found!")
    
    tournament = active_tournaments[tour_id]
    
    # Check if already joined
    if db_user.id in tournament_participants.get(tour_id, []):
        return await message.reply("❌ You already joined this tournament!")
    
    # Check entry fee
    entry_fee = tournament["entry_fee"]
    balance = await economy_service.get_balance(db_user.id)
    
    if balance < entry_fee:
        return await message.reply(f"❌ You need ${entry_fee} entry fee!")
    
    # Deduct entry fee
    await economy_service.deduct_money(db_user.id, entry_fee)
    
    # Add to prize pool
    tournament["prize_pool"] += entry_fee // 2
    
    # Add participant
    if tour_id not in tournament_participants:
        tournament_participants[tour_id] = []
    tournament_participants[tour_id].append(db_user.id)
    
    await message.reply(
        f"✅ <b>Joined Tournament!</b>\n\n"
        f"Tournament: {tournament['name']}\n"
        f"Entry Fee: ${entry_fee:,}\n"
        f"Prize Pool: ${tournament['prize_pool']:,}\n\n"
        f"Good luck! 🍀"
    )


@router.message(Command("tournamentstatus"))
@require_user()
@handle_errors()
async def tournamentstatus_command(message: types.Message, db_user=None):
    """Check tournament status"""
    # Find user's tournament
    user_tournament = None
    for tour_id, participants in tournament_participants.items():
        if db_user.id in participants:
            user_tournament = tour_id
            break
    
    if not user_tournament:
        return await message.reply("❌ You are not in any tournament!")
    
    tournament = active_tournaments[user_tournament]
    participants = tournament_participants[user_tournament]
    
    text = f"🏆 <b>{tournament['name']}</b>\n\n"
    text += f"Status: {tournament['status'].title()}\n"
    text += f"Type: {tournament['type'].title()}\n"
    text += f"Participants: {len(participants)}\n"
    text += f"Prize Pool: ${tournament['prize_pool']:,}\n\n"
    
    # Show user's rank
    # In production, this would calculate actual rank
    text += "Your current rank: #?\n"
    text += "Keep competing to climb the leaderboard!"
    
    await message.reply(text)


@router.message(Command("tournamentleaderboard"))
@require_user()
@handle_errors()
async def tournamentleaderboard_command(message: types.Message, db_user=None):
    """Show tournament leaderboard"""
    args = message.text.split()
    
    tour_id = args[1] if len(args) > 1 else None
    
    if not tour_id and active_tournaments:
        tour_id = list(active_tournaments.keys())[0]
    
    if not tour_id or tour_id not in active_tournaments:
        return await message.reply("❌ Tournament not found!")
    
    tournament = active_tournaments[tour_id]
    participants = tournament_participants.get(tour_id, [])
    
    text = f"🏆 <b>{tournament['name']} - Leaderboard</b>\n\n"
    
    # Show top participants
    for i in range(min(10, len(participants))):
        from src.services.user_service import UserService
        user_service = UserService()
        user = await user_service.get_user_by_id(participants[i])
        name = user.display_name if user else f"Player{i+1}"
        
        medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, f"{i+1}.")
        text += f"{medal} {name} - {1000 - i*50} pts\n"
    
    text += f"\n💰 Prize Pool: ${tournament['prize_pool']:,}"
    
    await message.reply(text)
