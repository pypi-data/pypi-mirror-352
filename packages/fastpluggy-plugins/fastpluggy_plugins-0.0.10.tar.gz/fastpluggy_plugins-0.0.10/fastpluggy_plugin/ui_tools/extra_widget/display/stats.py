"""
Statistics widget for displaying KPIs.
"""

from typing import Optional
from fastpluggy.core.widgets.base import AbstractWidget


class StatsWidget(AbstractWidget):
    """Statistics display widget with icon, value, and trend."""

    widget_type = "stats"
    template_name = "ui_tools/extra_widget/display/stats.html.j2"
    category = "display"
    description = "Statistics card showing KPI with icon, value, and optional trend indicator"
    icon = "bar-chart"

    def __init__(
        self,
        title: str = "",
        value: str = "",
        icon: str = "bar-chart",
        color: str = "primary",
        trend: Optional[str] = None,  # "up", "down", or percentage
        subtitle: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.trend = trend
        self.subtitle = subtitle

    def process(self, **kwargs) -> None:
        """Process stats data and determine trend styling."""
        self.card_classes = f"card bg-{self.color} text-white"

        # Process trend indicator
        if self.trend:
            if self.trend.startswith(('+', '-')) or '%' in self.trend:
                self.trend_value = self.trend
                self.trend_icon = "trending-up" if self.trend.startswith('+') else "trending-down"
                self.trend_color = "success" if self.trend.startswith('+') else "danger"
            elif self.trend in ['up', 'down']:
                self.trend_icon = f"trending-{self.trend}"
                self.trend_color = "success" if self.trend == 'up' else "danger"
