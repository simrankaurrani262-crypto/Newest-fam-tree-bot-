"""
Garden System Handlers
Commands: /garden, /add, /plant, /harvest, /barn, /boost
"""
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors, log_command
from src.services.garden_service import GardenService
from src.services.user_service import UserService
from src.database.repositories.garden_repo import GardenRepository
from src.database.repositories.barn_repo import BarnRepository
from src.database.connection import get_session
from src.core.constants import CROPS, SEASON_BONUS, BOOST_COST, BOOST_TIME_REDUCTION

router = Router()
garden_service = GardenService()
user_service = UserService()


@router.message(Command("garden"))
@require_user()
@rate_limit("garden", 10, 60)
@handle_errors()
@log_command()
async def garden_command(message: types.Message, db_user=None):
    """Show garden"""
    async for session in get_session():
        garden_repo = GardenRepository(session)
        garden = await garden_repo.get_by_user_id(db_user.id)
        
        if not garden:
            garden = await garden_repo.create_for_user(db_user.id)
        
        plots = await garden_repo.get_plots(garden.user_id)
        
        text = f"🌱 <b>Your Garden - {garden.season.title()}</b>\n\n"
        
        # Build 3x3 grid display
        for row in range(3):
            row_text = ""
            for col in range(3):
                plot_num = row * 3 + col + 1
                plot = next((p for p in plots if p.plot_number == plot_num), None)
                
                if not plot or plot.is_empty:
                    row_text += "⬜ "
                elif plot.is_ready:
                    crop_emoji = CROPS.get(plot.crop_type, {}).get("emoji", "🌾")
                    row_text += f"{crop_emoji} "
                else:
                    mins_left = plot.time_remaining // 60
                    row_text += f"[{mins_left}m] "
            
            text += row_text + "\n"
        
        text += f"\n📊 Slots: {len(plots)}/{garden.slots}\n"
        text += f"🌤️ Season: {garden.season.title()}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌱 Plant", callback_data="garden_plant"),
                InlineKeyboardButton(text="🚜 Harvest", callback_data="garden_harvest")
            ],
            [
                InlineKeyboardButton(text="⚡ Boost", callback_data="garden_boost"),
                InlineKeyboardButton(text="🏚️ Barn", callback_data="garden_barn")
            ]
        ])
        
        await message.reply(text, reply_markup=keyboard)


@router.message(Command("add"))
@require_user()
@rate_limit("add", 20, 60)
@handle_errors()
async def add_command(message: types.Message, db_user=None):
    """Buy seeds"""
    args = message.text.split()
    
    if len(args) < 3:
        crops_list = ", ".join(CROPS.keys())
        return await message.reply(
            f"❌ Usage: <code>/add [quantity] [crop]</code>\n"
            f"Example: <code>/add 5 corn</code>\n\n"
            f"Available crops: {crops_list}"
        )
    
    try:
        quantity = int(args[1])
    except:
        return await message.reply("❌ Invalid quantity!")
    
    crop_type = args[2].lower()
    
    if crop_type not in CROPS:
        return await message.reply(f"❌ Invalid crop type! Available: {', '.join(CROPS.keys())}")
    
    crop = CROPS[crop_type]
    total_cost = crop["buy_price"] * quantity
    
    # Check funds and add to barn
    from src.services.economy_service import EconomyService
    economy_service = EconomyService()
    
    try:
        await economy_service.deduct_money(db_user.id, total_cost)
        
        async for session in get_session():
            barn_repo = BarnRepository(session)
            barn = await barn_repo.get_by_user_id(db_user.id)
            
            if not barn:
                barn = await barn_repo.create_for_user(db_user.id)
            
            await barn_repo.add_item(barn.id, crop_type, quantity, "crop")
        
        await message.reply(
            f"✅ <b>Purchased!</b>\n\n"
            f"🌱 {quantity}x {crop['emoji']} {crop_type.title()}\n"
            f"💰 Cost: ${total_cost}\n\n"
            f"Use <code>/plant</code> to plant them!"
        )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")


