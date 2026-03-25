"""
Trading System Handlers
Commands: /market, /stand, /buy
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors, log_command
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.database.repositories.trading_repo import TradingRepository
from src.database.repositories.barn_repo import BarnRepository
from src.database.connection import get_session
from src.core.constants import CROPS

router = Router()
economy_service = EconomyService()
user_service = UserService()


@router.message(Command("market"))
@require_user()
@rate_limit("market", 10, 60)
@handle_errors()
async def market_command(message: types.Message, db_user=None):
    """Show global market"""
    async for session in get_session():
        trading_repo = TradingRepository(session)
        
        stands = await trading_repo.get_all_stands()
        
        text = f"🛒 <b>Global Market</b>\n\n"
        
        if stands:
            for stand in stands[:10]:  # Show first 10
                seller = await user_service.get_user_by_id(stand.seller_id)
                crop_emoji = CROPS.get(stand.crop_type, {}).get("emoji", "🌾")
                
                text += f"{crop_emoji} {stand.crop_type.title()} x{stand.quantity}\n"
                text += f"   💰 ${stand.price_per_unit:,.0f}/unit (${stand.total_price:,.0f} total)\n"
                text += f"   👤 Seller: {seller.display_name if seller else 'Unknown'}\n\n"
        else:
            text += "<i>No active stands. Create one with /stand!</i>\n\n"
        
        text += "💡 Use <code>/buy [crop] [qty]</code> to purchase"
        
        await message.reply(text)


@router.message(Command("stand"))
@require_user()
@rate_limit("stand", 5, 60)
@handle_errors()
@log_command()
async def stand_command(message: types.Message, db_user=None):
    """Create a market stand"""
    args = message.text.split()
    
    if len(args) < 4:
        return await message.reply(
            "❌ Usage: <code>/stand [crop] [qty] [price_per_unit]</code>\n"
            "Example: <code>/stand corn 10 50</code>"
        )
    
    crop_type = args[1].lower()
    
    try:
        quantity = int(args[2])
        price_per_unit = int(args[3])
    except:
        return await message.reply("❌ Invalid quantity or price!")
    
    if crop_type not in CROPS:
        return await message.reply(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
    
    async for session in get_session():
        barn_repo = BarnRepository(session)
        trading_repo = TradingRepository(session)
        
        barn = await barn_repo.get_by_user_id(db_user.id)
        
        # Check if has enough crops
        if not await barn_repo.has_item(barn.id, crop_type, quantity):
            return await message.reply(f"❌ You don't have enough {crop_type} in your barn!")
        
        # Remove from barn
        await barn_repo.remove_item(barn.id, crop_type, quantity)
        
        # Create stand
        await trading_repo.create_stand(db_user.id, crop_type, quantity, price_per_unit)
        
        await message.reply(
            f"✅ <b>Stand Created!</b>\n\n"
            f"🌾 {CROPS[crop_type]['emoji']} {crop_type.title()} x{quantity}\n"
            f"💰 Price: ${price_per_unit}/unit\n"
            f"📦 Total: ${price_per_unit * quantity}\n\n"
            f"Your crops are now on the market!"
        )


@router.message(Command("buy"))
@require_user()
@rate_limit("buy", 20, 60)
@handle_errors()
async def buy_command(message: types.Message, db_user=None):
    """Buy from market"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/buy [crop] [qty]</code>\n"
            "Example: <code>/buy corn 5</code>"
        )
    
    crop_type = args[1].lower()
    
    try:
        quantity = int(args[2])
    except:
        return await message.reply("❌ Invalid quantity!")
    
    if crop_type not in CROPS:
        return await message.reply(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
    
    async for session in get_session():
        trading_repo = TradingRepository(session)
        barn_repo = BarnRepository(session)
        
        # Find cheapest stand with enough quantity
        stand = await trading_repo.find_cheapest(crop_type, quantity)
        
        if not stand:
            return await message.reply(f"❌ No stands selling {quantity}x {crop_type}!")
        
        total_price = stand.price_per_unit * quantity
        
        # Check funds
        balance = await economy_service.get_balance(db_user.id)
        if balance < total_price:
            return await message.reply(f"❌ You need ${total_price}!")
        
        # Transfer money
        seller = await user_service.get_user_by_id(stand.seller_id)
        await economy_service.deduct_money(db_user.id, total_price)
        await economy_service.add_money(seller.id, total_price)
        
        # Add to buyer's barn
        barn = await barn_repo.get_by_user_id(db_user.id)
        await barn_repo.add_item(barn.id, crop_type, quantity, "crop")
        
        # Update or remove stand
        if stand.quantity == quantity:
            await trading_repo.delete_stand(stand.id)
        else:
            await trading_repo.update_quantity(stand.id, stand.quantity - quantity)
        
        await message.reply(
            f"✅ <b>Purchase Complete!</b>\n\n"
            f"🌾 {CROPS[crop_type]['emoji']} {crop_type.title()} x{quantity}\n"
            f"💰 Total: ${total_price}\n"
            f"👤 Seller: {seller.display_name if seller else 'Unknown'}"
        )
