"""
Custom Exceptions for Fam Tree Bot
"""


class FamTreeBotException(Exception):
    """Base exception for all bot errors"""
    pass


# Validation Exceptions
class ValidationError(FamTreeBotException):
    """Input validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


class InsufficientFundsError(FamTreeBotException):
    """Not enough money"""
    pass


class LimitExceededError(FamTreeBotException):
    """Daily limit exceeded"""
    pass


class UserNotFoundError(FamTreeBotException):
    """User not found in database"""
    pass


class AlreadyExistsError(FamTreeBotException):
    """Resource already exists"""
    pass


class NotFoundError(FamTreeBotException):
    """Resource not found"""
    pass


# Family System Exceptions
class FamilyError(FamTreeBotException):
    """Family-related error"""
    pass


class AlreadyMarriedError(FamilyError):
    """User is already married"""
    pass


class MaxChildrenError(FamilyError):
    """Maximum children limit reached"""
    pass


class MaxPartnersError(FamilyError):
    """Maximum partners limit reached"""
    pass


class HasParentError(FamilyError):
    """User already has a parent"""
    pass


class NotRelatedError(FamilyError):
    """Users are not related"""
    pass


class SelfRelationError(FamilyError):
    """Cannot relate to self"""
    pass


class BlockedError(FamilyError):
    """User has blocked you"""
    pass


# Friend System Exceptions
class FriendError(FamTreeBotException):
    """Friend-related error"""
    pass


class AlreadyFriendsError(FriendError):
    """Already friends with user"""
    pass


class MaxFriendsError(FriendError):
    """Maximum friends limit reached"""
    pass


class NotFriendsError(FriendError):
    """Not friends with user"""
    pass


# Combat System Exceptions
class CombatError(FamTreeBotException):
    """Combat-related error"""
    pass


class UserDeadError(CombatError):
    """User is dead"""
    pass


class RobberyFailedError(CombatError):
    """Robbery attempt failed"""
    pass


class KillFailedError(CombatError):
    """Kill attempt failed"""
    pass


class WeaponNotOwnedError(CombatError):
    """User doesn't own this weapon"""
    pass


# Garden System Exceptions
class GardenError(FamTreeBotException):
    """Garden-related error"""
    pass


class PlotOccupiedError(GardenError):
    """Plot is already occupied"""
    pass


class PlotEmptyError(GardenError):
    """Plot is empty"""
    pass


class CropNotReadyError(GardenError):
    """Crop is not ready to harvest"""
    pass


class InsufficientSeedsError(GardenError):
    """Not enough seeds in barn"""
    pass


class BarnFullError(GardenError):
    """Barn is full"""
    pass


# Factory System Exceptions
class FactoryError(FamTreeBotException):
    """Factory-related error"""
    pass


class WorkerOwnedError(FactoryError):
    """Worker is already owned"""
    pass


class MaxWorkersError(FactoryError):
    """Maximum workers limit reached"""
    pass


class ShieldActiveError(FactoryError):
    """Target has active shield"""
    pass


# Trading System Exceptions
class TradingError(FamTreeBotException):
    """Trading-related error"""
    pass


class InvalidPriceError(TradingError):
    """Invalid price for item"""
    pass


class InsufficientItemsError(TradingError):
    """Not enough items to sell"""
    pass


# Game Exceptions
class GameError(FamTreeBotException):
    """Game-related error"""
    pass


class GameInProgressError(GameError):
    """Game is already in progress"""
    pass


class InvalidAnswerError(GameError):
    """Invalid answer provided"""
    pass


class TimeoutError(GameError):
    """Game timed out"""
    pass


# Rate Limiting
class RateLimitError(FamTreeBotException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")


# Permission Errors
class PermissionError(FamTreeBotException):
    """Permission denied"""
    pass


class AdminRequiredError(PermissionError):
    """Admin privileges required"""
    pass


class OwnerRequiredError(PermissionError):
    """Owner privileges required"""
    pass


# State Machine Errors
class StateError(FamTreeBotException):
    """State machine error"""
    pass


class InvalidStateError(StateError):
    """Invalid state for operation"""
    pass


class StateTimeoutError(StateError):
    """State has timed out"""
    pass
