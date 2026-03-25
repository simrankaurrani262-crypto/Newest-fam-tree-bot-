"""
NFT Contract Handler
Manages NFT minting, transfers, and marketplace
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class NFT:
    """NFT data"""
    token_id: int
    owner_id: int
    name: str
    description: str
    image_url: str
    rarity: str  # common, uncommon, rare, epic, legendary
    attributes: Dict
    created_at: datetime
    price: Optional[Decimal] = None
    is_for_sale: bool = False


class NFTContract:
    """NFT contract handler"""
    
    RARITY_TIERS = {
        "common": {"chance": 0.5, "multiplier": 1},
        "uncommon": {"chance": 0.3, "multiplier": 2},
        "rare": {"chance": 0.15, "multiplier": 5},
        "epic": {"chance": 0.04, "multiplier": 10},
        "legendary": {"chance": 0.01, "multiplier": 50}
    }
    
    def __init__(self):
        self.nfts: Dict[int, NFT] = {}
        self.user_nfts: Dict[int, List[int]] = {}
        self.marketplace: Dict[int, NFT] = {}
        self.next_token_id = 1
        self.enabled = False
    
    def mint_achievement_nft(
        self,
        user_id: int,
        achievement_name: str,
        tier: str
    ) -> Optional[NFT]:
        """Mint achievement NFT"""
        if not self.enabled:
            return None
        
        rarity = self._determine_rarity()
        
        nft = NFT(
            token_id=self.next_token_id,
            owner_id=user_id,
            name=f"{achievement_name} Badge",
            description=f"Awarded for achieving {achievement_name}",
            image_url=f"https://api.famtreebot.com/nfts/{self.next_token_id}.png",
            rarity=rarity,
            attributes={
                "achievement": achievement_name,
                "tier": tier,
                "power": self.RARITY_TIERS[rarity]["multiplier"]
            },
            created_at=datetime.utcnow()
        )
        
        self.nfts[self.next_token_id] = nft
        
        if user_id not in self.user_nfts:
            self.user_nfts[user_id] = []
        self.user_nfts[user_id].append(self.next_token_id)
        
        logger.info(f"Minted NFT {self.next_token_id} for user {user_id}")
        
        self.next_token_id += 1
        return nft
    
    def mint_family_nft(self, user_id: int, family_size: int) -> Optional[NFT]:
        """Mint family milestone NFT"""
        if not self.enabled:
            return None
        
        rarity = "common"
        if family_size >= 50:
            rarity = "legendary"
        elif family_size >= 20:
            rarity = "epic"
        elif family_size >= 10:
            rarity = "rare"
        elif family_size >= 5:
            rarity = "uncommon"
        
        nft = NFT(
            token_id=self.next_token_id,
            owner_id=user_id,
            name=f"Family of {family_size}",
            description=f"Celebrating a family of {family_size} members!",
            image_url=f"https://api.famtreebot.com/nfts/family_{self.next_token_id}.png",
            rarity=rarity,
            attributes={
                "family_size": family_size,
                "power": self.RARITY_TIERS[rarity]["multiplier"]
            },
            created_at=datetime.utcnow()
        )
        
        self.nfts[self.next_token_id] = nft
        
        if user_id not in self.user_nfts:
            self.user_nfts[user_id] = []
        self.user_nfts[user_id].append(self.next_token_id)
        
        logger.info(f"Minted family NFT {self.next_token_id} for user {user_id}")
        
        self.next_token_id += 1
        return nft
    
    def list_for_sale(self, user_id: int, token_id: int, price: Decimal) -> bool:
        """List NFT for sale"""
        if token_id not in self.nfts:
            return False
        
        nft = self.nfts[token_id]
        
        if nft.owner_id != user_id:
            return False
        
        nft.is_for_sale = True
        nft.price = price
        self.marketplace[token_id] = nft
        
        logger.info(f"Listed NFT {token_id} for sale at {price}")
        return True
    
    def buy_nft(self, buyer_id: int, token_id: int) -> bool:
        """Buy NFT from marketplace"""
        if token_id not in self.marketplace:
            return False
        
        nft = self.marketplace[token_id]
        
        # Transfer ownership
        old_owner = nft.owner_id
        
        if old_owner in self.user_nfts:
            self.user_nfts[old_owner].remove(token_id)
        
        nft.owner_id = buyer_id
        nft.is_for_sale = False
        nft.price = None
        
        if buyer_id not in self.user_nfts:
            self.user_nfts[buyer_id] = []
        self.user_nfts[buyer_id].append(token_id)
        
        del self.marketplace[token_id]
        
        logger.info(f"NFT {token_id} bought by user {buyer_id}")
        return True
    
    def get_user_nfts(self, user_id: int) -> List[NFT]:
        """Get all NFTs owned by user"""
        if user_id not in self.user_nfts:
            return []
        
        return [self.nfts[tid] for tid in self.user_nfts[user_id]]
    
    def get_marketplace(self) -> List[NFT]:
        """Get all NFTs for sale"""
        return list(self.marketplace.values())
    
    def _determine_rarity(self) -> str:
        """Determine rarity based on chance"""
        import random
        
        roll = random.random()
        cumulative = 0
        
        for rarity, data in self.RARITY_TIERS.items():
            cumulative += data["chance"]
            if roll <= cumulative:
                return rarity
        
        return "common"
    
    def format_nft(self, nft: NFT) -> str:
        """Format NFT for display"""
        rarity_emoji = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }
        
        text = (
            f"{rarity_emoji.get(nft.rarity, '⚪')} <b>{nft.name}</b>\n"
            f"   Token ID: #{nft.token_id}\n"
            f"   Rarity: {nft.rarity.title()}\n"
            f"   {nft.description}\n"
        )
        
        if nft.is_for_sale and nft.price:
            text += f"   💰 For Sale: {nft.price} ETH\n"
        
        return text
