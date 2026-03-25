"""
Command Router - Setup all handlers
"""
from aiogram import Dispatcher, Router

# Import all handlers
from src.handlers import (
    family,
    friends,
    account,
    combat,
    daily,
    factory,
    garden,
    trading,
    games,
    stats,
    utility,
    settings as settings_handler,
    extra,
    clan,
    achievements,
    insurance,
    cooking,
    nft,
    ai_commands,
    blockchain_commands,
    tournament,
    admin,
    orders,
    pets,
    referral,
    money_rain,
    jobs,
    advanced_games,
    seasons,
    voting,
    notifications
)


def setup_routers(dp: Dispatcher):
    """Setup all command routers"""
    
    # Create main router
    main_router = Router()
    
    # Include all sub-routers
    main_router.include_router(family.router)
    main_router.include_router(friends.router)
    main_router.include_router(account.router)
    main_router.include_router(combat.router)
    main_router.include_router(daily.router)
    main_router.include_router(factory.router)
    main_router.include_router(garden.router)
    main_router.include_router(trading.router)
    main_router.include_router(games.router)
    main_router.include_router(stats.router)
    main_router.include_router(utility.router)
    main_router.include_router(settings_handler.router)
    main_router.include_router(extra.router)
    
    # Advanced features
    main_router.include_router(clan.router)
    main_router.include_router(achievements.router)
    main_router.include_router(insurance.router)
    main_router.include_router(cooking.router)
    main_router.include_router(nft.router)
    main_router.include_router(ai_commands.router)
    main_router.include_router(blockchain_commands.router)
    main_router.include_router(tournament.router)
    main_router.include_router(admin.router)
    main_router.include_router(orders.router)
    main_router.include_router(pets.router)
    main_router.include_router(referral.router)
    main_router.include_router(money_rain.router)
    main_router.include_router(jobs.router)
    main_router.include_router(advanced_games.router)
    main_router.include_router(seasons.router)
    main_router.include_router(voting.router)
    main_router.include_router(notifications.router)
    
    # Include main router in dispatcher
    dp.include_router(main_router)
