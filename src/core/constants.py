"""
Constants and Enums for Fam Tree Bot
"""
from enum import Enum
from typing import Dict, Any


# ============================================
# LANGUAGES
# ============================================
SUPPORTED_LANGUAGES = ["en", "ru", "fr", "es", "de", "zh", "it", "uk"]

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "zh": "Chinese",
    "it": "Italian",
    "uk": "Ukrainian"
}


# ============================================
# SYSTEM LIMITS
# ============================================
SYSTEM_LIMITS = {
    "max_friends": 100,
    "max_partners": 7,
    "max_children": 8,
    "max_robbery_per_day": 8,
    "max_kills_per_day": 5,
    "max_workers": 5,
    "garden_start_slots": 9,
    "garden_max_slots": 12,
    "barn_size": 500,
    "max_insurance": 10
}


# ============================================
# WEAPONS
# ============================================
WEAPONS: Dict[str, Dict[str, Any]] = {
    "punch": {
        "price": 0,
        "rob_power": 50,
        "kill_power": 50,
        "emoji": "👊"
    },
    "blade": {
        "price": 100,
        "rob_power": 80,
        "kill_power": 100,
        "emoji": "🔪"
    },
    "sword": {
        "price": 200,
        "rob_power": 100,
        "kill_power": 150,
        "emoji": "⚔️"
    },
    "pistol": {
        "price": 400,
        "rob_power": 160,
        "kill_power": 200,
        "emoji": "🔫"
    },
    "gun": {
        "price": 500,
        "rob_power": 200,
        "kill_power": 200,
        "emoji": "🔫"
    },
    "bow": {
        "price": 5000,
        "rob_power": 300,
        "kill_power": 100,
        "emoji": "🏹"
    },
    "poison": {
        "price": 8000,
        "rob_power": 400,
        "kill_power": 200,
        "emoji": "☠️"
    },
    "rocket_launcher": {
        "price": 10000,
        "rob_power": 500,
        "kill_power": 200,
        "emoji": "🚀"
    }
}


# ============================================
# CROPS
# ============================================
CROPS: Dict[str, Dict[str, Any]] = {
    "pepper": {
        "season": "spring",
        "growth_hours": 2,
        "buy_price": 50,
        "sell_price": 150,
        "order_price": 100,
        "emoji": "🌶️"
    },
    "potato": {
        "season": "autumn",
        "growth_hours": 3,
        "buy_price": 40,
        "sell_price": 120,
        "order_price": 80,
        "emoji": "🥔"
    },
    "eggplant": {
        "season": "cloudy",
        "growth_hours": 4,
        "buy_price": 60,
        "sell_price": 180,
        "order_price": 120,
        "emoji": "🍆"
    },
    "carrot": {
        "season": "winter",
        "growth_hours": 1.5,
        "buy_price": 30,
        "sell_price": 90,
        "order_price": 60,
        "emoji": "🥕"
    },
    "corn": {
        "season": "all",
        "growth_hours": 2.5,
        "buy_price": 45,
        "sell_price": 135,
        "order_price": 90,
        "emoji": "🌽"
    },
    "tomato": {
        "season": "all",
        "growth_hours": 1,
        "buy_price": 25,
        "sell_price": 75,
        "order_price": 50,
        "emoji": "🍅"
    }
}

SEASONS = ["spring", "summer", "autumn", "winter", "cloudy"]
SEASON_BONUS = 2.0  # 2x growth speed during crop's season


# ============================================
# GEMSTONES
# ============================================
GEMSTONES = {
    "ruby": {"emoji": "🔴", "color": "#FF0000"},
    "sapphire": {"emoji": "🔵", "color": "#0000FF"},
    "emerald": {"emoji": "🟢", "color": "#00FF00"},
    "topaz": {"emoji": "🟡", "color": "#FFFF00"},
    "onyx": {"emoji": "⚫", "color": "#000000"}
}

GEMSTONE_FUSE_REWARD = 5000


