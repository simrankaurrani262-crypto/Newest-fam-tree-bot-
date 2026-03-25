"""
Advanced Game Handlers
Commands: /dice, /coinflip, /rps, /slots, /blackjack, /roulette
"""
from aiogram import Router, types, F
from aiogram.filters import Command
import random

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService

router = Router()
economy_service = EconomyService()


@router.message(Command("dice"))
@require_user()
@rate_limit("dice", 20, 300)
@handle_errors()
async def dice_command(message: types.Message, db_user=None):
    """Roll dice game"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/dice [bet]</code>\n"
            "Example: <code>/dice 100</code>\n\n"
            "Roll 4-6 to win 1.5x, 1-3 to lose!"
        )
    
    try:
        bet = int(args[1])
    except:
        return await message.reply("❌ Invalid bet amount!")
    
    if bet <= 0:
        return await message.reply("❌ Bet must be positive!")
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Roll dice
    roll = random.randint(1, 6)
    
    if roll >= 4:
        winnings = int(bet * 1.5)
        await economy_service.add_money(db_user.id, winnings - bet)
        result = f"🎉 You rolled {roll} and WON ${winnings}!"
    else:
        await economy_service.deduct_money(db_user.id, bet)
        result = f"😢 You rolled {roll} and lost ${bet}!"
    
    dice_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][roll - 1]
    
    await message.reply(
        f"🎲 <b>Dice Roll</b>\n\n"
        f"{dice_emoji} You rolled: {roll}\n"
        f"{result}"
    )


@router.message(Command("coinflip"))
@router.message(Command("flip"))
@require_user()
@rate_limit("coinflip", 20, 300)
@handle_errors()
async def coinflip_command(message: types.Message, db_user=None):
    """Coin flip game"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/coinflip [heads/tails] [bet]</code>\n"
            "Example: <code>/coinflip heads 100</code>"
        )
    
    guess = args[1].lower()
    try:
        bet = int(args[2])
    except:
        return await message.reply("❌ Invalid bet amount!")
    
    if guess not in ["heads", "tails"]:
        return await message.reply("❌ Choose heads or tails!")
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Flip coin
    result = random.choice(["heads", "tails"])
    
    if guess == result:
        winnings = bet * 2
        await economy_service.add_money(db_user.id, bet)
        outcome = f"🎉 You won ${bet}!"
    else:
        await economy_service.deduct_money(db_user.id, bet)
        outcome = f"😢 You lost ${bet}!"
    
    emoji = "🦅" if result == "heads" else "🪙"
    
    await message.reply(
        f"🪙 <b>Coin Flip</b>\n\n"
        f"You chose: {guess.title()}\n"
        f"{emoji} Result: {result.title()}\n"
        f"{outcome}"
    )


@router.message(Command("rps"))
@router.message(Command("rockpaperscissors"))
@require_user()
@rate_limit("rps", 20, 300)
@handle_errors()
async def rps_command(message: types.Message, db_user=None):
    """Rock Paper Scissors game"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/rps [rock/paper/scissors] [bet]</code>\n"
            "Example: <code>/rps rock 100</code>"
        )
    
    guess = args[1].lower()
    try:
        bet = int(args[2])
    except:
        return await message.reply("❌ Invalid bet amount!")
    
    if guess not in ["rock", "paper", "scissors"]:
        return await message.reply("❌ Choose rock, paper, or scissors!")
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Bot choice
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    
    # Determine winner
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    
    if guess == bot_choice:
        outcome = "🤝 It's a tie!"
    elif (guess == "rock" and bot_choice == "scissors") or \
         (guess == "paper" and bot_choice == "rock") or \
         (guess == "scissors" and bot_choice == "paper"):
        await economy_service.add_money(db_user.id, bet)
        outcome = f"🎉 You won ${bet}!"
    else:
        await economy_service.deduct_money(db_user.id, bet)
        outcome = f"😢 You lost ${bet}!"
    
    await message.reply(
        f"🎮 <b>Rock Paper Scissors</b>\n\n"
        f"You: {emojis[guess]} {guess.title()}\n"
        f"Bot: {emojis[bot_choice]} {bot_choice.title()}\n\n"
        f"{outcome}"
    )


@router.message(Command("slots"))
@require_user()
@rate_limit("slots", 10, 300)
@handle_errors()
async def slots_command(message: types.Message, db_user=None):
    """Slot machine game"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/slots [bet]</code>\n"
            "Example: <code>/slots 100</code>\n\n"
            "Match 3 symbols to win!"
        )
    
    try:
        bet = int(args[1])
    except:
        return await message.reply("❌ Invalid bet amount!")
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Slot symbols
    symbols = ["🍒", "🍋", "🍇", "🍊", "💎", "7️⃣", "🎰"]
    
    # Spin
    result = [random.choice(symbols) for _ in range(3)]
    
    # Check win
    if result[0] == result[1] == result[2]:
        if result[0] == "7️⃣":
            winnings = bet * 10
            win_text = f"🎰 JACKPOT! You won ${winnings}!"
        elif result[0] == "💎":
            winnings = bet * 5
            win_text = f"💎 DIAMOND WIN! You won ${winnings}!"
        else:
            winnings = bet * 3
            win_text = f"🎉 Match! You won ${winnings}!"
        
        await economy_service.add_money(db_user.id, winnings - bet)
        outcome = win_text
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        winnings = bet
        await economy_service.add_money(db_user.id, 0)  # Break even
        outcome = f"🤝 Two match! You get your bet back!"
    else:
        await economy_service.deduct_money(db_user.id, bet)
        outcome = f"😢 No match! You lost ${bet}!"
    
    await message.reply(
        f"🎰 <b>Slot Machine</b>\n\n"
        f"| {result[0]} | {result[1]} | {result[2]} |\n\n"
        f"{outcome}"
    )


@router.message(Command("blackjack"))
@router.message(Command("bj"))
@require_user()
@rate_limit("blackjack", 5, 300)
@handle_errors()
async def blackjack_command(message: types.Message, db_user=None):
    """Blackjack game (simplified)"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/blackjack [bet]</code>\n"
            "Example: <code>/blackjack 100</code>\n\n"
            "Get closest to 21 without going over!"
        )
    
    try:
        bet = int(args[1])
    except:
        return await message.reply("❌ Invalid bet amount!")
    
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Deal cards
    player_cards = [random.randint(1, 11), random.randint(1, 11)]
    dealer_cards = [random.randint(1, 11), random.randint(1, 11)]
    
    player_total = sum(player_cards)
    dealer_total = sum(dealer_cards)
    
    # Determine winner (simplified)
    if player_total > 21:
        await economy_service.deduct_money(db_user.id, bet)
        outcome = f"💥 Bust! You lost ${bet}!"
    elif dealer_total > 21 or player_total > dealer_total:
        winnings = bet * 2
        await economy_service.add_money(db_user.id, bet)
        outcome = f"🎉 You won ${bet}!"
    elif player_total == dealer_total:
        outcome = "🤝 Push! It's a tie!"
    else:
        await economy_service.deduct_money(db_user.id, bet)
        outcome = f"😢 Dealer wins! You lost ${bet}!"
    
    await message.reply(
        f"🃏 <b>Blackjack</b>\n\n"
        f"Your cards: {player_cards} = {player_total}\n"
        f"Dealer cards: {dealer_cards} = {dealer_total}\n\n"
        f"{outcome}"
    )
