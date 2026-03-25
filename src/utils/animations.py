"""
Animation System for Fam Tree Bot
Generates animated GIFs for various events
"""
from typing import Optional, List, Dict
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


class AnimationGenerator:
    """Generate animated GIFs for bot events"""
    
    # Animation presets
    ANIMATIONS = {
        "marriage": {
            "frames": 10,
            "duration": 100,  # ms per frame
            "colors": ["#FF69B4", "#FFD700", "#FF1493"],
            "emoji": "💒"
        },
        "adoption": {
            "frames": 8,
            "duration": 150,
            "colors": ["#87CEEB", "#98FB98", "#FFB6C1"],
            "emoji": "👶"
        },
        "divorce": {
            "frames": 6,
            "duration": 200,
            "colors": ["#808080", "#696969", "#A9A9A9"],
            "emoji": "💔"
        },
        "rob_success": {
            "frames": 8,
            "duration": 120,
            "colors": ["#FFD700", "#FFA500", "#32CD32"],
            "emoji": "💰"
        },
        "rob_fail": {
            "frames": 6,
            "duration": 180,
            "colors": ["#FF0000", "#8B0000", "#DC143C"],
            "emoji": "🚔"
        },
        "kill_success": {
            "frames": 10,
            "duration": 100,
            "colors": ["#000000", "#8B0000", "#4B0082"],
            "emoji": "💀"
        },
        "daily_claim": {
            "frames": 12,
            "duration": 80,
            "colors": ["#FFD700", "#FFFF00", "#FFA500"],
            "emoji": "✨"
        },
        "gemstone_fuse": {
            "frames": 15,
            "duration": 70,
            "colors": ["#FF0000", "#0000FF", "#00FF00", "#FFFF00", "#000000"],
            "emoji": "💎"
        },
        "level_up": {
            "frames": 10,
            "duration": 100,
            "colors": ["#FFD700", "#FFA500", "#FF69B4"],
            "emoji": "🎉"
        },
        "work_complete": {
            "frames": 8,
            "duration": 120,
            "colors": ["#4682B4", "#87CEEB", "#B0C4DE"],
            "emoji": "🏭"
        },
        "harvest": {
            "frames": 10,
            "duration": 100,
            "colors": ["#228B22", "#32CD32", "#90EE90"],
            "emoji": "🚜"
        },
        "cooking_done": {
            "frames": 8,
            "duration": 120,
            "colors": ["#FFA500", "#FF8C00", "#FFD700"],
            "emoji": "🍳"
        },
        "game_win": {
            "frames": 12,
            "duration": 80,
            "colors": ["#FFD700", "#00FF00", "#FF69B4"],
            "emoji": "🏆"
        },
        "game_lose": {
            "frames": 6,
            "duration": 200,
            "colors": ["#808080", "#696969", "#A9A9A9"],
            "emoji": "😢"
        },
        "money_rain": {
            "frames": 20,
            "duration": 50,
            "colors": ["#FFD700", "#32CD32", "#00FF00"],
            "emoji": "🌧️"
        },
        "new_friend": {
            "frames": 8,
            "duration": 120,
            "colors": ["#FF69B4", "#FFB6C1", "#FFC0CB"],
            "emoji": "❤️"
        },
        "tree_growth": {
            "frames": 10,
            "duration": 100,
            "colors": ["#228B22", "#8B4513", "#90EE90"],
            "emoji": "🌳"
        }
    }
    
    def __init__(self):
        self.enabled = True
    
    def generate_animation(
        self,
        animation_type: str,
        text: Optional[str] = None,
        size: tuple = (400, 400)
    ) -> Optional[BytesIO]:
        """Generate animation GIF"""
        if animation_type not in self.ANIMATIONS:
            return None
        
        config = self.ANIMATIONS[animation_type]
        frames = []
        
        for i in range(config["frames"]):
            # Create frame
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw animated elements
            self._draw_frame(draw, i, config["frames"], config["colors"], size)
            
            # Add text if provided
            if text:
                self._draw_text(draw, text, size)
            
            frames.append(img)
        
        # Save to BytesIO
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=config["duration"],
            loop=0,
            transparency=0
        )
        output.seek(0)
        
        return output
    
    def _draw_frame(
        self,
        draw: ImageDraw.Draw,
        frame_num: int,
        total_frames: int,
        colors: List[str],
        size: tuple
    ):
        """Draw a single animation frame"""
        import random
        
        width, height = size
        progress = frame_num / total_frames
        
        # Draw particles
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(3, 10)
            color = random.choice(colors)
            
            # Pulsing effect
            pulse = abs((progress * 2) - 1)
            r = int(r * (0.5 + pulse))
            
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        
        # Draw center glow
        center_x, center_y = width // 2, height // 2
        glow_size = int(50 + 30 * progress)
        
        for i in range(5):
            alpha = int(100 * (1 - i/5) * (1 - progress))
            glow_color = self._hex_to_rgba(colors[0], alpha)
            draw.ellipse(
                [center_x - glow_size - i*10, center_y - glow_size - i*10,
                 center_x + glow_size + i*10, center_y + glow_size + i*10],
                outline=glow_color
            )
    
    def _draw_text(self, draw: ImageDraw.Draw, text: str, size: tuple):
        """Draw text on frame"""
        width, height = size
        
        # Use default font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - 20
        
        # Draw text with outline
        outline_color = "black"
        fill_color = "white"
        
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> tuple:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)
    
    def get_animation_info(self, animation_type: str) -> Dict:
        """Get animation configuration"""
        return self.ANIMATIONS.get(animation_type, {})
