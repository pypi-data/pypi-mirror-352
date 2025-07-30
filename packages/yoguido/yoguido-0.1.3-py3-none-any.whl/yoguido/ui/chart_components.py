"""
Chart components for YoGuido framework
Add to: yoguido/ui/chart_components.py
"""

from typing import Any, Dict, List
from .basic_components import UIElement, _add_to_current_container

def line_chart(data: List[Dict[str, Any]], x_key: str, y_key: str,
               title: str = "", **kwargs) -> UIElement:
    """Render a line chart"""
    if data is None:
        data = []
    print(f"📈 line_chart() called: {len(data)} data points")
    element = UIElement('line_chart',
                       data=data,
                       x_key=x_key,
                       y_key=y_key,
                       title=title,
                       **kwargs)
    _add_to_current_container(element)
    return element

def bar_chart(data: List[Dict[str, Any]], x_key: str, y_key: str,
              title: str = "", **kwargs) -> UIElement:
    """Render a bar chart"""
    if data is None:
        data = []
    print(f"📊 bar_chart() called: {len(data)} data points")
    element = UIElement('bar_chart',
                       data=data,
                       x_key=x_key,
                       y_key=y_key,
                       title=title,
                       **kwargs)
    _add_to_current_container(element)
    return element

def pie_chart(data: List[Dict[str, Any]], label_key: str, value_key: str,
              title: str = "", **kwargs) -> UIElement:
    """Render a pie chart"""
    if data is None:
        data = []
    print(f"🥧 pie_chart() called: {len(data)} segments")
    element = UIElement('pie_chart',
                       data=data,
                       label_key=label_key,
                       value_key=value_key,
                       title=title,
                       **kwargs)
    _add_to_current_container(element)
    return element