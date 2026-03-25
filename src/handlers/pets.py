"""
Pet System Handlers
Commands: /pet, /buypet, /feedpet, /playpet, /petshop
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService

router = Router()
economy_service = EconomyService()

# Pet definitions
PETS = {
    "dog": {"name": "Dog", "emoji": "🐕", "price": 5000, "happiness": 100},
    "cat": {"name": "Cat", "emoji": "🐈", "price": 5000, "happiness": 100},
    "rabbit": {"name": "Rabbit", "emoji": "🐇", "price": 3000, "happiness": 100},
    "parrot": {"name": "Parrot", "emoji": "🦜", "price": 4000, "happiness": 100},
    "hamster": {"name": "Hamster", "emoji": "🐹", "price": 2000, "happiness": 100},
    "fox": {"name": "Fox", "emoji": "🦊", "price": 8000, "happiness": 100},
    "panda": {"name": "Panda", "emoji": "🐼", "price": 10000, "happiness": 100}
}

# User pets storage
user_pets = {}


@router.message(Command("petshop"))
@require_user()
@rate_limit("petshop", 10, 60)
@handle_errors()
async def petshop_command(message: types.Message, db_user=None):
    """Show pet shop"""
    text = "🐾 <b>Pet Shop</b>\n\n"
    
    for pet_id, pet in PETS.items():
        text += f"{pet['emoji']} <b>{pet['name']}</b>\n"
        text += f"   💰 Price: ${pet['price']:,}\n"
        text += f"   😊 Happiness: {pet['happiness']}\n\n"
    
    text += "💡 Use <code>/buypet [pet]</code> to purchase!"
    
    await message.reply(text)


@router.message(Command("buypet"))
@require_user()
@rate_limit("buypet", 3, 86400)
@handle_errors()
async def buypet_command(message: types.Message, db_user=None):
    """Buy a pet"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/buypet [pet]</code>\n"
            "Use <code>/petshop</code> to see available pets."
        )
    
    pet_id = args[1].lower()
    
    if pet_id not in PETS:
        return await message.reply(f"❌ Pet '{pet_id}' not found!")
    
    pet = PETS[pet_id]
    
    # Check if already has pet
    if db_user.id in user_pets:
        return await message.reply("❌ You already have a pet! Use /pet to see it.")
    
    # Check funds
    balance = await economy_service.get_balance(db_user.id)
    if balance < pet["price"]:
        return await message.reply(f"❌ You need ${pet['price']:,} to buy this pet!")
    
    # Deduct cost
    await economy_service.deduct_money(db_user.id, pet["price"])
    
    # Give pet
    user_pets[db_user.id] = {
        "type": pet_id,
        "name": pet["name"],
        "emoji": pet["emoji"],
        "happiness": 100,
        "hunger": 100,
        "level": 1,
        "xp": 0
    }
    
    await message.reply(
        f"🎉 <b>Pet Purchased!</b>\n\n"
        f"{pet['emoji']} You got a {pet['name']}!\n"
        f"💰 Cost: ${pet['price']:,}\n\n"
        f"Take care of your new pet with /pet!"
    )


@router.message(Command("pet"))
@require_user()
@rate_limit("pet", 10, 60)
@handle_errors()
async def pet_command(message: types.Message, db_user=None):
    """Show pet status"""
    if db_user.id not in user_pets:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🐾 Pet Shop", callback_data="pet_shop")]
        ])
        return await message.reply(
            "🐾 <b>You don't have a pet!</b>\n\n"
            "Buy a pet to have a loyal companion!",
            reply_markup=keyboard
        )
    
    pet = user_pets[db_user.id]
    
    # Calculate happiness bar
    happy_bar = "█" * (pet["happiness"] // 10) + "░" * (10 - pet["happiness"] // 10)
    hunger_bar = "█" * (pet["hunger"] // 10) + "░" * (10 - pet["hunger"] // 10)
    
    text = f"{pet['emoji']} <b>Your {pet['name']}</b>\n\n"
    text += f"😊 Happiness: [{happy_bar}] {pet['happiness']}%\n"
    text += f"🍖 Hunger: [{hunger_bar}] {pet['hunger']}%\n"
    text += f"⭐ Level: {pet['level']}\n"
    text += f"📊 XP: {pet['xp']}/{pet['level'] * 100}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍖 Feed", callback_data="pet_feed")],
        [InlineKeyboardButton(text="🎾 Play", callback_data="pet_play")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("feedpet"))
@require_user()
@rate_limit("feedpet", 20, 3600)
@handle_errors()
async def feedpet_command(message: types.Message, db_user=None):
    """Feed pet"""
    if db_user.id not in user_pets:
        return await message.reply("❌ You don't have a pet!")
    
    pet = user_pets[db_user.id]
    
    # Cost to feed
    feed_cost = 50
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < feed_cost:
        return await message.reply(f"❌ You need ${feed_cost} to feed your pet!")
    
    # Feed
    await economy_service.deduct_money(db_user.id, feed_cost)
    pet["hunger"] = min(100, pet["hunger"] + 20)
    pet["happiness"] = min(100, pet["happiness"] + 5)
    
    await message.reply(
        f"🍖 <b>Pet Fed!</b>\n\n"
        f"{pet['emoji']} Your {pet['name']} enjoyed the meal!\n"
        f"😊 Happiness: {pet['happiness']}%\n"
        f"🍖 Hunger: {pet['hunger']}%\n"
        f"💰 Cost: ${feed_cost}"
    )


@router.message(Command("playpet"))
@require_user()
@rate_limit("playpet", 20, 3600)
@handle_errors()
async def playpet_command(message: types.Message, db_user=None):
    """Play with pet"""
    if db_user.id not in user_pets:
        return await message.reply("❌ You don't have a pet!")
    
    pet = user_pets[db_user.id]
    
    # Check hunger
    if pet["hunger"] < 20:
        return await message.reply("❌ Your pet is too hungry to play! Feed it first.")
    
    # Play
    pet["happiness"] = min(100, pet["happiness"] + 15)
    pet["hunger"] = max(0, pet["hunger"] - 10)
    pet["xp"] += 10
    
    # Level up
    if pet["xp"] >= pet["level"] * 100:
        pet["level"] += 1
        pet["xp"] = 0
        level_up = f"\n🎉 Your pet leveled up to level {pet['level']}!"
    else:
        level_up = ""
    
    await message.reply(
        f"🎾 <b>Play Time!</b>\n\n"
        f"{pet['emoji']} Your {pet['name']} had fun playing!\n"
        f"😊 Happiness: {pet['happiness']}%\n"
        f"📊 XP: {pet['xp']}/{pet['level'] * 100}{level_up}"
    )
