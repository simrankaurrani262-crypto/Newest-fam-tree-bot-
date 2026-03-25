"""
Cooking System Handlers
Commands: /cook, /recipes, /kitchen, /contribute
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import RECIPES
from src.database.connection import get_session
from src.database.repositories.barn_repo import BarnRepository

router = Router()
economy_service = EconomyService()

# Active cooking sessions
active_cooking = {}


@router.message(Command("recipes"))
@require_user()
@rate_limit("recipes", 10, 60)
@handle_errors()
async def recipes_command(message: types.Message, db_user=None):
    """Show available recipes"""
    text = "📖 <b>Cooking Recipes</b>\n\n"
    
    for recipe_id, recipe in RECIPES.items():
        text += f"{recipe['emoji']} <b>{recipe_id.replace('_', ' ').title()}</b>\n"
        text += "   Ingredients:\n"
        
        for ingredient, amount in recipe["ingredients"].items():
            text += f"     • {ingredient}: {amount}\n"
        
        text += f"   ⏰ Time: {recipe['time_minutes']} minutes\n"
        text += f"   📦 Output: {recipe['output']}x\n\n"
    
    text += "💡 Use <code>/cook [recipe]</code> to start cooking!"
    
    await message.reply(text)


@router.message(Command("cook"))
@require_user()
@rate_limit("cook", 5, 300)
@handle_errors()
async def cook_command(message: types.Message, db_user=None):
    """Start cooking"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/cook [recipe]</code>\n"
            "Example: <code>/cook popcorn</code>\n\n"
            "Use <code>/recipes</code> to see available recipes."
        )
    
    recipe_id = args[1].lower()
    
    if recipe_id not in RECIPES:
        return await message.reply(f"❌ Recipe '{recipe_id}' not found! Use /recipes to see available recipes.")
    
    recipe = RECIPES[recipe_id]
    
    # Check ingredients
    async for session in get_session():
        barn_repo = BarnRepository(session)
        barn = await barn_repo.get_by_user_id(db_user.id)
        
        missing = []
        for ingredient, amount in recipe["ingredients"].items():
            if not await barn_repo.has_item(barn.id, ingredient, amount):
                missing.append(f"{ingredient} ({amount})")
        
        if missing:
            return await message.reply(
                f"❌ <b>Missing Ingredients!</b>\n\n"
                f"You need:\n" + "\n".join(f"  • {m}" for m in missing)
            )
        
        # Remove ingredients
        for ingredient, amount in recipe["ingredients"].items():
            await barn_repo.remove_item(barn.id, ingredient, amount)
    
    # Start cooking
    from datetime import datetime, timedelta
    ready_at = datetime.utcnow() + timedelta(minutes=recipe["time_minutes"])
    
    active_cooking[db_user.id] = {
        "recipe": recipe_id,
        "ready_at": ready_at,
        "contributors": [db_user.id]
    }
    
    await message.reply(
        f"🍳 <b>Cooking Started!</b>\n\n"
        f"Recipe: {recipe['emoji']} {recipe_id.replace('_', ' ').title()}\n"
        f"⏰ Ready in: {recipe['time_minutes']} minutes\n\n"
        f"Others can contribute ingredients with <code>/contribute</code>!"
    )


@router.message(Command("kitchen"))
@require_user()
@rate_limit("kitchen", 10, 60)
@handle_errors()
async def kitchen_command(message: types.Message, db_user=None):
    """Check cooking status"""
    if db_user.id not in active_cooking:
        return await message.reply(
            "🍳 <b>Kitchen is Empty</b>\n\n"
            "Start cooking with <code>/cook [recipe]</code>!"
        )
    
    cooking = active_cooking[db_user.id]
    recipe = RECIPES[cooking["recipe"]]
    
    from datetime import datetime
    time_left = (cooking["ready_at"] - datetime.utcnow()).total_seconds()
    
    if time_left <= 0:
        # Cooking done
        async for session in get_session():
            barn_repo = BarnRepository(session)
            barn = await barn_repo.get_by_user_id(db_user.id)
            
            # Add output to barn
            await barn_repo.add_item(barn.id, cooking["recipe"], recipe["output"], "recipe")
        
        del active_cooking[db_user.id]
        
        return await message.reply(
            f"✅ <b>Cooking Complete!</b>\n\n"
            f"{recipe['emoji']} {recipe['output']}x {cooking['recipe'].replace('_', ' ').title()} added to your barn!"
        )
    
    mins_left = int(time_left // 60) + 1
    
    text = f"🍳 <b>Cooking in Progress</b>\n\n"
    text += f"Recipe: {recipe['emoji']} {cooking['recipe'].replace('_', ' ').title()}\n"
    text += f"⏰ Time Left: {mins_left} minutes\n"
    text += f"👥 Contributors: {len(cooking['contributors'])}\n\n"
    text += "Use <code>/contribute</code> to help speed up cooking!"
    
    await message.reply(text)


@router.message(Command("contribute"))
@require_user()
@handle_errors()
async def contribute_command(message: types.Message, db_user=None):
    """Contribute to active cooking"""
    # Find active cooking session
    target_cooking = None
    target_user = None
    
    for user_id, cooking in active_cooking.items():
        if db_user.id not in cooking["contributors"]:
            target_cooking = cooking
            target_user = user_id
            break
    
    if not target_cooking:
        return await message.reply("❌ No active cooking to contribute to!")
    
    # Add contributor
    target_cooking["contributors"].append(db_user.id)
    
    # Reduce time
    from datetime import timedelta
    target_cooking["ready_at"] -= timedelta(minutes=2)
    
    # Reward contributor
    await economy_service.add_money(db_user.id, 100)
    
    await message.reply(
        f"✅ <b>Contributed!</b>\n\n"
        f"You helped speed up the cooking!\n"
        f"💰 Reward: $100\n"
        f"⏰ Cooking time reduced by 2 minutes!"
    )
