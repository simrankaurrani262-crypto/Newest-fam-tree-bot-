"""
Natural Language Processing for Fam Tree Bot
Handles intent classification, sentiment analysis, and entity extraction
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Intent classification result"""
    name: str
    confidence: float
    entities: Dict[str, str]


@dataclass
class Sentiment:
    """Sentiment analysis result"""
    score: float  # -1.0 to 1.0
    label: str    # negative, neutral, positive
    emotions: Dict[str, float]


class NLPProcessor:
    """Natural Language Processor"""
    
    # Intent patterns
    INTENTS = {
        "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good evening"],
        "help": ["help", "assist", "support", "how to", "what can you do"],
        "balance": ["balance", "money", "how much", "account", "wallet"],
        "family": ["family", "tree", "parents", "children", "spouse", "marry", "adopt"],
        "garden": ["garden", "plant", "crop", "harvest", "farm"],
        "combat": ["rob", "kill", "attack", "fight", "weapon"],
        "games": ["game", "play", "bet", "lottery", "trivia"],
        "goodbye": ["bye", "goodbye", "see you", "later"],
        "thanks": ["thanks", "thank you", "appreciate"]
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        "amount": r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        "username": r'@(\w+)',
        "crop": r'\b(corn|tomato|potato|carrot|pepper|eggplant)\b',
        "weapon": r'\b(punch|blade|sword|pistol|gun|bow|poison|rocket)\b'
    }
    
    # Sentiment keywords
    POSITIVE_WORDS = ["good", "great", "awesome", "excellent", "love", "happy", "amazing", "best", "fantastic"]
    NEGATIVE_WORDS = ["bad", "terrible", "hate", "awful", "worst", "sad", "angry", "disappointed", "sucks"]
    
    def __init__(self):
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.entity_extractor = None
        
    def classify_intent(self, text: str) -> Intent:
        """Classify user intent from text"""
        text_lower = text.lower()
        
        best_intent = "unknown"
        best_score = 0.0
        
        for intent_name, patterns in self.INTENTS.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_intent = intent_name
        
        # Calculate confidence
        confidence = min(1.0, best_score / 2) if best_score > 0 else 0.0
        
        # Extract entities
        entities = self.extract_entities(text)
        
        return Intent(
            name=best_intent,
            confidence=confidence,
            entities=entities
        )
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text"""
        entities = {}
        
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0]
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in self.NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        
        if total == 0:
            score = 0.0
            label = "neutral"
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                label = "positive"
            elif score < -0.2:
                label = "negative"
            else:
                label = "neutral"
        
        emotions = {
            "joy": positive_count / max(len(words), 1),
            "anger": negative_count / max(len(words), 1),
            "neutral": 1 - (positive_count + negative_count) / max(len(words), 1)
        }
        
        return Sentiment(
            score=score,
            label=label,
            emotions=emotions
        )
    
    def process_command(self, text: str) -> Tuple[str, Dict]:
        """Process natural language command"""
        intent = self.classify_intent(text)
        sentiment = self.analyze_sentiment(text)
        
        result = {
            "intent": intent.name,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "sentiment": {
                "score": sentiment.score,
                "label": sentiment.label
            }
        }
        
        # Map intent to command
        command_map = {
            "greeting": "/start",
            "help": "/help",
            "balance": "/account",
            "family": "/tree",
            "garden": "/garden",
            "combat": "/weapon",
            "games": "/games",
            "goodbye": "Goodbye! Have a great day!",
            "thanks": "You're welcome! 😊"
        }
        
        return command_map.get(intent.name, "/help"), result
    
    def generate_response(self, intent: str, context: Dict) -> str:
        """Generate natural language response"""
        responses = {
            "greeting": [
                "Hello there! 👋 How can I help you today?",
                "Hi! Welcome to Fam Tree Bot! 🌳",
                "Hey! Ready to build your family empire?"
            ],
            "help": [
                "I can help you with families, gardens, combat, and more! Try /help for all commands.",
                "Need assistance? Check out /help or ask me anything!"
            ],
            "balance": [
                "Check your balance with /account or /bank! 💰",
                "Want to see your wealth? Use /account!"
            ],
            "family": [
                "Build your family tree with /tree! 👨‍👩‍👧‍👦",
                "Find family members or adopt new ones with /adopt!"
            ],
            "garden": [
                "Grow crops in your garden with /garden! 🌱",
                "Plant some seeds and watch them grow! 🌾"
            ],
            "combat": [
                "Ready for battle? Check your weapons with /weapon! ⚔️",
                "Feeling fierce? Try /rob or /kill! 💀"
            ],
            "games": [
                "Let's play! Try /4p, /ripple, or /lottery! 🎮",
                "Games are fun! Check out /games for more!"
            ]
        }
        
        import random
        return random.choice(responses.get(intent, ["I'm not sure I understand. Try /help!"]))
