"""
Data display components for YoGuido framework
Add to: yoguido/ui/data_components.py
"""

import uuid
from typing import Any, Callable, Dict, List, Optional, Union
from .basic_components import UIElement, _add_to_current_container, LayoutContainer

def table(data: List[Dict[str, Any]], columns: Optional[List[str]] = None, 
          actions: Optional[List[Dict[str, Any]]] = None, **kwargs) -> UIElement:
    """
    Render a data table with optional actions
    
    Args:
        data: List of dictionaries representing rows
        columns: List of column keys to display (if None, uses all keys from first row)
        actions: List of action buttons per row [{"label": "Edit", "handler": callback}]
    """
    if data is None:
        data = []
    
    print(f"📊 table() called with {len(data)} rows")
    
    if not data:
        columns = columns or []
    else:
        columns = columns or list(data[0].keys())
    
    element = UIElement('table', 
                       data=data, 
                       columns=columns,
                       actions=actions or [],
                       **kwargs)
    _add_to_current_container(element)
    return element

def card(title: str = "", subtitle: str = "", **kwargs) -> LayoutContainer:
    """Create a card container with title and subtitle"""
    print(f"🃏 card() called: title='{title}'")
    element = UIElement('card', title=title, subtitle=subtitle, **kwargs)
    return LayoutContainer(element)

def stats_card(title: str, value: Union[str, int, float], 
               change: Optional[str] = None, trend: str = "neutral", **kwargs) -> UIElement:
    """Render a statistics card"""
    print(f"📈 stats_card() called: {title} = {value}")
    element = UIElement('stats_card', 
                       title=title, 
                       value=str(value),
                       change=change,
                       trend=trend,  # "up", "down", "neutral"
                       **kwargs)
    _add_to_current_container(element)
    return element

def progress_bar(value: Union[int, float], max_value: Union[int, float] = 100,
                label: str = "", color: str = "blue", **kwargs) -> UIElement:
    """Render a progress bar"""
    print(f"📊 progress_bar() called: {value}/{max_value}")
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    element = UIElement('progress_bar',
                       value=value,
                       max_value=max_value,
                       percentage=percentage,
                       label=label,
                       color=color,
                       **kwargs)
    _add_to_current_container(element)
    return element

def badge(text: str, variant: str = "default", **kwargs) -> UIElement:
    """Render a badge/tag"""
    print(f"🏷️ badge() called: '{text}' ({variant})")
    element = UIElement('badge', text=text, variant=variant, **kwargs)
    _add_to_current_container(element)
    return element

def alert(message: str, type: str = "info", dismissible: bool = True, **kwargs) -> UIElement:
    """Render an alert/notification"""
    print(f"⚠️ alert() called: {type} - '{message}'")
    element = UIElement('alert', 
                       message=message, 
                       alert_type=type,  # "info", "success", "warning", "error"
                       dismissible=dismissible,
                       **kwargs)
    _add_to_current_container(element)
    return element

def loading_spinner(text: str = "Loading...", **kwargs) -> UIElement:
    """Render a loading spinner"""
    print(f"⏳ loading_spinner() called: '{text}'")
    element = UIElement('loading_spinner', text=text, **kwargs)
    _add_to_current_container(element)
    return element