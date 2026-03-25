"""
Orders System Handlers
Commands: /orders, /completeorder, /orderboard
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import CROPS
from src.database.connection import get_session
from src.database.repositories.barn_repo import BarnRepository
from src.database.repositories.garden_repo import GardenRepository

router = Router()
economy_service = EconomyService()

# Orders storage
active_orders = {}
completed_orders = {}


@router.message(Command("orders"))
@router.message(Command("order"))
@require_user()
@rate_limit("orders", 10, 60)
@handle_errors()
async def orders_command(message: types.Message, db_user=None):
    """Show available orders"""
    # Generate orders if none exist
    if not active_orders:
        import random
        for i in range(5):
            crop = random.choice(list(CROPS.keys()))
            quantity = random.randint(5, 20)
            active_orders[f"order_{i}"] = {
                "crop": crop,
                "quantity": quantity,
                "reward": CROPS[crop]["order_price"] * quantity,
                "requester": "NPC_Merchant"
            }
    
    text = "📋 <b>Available Orders</b>\n\n"
    
    for order_id, order in active_orders.items():
        crop = CROPS[order["crop"]]
        text += f"<b>Order #{order_id.split('_')[1]}</b>\n"
        text += f"{crop['emoji']} {order['crop'].title()}: {order['quantity']}\n"
        text += f"💰 Reward: ${order['reward']:,}\n"
        text += f"Use <code>/completeorder {order_id.split('_')[1]}</code>\n\n"
    
    await message.reply(text)


@router.message(Command("completeorder"))
@require_user()
@rate_limit("completeorder", 10, 60)
@handle_errors()
async def completeorder_command(message: types.Message, db_user=None):
    """Complete an order"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/completeorder [order_id]</code>\n"
            "Use <code>/orders</code> to see available orders."
        )
    
    order_id = f"order_{args[1]}"
    
    if order_id not in active_orders:
        return await message.reply("❌ Order not found!")
    
    order = active_orders[order_id]
    
    # Check if user has crops
    async for session in get_session():
        barn_repo = BarnRepository(session)
        garden_repo = GardenRepository(session)
        
        barn = await barn_repo.get_by_user_id(db_user.id)
        
        if not await barn_repo.has_item(barn.id, order["crop"], order["quantity"]):
            return await message.reply(
                f"❌ You don't have enough {order['crop']}!")
        
        # Remove crops
        await barn_repo.remove_item(barn.id, order["crop"], order["quantity"])
        
        # Give reward
        await economy_service.add_money(db_user.id, order["reward"])
        
        # Track completed orders
        if db_user.id not in completed_orders:
            completed_orders[db_user.id] = 0
        completed_orders[db_user.id] += 1
        
        # Expand garden slot every 5 orders
        if completed_orders[db_user.id] % 5 == 0:
            garden = await garden_repo.get_by_user_id(db_user.id)
            if garden and garden.slots < garden.max_slots:
                await garden_repo.expand_garden(db_user.id, 1)
                bonus = "\n🎉 Garden slot expanded!"
            else:
                bonus = ""
        else:
            bonus = ""
        
        # Remove order
        del active_orders[order_id]
        
        await message.reply(
            f"✅ <b>Order Completed!</b>\n\n"
            f"Delivered: {order['quantity']}x {order['crop']}\n"
            f"💰 Reward: ${order['reward']:,}\n"
            f"📊 Orders Completed: {completed_orders[db_user.id]}{bonus}"
        )


@router.message(Command("orderboard"))
@require_user()
@handle_errors()
async def orderboard_command(message: types.Message, db_user=None):
    """Show order completion leaderboard"""
    if not completed_orders:
        return await message.reply(
            "📋 <b>Order Leaderboard</b>\n\n"
            "<i>No orders completed yet!</i>\n\n"
            "Be the first to complete orders!"
        )
    
    # Sort by completed orders
    sorted_users = sorted(
        completed_orders.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    text = "📋 <b>Order Leaderboard</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user_id, count) in enumerate(sorted_users, 1):
        from src.services.user_service import UserService
        user_service = UserService()
        user = await user_service.get_user_by_id(user_id)
        name = user.display_name if user else f"User{user_id}"
        
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {name} - {count} orders\n"
    
    await message.reply(text)
