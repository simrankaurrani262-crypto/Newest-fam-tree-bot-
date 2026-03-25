"""
Clan System Handlers
Commands: /clan, /createclan, /joinclan, /leaveclan, /clanwar, /clandeposit, /clanwithdraw
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors, log_command
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.database.connection import get_session

router = Router()
economy_service = EconomyService()
user_service = UserService()

# In-memory clan storage (would be in DB in production)
clans = {}
clan_members = {}


@router.message(Command("clan"))
@require_user()
@rate_limit("clan", 10, 60)
@handle_errors()
async def clan_command(message: types.Message, db_user=None):
    """Show clan info"""
    user_clan = None
    for clan_id, members in clan_members.items():
        if db_user.id in members:
            user_clan = clan_id
            break
    
    if not user_clan:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Create Clan", callback_data="clan_create")],
            [InlineKeyboardButton(text="🔍 Join Clan", callback_data="clan_join")]
        ])
        return await message.reply(
            "🏰 <b>You are not in a clan!</b>\n\n"
            "Create or join a clan to participate in clan wars and earn bonuses!",
            reply_markup=keyboard
        )
    
    clan = clans.get(user_clan, {})
    members = clan_members.get(user_clan, [])
    
    text = f"🏰 <b>{clan.get('name', 'Unknown Clan')}</b>\n\n"
    text += f"📜 {clan.get('description', 'No description')}\n\n"
    text += f"👑 Leader: {clan.get('leader_name', 'Unknown')}\n"
    text += f"👥 Members: {len(members)}/{clan.get('max_members', 50)}\n"
    text += f"💰 Treasury: ${clan.get('treasury', 0):,}\n"
    text += f"⚔️ Wars Won: {clan.get('wars_won', 0)}\n"
    text += f"🏆 Clan Level: {clan.get('level', 1)}\n\n"
    
    text += "<b>Member List:</b>\n"
    for member_id in members[:10]:
        member = await user_service.get_user_by_id(member_id)
        if member:
            text += f"  • {member.display_name}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Deposit", callback_data="clan_deposit")],
        [InlineKeyboardButton(text="⚔️ Clan War", callback_data="clan_war")],
        [InlineKeyboardButton(text="🚪 Leave Clan", callback_data="clan_leave")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("createclan"))
@require_user()
@rate_limit("createclan", 1, 86400)
@handle_errors()
@log_command()
async def createclan_command(message: types.Message, db_user=None):
    """Create a new clan"""
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/createclan [name] [description]</code>\n"
            "Example: <code>/createclan Dragons We are the fire!</code>\n\n"
            "💰 Cost: $100,000"
        )
    
    clan_name = args[1]
    description = args[2] if len(args) > 2 else "No description"
    
    # Check if user already in clan
    for members in clan_members.values():
        if db_user.id in members:
            return await message.reply("❌ You are already in a clan! Leave first with /leaveclan")
    
    # Check funds
    balance = await economy_service.get_balance(db_user.id)
    if balance < 100000:
        return await message.reply("❌ You need $100,000 to create a clan!")
    
    # Deduct cost
    await economy_service.deduct_money(db_user.id, 100000)
    
    # Create clan
    clan_id = f"clan_{db_user.id}_{len(clans)}"
    clans[clan_id] = {
        "name": clan_name,
        "description": description,
        "leader_id": db_user.id,
        "leader_name": db_user.display_name,
        "treasury": 0,
        "wars_won": 0,
        "level": 1,
        "max_members": 50,
        "created_at": "2024-01-01"
    }
    clan_members[clan_id] = [db_user.id]
    
    await message.reply(
        f"🏰 <b>Clan Created!</b>\n\n"
        f"Name: {clan_name}\n"
        f"Description: {description}\n"
        f"💰 Cost: $100,000\n\n"
        f"Use <code>/clan</code> to manage your clan!"
    )


@router.message(Command("joinclan"))
@require_user()
@rate_limit("joinclan", 3, 3600)
@handle_errors()
async def joinclan_command(message: types.Message, db_user=None):
    """Join a clan"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/joinclan [clan_name]</code>\n"
            "Example: <code>/joinclan Dragons</code>"
        )
    
    clan_name = args[1]
    
    # Check if user already in clan
    for members in clan_members.values():
        if db_user.id in members:
            return await message.reply("❌ You are already in a clan!")
    
    # Find clan
    target_clan = None
    for clan_id, clan in clans.items():
        if clan["name"].lower() == clan_name.lower():
            target_clan = clan_id
            break
    
    if not target_clan:
        return await message.reply(f"❌ Clan '{clan_name}' not found!")
    
    # Check if clan is full
    if len(clan_members[target_clan]) >= clans[target_clan]["max_members"]:
        return await message.reply("❌ This clan is full!")
    
    # Add member
    clan_members[target_clan].append(db_user.id)
    
    await message.reply(
        f"✅ <b>Joined Clan!</b>\n\n"
        f"You are now a member of {clans[target_clan]['name']}!\n\n"
        f"Use <code>/clan</code> to view clan info!"
    )


