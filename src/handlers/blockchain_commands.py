"""
Blockchain Commands
Commands: /wallet, /depositcrypto, /withdrawcrypto, /cryptobalance
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.decorators import require_user, rate_limit, handle_errors
from src.blockchain.wallets.manager import WalletManager
from src.blockchain.payments.processor import PaymentProcessor

router = Router()
wallet_manager = WalletManager()
payment_processor = PaymentProcessor()


@router.message(Command("wallet"))
@router.message(Command("crypto"))
@require_user()
@rate_limit("wallet", 10, 60)
@handle_errors()
async def wallet_command(message: types.Message, db_user=None):
    """Show crypto wallet"""
    wallets = wallet_manager.get_all_wallets(db_user.id)
    
    if not wallets:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Create Wallet", callback_data="wallet_create")]
        ])
        return await message.reply(
            "💎 <b>No Crypto Wallet</b>\n\n"
            "Create a wallet to start using blockchain features!",
            reply_markup=keyboard
        )
    
    text = "💎 <b>Your Crypto Wallets</b>\n\n"
    
    for wallet in wallets:
        text += wallet_manager.format_wallet_info(wallet)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Deposit", callback_data="crypto_deposit")],
        [InlineKeyboardButton(text="🏧 Withdraw", callback_data="crypto_withdraw")]
    ])
    
    await message.reply(text, reply_markup=keyboard)


@router.message(Command("createwallet"))
@require_user()
@rate_limit("createwallet", 3, 86400)
@handle_errors()
async def createwallet_command(message: types.Message, db_user=None):
    """Create crypto wallet"""
    args = message.text.split()
    
    if len(args) < 2:
        chains = ", ".join(WalletManager.SUPPORTED_CHAINS)
        return await message.reply(
            f"❌ Usage: <code>/createwallet [chain]</code>\n"
            f"Supported chains: {chains}"
        )
    
    chain = args[1].lower()
    
    if chain not in WalletManager.SUPPORTED_CHAINS:
        return await message.reply(f"❌ Unsupported chain: {chain}")
    
    wallet = wallet_manager.create_wallet(db_user.id, chain)
    
    if not wallet:
        return await message.reply("❌ Failed to create wallet!")
    
    await message.reply(
        f"✅ <b>Wallet Created!</b>\n\n"
        f"Chain: {chain.title()}\n"
        f"Address: <code>{wallet.address}</code>\n\n"
        f"⚠️ Save your address! You'll need it for deposits."
    )


@router.message(Command("cryptobalance"))
@require_user()
@rate_limit("cryptobalance", 10, 60)
@handle_errors()
async def cryptobalance_command(message: types.Message, db_user=None):
    """Show crypto balances"""
    text = "💰 <b>Crypto Balances</b>\n\n"
    
    for chain in WalletManager.SUPPORTED_CHAINS:
        balance = wallet_manager.get_balance(db_user.id, chain)
        emoji = {"ethereum": "Ξ", "solana": "◎", "bitcoin": "₿", "polygon": "M"}.get(chain, "💎")
        text += f"{emoji} {chain.title()}: {balance}\n"
    
    await message.reply(text)


@router.message(Command("depositcrypto"))
@require_user()
@rate_limit("depositcrypto", 5, 3600)
@handle_errors()
async def depositcrypto_command(message: types.Message, db_user=None):
    """Deposit cryptocurrency"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/depositcrypto [chain] [amount]</code>\n"
            "Example: <code>/depositcrypto ethereum 0.5</code>"
        )
    
    chain = args[1].lower()
    try:
        amount = float(args[2])
    except:
        return await message.reply("❌ Invalid amount!")
    
    wallet = wallet_manager.get_wallet(db_user.id, chain)
    
    if not wallet:
        return await message.reply(f"❌ You don't have a {chain} wallet! Create one with /createwallet")
    
    await message.reply(
        f"💰 <b>Deposit {chain.title()}</b>\n\n"
        f"Send {amount} {chain.upper()} to:\n"
        f"<code>{wallet.address}</code>\n\n"
        f"⚠️ Use <code>/confirmd deposit [tx_hash]</code> after sending!"
    )


@router.message(Command("withdrawcrypto"))
@require_user()
@rate_limit("withdrawcrypto", 3, 86400)
@handle_errors()
async def withdrawcrypto_command(message: types.Message, db_user=None):
    """Withdraw cryptocurrency"""
    args = message.text.split()
    
    if len(args) < 4:
        return await message.reply(
            "❌ Usage: <code>/withdrawcrypto [chain] [amount] [address]</code>\n"
            "Example: <code>/withdrawcrypto ethereum 0.5 0x123...</code>"
        )
    
    chain = args[1].lower()
    try:
        amount = float(args[2])
    except:
        return await message.reply("❌ Invalid amount!")
    
    address = args[3]
    
    wallet = wallet_manager.get_wallet(db_user.id, chain)
    
    if not wallet:
        return await message.reply(f"❌ You don't have a {chain} wallet!")
    
    if wallet.balance < amount:
        return await message.reply("❌ Insufficient balance!")
    
    # Process withdrawal
    success = wallet_manager.withdraw(db_user.id, chain, amount)
    
    if success:
        await message.reply(
            f"✅ <b>Withdrawal Initiated</b>\n\n"
            f"Amount: {amount} {chain.upper()}\n"
            f"To: <code>{address}</code>\n\n"
            f"⏰ Processing time: 10-30 minutes"
        )
    else:
        await message.reply("❌ Withdrawal failed!")


@router.message(Command("convert"))
@require_user()
@rate_limit("convert", 10, 60)
@handle_errors()
async def convert_command(message: types.Message, db_user=None):
    """Convert crypto to USD or vice versa"""
    args = message.text.split()
    
    if len(args) < 3:
        return await message.reply(
            "❌ Usage: <code>/convert [amount] [currency]</code>\n"
            "Example: <code>/convert 1 ETH</code> or <code>/convert 1000 USD BTC</code>"
        )
    
    try:
        amount = float(args[1])
    except:
        return await message.reply("❌ Invalid amount!")
    
    currency = args[2].upper()
    
    from decimal import Decimal
    
    if currency in PaymentProcessor.SUPPORTED_CURRENCIES:
        usd_value = payment_processor.convert_to_usd(Decimal(str(amount)), currency)
        await message.reply(
            f"💱 <b>Conversion</b>\n\n"
            f"{amount} {currency} = ${usd_value:,.2f} USD"
        )
    elif currency == "USD":
        target = args[3].upper() if len(args) > 3 else "ETH"
        if target in PaymentProcessor.SUPPORTED_CURRENCIES:
            crypto_value = payment_processor.convert_from_usd(Decimal(str(amount)), target)
            await message.reply(
                f"💱 <b>Conversion</b>\n\n"
                f"${amount} USD = {crypto_value:.6f} {target}"
            )
        else:
            await message.reply(f"❌ Unsupported currency: {target}")
    else:
        await message.reply(f"❌ Unsupported currency: {currency}")
