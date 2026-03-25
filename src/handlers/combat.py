"""
Combat System Handlers
Commands: /rob, /kill, /donateblood
"""
from aiogram import Router, types
from aiogram.filters import Command

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors, log_command
from src.services.combat_service import CombatService
from src.services.user_service import UserService
from src.services.economy_service import EconomyService

router = Router()
combat_service = CombatService()
user_service = UserService()
economy_service = EconomyService()


@router.message(Command("rob"))
@require_user()
@require_reply("Please reply to the user you want to rob!")
@rate_limit("rob", 8, 86400)  # 8 per day
@handle_errors()
@log_command()
async def rob_command(message: types.Message, db_user=None):
    """Rob another user"""
    robber = db_user
    target_tg = message.reply_to_message.from_user
    
    target = await user_service.get_or_create_user(target_tg)
    
    if robber.id == target.id:
        return await message.reply("❌ You cannot rob yourself!")
    
    # Check if alive
    if not await economy_service.is_alive(robber.id):
        return await message.reply("❌ You are dead! Use /medical to revive.")
    
    # Attempt robbery
    result = await combat_service.rob(robber.id, target.id)
    
    if result["success"]:
        await message.reply(
            f"🦹 <b>Robbery Successful!</b>\n\n"
            f"💰 You stole ${result['amount']:,.0f} from {target.display_name}!\n\n"
            f"🏃 You got away safely!"
        )
        
        # Notify victim
        await message.bot.send_message(
            chat_id=target_tg.id,
            text=f"🚨 <b>You were robbed!</b>\n\n"
                 f"🦹 {robber.display_name} stole ${result['amount']:,.0f} from you!"
        )
    else:
        await message.reply(
            f"🚔 <b>Robbery Failed!</b>\n\n"
            f"{result['message']}\n\n"
            f"Better luck next time!"
        )
        
        # Notify target
        await message.bot.send_message(
            chat_id=target_tg.id,
            text=f"🛡️ <b>Robbery Attempt!</b>\n\n"
                 f"🦹 {robber.display_name} tried to rob you but failed!"
        )


@router.message(Command("kill"))
@require_user()
@require_reply("Please reply to the user you want to kill!")
@rate_limit("kill", 5, 86400)  # 5 per day
@handle_errors()
@log_command()
async def kill_command(message: types.Message, db_user=None):
    """Kill another user"""
    killer = db_user
    target_tg = message.reply_to_message.from_user
    
    target = await user_service.get_or_create_user(target_tg)
    
    if killer.id == target.id:
        return await message.reply("❌ You cannot kill yourself!")
    
    # Check if alive
    if not await economy_service.is_alive(killer.id):
        return await message.reply("❌ You are dead! Use /medical to revive.")
    
    # Check if target is already dead
    if not await economy_service.is_alive(target.id):
        return await message.reply("❌ Target is already dead!")
    
    # Attempt kill
    result = await combat_service.kill(killer.id, target.id)
    
    if result["success"]:
        await message.reply(
            f"💀 <b>Kill Successful!</b>\n\n"
            f"⚔️ You killed {target.display_name}!\n"
            f"💰 Reward: ${result['reward']:,.0f}"
        )
        
        # Notify victim
        await message.bot.send_message(
            chat_id=target_tg.id,
            text=f"💀 <b>You were killed!</b>\n\n"
                 f"⚔️ {killer.display_name} killed you!\n\n"
                 f"🏥 Use /medical to revive ($500)"
        )
    else:
        await message.reply(
            f"🛡️ <b>Kill Failed!</b>\n\n"
            f"{result['message']}"
        )


@router.message(Command("donateblood"))
@require_user()
@require_reply("Please reply to the user you want to revive!")
@rate_limit("donateblood", 1, 86400)  # 1 per day
@handle_errors()
@log_command()
async def donateblood_command(message: types.Message, db_user=None):
    """Donate blood to revive someone"""
    donor = db_user
    target_tg = message.reply_to_message.from_user
    
    target = await user_service.get_or_create_user(target_tg)
    
    if donor.id == target.id:
        return await message.reply("❌ You cannot donate blood to yourself!")
    
    # Check if donor is alive
    if not await economy_service.is_alive(donor.id):
        return await message.reply("❌ You are dead! Use /medical to revive.")
    
    # Check if target is dead
    if await economy_service.is_alive(target.id):
        return await message.reply("❌ Target is already alive!")
    
    # Donate blood
    result = await combat_service.donate_blood(donor.id, target.id)
    
    await message.reply(
        f"🩸 <b>Blood Donated!</b>\n\n"
        f"You revived {target.display_name}!\n"
        f"⭐ +10 Reputation"
    )
    
    # Notify target
    await message.bot.send_message(
        chat_id=target_tg.id,
        text=f"🩸 <b>You were revived!</b>\n\n"
             f"{donor.display_name} donated blood to save you!\n"
             f"❤️ Health: 1/5"
    )
