"""
Recommendation Engine for Fam Tree Bot
Provides personalized recommendations for users
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Recommendation item"""
    type: str
    title: str
    description: str
    confidence: float
    action: str


class RecommendationEngine:
    """AI-powered recommendation engine"""
    
    def __init__(self):
        self.user_profiles = {}
        self.item_matrix = {}
    
    def get_family_recommendations(self, user_id: int, family_data: Dict) -> List[Recommendation]:
        """Recommend family actions"""
        recommendations = []
        
        spouse_count = len(family_data.get("spouses", []))
        child_count = len(family_data.get("children", []))
        
        if spouse_count == 0:
            recommendations.append(Recommendation(
                type="family",
                title="Find a Partner! 💍",
                description="You're single! Use /marry to find a spouse.",
                confidence=0.95,
                action="/marry"
            ))
        
        if child_count < 8 and spouse_count > 0:
            recommendations.append(Recommendation(
                type="family",
                title="Expand Your Family! 👶",
                description=f"You have {child_count}/8 children. Use /adopt to grow your family!",
                confidence=0.8,
                action="/adopt"
            ))
        
        return recommendations
    
    def get_garden_recommendations(self, user_id: int, garden_data: Dict) -> List[Recommendation]:
        """Recommend garden actions"""
        recommendations = []
        
        plots = garden_data.get("plots", [])
        empty_plots = sum(1 for p in plots if p.get("is_empty"))
        ready_plots = sum(1 for p in plots if p.get("is_ready"))
        
        if ready_plots > 0:
            recommendations.append(Recommendation(
                type="garden",
                title="Harvest Ready! 🚜",
                description=f"You have {ready_plots} crops ready to harvest!",
                confidence=0.95,
                action="/harvest"
            ))
        
        if empty_plots > 0:
            recommendations.append(Recommendation(
                type="garden",
                title="Empty Plots Available! 🌱",
                description=f"You have {empty_plots} empty plots. Plant some crops!",
                confidence=0.85,
                action="/plant"
            ))
        
        return recommendations
    
    def get_economy_recommendations(self, user_id: int, economy_data: Dict) -> List[Recommendation]:
        """Recommend economic actions"""
        recommendations = []
        
        balance = economy_data.get("balance", 0)
        bank_balance = economy_data.get("bank_balance", 0)
        
        if balance > 10000 and bank_balance < balance * 0.5:
            recommendations.append(Recommendation(
                type="economy",
                title="Secure Your Wealth! 🏦",
                description="You have a lot of cash! Consider depositing in the bank.",
                confidence=0.75,
                action="/deposit"
            ))
        
        if balance < 1000:
            recommendations.append(Recommendation(
                type="economy",
                title="Low on Funds! 💸",
                description="Your balance is low. Claim /daily or play games!",
                confidence=0.9,
                action="/daily"
            ))
        
        return recommendations
    
    def get_game_recommendations(self, user_id: int, game_history: Dict) -> List[Recommendation]:
        """Recommend games based on history"""
        recommendations = []
        
        # Simple recommendation based on randomness for now
        games = [
            ("/4p", "4 Pics 1 Word", "Test your word skills!"),
            ("/ripple", "Ripple Betting", "Risk it for the biscuit!"),
            ("/lottery", "Lottery", "Try your luck!"),
            ("/nation", "Nation Guessing", "Test your geography!"),
            ("/question", "Trivia", "Show what you know!")
        ]
        
        game = random.choice(games)
        recommendations.append(Recommendation(
            type="game",
            title=f"Play {game[1]}! 🎮",
            description=game[2],
            confidence=0.7,
            action=game[0]
        ))
        
        return recommendations
    
    def get_friend_recommendations(self, user_id: int, friends_data: Dict) -> List[Recommendation]:
        """Recommend friends to add"""
        recommendations = []
        
        friend_count = friends_data.get("count", 0)
        
        if friend_count < 10:
            recommendations.append(Recommendation(
                type="social",
                title="Make More Friends! 👥",
                description=f"You only have {friend_count} friends. Use /friend to connect!",
                confidence=0.8,
                action="/circle"
            ))
        
        return recommendations
    
    def get_all_recommendations(self, user_id: int, user_data: Dict) -> List[Recommendation]:
        """Get all personalized recommendations"""
        all_recommendations = []
        
        if "family" in user_data:
            all_recommendations.extend(
                self.get_family_recommendations(user_id, user_data["family"])
            )
        
        if "garden" in user_data:
            all_recommendations.extend(
                self.get_garden_recommendations(user_id, user_data["garden"])
            )
        
        if "economy" in user_data:
            all_recommendations.extend(
                self.get_economy_recommendations(user_id, user_data["economy"])
            )
        
        if "games" in user_data:
            all_recommendations.extend(
                self.get_game_recommendations(user_id, user_data["games"])
            )
        
        if "friends" in user_data:
            all_recommendations.extend(
                self.get_friend_recommendations(user_id, user_data["friends"])
            )
        
        # Sort by confidence
        all_recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return all_recommendations[:5]  # Return top 5
    
    def format_recommendations(self, recommendations: List[Recommendation]) -> str:
        """Format recommendations for display"""
        if not recommendations:
            return "No recommendations at the moment. You're doing great! 🌟"
        
        text = "🤖 <b>AI Recommendations</b>\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            confidence_bar = "█" * int(rec.confidence * 10) + "░" * (10 - int(rec.confidence * 10))
            text += f"{i}. <b>{rec.title}</b>\n"
            text += f"   {rec.description}\n"
            text += f"   💡 Try: <code>{rec.action}</code>\n"
            text += f"   Match: {confidence_bar}\n\n"
        
        return text
