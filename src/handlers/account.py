"""
Account & Economy Handlers
Commands: /account, /profile, /bank, /deposit, /withdraw, /pay, /weapon
"""
from decimal import Decimal

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors, log_command
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.core.constants import WEAPONS

router = Router()
economy_service = EconomyService()
user_service = UserService()


@router.message(Command("account"))
@router.message(Command("profile"))
@router.message(Command("acc"))
@router.message(Command("me"))
@require_user()
@rate_limit("account", 10, 60)
@handle_errors()
@log_command()
async def account_command(message: types.Message, db_user=None):
    """Show user profile"""
    # Get economy data
    balance = await economy_service.get_balance(db_user.id)
    bank_balance = await economy_service.get_bank_balance(db_user.id)
    net_worth = await economy_service.get_net_worth(db_user.id)
    health = await economy_service.get_health(db_user.id)
    reputation = await economy_service.get_reputation(db_user.id)
    
    # Build profile text
    text = f"┌─────────────────────────────────┐\n"
    text += f"│     👤 USER PROFILE             │\n"
    text += f"├─────────────────────────────────┤\n"
    text += f"│  {db_user.display_name:<30} │\n"
    text += f"├─────────────────────────────────┤\n"
    text += f"│  💰 Balance: ${balance:>15,.0f}  │\n"
    text += f"│  🏦 Bank:    ${bank_balance:>15,.0f}  │\n"
    text += f"│  💎 Net:     ${net_worth:>15,.0f}  │\n"
    text += f"├─────────────────────────────────┤\n"
    text += f"│  ⭐ Reputation: {reputation}/200       │\n"
    text += f"│  ❤️ Health:     {'❤️' * health}{'🖤' * (5-health)}  │\n"
    text += f"├─────────────────────────────────┤\n"
    text += f"│  [🏦 Bank]  [⚔️ Weapons]        │\n"
    text += f"│  [🛡️ Insurance] [📊 Stats]      │\n"
    text += f"└─────────────────────────────────┘"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏦 Bank", callback_data="menu_bank"),
            InlineKeyboardButton(text="⚔️ Weapons", callback_data="menu_weapons")
        ],
        [
            InlineKeyboardButton(text="🛡️ Insurance", callback_data="menu_insurance"),
            InlineKeyboardButton(text="📊 Stats", callback_data="menu_stats")
        ]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("bank"))
@require_user()
@rate_limit("bank", 10, 60)
@handle_errors()
async def bank_command(message: types.Message, db_user=None):
    """Show bank balance"""
    balance = await economy_service.get_balance(db_user.id)
    bank_balance = await economy_service.get_bank_balance(db_user.id)
    
    text = f"🏦 <b>Bank Account</b>\n\n"
    text += f"💳 Wallet: ${balance:,.0f}\n"
    text += f"🏦 Bank:   ${bank_balance:,.0f}\n\n"
    text += f"💡 Use <code>/deposit [amount]</code> to save money\n"
    text += f"💡 Use <code>/withdraw [amount]</code> to take money out"
    
    await message.reply(text)


