"""
Mini Games Handlers
Commands: /4p, /ripple, /nation, /question, /lottery
"""
import random
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors, log_command
from src.services.economy_service import EconomyService
from src.services.user_service import UserService

router = Router()
economy_service = EconomyService()
user_service = UserService()


# 4 Pics 1 Word Game
GAME_WORDS = [
    {"word": "apple", "hint": "A red or green fruit"},
    {"word": "beach", "hint": "Sandy place by the ocean"},
    {"word": "music", "hint": "Sounds arranged in rhythm"},
    {"word": "pizza", "hint": "Italian dish with cheese"},
    {"word": "tiger", "hint": "Large striped cat"},
]

active_games = {}


@router.message(Command("4p"))
@router.message(Command("fourpics"))
@require_user()
@rate_limit("4p", 5, 300)
@handle_errors()
@log_command()
async def fourpics_command(message: types.Message, db_user=None):
    """Start 4 Pics 1 Word game"""
    # Select random word
    game_data = random.choice(GAME_WORDS)
    word = game_data["word"]
    
    # Store game
    active_games[db_user.id] = {
        "word": word,
        "hint": game_data["hint"],
        "start_time": datetime.utcnow(),
        "chat_id": message.chat.id
    }
    
    # Create masked word
    masked = " ".join(["_" * len(word)])
    
    await message.reply(
        f"🎮 <b>4 Pics 1 Word</b>\n\n"
        f"💡 <b>Hint:</b> {game_data['hint']}\n\n"
        f"🔤 Word: <code>{masked}</code> ({len(word)} letters)\n\n"
        f"⏰ You have 5 minutes to guess!\n"
        f"💰 Reward: $50-$200 based on difficulty\n\n"
        f"Type your guess as a message!"
    )


@router.message()
@require_user()
@handle_errors()
async def check_guess(message: types.Message, db_user=None, session=None):
    """Check if message is a game guess"""
    if db_user.id not in active_games:
        return  # No active game
    
    game = active_games[db_user.id]
    
    # Check timeout
    if datetime.utcnow() - game["start_time"] > timedelta(minutes=5):
        del active_games[db_user.id]
        return
    
    guess = message.text.lower().strip()
    
    if guess == game["word"]:
        # Correct!
        reward = random.randint(50, 200)
        await economy_service.add_money(db_user.id, reward)
        
        await message.reply(
            f"🎉 <b>Correct!</b>\n\n"
            f"✅ The word was: <b>{game['word'].upper()}</b>\n"
            f"💰 Reward: ${reward}"
        )
        
        del active_games[db_user.id]


@router.message(Command("ripple"))
@require_user()
@rate_limit("ripple", 10, 300)
@handle_errors()
@log_command()
async def ripple_command(message: types.Message, db_user=None):
    """Ripple betting game"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/ripple [amount]</code>\n"
            "Example: <code>/ripple 100</code>"
        )
    
    try:
        bet = int(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    if bet <= 0:
        return await message.reply("❌ Bet must be positive!")
    
    # Check balance
    balance = await economy_service.get_balance(db_user.id)
    if balance < bet:
        return await message.reply("❌ Insufficient funds!")
    
    # Game logic: 2 out of 3 paths are safe
    paths = ["🌻", "🐍", "🌻"]  # 2 sunflowers (win), 1 snake (lose)
    random.shuffle(paths)
    
    chosen = random.choice(paths)
    
    if chosen == "🌻":
        # Win - 1.5x multiplier
        winnings = int(bet * 1.5)
        await economy_service.add_money(db_user.id, winnings - bet)
        
        await message.reply(
            f"🌻 <b>Sunflower!</b>\n\n"
            f"✅ You won!\n"
            f"💰 Bet: ${bet}\n"
            f"💵 Winnings: ${winnings}\n"
            f"📈 Profit: ${winnings - bet}"
        )
    else:
        # Lose
        await economy_service.deduct_money(db_user.id, bet)
        
        await message.reply(
            f"🐍 <b>Snake!</b>\n\n"
            f"❌ You lost ${bet}!\n\n"
            f"Better luck next time!"
        )


@router.message(Command("nation"))
@require_user()
@rate_limit("nation", 5, 300)
@handle_errors()
async def nation_command(message: types.Message, db_user=None):
    """Nation guessing game"""
    countries = [
        "France", "Germany", "Italy", "Spain", "Japan",
        "China", "India", "Brazil", "Canada", "Australia"
    ]
    
    country = random.choice(countries)
    
    # Store game
    active_games[f"nation_{db_user.id}"] = {
        "answer": country.lower(),
        "start_time": datetime.utcnow()
    }
    
    await message.reply(
        f"🌍 <b>Nation Guessing Game</b>\n\n"
        f"💡 I'm thinking of a country...\n"
        f"📝 Type the country name to guess!\n\n"
        f"💰 Reward: $100 for correct answer\n"
        f"⏰ You have 60 seconds!"
    )


@router.message(Command("question"))
@require_user()
@rate_limit("question", 5, 300)
@handle_errors()
async def question_command(message: types.Message, db_user=None):
    """Trivia game"""
    trivia_questions = [
        {
            "question": "What is the capital of France?",
            "answer": "paris",
            "options": ["London", "Paris", "Berlin", "Madrid"]
        },
        {
            "question": "How many continents are there?",
            "answer": "7",
            "options": ["5", "6", "7", "8"]
        },
        {
            "question": "What is the largest planet?",
            "answer": "jupiter",
            "options": ["Mars", "Earth", "Jupiter", "Saturn"]
        }
    ]
    
    q = random.choice(trivia_questions)
    
    # Cost to play
    cost = 5
    try:
        await economy_service.deduct_money(db_user.id, cost)
    except:
        return await message.reply("❌ You need $5 to play!")
    
    # Store game
    active_games[f"trivia_{db_user.id}"] = {
        "answer": q["answer"].lower(),
        "start_time": datetime.utcnow()
    }
    
    options_text = "\n".join([f"  {opt}" for opt in q["options"]])
    
    await message.reply(
        f"❓ <b>Trivia Question</b>\n\n"
        f"{q['question']}\n\n"
        f"Options:\n{options_text}\n\n"
        f"💰 Cost: $5\n"
        f"🏆 Reward: $50\n"
        f"⏰ 60 seconds!"
    )


@router.message(Command("lottery"))
@require_user()
@rate_limit("lottery", 3, 3600)
@handle_errors()
async def lottery_command(message: types.Message, db_user=None):
    """Lottery game"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/lottery [amount]</code>\n"
            "Example: <code>/lottery 50</code>"
        )
    
    try:
        amount = int(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    if amount < 10:
        return await message.reply("❌ Minimum bet is $10!")
    
    # Check balance
    balance = await economy_service.get_balance(db_user.id)
    if balance < amount:
        return await message.reply("❌ Insufficient funds!")
    
    # Deduct entry fee
    await economy_service.deduct_money(db_user.id, amount)
    
    # 10% chance to win
    if random.randint(1, 10) == 1:
        winnings = amount * 5
        await economy_service.add_money(db_user.id, winnings)
        
        await message.reply(
            f"🎰 <b>Lottery Win!</b>\n\n"
            f"🎉 Congratulations!\n"
            f"💰 Entry: ${amount}\n"
            f"🏆 Winnings: ${winnings}\n"
            f"📈 Profit: ${winnings - amount}"
        )
    else:
        await message.reply(
            f"🎰 <b>Lottery Result</b>\n\n"
            f"❌ Not this time!\n"
            f"💰 Lost: ${amount}\n\n"
            f"Try again later!"
)
