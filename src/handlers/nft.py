"""
NFT Marketplace Handlers
Commands: /mynfts, /nftmarket, /mintnft, /sellnft, /buynft
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.blockchain.contracts.nft_contract import NFTContract
from src.services.economy_service import EconomyService

router = Router()
nft_contract = NFTContract()
economy_service = EconomyService()


@router.message(Command("mynfts"))
@router.message(Command("my_nfts"))
@require_user()
@rate_limit("mynfts", 10, 60)
@handle_errors()
async def mynfts_command(message: types.Message, db_user=None):
    """Show user's NFTs"""
    nfts = nft_contract.get_user_nfts(db_user.id)
    
    if not nfts:
        return await message.reply(
            "🖼️ <b>No NFTs Yet!</b>\n\n"
            "Complete achievements or participate in events to earn NFTs!\n"
            "Use <code>/mintnft</code> to mint achievement NFTs."
        )
    
    text = f"🖼️ <b>Your NFT Collection</b>\n\n"
    text += f"Total: {len(nfts)} NFTs\n\n"
    
    for nft in nfts[:10]:  # Show first 10
        text += nft_contract.format_nft(nft)
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Sell NFT", callback_data="nft_sell")],
        [InlineKeyboardButton(text="🎁 Gift NFT", callback_data="nft_gift")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("nftmarket"))
@router.message(Command("nft_market"))
@require_user()
@rate_limit("nftmarket", 10, 60)
@handle_errors()
async def nftmarket_command(message: types.Message, db_user=None):
    """Show NFT marketplace"""
    listings = nft_contract.get_marketplace()
    
    if not listings:
        return await message.reply(
            "🛒 <b>NFT Marketplace</b>\n\n"
            "<i>No NFTs for sale currently.</i>\n\n"
            "Be the first to list your NFT with <code>/sellnft</code>!"
        )
    
    text = f"🛒 <b>NFT Marketplace</b>\n\n"
    text += f"Listings: {len(listings)}\n\n"
    
    for i, nft in enumerate(listings[:10], 1):
        text += f"{i}. {nft.name}\n"
        text += f"   Rarity: {nft.rarity.title()}\n"
        text += f"   💰 Price: {nft.price} ETH\n"
        text += f"   Token ID: #{nft.token_id}\n\n"
    
    text += "💡 Use <code>/buynft [token_id]</code> to purchase!"
    
    await message.reply(text)


@router.message(Command("mintnft"))
@require_user()
@rate_limit("mintnft", 5, 86400)
@handle_errors()
async def mintnft_command(message: types.Message, db_user=None):
    """Mint achievement NFT"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/mintnft [achievement]</code>\n"
            "Example: <code>/mintnft first_steps</code>\n\n"
            "💰 Cost: 0.01 ETH + gas fees"
        )
    
    achievement = args[1]
    
    # Mint NFT
    nft = nft_contract.mint_achievement_nft(db_user.id, achievement, "bronze")
    
    if not nft:
        return await message.reply(
            "❌ NFT minting is currently unavailable.\n"
            "Please try again later!"
        )
    
    await message.reply(
        f"🎉 <b>NFT Minted!</b>\n\n"
        f"{nft_contract.format_nft(nft)}\n"
        f"View your NFTs with <code>/mynfts</code>!"
    )


@router.message(Command("sellnft"))
@require_user()
@rate_limit("sellnft", 5, 3600)
@handle_errors()
async def sellnft_command(message: types.Message, db_user=None):
    """List NFT for sale"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/sellnft [token_id] [price_eth]</code>\n"
            "Example: <code>/sellnft 123 0.5</code>"
        )
    
    try:
        token_id = int(args[1])
        price = float(args[2])
    except:
        return await message.reply("❌ Invalid token ID or price!")
    
    from decimal import Decimal
    
    success = nft_contract.list_for_sale(db_user.id, token_id, Decimal(str(price)))
    
    if not success:
        return await message.reply("❌ Failed to list NFT. Make sure you own it!")
    
    await message.reply(
        f"✅ <b>NFT Listed!</b>\n\n"
        f"Token ID: #{token_id}\n"
        f"💰 Price: {price} ETH\n\n"
        f"Your NFT is now on the marketplace!"
    )


@router.message(Command("buynft"))
@require_user()
@rate_limit("buynft", 10, 3600)
@handle_errors()
async def buynft_command(message: types.Message, db_user=None):
    """Buy NFT from marketplace"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/buynft [token_id]</code>\n"
            "Use <code>/nftmarket</code> to see available NFTs."
        )
    
    try:
        token_id = int(args[1])
    except:
        return await message.reply("❌ Invalid token ID!")
    
    success = nft_contract.buy_nft(db_user.id, token_id)
    
    if not success:
        return await message.reply("❌ Failed to buy NFT. It may have been sold!")
    
    await message.reply(
        f"🎉 <b>NFT Purchased!</b>\n\n"
        f"Token ID: #{token_id}\n"
        f"View your NFTs with <code>/mynfts</code>!"
    )
