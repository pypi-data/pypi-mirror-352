"""
Navigation components for YoGuido framework
Add to: yoguido/ui/navigation_components.py
"""

from typing import Any, Callable, Dict, List, Optional
from .components import UIElement, _add_to_current_container

def breadcrumb(items: List[Dict[str, str]], **kwargs) -> UIElement:
    """
    Render breadcrumb navigation
    items: [{"label": "Home", "url": "/"}, {"label": "Users"}]
    """
    print(f"🍞 breadcrumb() called: {len(items)} items")
    element = UIElement('breadcrumb', items=items, **kwargs)
    _add_to_current_container(element)
    return element

def tabs(items: List[Dict[str, Any]], active_tab: str = "", **kwargs) -> str:
    """
    Render tab navigation
    items: [{"id": "tab1", "label": "Tab 1", "content": "..."}]
    """
    print(f"📑 tabs() called: {len(items)} tabs, active='{active_tab}'")
    element = UIElement('tabs', items=items, active_tab=active_tab, **kwargs)
    _add_to_current_container(element)
    return active_tab

def pagination(current_page: int, total_pages: int, 
               on_page_change: Optional[Callable] = None, **kwargs) -> int:
    """Render pagination controls"""
    print(f"📄 pagination() called: page {current_page}/{total_pages}")
    element = UIElement('pagination',
                       current_page=current_page,
                       total_pages=total_pages,
                       **kwargs)
    
    if on_page_change:
        from ..server.app import EventRegistry
        handler_id = f"page_{element.element_id}"
        EventRegistry.register_handler(handler_id, on_page_change)
        element.register_handler('page_change', handler_id)
    
    _add_to_current_container(element)
    return current_page