# ============================================
# JOBS
# ============================================
JOBS: Dict[str, Dict[str, Any]] = {
    "unemployed": {
        "salary": 0,
        "benefit": None,
        "emoji": "😴"
    },
    "banker": {
        "salary": 100,
        "benefit": None,
        "emoji": "🏦"
    },
    "policeman": {
        "salary": 100,
        "benefit": "Higher thief protection",
        "emoji": "👮"
    },
    "doctor": {
        "salary": 300,
        "benefit": "Revive 1 heart daily",
        "emoji": "👨‍⚕️"
    },
    "scientist": {
        "salary": 200,
        "benefit": None,
        "emoji": "👨‍🔬"
    },
    "baby_sitter": {
        "salary": 500,
        "benefit": "Requires 3+ children",
        "emoji": "👶"
    }
}


# ============================================
# RECIPES
# ============================================
RECIPES: Dict[str, Dict[str, Any]] = {
    "popcorn": {
        "ingredients": {"corn": 3},
        "time_minutes": 10,
        "output": 1,
        "emoji": "🍿"
    },
    "corn_flour": {
        "ingredients": {"corn": 5},
        "time_minutes": 15,
        "output": 1,
        "emoji": "🌾"
    },
    "fries": {
        "ingredients": {"potato": 3},
        "time_minutes": 12,
        "output": 1,
        "emoji": "🍟"
    },
    "chips": {
        "ingredients": {"potato": 5},
        "time_minutes": 18,
        "output": 1,
        "emoji": "🥔"
    },
    "juice": {
        "ingredients": {"tomato": 10},
        "time_minutes": 20,
        "output": 1,
        "emoji": "🧃"
    },
    "bread": {
        "ingredients": {"corn": 5, "wheat": 5},
        "time_minutes": 25,
        "output": 1,
        "emoji": "🍞"
    },
    "salad": {
        "ingredients": {"tomato": 2, "cucumber": 1},
        "time_minutes": 15,
        "output": 1,
        "emoji": "🥗"
    },
    "breadjam": {
        "ingredients": {"bread": 2, "jam": 1},
        "time_minutes": 20,
        "output": 1,
        "emoji": "🥪"
    },
    "sandwich": {
        "ingredients": {"bread": 1, "tomato": 5, "cheese": 1},
        "time_minutes": 30,
        "output": 1,
        "emoji": "🥪"
    }
}


# ============================================
# INSURANCE
# ============================================
INSURANCE_TYPES: Dict[str, Dict[str, Any]] = {
    "close_family": {
        "multiplier": 3,
        "max_payout": 10000,
        "emoji": "🏠"
    },
    "family": {
        "multiplier": 2,
        "max_payout": 5000,
        "emoji": "👨‍👩‍👧‍👦"
    },
    "friend": {
        "multiplier": 1,
        "max_payout": 2000,
        "emoji": "👫"
    }
}

INSURANCE_DECAY_RATE = 0.05  # 5% per hour


# ============================================
# DAILY REWARDS
# ============================================
DAILY_BASE_REWARD = 1000
DAILY_FAMILY_BONUS = 100  # per family member
DAILY_STREAK_BONUS = 50   # per day of streak


# ============================================
# REPUTATION
# ============================================
REPUTATION_LEVELS = {
    "criminal": (0, 50),
    "normal": (50, 100),
    "good": (100, 150),
    "elite": (150, 200)
}


# ============================================
# HEALTH
# ============================================
MAX_HEALTH = 5
MEDICAL_COST = 500


# ============================================
# FACTORY
# ============================================
WORKER_BASE_PRICE = 1000
WORKER_PRICE_PER_RATING = 25
WORK_CYCLE_HOURS = 1
SHIELD_COST = 500
SHIELD_DURATION_HOURS = 24
SWORD_COST = 300


# ============================================
# BOOST
# ============================================
BOOST_COST = 30
BOOST_TIME_REDUCTION = 20  # minutes


