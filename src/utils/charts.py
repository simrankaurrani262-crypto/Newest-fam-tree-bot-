"""
Chart and Graph Generation for Fam Tree Bot
Creates visual charts for statistics and analytics
"""
from typing import List, Dict, Optional, Tuple
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available, charts will be disabled")


class ChartGenerator:
    """Generate charts and graphs"""
    
    # Color schemes
    COLORS = {
        "primary": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
        "pastel": ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#FFDFBA"],
        "dark": ["#2C3E50", "#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
        "gradient": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
    }
    
    def __init__(self):
        self.enabled = MATPLOTLIB_AVAILABLE
    
    def generate_balance_chart(
        self,
        data: List[Tuple[str, float]],
        title: str = "Balance History",
        color_scheme: str = "primary"
    ) -> Optional[BytesIO]:
        """Generate line chart for balance history"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        dates = [d[0] for d in data]
        values = [d[1] for d in data]
        colors = self.COLORS.get(color_scheme, self.COLORS["primary"])
        
        # Plot line
        ax.plot(dates, values, color=colors[0], linewidth=2, marker='o', markersize=8)
        
        # Fill area under line
        ax.fill_between(dates, values, alpha=0.3, color=colors[0])
        
        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Balance ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save to BytesIO
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def generate_pie_chart(
        self,
        data: Dict[str, float],
        title: str = "Distribution",
        color_scheme: str = "pastel"
    ) -> Optional[BytesIO]:
        """Generate pie chart"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = list(data.keys())
        sizes = list(data.values())
        colors = self.COLORS.get(color_scheme, self.COLORS["pastel"])
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors[:len(labels)],
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05] * len(labels)
        )
        
        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Style text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def generate_bar_chart(
        self,
        data: Dict[str, float],
        title: str = "Comparison",
        color_scheme: str = "primary",
        horizontal: bool = False
    ) -> Optional[BytesIO]:
        """Generate bar chart"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = list(data.keys())
        values = list(data.values())
        colors = self.COLORS.get(color_scheme, self.COLORS["primary"])
        
        if horizontal:
            bars = ax.barh(labels, values, color=colors[:len(labels)])
            ax.set_xlabel('Value', fontsize=12)
        else:
            bars = ax.bar(labels, values, color=colors[:len(labels)])
            ax.set_ylabel('Value', fontsize=12)
            plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            if horizontal:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       f' ${width:,.0f}',
                       ha='left', va='center', fontsize=10)
            else:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=10)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x' if horizontal else 'y')
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def generate_leaderboard_chart(
        self,
        data: List[Tuple[str, float]],
        title: str = "Leaderboard"
    ) -> Optional[BytesIO]:
        """Generate leaderboard bar chart"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        names = [d[0] for d in data]
        values = [d[1] for d in data]
        
        # Create horizontal bar chart
        colors = plt.cm.viridis([i/len(data) for i in range(len(data))])
        bars = ax.barh(names, values, color=colors)
        
        # Add rank medals for top 3
        medals = ["🥇", "🥈", "🥉"]
        for i, (bar, medal) in enumerate(zip(bars[:3], medals)):
            ax.text(0, bar.get_y() + bar.get_height()/2,
                   f' {medal} ',
                   ha='left', va='center', fontsize=16)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(value, bar.get_y() + bar.get_height()/2,
                   f' ${value:,.0f} ',
                   ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Balance ($)', fontsize=12)
        ax.invert_yaxis()  # Highest at top
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def generate_activity_heatmap(
        self,
        data: List[List[int]],
        title: str = "Activity Heatmap"
    ) -> Optional[BytesIO]:
        """Generate activity heatmap"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [f'{h:02d}:00' for h in range(24)]
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
        
        # Set ticks
        ax.set_xticks(range(24))
        ax.set_xticklabels(hours, rotation=45)
        ax.set_yticks(range(7))
        ax.set_yticklabels(days)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Activity Level', rotation=270, labelpad=20)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Day of Week', fontsize=12)
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def generate_family_tree_visual(
        self,
        family_data: Dict,
        title: str = "Family Tree"
    ) -> Optional[BytesIO]:
        """Generate family tree visualization"""
        if not self.enabled:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Title
        ax.text(50, 95, title, ha='center', va='top',
               fontsize=20, fontweight='bold')
        
        # Draw root (user)
        self._draw_person_node(ax, 50, 80, "You", "#4ECDC4")
        
        # Draw spouses
        spouses = family_data.get("spouses", [])
        for i, spouse in enumerate(spouses[:3]):
            x = 30 + i * 20
            self._draw_person_node(ax, x, 65, spouse.get("name", "Spouse"), "#FF6B6B")
            self._draw_connection(ax, 50, 75, x, 70)
        
        # Draw children
        children = family_data.get("children", [])
        for i, child in enumerate(children[:5]):
            x = 20 + i * 15
            self._draw_person_node(ax, x, 40, child.get("name", "Child"), "#96CEB4")
            self._draw_connection(ax, 50, 75, x, 45)
        
        # Draw parents
        parents = family_data.get("parents", [])
        for i, parent in enumerate(parents[:2]):
            x = 40 + i * 20
            self._draw_person_node(ax, x, 90, parent.get("name", "Parent"), "#FFEAA7")
            self._draw_connection(ax, x, 85, 50, 85)
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
    
    def _draw_person_node(self, ax, x, y, name, color):
        """Draw a person node"""
        circle = plt.Circle((x, y), 5, color=color, ec='black', linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, name[:8], ha='center', va='center',
               fontsize=8, fontweight='bold', zorder=4)
    
    def _draw_connection(self, ax, x1, y1, x2, y2):
        """Draw connection line between nodes"""
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, zorder=1)
    
    def generate_radar_chart(
        self,
        data: Dict[str, float],
        title: str = "Stats Overview"
    ) -> Optional[BytesIO]:
        """Generate radar/spider chart"""
        if not self.enabled:
            return None
        
        categories = list(data.keys())
        values = list(data.values())
        
        # Close the plot
        values += values[:1]
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#4ECDC4')
        ax.fill(angles, values, alpha=0.25, color='#4ECDC4')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        output = BytesIO()
        plt.savefig(output, format='png', dpi=100, bbox_inches='tight')
        output.seek(0)
        plt.close()
        
        return output