@router.message(Command("plant"))
@require_user()
@rate_limit("plant", 20, 60)
@handle_errors()
async def plant_command(message: types.Message, db_user=None):
    """Plant crops"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/plant [plot] [crop]</code> or <code>/plant * [crop]</code>\n"
            "Example: <code>/plant 3 corn</code> or <code>/plant * tomato</code>"
        )
    
    plot_str = args[1]
    crop_type = args[2].lower()
    
    if crop_type not in CROPS:
        return await message.reply(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
    
    async for session in get_session():
        garden_repo = GardenRepository(session)
        barn_repo = BarnRepository(session)
        
        garden = await garden_repo.get_by_user_id(db_user.id)
        barn = await barn_repo.get_by_user_id(db_user.id)
        
        # Check if has seeds
        if not await barn_repo.has_item(barn.id, crop_type, 1):
            return await message.reply(f"❌ You don't have any {crop_type} seeds! Buy with /add")
        
        crop = CROPS[crop_type]
        
        # Calculate grow time
        grow_hours = crop["growth_hours"]
        
        # Season bonus
        if garden.season == crop["season"] or crop["season"] == "all":
            grow_hours /= SEASON_BONUS
        
        ready_at = datetime.utcnow() + timedelta(hours=grow_hours)
        
        if plot_str == "*":
            # Plant in all empty plots
            plots = await garden_repo.get_plots(garden.user_id)
            planted = 0
            
            for plot_num in range(1, garden.slots + 1):
                existing = next((p for p in plots if p.plot_number == plot_num), None)
                if not existing and await barn_repo.has_item(barn.id, crop_type, 1):
                    await garden_repo.plant_crop(garden.user_id, plot_num, crop_type, ready_at)
                    await barn_repo.remove_item(barn.id, crop_type, 1)
                    planted += 1
            
            await message.reply(
                f"✅ <b>Planted!</b>\n\n"
                f"🌱 Planted {planted}x {crop['emoji']} {crop_type.title()}\n"
                f"⏰ Ready in: {grow_hours:.1f} hours"
            )
        else:
            try:
                plot_num = int(plot_str)
            except:
                return await message.reply("❌ Invalid plot number!")
            
            if plot_num < 1 or plot_num > garden.slots:
                return await message.reply(f"❌ Plot number must be 1-{garden.slots}!")
            
            # Check if plot is empty
            existing = await garden_repo.get_plot(garden.user_id, plot_num)
            if existing:
                return await message.reply("❌ This plot is already occupied!")
            
            # Plant
            await garden_repo.plant_crop(garden.user_id, plot_num, crop_type, ready_at)
            await barn_repo.remove_item(barn.id, crop_type, 1)
            
            await message.reply(
                f"✅ <b>Planted!</b>\n\n"
                f"🌱 {crop['emoji']} {crop_type.title()} in plot {plot_num}\n"
                f"⏰ Ready in: {grow_hours:.1f} hours"
            )


@router.message(Command("harvest"))
@require_user()
@rate_limit("harvest", 20, 60)
@handle_errors()
async def harvest_command(message: types.Message, db_user=None):
    """Harvest ready crops"""
    async for session in get_session():
        garden_repo = GardenRepository(session)
        barn_repo = BarnRepository(session)
        
        garden = await garden_repo.get_by_user_id(db_user.id)
        plots = await garden_repo.get_plots(garden.user_id)
        
        ready_plots = [p for p in plots if p.is_ready]
        
        if not ready_plots:
            return await message.reply("❌ No crops ready to harvest!")
        
        harvested = {}
        
        for plot in ready_plots:
            crop_type = plot.crop_type
            
            # Add to barn
            barn = await barn_repo.get_by_user_id(db_user.id)
            await barn_repo.add_item(barn.id, crop_type, 1, "crop")
            
            harvested[crop_type] = harvested.get(crop_type, 0) + 1
            
            # Remove plot
            await garden_repo.harvest_plot(plot.id)
        
        # Build result text
        text = f"🚜 <b>Harvested!</b>\n\n"
        
        for crop_type, count in harvested.items():
            emoji = CROPS.get(crop_type, {}).get("emoji", "🌾")
            text += f"{emoji} {count}x {crop_type.title()}\n"
        
        await message.reply(text)


@router.message(Command("barn"))
@router.message(Command("bn"))
@require_user()
@rate_limit("barn", 10, 60)
@handle_errors()
async def barn_command(message: types.Message, db_user=None):
    """Show barn contents"""
    async for session in get_session():
        barn_repo = BarnRepository(session)
        
        barn = await barn_repo.get_by_user_id(db_user.id)
        
        if not barn:
            barn = await barn_repo.create_for_user(db_user.id)
        
        items = await barn_repo.get_items(barn.id)
        
        text = f"🏚️ <b>Your Barn</b>\n\n"
        
        if not items:
            text += "<i>Empty</i>\n\n"
        else:
            for item in items:
                emoji = CROPS.get(item.item_name, {}).get("emoji", "📦")
                text += f"{emoji} {item.item_name.title()}: {item.quantity}\n"
            text += "\n"
        
        text += f"📊 Capacity: {barn.used_space}/{barn.capacity}"
        
        await message.reply(text)


@router.message(Command("boost"))
@require_user()
@rate_limit("boost", 10, 60)
@handle_errors()
async def boost_command(message: types.Message, db_user=None):
    """Boost crop growth"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            f"❌ Usage: <code>/boost [plot]</code>\n"
            f"💰 Cost: ${BOOST_COST} per boost\n"
            f"⚡ Reduces growth time by {BOOST_TIME_REDUCTION} minutes"
        )
    
    try:
        plot_num = int(args[1])
    except:
        return await message.reply("❌ Invalid plot number!")
    
    async for session in get_session():
        garden_repo = GardenRepository(session)
        
        garden = await garden_repo.get_by_user_id(db_user.id)
        plot = await garden_repo.get_plot(garden.user_id, plot_num)
        
        if not plot or plot.is_empty:
            return await message.reply("❌ This plot is empty!")
        
        if plot.is_ready:
            return await message.reply("❌ This crop is already ready!")
        
        # Check funds
        from src.services.economy_service import EconomyService
        economy_service = EconomyService()
        
        try:
            await economy_service.deduct_money(db_user.id, BOOST_COST)
            
            # Calculate new ready time
            new_ready_at = plot.ready_at - timedelta(minutes=BOOST_TIME_REDUCTION)
            if new_ready_at < datetime.utcnow():
                new_ready_at = datetime.utcnow()
            
            await garden_repo.fertilize_plot(plot.id, new_ready_at)
            
            remaining_mins = (new_ready_at - datetime.utcnow()).total_seconds() // 60
            
            await message.reply(
                f"⚡ <b>Boosted!</b>\n\n"
                f"🌱 Plot {plot_num} boosted!\n"
                f"⏰ Time remaining: {int(remaining_mins)} minutes\n"
                f"💰 Cost: ${BOOST_COST}"
            )
        except Exception as e:
            await message.reply(f"❌ {str(e)}")
