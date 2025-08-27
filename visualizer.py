"""
Data Visualizer
===============
Charts. Graphs. Visual clarity.
"""

from typing import List, Optional
import math

class Visualizer:
    """ASCII visualization tools for terminal display"""
    
    # Sparkline characters for different heights (8 levels)
    SPARK_CHARS = ' ▁▂▃▄▅▆▇█'
    
    # Bar chart characters
    BAR_CHARS = '│▌█'
    
    @staticmethod
    def generate_sparkline(prices: List[float], width: int = 50) -> str:
        """Generate a sparkline chart from price data
        
        Args:
            prices: List of price values
            width: Maximum width of the sparkline
            
        Returns:
            ASCII sparkline string
        """
        if not prices or len(prices) < 2:
            return "No data"
            
        # Use last 'width' prices if we have more
        if len(prices) > width:
            prices = prices[-width:]
            
        # Find min and max for scaling
        min_price = min(prices)
        max_price = max(prices)
        
        # Handle flat lines
        if max_price == min_price:
            return Visualizer.SPARK_CHARS[4] * len(prices)
            
        # Scale prices to 0-8 range
        scaled = []
        for price in prices:
            # Normalize to 0-1
            normalized = (price - min_price) / (max_price - min_price)
            # Scale to 0-8 (9 levels)
            level = int(normalized * 8)
            scaled.append(min(8, max(0, level)))
            
        # Build sparkline
        return ''.join(Visualizer.SPARK_CHARS[level] for level in scaled)
        
    @staticmethod
    def generate_bar_chart(values: List[float], labels: List[str], 
                          width: int = 40, height: int = 10) -> List[str]:
        """Generate a horizontal bar chart
        
        Args:
            values: List of values to chart
            labels: List of labels for each bar
            width: Maximum bar width
            height: Maximum number of bars to show
            
        Returns:
            List of strings representing the chart
        """
        if not values or not labels:
            return ["No data to display"]
            
        # Limit to height
        if len(values) > height:
            values = values[:height]
            labels = labels[:height]
            
        # Find max value for scaling
        max_val = max(values) if max(values) > 0 else 1
        
        lines = []
        
        # Calculate label width
        label_width = max(len(label) for label in labels) + 2
        
        for label, value in zip(labels, values):
            # Create label
            label_str = f"{label:<{label_width}}"
            
            # Calculate bar length
            if value > 0:
                bar_length = int((value / max_val) * width)
                bar_length = max(1, bar_length)  # At least 1 char
                
                # Create bar
                bar = '█' * bar_length
                
                # Add value at end
                value_str = f" {value:.2f}"
                
                lines.append(f"{label_str}{bar}{value_str}")
            else:
                lines.append(f"{label_str}│ {value:.2f}")
                
        return lines
        
    @staticmethod
    def generate_price_chart(prices: List[float], width: int = 60, height: int = 12) -> List[str]:
        """Generate a full ASCII price chart with scale
        
        Args:
            prices: List of price values
            width: Chart width
            height: Chart height
            
        Returns:
            List of strings representing the chart
        """
        if not prices or len(prices) < 2:
            return ["Insufficient data for chart"]
            
        # Use last 'width' prices
        if len(prices) > width:
            prices = prices[-width:]
            
        min_price = min(prices)
        max_price = max(prices)
        
        # Create chart grid
        chart = []
        
        # Add title
        chart.append(f"Price Chart (Last {len(prices)} periods)")
        chart.append("=" * (width + 10))
        
        # Create the plot area
        for h in range(height, 0, -1):
            line = ""
            
            # Y-axis label
            price_at_height = min_price + (max_price - min_price) * (h / height)
            line += f"{price_at_height:8.2f} │"
            
            # Plot points
            for i, price in enumerate(prices):
                normalized = (price - min_price) / (max_price - min_price) if max_price > min_price else 0.5
                price_height = int(normalized * height)
                
                if price_height >= h:
                    line += "█"
                elif price_height == h - 1:
                    line += "▄"
                else:
                    line += " "
                    
            chart.append(line)
            
        # Add x-axis
        chart.append(" " * 9 + "└" + "─" * width)
        
        # Add time labels
        if len(prices) <= 10:
            # Show all indices
            time_labels = " " * 10 + "".join(f"{i:<6}" for i in range(len(prices)))
        else:
            # Show start, middle, end
            time_labels = f"{' ' * 10}0{' ' * (width//2 - 2)}{len(prices)//2}{' ' * (width//2 - 4)}{len(prices)-1}"
            
        chart.append(time_labels[:width + 10])
        
        return chart
        
    @staticmethod
    def colorize_value(value: float, positive_color: str = '', negative_color: str = '') -> str:
        """Add color to a value based on positive/negative
        
        Args:
            value: The value to colorize
            positive_color: ANSI color code for positive
            negative_color: ANSI color code for negative
            
        Returns:
            Colored string (if colors provided)
        """
        if value >= 0 and positive_color:
            return f"{positive_color}{value:+.2f}%\033[0m"
        elif value < 0 and negative_color:
            return f"{negative_color}{value:+.2f}%\033[0m"
        else:
            return f"{value:+.2f}%"
            
    @staticmethod
    def generate_volume_bars(volumes: List[int], width: int = 50) -> str:
        """Generate a simple volume indicator bar
        
        Args:
            volumes: List of volume values
            width: Width of the bar
            
        Returns:
            Volume bar string
        """
        if not volumes:
            return "No volume data"
            
        # Use recent volumes
        recent = volumes[-20:] if len(volumes) > 20 else volumes
        avg_volume = sum(recent) / len(recent)
        current_volume = volumes[-1]
        
        # Calculate relative volume
        rel_volume = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Create bar
        bar_length = int(min(rel_volume * 20, width))
        bar = '█' * bar_length
        
        return f"Vol: {bar} {rel_volume:.1f}x avg"