"""
Fraud Detection System for Fam Tree Bot
Detects suspicious activities and cheating attempts
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class FraudAlert:
    """Fraud alert data"""
    user_id: int
    alert_type: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: Dict
    timestamp: datetime


class FraudDetector:
    """AI-powered fraud detection system"""
    
    # Thresholds
    MAX_TRANSACTIONS_PER_MINUTE = 20
    MAX_ROBBERY_SUCCESS_RATE = 0.9
    MAX_KILL_SUCCESS_RATE = 0.8
    MAX_MONEY_GROWTH_RATE = 10.0  # 10x in 24 hours
    
    def __init__(self):
        self.alerts = []
        self.user_patterns = {}
        self.suspicious_users = set()
    
    def analyze_transaction_pattern(self, user_id: int, transactions: List[Dict]) -> Optional[FraudAlert]:
        """Analyze transaction patterns for fraud"""
        if len(transactions) < 5:
            return None
        
        # Check transaction frequency
        recent_transactions = [
            t for t in transactions
            if datetime.utcnow() - t["timestamp"] < timedelta(minutes=1)
        ]
        
        if len(recent_transactions) > self.MAX_TRANSACTIONS_PER_MINUTE:
            return FraudAlert(
                user_id=user_id,
                alert_type="transaction_spam",
                severity="high",
                description=f"User made {len(recent_transactions)} transactions in 1 minute",
                evidence={"transactions": recent_transactions},
                timestamp=datetime.utcnow()
            )
        
        return None
    
    def analyze_combat_pattern(self, user_id: int, combat_history: List[Dict]) -> Optional[FraudAlert]:
        """Analyze combat patterns for fraud"""
        if len(combat_history) < 10:
            return None
        
        # Check robbery success rate
        robberies = [c for c in combat_history if c["type"] == "rob"]
        if len(robberies) >= 10:
            success_rate = sum(1 for r in robberies if r["success"]) / len(robberies)
            
            if success_rate > self.MAX_ROBBERY_SUCCESS_RATE:
                return FraudAlert(
                    user_id=user_id,
                    alert_type="suspicious_robbery_rate",
                    severity="high",
                    description=f"Robbery success rate: {success_rate:.1%} (suspicious)",
                    evidence={"success_rate": success_rate, "total": len(robberies)},
                    timestamp=datetime.utcnow()
                )
        
        # Check kill success rate
        kills = [c for c in combat_history if c["type"] == "kill"]
        if len(kills) >= 5:
            success_rate = sum(1 for k in kills if k["success"]) / len(kills)
            
            if success_rate > self.MAX_KILL_SUCCESS_RATE:
                return FraudAlert(
                    user_id=user_id,
                    alert_type="suspicious_kill_rate",
                    severity="critical",
                    description=f"Kill success rate: {success_rate:.1%} (highly suspicious)",
                    evidence={"success_rate": success_rate, "total": len(kills)},
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    def analyze_money_growth(self, user_id: int, balance_history: List[Dict]) -> Optional[FraudAlert]:
        """Analyze money growth for exploitation"""
        if len(balance_history) < 2:
            return None
        
        # Get 24-hour change
        day_ago = datetime.utcnow() - timedelta(hours=24)
        old_balance = None
        
        for entry in balance_history:
            if entry["timestamp"] <= day_ago:
                old_balance = entry["balance"]
                break
        
        if old_balance and old_balance > 0:
            current_balance = balance_history[-1]["balance"]
            growth_rate = current_balance / old_balance
            
            if growth_rate > self.MAX_MONEY_GROWTH_RATE:
                return FraudAlert(
                    user_id=user_id,
                    alert_type="suspicious_money_growth",
                    severity="critical",
                    description=f"Money grew {growth_rate:.1f}x in 24 hours",
                    evidence={
                        "old_balance": old_balance,
                        "current_balance": current_balance,
                        "growth_rate": growth_rate
                    },
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    def detect_bot_behavior(self, user_id: int, activity_log: List[Dict]) -> Optional[FraudAlert]:
        """Detect automated/bot behavior"""
        if len(activity_log) < 20:
            return None
        
        # Check for inhuman response times
        response_times = []
        for i in range(1, len(activity_log)):
            time_diff = (activity_log[i]["timestamp"] - activity_log[i-1]["timestamp"]).total_seconds()
            response_times.append(time_diff)
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            
            # If average response is too fast (< 0.5 seconds)
            if avg_response < 0.5:
                return FraudAlert(
                    user_id=user_id,
                    alert_type="possible_bot",
                    severity="medium",
                    description=f"Average response time: {avg_response:.2f}s (suspiciously fast)",
                    evidence={"avg_response": avg_response},
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    def check_user(self, user_id: int, user_data: Dict) -> List[FraudAlert]:
        """Run all fraud checks on a user"""
        alerts = []
        
        # Transaction analysis
        if "transactions" in user_data:
            alert = self.analyze_transaction_pattern(user_id, user_data["transactions"])
            if alert:
                alerts.append(alert)
        
        # Combat analysis
        if "combat_history" in user_data:
            alert = self.analyze_combat_pattern(user_id, user_data["combat_history"])
            if alert:
                alerts.append(alert)
        
        # Money growth analysis
        if "balance_history" in user_data:
            alert = self.analyze_money_growth(user_id, user_data["balance_history"])
            if alert:
                alerts.append(alert)
        
        # Bot detection
        if "activity_log" in user_data:
            alert = self.detect_bot_behavior(user_id, user_data["activity_log"])
            if alert:
                alerts.append(alert)
        
        # Store alerts
        self.alerts.extend(alerts)
        
        # Mark suspicious users
        for alert in alerts:
            if alert.severity in ["high", "critical"]:
                self.suspicious_users.add(user_id)
        
        return alerts
    
    def get_suspicious_users(self) -> List[int]:
        """Get list of suspicious user IDs"""
        return list(self.suspicious_users)
    
    def format_alert(self, alert: FraudAlert) -> str:
        """Format alert for display"""
        severity_emoji = {
            "low": "⚪",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        
        return (
            f"{severity_emoji.get(alert.severity, '⚪')} <b>Fraud Alert</b>\n\n"
            f"Type: {alert.alert_type}\n"
            f"Severity: {alert.severity.upper()}\n"
            f"User: {alert.user_id}\n\n"
            f"Description: {alert.description}\n\n"
            f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
