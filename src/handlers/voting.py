"""
Voting System Handlers
Commands: /vote, /poll, /voteresults
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors

router = Router()

# Polls storage
active_polls = {}
poll_votes = {}


@router.message(Command("poll"))
@require_user()
@rate_limit("poll", 3, 3600)
@handle_errors()
async def poll_command(message: types.Message, db_user=None):
    """Create a poll"""
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/poll [question] | [option1] | [option2] | ...</code>\n"
            "Example: <code>/poll Best crop? | Corn | Tomato | Potato</code>"
        )
    
    parts = message.text.split("|")
    question = parts[0].replace("/poll", "").strip()
    options = [p.strip() for p in parts[1:] if p.strip()]
    
    if len(options) < 2:
        return await message.reply("❌ Need at least 2 options!")
    
    # Create poll
    poll_id = f"poll_{db_user.id}_{len(active_polls)}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i, option in enumerate(options):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{i+1}. {option}",
                callback_data=f"vote_{poll_id}_{i}"
            )
        ])
    
    active_polls[poll_id] = {
        "question": question,
        "options": options,
        "creator": db_user.id,
        "votes": {i: 0 for i in range(len(options))}
    }
    poll_votes[poll_id] = {}
    
    await message.reply(
        f"📊 <b>Poll: {question}</b>\n\n"
        f"Vote below!",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("vote_"))
@handle_errors()
async def vote_callback(callback: types.CallbackQuery):
    """Handle vote"""
    parts = callback.data.split("_")
    poll_id = f"{parts[1]}_{parts[2]}_{parts[3]}"
    option = int(parts[4])
    
    if poll_id not in active_polls:
        return await callback.answer("❌ Poll not found!", show_alert=True)
    
    user_id = callback.from_user.id
    
    # Check if already voted
    if user_id in poll_votes.get(poll_id, {}):
        old_vote = poll_votes[poll_id][user_id]
        active_polls[poll_id]["votes"][old_vote] -= 1
    
    # Record vote
    poll_votes[poll_id][user_id] = option
    active_polls[poll_id]["votes"][option] += 1
    
    await callback.answer("✅ Vote recorded!")
    
    # Update poll display
    poll = active_polls[poll_id]
    total_votes = sum(poll["votes"].values())
    
    text = f"📊 <b>Poll: {poll['question']}</b>\n\n"
    text += f"Total Votes: {total_votes}\n\n"
    
    for i, option in enumerate(poll["options"]):
        votes = poll["votes"][i]
        pct = (votes / total_votes * 100) if total_votes > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        text += f"{i+1}. {option}\n"
        text += f"   [{bar}] {votes} ({pct:.1f}%)\n\n"
    
    await callback.message.edit_text(text)


@router.message(Command("voteresults"))
@require_user()
@handle_errors()
async def voteresults_command(message: types.Message, db_user=None):
    """Show poll results"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Usage: <code>/voteresults [poll_id]</code>")
    
    poll_id = args[1]
    
    if poll_id not in active_polls:
        return await message.reply("❌ Poll not found!")
    
    poll = active_polls[poll_id]
    total_votes = sum(poll["votes"].values())
    
    text = f"📊 <b>Poll Results: {poll['question']}</b>\n\n"
    text += f"Total Votes: {total_votes}\n\n"
    
    # Find winner
    winner = max(poll["votes"], key=poll["votes"].get)
    
    for i, option in enumerate(poll["options"]):
        votes = poll["votes"][i]
        pct = (votes / total_votes * 100) if total_votes > 0 else 0
        
        if i == winner:
            text += f"🏆 <b>{option}</b>: {votes} votes ({pct:.1f}%)\n"
        else:
            text += f"{option}: {votes} votes ({pct:.1f}%)\n"
    
    await message.reply(text)