# ============================================
# ANIMATIONS
# ============================================
ANIMATIONS: Dict[str, Dict[str, Any]] = {
    "marriage": {
        "duration": 3,
        "sound": "wedding_bells",
        "visual": "bells_hearts",
        "emoji": "💒"
    },
    "adoption": {
        "duration": 2,
        "sound": "lullaby",
        "visual": "cradle_tree",
        "emoji": "👶"
    },
    "divorce": {
        "duration": 2,
        "sound": "glass_break",
        "visual": "heart_shatter",
        "emoji": "💔"
    },
    "rob_success": {
        "duration": 2,
        "sound": "coin_drop",
        "visual": "thief_money",
        "emoji": "💰"
    },
    "rob_fail": {
        "duration": 2,
        "sound": "siren",
        "visual": "police_chase",
        "emoji": "🚔"
    },
    "kill_success": {
        "duration": 3,
        "sound": "dark_sound",
        "visual": "skull_ghost",
        "emoji": "💀"
    },
    "daily_claim": {
        "duration": 2,
        "sound": "chime",
        "visual": "sparkles_coins",
        "emoji": "✨"
    },
    "gemstone_fuse": {
        "duration": 3,
        "sound": "magical",
        "visual": "diamond_merge",
        "emoji": "💎"
    },
    "level_up": {
        "duration": 3,
        "sound": "fanfare",
        "visual": "badge_confetti",
        "emoji": "🎉"
    },
    "work_complete": {
        "duration": 2,
        "sound": "whistle",
        "visual": "factory_smoke",
        "emoji": "🏭"
    },
    "harvest": {
        "duration": 2,
        "sound": "rustle",
        "visual": "tractor_crops",
        "emoji": "🚜"
    },
    "cooking_done": {
        "duration": 2,
        "sound": "ding",
        "visual": "steam_reveal",
        "emoji": "🍳"
    },
    "game_win": {
        "duration": 3,
        "sound": "applause",
        "visual": "celebration",
        "emoji": "🏆"
    },
    "game_lose": {
        "duration": 2,
        "sound": "sad_trombone",
        "visual": "sad_retry",
        "emoji": "😢"
    },
    "money_rain": {
        "duration": 5,
        "sound": "coin_rain",
        "visual": "rain_coins",
        "emoji": "🌧️"
    },
    "new_friend": {
        "duration": 2,
        "sound": "pop",
        "visual": "heart_connection",
        "emoji": "❤️"
    },
    "tree_growth": {
        "duration": 2,
        "sound": "wood_creak",
        "visual": "branch_expansion",
        "emoji": "🌳"
    }
}


# ============================================
# ACHIEVEMENTS
# ============================================
ACHIEVEMENT_CATEGORIES = [
    "family",
    "wealth",
    "farming",
    "combat",
    "gaming",
    "social",
    "factory",
    "special"
]

RARITY_LEVELS = ["bronze", "silver", "gold", "diamond", "platinum"]


# ============================================
# REFERRAL
# ============================================
REFERRAL_REWARD_REFERRER = 5000
REFERRAL_REWARD_REFERRED = 10000


# ============================================
# MONEY RAIN
# ============================================
MONEY_RAIN_INTERVAL_HOURS = 3
MONEY_RAIN_COLLECTORS = 3
MONEY_RAIN_REWARD = 500


# ============================================
# REACTIONS
# ============================================
REACTIONS = {
    "hug": {"emoji": "🤗", "gif_type": "hug"},
    "pat": {"emoji": "🫳", "gif_type": "pat"},
    "kiss": {"emoji": "😘", "gif_type": "kiss"},
    "sad": {"emoji": "😢", "gif_type": "sad"},
    "smile": {"emoji": "😊", "gif_type": "smile"},
    "cry": {"emoji": "😭", "gif_type": "cry"},
    "slap": {"emoji": "👋", "gif_type": "slap"},
    "poke": {"emoji": "👉", "gif_type": "poke"}
}
