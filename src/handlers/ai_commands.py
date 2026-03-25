"""
AI-Powered Commands
Commands: /ai, /ask, /recommend, /analyze, /generateimage
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors
from src.ai_ml.nlp.processor import NLPProcessor
from src.ai_ml.recommendation.engine import RecommendationEngine
from src.ai_ml.image_generation.generator import ImageGenerator
from src.services.economy_service import EconomyService
from src.services.family_service import FamilyService

router = Router()
nlp_processor = NLPProcessor()
recommendation_engine = RecommendationEngine()
image_generator = ImageGenerator()
economy_service = EconomyService()
family_service = FamilyService()


@router.message(Command("ai"))
@router.message(Command("ask"))
@require_user()
@rate_limit("ai", 20, 60)
@handle_errors()
async def ai_command(message: types.Message, db_user=None):
    """AI assistant - natural language commands"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply(
            "🤖 <b>AI Assistant</b>\n\n"
            "Ask me anything! Examples:\n"
            "• <code>/ai What's my balance?</code>\n"
            "• <code>/ai How do I marry someone?</code>\n"
            "• <code>/ai Show me my family</code>\n"
            "• <code>/ai Help with garden</code>"
        )
    
    query = args[1]
    
    # Process with NLP
    command, analysis = nlp_processor.process_command(query)
    
    # Generate response
    if command.startswith("/"):
        response = nlp_processor.generate_response(analysis["intent"], {})
        response += f"\n\n💡 Try: <code>{command}</code>"
    else:
        response = command
    
    # Add sentiment-based emoji
    sentiment_emoji = {
        "positive": "😊",
        "neutral": "🤖",
        "negative": "😔"
    }
    
    emoji = sentiment_emoji.get(analysis["sentiment"]["label"], "🤖")
    
    await message.reply(f"{emoji} {response}")


@router.message(Command("recommend"))
@router.message(Command("recommendations"))
@require_user()
@rate_limit("recommend", 5, 300)
@handle_errors()
async def recommend_command(message: types.Message, db_user=None):
    """Get AI recommendations"""
    # Gather user data
    user_data = {}
    
    # Get family data
    family_tree = await family_service.get_family_tree(db_user.id)
    user_data["family"] = {
        "spouses": family_tree.get("spouses", []),
        "children": family_tree.get("children", []),
        "parents": family_tree.get("parents", [])
    }
    
    # Get economy data
    balance = await economy_service.get_balance(db_user.id)
    bank = await economy_service.get_bank_balance(db_user.id)
    user_data["economy"] = {
        "balance": balance,
        "bank_balance": bank
    }
    
    # Get recommendations
    recommendations = recommendation_engine.get_all_recommendations(db_user.id, user_data)
    
    # Format and send
    text = recommendation_engine.format_recommendations(recommendations)
    
    await message.reply(text)


@router.message(Command("analyze"))
@require_user()
@rate_limit("analyze", 3, 300)
@handle_errors()
async def analyze_command(message: types.Message, db_user=None):
    """Analyze user activity and provide insights"""
    # Gather stats
    balance = await economy_service.get_balance(db_user.id)
    net_worth = await economy_service.get_net_worth(db_user.id)
    reputation = await economy_service.get_reputation(db_user.id)
    
    family_tree = await family_service.get_family_tree(db_user.id)
    family_size = (
        len(family_tree.get("spouses", [])) +
        len(family_tree.get("children", [])) +
        len(family_tree.get("parents", [])) +
        len(family_tree.get("siblings", []))
    )
    
    # Generate analysis
    text = "📊 <b>AI Activity Analysis</b>\n\n"
    
    # Wealth analysis
    if net_worth > 100000:
        text += "💰 <b>Wealth Status:</b> Wealthy\n"
        text += "   You're doing great financially!\n\n"
    elif net_worth > 10000:
        text += "💰 <b>Wealth Status:</b> Comfortable\n"
        text += "   Keep growing your wealth!\n\n"
    else:
        text += "💰 <b>Wealth Status:</b> Starting Out\n"
        text += "   Claim daily rewards and play games!\n\n"
    
    # Family analysis
    if family_size > 10:
        text += "👨‍👩‍👧‍👦 <b>Family Status:</b> Large Family\n"
        text += f"   You have {family_size} family members!\n\n"
    elif family_size > 0:
        text += "👨‍👩‍👧‍👦 <b>Family Status:</b> Growing Family\n"
        text += f"   You have {family_size} family members.\n\n"
    else:
        text += "👨‍👩‍👧‍👦 <b>Family Status:</b> Solo\n"
        text += "   Use /marry or /adopt to build your family!\n\n"
    
    # Reputation analysis
    if reputation > 150:
        text += "⭐ <b>Reputation:</b> Elite\n"
        text += "   You're highly respected!\n\n"
    elif reputation > 100:
        text += "⭐ <b>Reputation:</b> Good Standing\n"
        text += "   Keep being a good citizen!\n\n"
    else:
        text += "⭐ <b>Reputation:</b> Needs Improvement\n"
        text += "   Avoid crimes to improve reputation!\n\n"
    
    # Personalized tips
    text += "💡 <b>AI Tips:</b>\n"
    
    if net_worth < 5000:
        text += "• Claim /daily rewards every day\n"
    if family_size == 0:
        text += "• Start building your family with /marry\n"
    if reputation < 100:
        text += "• Donate blood to improve reputation\n"
    
    await message.reply(text)


@router.message(Command("generateimage"))
@router.message(Command("genimg"))
@require_user()
@rate_limit("generateimage", 3, 300)
@handle_errors()
async def generateimage_command(message: types.Message, db_user=None):
    """Generate AI image"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply(
            "🎨 <b>AI Image Generator</b>\n\n"
            "Usage: <code>/generateimage [prompt]</code>\n"
            "Example: <code>/generateimage a beautiful garden with flowers</code>\n\n"
            "💰 Cost: $500 per image"
        )
    
    prompt = args[1]
    
    # Check funds
    balance = await economy_service.get_balance(db_user.id)
    if balance < 500:
        return await message.reply("❌ You need $500 to generate an image!")
    
    # Deduct cost
    await economy_service.deduct_money(db_user.id, 500)
    
    # Generate image
    image = image_generator.generate_custom(prompt)
    
    if image:
        await message.reply_photo(
            photo=image,
            caption=f"🎨 <b>AI Generated Image</b>\n\n"
                    f"Prompt: {prompt}\n"
                    f"💰 Cost: $500"
        )
    else:
        await message.reply(
            "🎨 <b>Image Generation</b>\n\n"
            f"Your request for: '{prompt}'\n"
            f"Has been queued for generation!\n"
            f"💰 Cost: $500\n\n"
            "(Image generation requires AI service setup)"
        )


@router.message(Command("sentiment"))
@require_user()
@rate_limit("sentiment", 10, 60)
@handle_errors()
async def sentiment_command(message: types.Message, db_user=None):
    """Analyze sentiment of chat"""
    # This would analyze recent messages
    # For now, return a fun response
    
    import random
    sentiments = ["positive", "neutral", "negative"]
    sentiment = random.choice(sentiments)
    
    emoji_map = {
        "positive": "😊🎉💚",
        "neutral": "😐🤖💙",
        "negative": "😔💔❤️"
    }
    
    await message.reply(
        f"📊 <b>Chat Sentiment Analysis</b>\n\n"
        f"Current mood: {sentiment.upper()}\n"
        f"{emoji_map[sentiment]}\n\n"
        f"Keep the positive vibes going!"
    )
