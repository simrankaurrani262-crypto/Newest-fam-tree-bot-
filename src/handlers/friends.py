"""
Friend System Handlers
Commands: /circle, /friend, /unfriend, /activefriends
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, require_reply, rate_limit, handle_errors, log_command
from src.services.user_service import UserService
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.friendship_repo import FriendshipRepository
from src.database.connection import get_session
from src.core.constants import SYSTEM_LIMITS
from src.core.state_machine import state_manager, UserState

router = Router()
user_service = UserService()


@router.message(Command("circle"))
@router.message(Command("friends"))
@require_user()
@rate_limit("circle", 10, 60)
@handle_errors()
async def circle_command(message: types.Message, db_user=None):
    """Show friend circle"""
    async for session in get_session():
        friend_repo = FriendshipRepository(session)
        user_repo = UserRepository(session)
        
        friends = await friend_repo.get_friends(db_user.id)
        
        text = f"👥 <b>Your Friend Circle</b>\n\n"
        text += f"📊 Friends: {len(friends)}/{SYSTEM_LIMITS['max_friends']}\n\n"
        
        if friends:
            text += "<b>Friends:</b>\n"
            for friend_rel in friends:
                friend = await user_repo.get_by_id(friend_rel.friend_id)
                if friend:
                    text += f"  • {friend.display_name}\n"
        else:
            text += "<i>No friends yet. Use /friend to add friends!</i>"
        
        await message.reply(text)


@router.message(Command("friend"))
@require_user()
@require_reply("Please reply to the user you want to friend!")
@rate_limit("friend", 20, 60)
@handle_errors()
@log_command()
async def friend_command(message: types.Message, db_user=None):
    """Send friend request"""
    user1 = db_user
    user2_tg = message.reply_to_message.from_user
    
    if user1.telegram_id == user2_tg.id:
        return await message.reply("❌ You cannot friend yourself!")
    
    # Get or create user2
    user2 = await user_service.get_or_create_user(user2_tg)
    
    async for session in get_session():
        friend_repo = FriendshipRepository(session)
        
        # Check if already friends
        if await friend_repo.are_friends(user1.id, user2.id):
            return await message.reply("❌ You are already friends!")
        
        # Check max friends
        friends_count = await friend_repo.get_friends_count(user1.id)
        if friends_count >= SYSTEM_LIMITS['max_friends']:
            return await message.reply(f"❌ You have reached the max friends limit ({SYSTEM_LIMITS['max_friends']})!")
        
        # Send friend request
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Accept",
                    callback_data=f"friend_yes_{user1.telegram_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Decline",
                    callback_data=f"friend_no_{user1.telegram_id}"
                )
            ]
        ])
        
        await message.bot.send_message(
            chat_id=user2_tg.id,
            text=f"👋 <b>Friend Request</b>\n\n"
                 f"{user1.display_name} wants to be your friend!\n\n"
                 f"Do you accept?",
            reply_markup=keyboard
        )
        
        # Set state
        await state_manager.set_state(
            user2_tg.id,
            UserState.WAITING_FRIEND_CONFIRMATION,
            {"requester_id": user1.id, "requester_tg_id": user1.telegram_id}
        )
        
        await message.reply(f"📨 Friend request sent to {user2.display_name}!")


@router.callback_query(F.data.startswith("friend_"))
@handle_errors()
async def friend_callback(callback: types.CallbackQuery):
    """Handle friend request response"""
    action, requester_tg_id = callback.data.split("_")[1], int(callback.data.split("_")[2])
    responder_tg_id = callback.from_user.id
    
    # Get state
    state = await state_manager.get_state(responder_tg_id)
    
    if not state or state.get("state") != UserState.WAITING_FRIEND_CONFIRMATION.value:
        return await callback.answer("❌ This request has expired!", show_alert=True)
    
    requester = await user_service.get_user(requester_tg_id)
    responder = await user_service.get_user(responder_tg_id)
    
    if action == "yes":
        async for session in get_session():
            friend_repo = FriendshipRepository(session)
            economy_repo = EconomyRepository(session)
            
            # Create friendship (bidirectional)
            await friend_repo.create_friendship(requester.id, responder.id)
            
            # Give rewards
            await economy_repo.add_money(requester.id, 3000)
            await economy_repo.add_money(responder.id, 3000)
            
            await callback.message.edit_text(
                f"✅ <b>Friend Request Accepted!</b>\n\n"
                f"You are now friends with {requester.display_name}!\n"
                f"💰 Reward: $3,000"
            )
            
            # Notify requester
            await callback.bot.send_message(
                chat_id=requester_tg_id,
                text=f"🎉 <b>Friend Request Accepted!</b>\n\n"
                     f"{responder.display_name} accepted your friend request!\n"
                     f"💰 Reward: $3,000"
            )
    else:
        await callback.message.edit_text(
            f"❌ <b>Friend Request Declined</b>\n\n"
            f"You declined the friend request."
        )
        
        # Notify requester
        await callback.bot.send_message(
            chat_id=requester_tg_id,
            text=f"❌ {responder.display_name} declined your friend request."
        )
    
    await state_manager.clear_state(responder_tg_id)
    await callback.answer()


@router.message(Command("unfriend"))
@require_user()
@require_reply("Please reply to the user you want to unfriend!")
@handle_errors()
@log_command()
async def unfriend_command(message: types.Message, db_user=None):
    """Remove a friend"""
    user1 = db_user
    user2_tg = message.reply_to_message.from_user
    
    user2 = await user_service.get_user(user2_tg.id)
    
    if not user2:
        return await message.reply("❌ User not found!")
    
    async for session in get_session():
        friend_repo = FriendshipRepository(session)
        
        if not await friend_repo.are_friends(user1.id, user2.id):
            return await message.reply("❌ You are not friends with this user!")
        
        await friend_repo.remove_friendship(user1.id, user2.id)
        
        await message.reply(
            f"👋 <b>Unfriended!</b>\n\n"
            f"You are no longer friends with {user2.display_name}."
        )


@router.message(Command("activefriends"))
@require_user()
@handle_errors()
async def activefriends_command(message: types.Message, db_user=None):
    """Show online/active friends"""
    # TODO: Implement online status tracking
    await message.reply(
        "👥 <b>Active Friends</b>\n\n"
        "<i>Online status tracking coming soon!</i>"
    )
