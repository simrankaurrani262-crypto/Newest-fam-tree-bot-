# 🌳 Fam Tree Bot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot API 7.0+](https://img.shields.io/badge/Telegram%20Bot%20API-7.0+-blue.svg)](https://core.telegram.org/bots/api)

> **The Ultimate Real-Life Simulator RPG Telegram Bot**

Fam Tree Bot is a revolutionary, world-class Telegram bot that delivers the ultimate Family Simulation & Gardening RPG experience, combining social family-building, strategic PvP combat, immersive farming simulation, dynamic trading economy, competitive mini-games, AI-powered features, and blockchain integration.

## ✨ Features

### 🏠 Family System (Module 1)
- **Dynamic Family Tree Visualization** - Hierarchical tree diagram with profile pictures
- **Adoption System** - Adopt users as children with confirmation flow
- **Marriage System** - Propose, marry, and divorce with animations
- **Relationship Management** - Parents, children, siblings, spouses
- **Profile Pictures** - Custom PFPs with GIF/sticker support

### 👥 Friend System (Module 2)
- **Radial Friend Network** - Visual friend circle with connections
- **Friend Requests** - Send/receive friend requests with rewards
- **Global Network** - Cross-chat friend discovery
- **Activity Status** - Online/offline tracking

### 💰 Economy System (Module 3)
- **Rich Dashboard** - Complete profile with stats
- **Bank System** - Secure deposits and withdrawals
- **Payment System** - Transfer money with math expressions
- **Reputation System** - 0-200 reputation scale
- **Health System** - 5-heart health mechanic

### ⚔️ Combat System (Module 3.2)
- **Weapon Arsenal** - 8 weapons with different stats
- **Robbery System** - Steal money (8/day limit)
- **Kill System** - PvP combat (5/day limit)
- **Medical System** - Self-revive and blood donation
- **Insurance System** - Protect against death

### 🌱 Garden System (Module 6)
- **3x3 Garden Grid** - Expandable to 12 slots
- **6 Crop Types** - Pepper, Potato, Eggplant, Carrot, Corn, Tomato
- **Seasonal System** - 2x growth speed in season
- **Barn Management** - 500 capacity storage
- **Order System** - Complete orders for rewards
- **Fertilizing** - Speed up crop growth

### 🏭 Factory System (Module 5)
- **Worker Hiring** - Hire up to 5 workers
- **Work Cycles** - 1-hour work periods
- **Equipment System** - Shields and swords
- **Rating System** - Worker productivity tracking

### 🛒 Trading System (Module 7)
- **Global Marketplace** - Buy/sell crops worldwide
- **Personal Stands** - Create your own shop
- **Price Alerts** - Get notified of deals
- **Auto-boxing** - 50 crops per box

### 🍳 Cooking System (Module 8)
- **Collaborative Cooking** - Multiple users contribute
- **9 Recipes** - Popcorn, Fries, Salad, etc.
- **Ingredient Sharing** - Cross-chat sync

### 🎮 Mini Games (Module 9)
- **4 Pics 1 Word** - Image puzzle game
- **Ripple Betting** - Risk/reward betting
- **Nation Guessing** - Geography quiz
- **Trivia** - Knowledge testing
- **Lottery** - Group lottery system
- **Paper Tactics** - Grid-based strategy

### 📊 Statistics (Module 10)
- **Money Leaderboard** - Richest players
- **Interactive Graphs** - Balance history charts
- **Activity Stats** - Personal analytics
- **Heatmaps** - Activity patterns

### 🤖 AI Features (Module 21)
- **AI Assistant** - Smart recommendations
- **Image Generation** - AI-powered artwork
- **Sentiment Analysis** - Chat mood detection
- **Natural Language** - Free-form commands

### ⛓️ Blockchain (Module 22)
- **NFT Badges** - Collectible achievements
- **Crypto Payments** - BTC, ETH, USDT, SOL
- **NFT Marketplace** - Trade digital assets
- **Smart Contracts** - Automated payouts

### 🎨 Customization (Module 32)
- **Theme Engine** - 9 visual themes
- **Avatar System** - 1000+ customization options
- **Custom Animations** - Upload your own
- **Sound Effects** - Custom sound packs

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Telegram Bot Token

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fam-tree-bot.git
cd fam-tree-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start the bot
python src/main.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Command Reference](docs/commands/family_commands.md)
- [Deployment Guide](docs/deployment/production_checklist.md)
- [Development Setup](docs/development/setup.md)

## 🌐 Supported Languages

- 🇺🇸 English (EN)
- 🇷🇺 Russian (RU)
- 🇫🇷 French (FR)
- 🇪🇸 Spanish (ES)
- 🇩🇪 German (DE)
- 🇨🇳 Chinese (ZH)
- 🇮🇹 Italian (IT)
- 🇺🇦 Ukrainian (UK)

## 🛡️ Security

- Two-Factor Authentication (2FA)
- End-to-End Encryption
- Anti-Cheat System
- Privacy Controls
- GDPR Compliance

## 📊 Performance

- Response Time: < 1.5 seconds (target < 1s)
- Uptime: 99.99%
- Concurrent Users: 100,000+
- Animation FPS: 60fps smooth

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot Framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Celery](https://docs.celeryq.dev/) - Distributed Task Queue
- [Redis](https://redis.io/) - In-memory Data Store

---
