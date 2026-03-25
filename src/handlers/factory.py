"""
Factory System Handlers
Commands: /factory, /hire, /work, /shield, /sword
"""
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors, log_command
from src.services.economy_service import EconomyService
from src.services.user_service import UserService
from src.database.repositories.factory_repo import FactoryRepository
from src.database.connection import get_session
from src.core.constants import WORKER_BASE_PRICE, WORKER_PRICE_PER_RATING, WORK_CYCLE_HOURS, SHIELD_COST, SWORD_COST

router = Router()
economy_service = EconomyService()
user_service = UserService()


@router.message(Command("factory"))
@require_user()
@rate_limit("factory", 10, 60)
@handle_errors()
async def factory_command(message: types.Message, db_user=None):
    """Show factory"""
    async for session in get_session():
        factory_repo = FactoryRepository(session)
        
        workers = await factory_repo.get_workers(db_user.id)
        
        text = f"🏭 <b>Your Factory</b>\n\n"
        text += f"👷 Workers: {len(workers)}/5\n\n"
        
        if workers:
            for worker in workers:
                worker_user = await user_service.get_user_by_id(worker.worker_id)
                status = "🟢 Working" if worker.is_working else "⚪ Idle"
                if worker.time_remaining:
                    status += f" ({worker.time_remaining // 60}m left)"
                
                shield = "🛡️" if worker.has_shield else ""
                text += f"• {worker_user.display_name if worker_user else 'Unknown'} - Rating: {worker.rating} {shield}\n"
                text += f"  Status: {status}\n\n"
        else:
            text += "<i>No workers hired. Use /hire to add workers!</i>\n\n"
        
        text += "💡 Workers earn money every hour of work!"
        
        await message.reply(text)


@router.message(Command("hire"))
@require_user()
@require_reply("Please reply to the user you want to hire!")
@rate_limit("hire", 5, 60)
@handle_errors()
@log_command()
async def hire_command(message: types.Message, db_user=None):
    """Hire a worker"""
    owner = db_user
    worker_tg = message.reply_to_message.from_user
    
    if owner.telegram_id == worker_tg.id:
        return await message.reply("❌ You cannot hire yourself!")
    
    worker = await user_service.get_or_create_user(worker_tg)
    
    async for session in get_session():
        factory_repo = FactoryRepository(session)
        
        # Check max workers
        workers = await factory_repo.get_workers(owner.id)
        if len(workers) >= 5:
            return await message.reply("❌ You already have 5 workers (max limit)!")
        
        # Check if already hired
        if await factory_repo.is_worker_hired(owner.id, worker.id):
            return await message.reply("❌ This user is already your worker!")
        
        # Calculate price based on rating
        rating = 0  # New worker
        price = WORKER_BASE_PRICE + (rating * WORKER_PRICE_PER_RATING)
        
        # Check funds
        balance = await economy_service.get_balance(owner.id)
        if balance < price:
            return await message.reply(f"❌ You need ${price} to hire this worker!")
        
        # Deduct money and hire
        await economy_service.deduct_money(owner.id, price)
        await factory_repo.hire_worker(owner.id, worker.id, price)
        
        await message.reply(
            f"✅ <b>Worker Hired!</b>\n\n"
            f"👷 {worker.display_name} is now working for you!\n"
            f"💰 Cost: ${price}\n\n"
            f"Use /work to start work cycles!"
        )
        
        # Notify worker
        await message.bot.send_message(
            chat_id=worker_tg.id,
            text=f"🏭 <b>You've been hired!</b>\n\n"
                 f"{owner.display_name} hired you as a factory worker!\n"
                 f"💰 They paid ${price} for you."
        )


@router.message(Command("work"))
@require_user()
@rate_limit("work", 5, 3600)  # 5 per hour
@handle_errors()
@log_command()
async def work_command(message: types.Message, db_user=None):
    """Start work cycle"""
    async for session in get_session():
        factory_repo = FactoryRepository(session)
        
        workers = await factory_repo.get_workers(db_user.id)
        
        if not workers:
            return await message.reply("❌ You don't have any workers! Use /hire to add workers.")
        
        # Check if any workers are already working
        working = [w for w in workers if w.is_working]
        if working:
            return await message.reply(
                f"❌ Some workers are already working!\n"
                f"Wait for them to finish."
            )
        
        # Start work for all workers
        work_end = datetime.utcnow() + timedelta(hours=WORK_CYCLE_HOURS)
        
        for worker in workers:
            await factory_repo.start_work(worker.id, work_end)
        
        await message.reply(
            f"🏭 <b>Work Started!</b>\n\n"
            f"👷 {len(workers)} workers started working!\n"
            f"⏰ Work ends in {WORK_CYCLE_HOURS} hour(s)\n\n"
            f"💰 You'll earn money based on worker ratings!"
        )


@router.message(Command("shield"))
@require_user()
@rate_limit("shield", 5, 60)
@handle_errors()
async def shield_command(message: types.Message, db_user=None):
    """Buy shield for workers"""
    async for session in get_session():
        factory_repo = FactoryRepository(session)
        
        workers = await factory_repo.get_workers(db_user.id)
        
        if not workers:
            return await message.reply("❌ You don't have any workers!")
        
        # Check funds
        balance = await economy_service.get_balance(db_user.id)
        if balance < SHIELD_COST:
            return await message.reply(f"❌ You need ${SHIELD_COST} for a shield!")
        
        # Buy shield for all workers
        await economy_service.deduct_money(db_user.id, SHIELD_COST)
        
        for worker in workers:
            await factory_repo.add_shield(worker.id)
        
        await message.reply(
            f"🛡️ <b>Shields Purchased!</b>\n\n"
            f"All your workers are now protected!\n"
            f"💰 Cost: ${SHIELD_COST}\n"
            f"⏰ Duration: 24 hours"
        )