@router.message(Command("leaveclan"))
@require_user()
@handle_errors()
async def leaveclan_command(message: types.Message, db_user=None):
    """Leave current clan"""
    user_clan = None
    for clan_id, members in clan_members.items():
        if db_user.id in members:
            user_clan = clan_id
            break
    
    if not user_clan:
        return await message.reply("❌ You are not in a clan!")
    
    # Check if leader
    if clans[user_clan]["leader_id"] == db_user.id:
        return await message.reply(
            "❌ You are the clan leader!\n"
            "Transfer leadership or disband the clan first."
        )
    
    # Remove member
    clan_members[user_clan].remove(db_user.id)
    
    await message.reply(
        f"✅ <b>Left Clan!</b>\n\n"
        f"You have left {clans[user_clan]['name']}."
    )


@router.message(Command("clanwar"))
@require_user()
@rate_limit("clanwar", 1, 86400)
@handle_errors()
async def clanwar_command(message: types.Message, db_user=None):
    """Start clan war"""
    user_clan = None
    for clan_id, members in clan_members.items():
        if db_user.id in members:
            user_clan = clan_id
            break
    
    if not user_clan:
        return await message.reply("❌ You are not in a clan!")
    
    # Check if leader
    if clans[user_clan]["leader_id"] != db_user.id:
        return await message.reply("❌ Only the clan leader can start wars!")
    
    # Find opponent clan
    opponent_clan = None
    for clan_id in clans:
        if clan_id != user_clan:
            opponent_clan = clan_id
            break
    
    if not opponent_clan:
        return await message.reply("❌ No opponent clans available!")
    
    # Simulate war
    import random
    user_power = len(clan_members[user_clan]) * random.randint(10, 50)
    opponent_power = len(clan_members[opponent_clan]) * random.randint(10, 50)
    
    if user_power > opponent_power:
        clans[user_clan]["wars_won"] += 1
        clans[user_clan]["treasury"] += 50000
        result = "🏆 VICTORY!"
        reward = "$50,000 added to treasury!"
    else:
        result = "😢 DEFEAT!"
        reward = "Better luck next time!"
    
    await message.reply(
        f"⚔️ <b>Clan War Result</b>\n\n"
        f"{clans[user_clan]['name']} vs {clans[opponent_clan]['name']}\n\n"
        f"Your Power: {user_power}\n"
        f"Opponent Power: {opponent_power}\n\n"
        f"{result}\n"
        f"{reward}"
    )


@router.message(Command("clandeposit"))
@require_user()
@handle_errors()
async def clandeposit_command(message: types.Message, db_user=None):
    """Deposit to clan treasury"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/clandeposit [amount]</code>")
    
    try:
        amount = int(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    user_clan = None
    for clan_id, members in clan_members.items():
        if db_user.id in members:
            user_clan = clan_id
            break
    
    if not user_clan:
        return await message.reply("❌ You are not in a clan!")
    
    # Check funds
    balance = await economy_service.get_balance(db_user.id)
    if balance < amount:
        return await message.reply("❌ Insufficient funds!")
    
    # Transfer
    await economy_service.deduct_money(db_user.id, amount)
    clans[user_clan]["treasury"] += amount
    
    await message.reply(
        f"✅ <b>Deposited to Clan!</b>\n\n"
        f"💰 Amount: ${amount:,}\n"
        f"🏰 Clan Treasury: ${clans[user_clan]['treasury']:,}"
    )


@router.message(Command("clanwithdraw"))
@require_user()
@handle_errors()
async def clanwithdraw_command(message: types.Message, db_user=None):
    """Withdraw from clan treasury (leader only)"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/clanwithdraw [amount]</code>")
    
    try:
        amount = int(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    user_clan = None
    for clan_id, members in clan_members.items():
        if db_user.id in members:
            user_clan = clan_id
            break
    
    if not user_clan:
        return await message.reply("❌ You are not in a clan!")
    
    # Check if leader
    if clans[user_clan]["leader_id"] != db_user.id:
        return await message.reply("❌ Only the clan leader can withdraw!")
    
    # Check treasury
    if clans[user_clan]["treasury"] < amount:
        return await message.reply("❌ Insufficient treasury funds!")
    
    # Transfer
    await economy_service.add_money(db_user.id, amount)
    clans[user_clan]["treasury"] -= amount
    
    await message.reply(
        f"✅ <b>Withdrawn from Clan!</b>\n\n"
        f"💰 Amount: ${amount:,}\n"
        f"🏰 Remaining Treasury: ${clans[user_clan]['treasury']:,}"
    )