@router.message(Command("deposit"))
@require_user()
@rate_limit("deposit", 10, 60)
@handle_errors()
async def deposit_command(message: types.Message, db_user=None):
    """Deposit money to bank"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/deposit [amount]</code>\n"
            "Example: <code>/deposit 1000</code> or <code>/deposit all</code>"
        )
    
    amount_str = args[1].lower()
    
    if amount_str == "all":
        balance = await economy_service.get_balance(db_user.id)
        amount = balance
    else:
        try:
            amount = Decimal(amount_str)
        except:
            return await message.reply("❌ Invalid amount!")
    
    if amount <= 0:
        return await message.reply("❌ Amount must be positive!")
    
    try:
        new_balance, new_bank = await economy_service.deposit(db_user.id, amount)
        
        await message.reply(
            f"✅ <b>Deposited!</b>\n\n"
            f"💳 Wallet: ${new_balance:,.0f}\n"
            f"🏦 Bank:   ${new_bank:,.0f}"
        )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")


@router.message(Command("withdraw"))
@require_user()
@rate_limit("withdraw", 10, 60)
@handle_errors()
async def withdraw_command(message: types.Message, db_user=None):
    """Withdraw money from bank"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/withdraw [amount]</code>\n"
            "Example: <code>/withdraw 1000</code> or <code>/withdraw all</code>"
        )
    
    amount_str = args[1].lower()
    
    if amount_str == "all":
        bank_balance = await economy_service.get_bank_balance(db_user.id)
        amount = bank_balance
    else:
        try:
            amount = Decimal(amount_str)
        except:
            return await message.reply("❌ Invalid amount!")
    
    if amount <= 0:
        return await message.reply("❌ Amount must be positive!")
    
    try:
        new_balance, new_bank = await economy_service.withdraw(db_user.id, amount)
        
        await message.reply(
            f"✅ <b>Withdrawn!</b>\n\n"
            f"💳 Wallet: ${new_balance:,.0f}\n"
            f"🏦 Bank:   ${new_bank:,.0f}"
        )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")


@router.message(Command("pay"))
@require_user()
@rate_limit("pay", 20, 60)
@handle_errors()
async def pay_command(message: types.Message, db_user=None):
    """Transfer money to another user"""
    if not message.reply_to_message:
        return await message.reply("❌ Please reply to the user you want to pay!")
    
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/pay [amount]</code> (reply to user)\n"
            "Example: <code>/pay 1000</code> or <code>/pay 5+3</code>"
        )
    
    # Parse amount (support simple math)
    amount_str = args[1]
    try:
        # Evaluate simple expressions
        amount = Decimal(str(eval(amount_str)))
    except:
        return await message.reply("❌ Invalid amount!")
    
    if amount <= 0:
        return await message.reply("❌ Amount must be positive!")
    
    target_tg = message.reply_to_message.from_user
    target = await user_service.get_or_create_user(target_tg)
    
    try:
        await economy_service.transfer(db_user.id, target.id, amount)
        
        await message.reply(
            f"✅ <b>Payment Sent!</b>\n\n"
            f"💸 ${amount:,.0f} sent to {target.display_name}"
        )
        
        # Notify recipient
        await message.bot.send_message(
            chat_id=target_tg.id,
            text=f"💰 <b>You received money!</b>\n\n"
                 f"${amount:,.0f} from {db_user.display_name}"
        )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")


@router.message(Command("weapon"))
@require_user()
@rate_limit("weapon", 10, 60)
@handle_errors()
async def weapon_command(message: types.Message, db_user=None):
    """Show weapon menu"""
    text = f"⚔️ <b>Weapon Shop</b>\n\n"
    
    for name, weapon in WEAPONS.items():
        text += f"{weapon['emoji']} <b>{name.title()}</b>\n"
        text += f"   💰 Price: ${weapon['price']:,}\n"
        text += f"   🦹 Rob Power: {weapon['rob_power']}\n"
        text += f"   💀 Kill Power: {weapon['kill_power']}\n\n"
    
    text += "💡 Use <code>/buy [weapon]</code> to purchase"
    
    await message.reply(text)


@router.message(Command("medical"))
@require_user()
@rate_limit("medical", 5, 60)
@handle_errors()
async def medical_command(message: types.Message, db_user=None):
    """Self-revive using medical"""
    from src.core.constants import MEDICAL_COST
    
    health = await economy_service.get_health(db_user.id)
    
    if health > 0:
        return await message.reply(
            f"❌ You are already alive!\n"
            f"❤️ Health: {health}/5"
        )
    
    try:
        new_health = await economy_service.medical(db_user.id)
        
        await message.reply(
            f"🏥 <b>Revived!</b>\n\n"
            f"❤️ Health: {new_health}/5\n"
            f"💰 Cost: ${MEDICAL_COST}"
        )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")
