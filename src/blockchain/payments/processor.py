"""
Crypto Payment Processor
Handles cryptocurrency payments and conversions
"""
from typing import Dict, Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Payment:
    """Payment transaction"""
    id: str
    user_id: int
    amount: Decimal
    currency: str
    status: str  # pending, confirmed, failed
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    tx_hash: Optional[str] = None


class PaymentProcessor:
    """Cryptocurrency payment processor"""
    
    SUPPORTED_CURRENCIES = ["BTC", "ETH", "USDT", "SOL", "MATIC"]
    
    # Conversion rates (would be fetched from API in production)
    CONVERSION_RATES = {
        "BTC": Decimal("50000"),
        "ETH": Decimal("3000"),
        "USDT": Decimal("1"),
        "SOL": Decimal("100"),
        "MATIC": Decimal("0.5")
    }
    
    def __init__(self):
        self.payments: Dict[str, Payment] = {}
        self.enabled = False
    
    def create_payment(
        self,
        user_id: int,
        amount: Decimal,
        currency: str
    ) -> Optional[Payment]:
        """Create new payment request"""
        if currency not in self.SUPPORTED_CURRENCIES:
            return None
        
        if not self.enabled:
            return None
        
        payment_id = f"pay_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        payment = Payment(
            id=payment_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.payments[payment_id] = payment
        
        logger.info(f"Created payment {payment_id} for {amount} {currency}")
        return payment
    
    def confirm_payment(self, payment_id: str, tx_hash: str) -> bool:
        """Confirm payment with transaction hash"""
        if payment_id not in self.payments:
            return False
        
        payment = self.payments[payment_id]
        payment.status = "confirmed"
        payment.tx_hash = tx_hash
        payment.confirmed_at = datetime.utcnow()
        
        logger.info(f"Confirmed payment {payment_id} with tx {tx_hash}")
        return True
    
    def convert_to_usd(self, amount: Decimal, currency: str) -> Decimal:
        """Convert crypto amount to USD"""
        rate = self.CONVERSION_RATES.get(currency, Decimal("1"))
        return amount * rate
    
    def convert_from_usd(self, usd_amount: Decimal, currency: str) -> Decimal:
        """Convert USD to crypto amount"""
        rate = self.CONVERSION_RATES.get(currency, Decimal("1"))
        if rate == 0:
            return Decimal("0")
        return usd_amount / rate
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        return self.payments.get(payment_id)
    
    def get_user_payments(self, user_id: int) -> list:
        """Get all payments for user"""
        return [p for p in self.payments.values() if p.user_id == user_id]
    
    def format_payment(self, payment: Payment) -> str:
        """Format payment for display"""
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "failed": "❌"
        }
        
        text = (
            f"{status_emoji.get(payment.status, '⚪')} <b>Payment</b>\n"
            f"   ID: <code>{payment.id}</code>\n"
            f"   Amount: {payment.amount} {payment.currency}\n"
            f"   Status: {payment.status.title()}\n"
        )
        
        if payment.tx_hash:
            text += f"   Tx: <code>{payment.tx_hash}</code>\n"
        
        return text
