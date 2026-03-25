"""
Family System Handlers
Commands: /tree, /adopt, /marry, /divorce, /disown, /runaway, /relations, /family
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import (
    require_user,
    require_reply,
    rate_limit,
    handle_errors,
    log_command
)
from src.core.state_machine import state_manager, UserState
from src.services.family_service import FamilyService
from src.services.user_service import UserService

router = Router()
family_service = FamilyService()
user_service = UserService()


@router.message(Command("tree"))
@require_user()
@rate_limit("tree", 10, 60)
@handle_errors()
@log_command()
async def tree_command(message: types.Message, db_user=None):
    """Show family tree"""
    # Get target user (mentioned or self)
    args = message.text.split()
    target_username = None
    
    if len(args) > 1:
        target_username = args[1].replace("@", "")
        target = await user_service.get_user_by_username(target_username)
        if not target:
            return await message.reply("❌ User not found!")
    else:
        target = db_user
    
    # Get family tree
    tree = await family_service.get_family_tree(target.id)
    
    # Build visual tree
    text = f"🌳 <b>Family Tree of {target.display_name}</b>\n\n"
    
    # Spouses
    if tree["spouses"]:
        text += "💍 <b>Spouses:</b>\n"
        for spouse in tree["spouses"]:
            text += f"  ❤️ {spouse['name']}\n"
        text += "\n"
    
    # Parents
    if tree["parents"]:
        text += "👨‍👩‍👧 <b>Parents:</b>\n"
        for parent in tree["parents"]:
            text += f"  👤 {parent['name']}\n"
        text += "\n"
    
    # Children
    if tree["children"]:
        text += "👶 <b>Children:</b>\n"
        for child in tree["children"]:
            text += f"  🧒 {child['name']}\n"
        text += "\n"
    
    # Siblings
    if tree["siblings"]:
        text += "👫 <b>Siblings:</b>\n"
        for sibling in tree["siblings"]:
            text += f"  👤 {sibling['name']}\n"
        text += "\n"
    
    if not any([tree["spouses"], tree["parents"], tree["children"], tree["siblings"]]):
        text += "📭 <i>No family members yet. Use /adopt or /marry to build your family!</i>"
    
    await message.reply(text)


@router.message(Command("fulltree"))
@require_user()
@rate_limit("fulltree", 5, 60)
@handle_errors()
async def fulltree_command(message: types.Message, db_user=None):
    """Show extended family tree"""
    tree = await family_service.get_family_tree(db_user.id)
    
    text = f"🌳 <b>Extended Family Tree</b>\n\n"
    
    total_members = (
        len(tree["spouses"]) +
        len(tree["parents"]) +
        len(tree["children"]) +
        len(tree["siblings"])
    )
    
    text += f"📊 <b>Total Family Members:</b> {total_members}\n\n"
    
    # Show all relations
    all_members = (
        tree["spouses"] +
        tree["parents"] +
        tree["children"] +
        tree["siblings"]
    )
    
    if all_members:
        text += "<b>All Family Members:</b>\n"
        for member in all_members:
            text += f"  • {member['name']}\n"
    else:
        text += "<i>No family members yet.</i>"
    
    await message.reply(text)


@router.message(Command("adopt"))
@require_user()
@require_reply("Please reply to the user you want to adopt!")
@rate_limit("adopt", 5, 60)
@handle_errors()
@log_command()
async def adopt_command(message: types.Message, db_user=None):
    """Adopt a user as child"""
    parent = db_user
    child_tg = message.reply_to_message.from_user
    
    # Get or create child user
    child = await user_service.get_or_create_user(child_tg)
    
    # Check self-adoption
    if parent.id == child.id:
        return await message.reply("❌ You cannot adopt yourself!")
    
    # Send confirmation to child
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Yes, accept",
                callback_data=f"adopt_yes_{parent.telegram_id}"
            ),
            InlineKeyboardButton(
                text="❌ No, decline",
                callback_data=f"adopt_no_{parent.telegram_id}"
            )
        ]
    ])
    
    await message.bot.send_message(
        chat_id=child.telegram_id,
        text=f"👶 <b>Adoption Request</b>\n\n"
             f"@{parent.username or parent.first_name} wants to adopt you as their child.\n\n"
             f"Do you accept?",
        reply_markup=keyboard
    )
    
    # Set state
    await state_manager.set_state(
        child.telegram_id,
        UserState.WAITING_ADOPTION_CONFIRMATION,
        {"parent_id": parent.id, "parent_tg_id": parent.telegram_id}
    )
    
    await message.reply(
        f"📨 <b>Adoption request sent!</b>\n\n"
        f"Waiting for {child.display_name} to respond..."
    )


@router.callback_query(F.data.startswith("adopt_"))
@handle_errors()
async def adopt_callback(callback: types.CallbackQuery):
    """Handle adoption confirmation"""
    action, parent_tg_id = callback.data.split("_")[1], int(callback.data.split("_")[2])
    child_tg_id = callback.from_user.id
    
    # Get state
    state = await state_manager.get_state(child_tg_id)
    
    if not state or state.get("state") != UserState.WAITING_ADOPTION_CONFIRMATION.value:
        return await callback.answer("❌ This request has expired!", show_alert=True)
    
    if action == "yes":
        # Accept adoption
        parent = await user_service.get_user(parent_tg_id)
        child = await user_service.get_user(child_tg_id)
        
        if parent and child:
            await family_service.adopt(parent.id, child.id)
            
            await callback.message.edit_text(
                f"✅ <b>Adoption Accepted!</b>\n\n"
                f"You are now the child of {parent.display_name}!"
            )
            
            # Notify parent
            await callback.bot.send_message(
                chat_id=parent_tg_id,
                text=f"🎉 <b>Adoption Complete!</b>\n\n"
                     f"{child.display_name} is now your child!"
            )
    else:
        # Decline adoption
        await callback.message.edit_text(
            f"❌ <b>Adoption Declined</b>\n\n"
            f"You declined the adoption request."
        )
        
        # Notify parent
        await callback.bot.send_message(
            chat_id=parent_tg_id,
            text=f"❌ {callback.from_user.first_name} declined your adoption request."
        )
    
    # Clear state
    await state_manager.clear_state(child_tg_id)
    await callback.answer()


@router.message(Command("marry"))
@require_user()
@require_reply("Please reply to the user you want to marry!")
@rate_limit("marry", 3, 60)
@handle_errors()
@log_command()
async def marry_command(message: types.Message, db_user=None):
    """Propose marriage to a user"""
    proposer = db_user
    partner_tg = message.reply_to_message.from_user
    
    # Get or create partner user
    partner = await user_service.get_or_create_user(partner_tg)
    
    # Check self-marriage
    if proposer.id == partner.id:
        return await message.reply("❌ You cannot marry yourself!")
    
    # Send proposal
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💍 Yes, I do!",
                callback_data=f"marry_yes_{proposer.telegram_id}"
            ),
            InlineKeyboardButton(
                text="❌ No, thanks",
                callback_data=f"marry_no_{proposer.telegram_id}"
            )
        ]
    ])
    
    await message.bot.send_message(
        chat_id=partner.telegram_id,
        text=f"💍 <b>Marriage Proposal</b>\n\n"
             f"@{proposer.username or proposer.first_name} has proposed to you!\n\n"
             f"Will you marry them?",
        reply_markup=keyboard
    )
    
    # Set state
    await state_manager.set_state(
        partner.telegram_id,
        UserState.WAITING_MARRIAGE_CONFIRMATION,
        {"proposer_id": proposer.id, "proposer_tg_id": proposer.telegram_id}
    )
    
    await message.reply(
        f"💌 <b>Marriage proposal sent!</b>\n\n"
        f"Waiting for {partner.display_name} to respond..."
    )


@router.callback_query(F.data.startswith("marry_"))
@handle_errors()
async def marry_callback(callback: types.CallbackQuery):
    """Handle marriage confirmation"""
    action, proposer_tg_id = callback.data.split("_")[1], int(callback.data.split("_")[2])
    partner_tg_id = callback.from_user.id
    
    # Get state
    state = await state_manager.get_state(partner_tg_id)
    
    if not state or state.get("state") != UserState.WAITING_MARRIAGE_CONFIRMATION.value:
        return await callback.answer("❌ This proposal has expired!", show_alert=True)
    
    if action == "yes":
        # Accept marriage
        proposer = await user_service.get_user(proposer_tg_id)
        partner = await user_service.get_user(partner_tg_id)
        
        if proposer and partner:
            await family_service.marry(proposer.id, partner.id)
            
            await callback.message.edit_text(
                f"💒 <b>Marriage Accepted!</b>\n\n"
                f"You are now married to {proposer.display_name}!\n\n"
                f"💕 May your love last forever! 💕"
            )
            
            # Notify proposer
            await callback.bot.send_message(
                chat_id=proposer_tg_id,
                text=f"🎉 <b>Marriage Complete!</b>\n\n"
                     f"{partner.display_name} said YES!\n\n"
                     f"💕 You are now married! 💕"
            )
    else:
        # Decline marriage
        await callback.message.edit_text(
            f"❌ <b>Marriage Declined</b>\n\n"
            f"You declined the marriage proposal."
        )
        
        # Notify proposer
        await callback.bot.send_message(
            chat_id=proposer_tg_id,
            text=f"💔 {callback.from_user.first_name} declined your marriage proposal."
        )
    
    # Clear state
    await state_manager.clear_state(partner_tg_id)
    await callback.answer()


@router.message(Command("divorce"))
@require_user()
@rate_limit("divorce", 3, 60)
@handle_errors()
@log_command()
async def divorce_command(message: types.Message, db_user=None):
    """Divorce a spouse"""
    # Get spouses
    spouses = await family_service.get_spouses(db_user.id)
    
    if not spouses:
        return await message.reply("❌ You are not married to anyone!")
    
    if len(spouses) == 1:
        # Divorce directly
        spouse_relation = spouses[0]
        await family_service.divorce(db_user.id, spouse_relation.related_user_id)
        
        await message.reply(
            f"💔 <b>Divorced!</b>\n\n"
            f"You are now divorced."
        )
    else:
        # Show list of spouses to select
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for spouse_rel in spouses:
            spouse = await user_service.get_user(spouse_rel.related_user_id)
            if spouse:
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=f"💔 Divorce {spouse.display_name}",
                        callback_data=f"divorce_{spouse.telegram_id}"
                    )
                ])
        
        await message.reply(
            "💔 <b>Select spouse to divorce:</b>",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("divorce_"))
@handle_errors()
async def divorce_callback(callback: types.CallbackQuery):
    """Handle divorce selection"""
    spouse_tg_id = int(callback.data.split("_")[1])
    
    user = await user_service.get_user(callback.from_user.id)
    spouse = await user_service.get_user(spouse_tg_id)
    
    if user and spouse:
        await family_service.divorce(user.id, spouse.id)
        
        await callback.message.edit_text(
            f"💔 <b>Divorced!</b>\n\n"
            f"You are no longer married to {spouse.display_name}."
        )
        
        # Notify spouse
        await callback.bot.send_message(
            chat_id=spouse_tg_id,
            text=f"💔 {user.display_name} has divorced you."
        )
    
    await callback.answer()


@router.message(Command("relations"))
@require_user()
@rate_limit("relations", 10, 60)
@handle_errors()
async def relations_command(message: types.Message, db_user=None):
    """Show all relationships"""
    tree = await family_service.get_family_tree(db_user.id)
    
    text = f"👨‍👩‍👧‍👦 <b>Your Relationships</b>\n\n"
    
    # Count each type
    spouse_count = len(tree["spouses"])
    parent_count = len(tree["parents"])
    child_count = len(tree["children"])
    sibling_count = len(tree["siblings"])
    
    text += f"💍 Spouses: {spouse_count}/7\n"
    text += f"👨‍👩‍👧 Parents: {parent_count}\n"
    text += f"👶 Children: {child_count}/8\n"
    text += f"👫 Siblings: {sibling_count}\n\n"
    
    text += f"📊 <b>Total Relations:</b> {spouse_count + parent_count + child_count + sibling_count}"
    
    await message.reply(text)


@router.message(Command("disown"))
@require_user()
@require_reply("Please reply to the child you want to disown!")
@handle_errors()
@log_command()
async def disown_command(message: types.Message, db_user=None):
    """Disown a child"""
    parent = db_user
    child_tg = message.reply_to_message.from_user
    
    child = await user_service.get_user(child_tg.id)
    
    if not child:
        return await message.reply("❌ User not found!")
    
    await family_service.disown(parent.id, child.id)
    
    await message.reply(
        f"👋 <b>Disowned!</b>\n\n"
        f"You have disowned {child.display_name}."
    )


@router.message(Command("runaway"))
@require_user()
@handle_errors()
@log_command()
async def runaway_command(message: types.Message, db_user=None):
    """Self-disown from parent"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Yes, run away",
                callback_data="runaway_confirm"
            ),
            InlineKeyboardButton(
                text="❌ No, stay",
                callback_data="runaway_cancel"
            )
        ]
    ])
    
    await message.reply(
        "🏃 <b>Run Away?</b>\n\n"
        "This will remove you from your parent's family.\n"
        "Are you sure?",
        reply_markup=keyboard
    )


@router.callback_query(F.data.in_(["runaway_confirm", "runaway_cancel"]))
@handle_errors()
async def runaway_callback(callback: types.CallbackQuery):
    """Handle runaway confirmation"""
    if callback.data == "runaway_confirm":
        user = await user_service.get_user(callback.from_user.id)
        await family_service.runaway(user.id)
        
        await callback.message.edit_text(
            "🏃 <b>You ran away!</b>\n\n"
            "You are no longer part of your parent's family."
        )
    else:
        await callback.message.edit_text("✅ You decided to stay.")
    
    await callback.answer()
