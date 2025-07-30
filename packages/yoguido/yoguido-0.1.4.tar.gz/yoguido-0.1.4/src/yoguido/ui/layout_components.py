"""
Layout components for YoGuido framework
Add to: yoguido/ui/layout_components.py
"""

from typing import Any, Callable, Optional
from .components import UIElement, _add_to_current_container, LayoutContainer

def sidebar(**kwargs) -> LayoutContainer:
    """Create a sidebar container"""
    print(f"📌 sidebar() called")
    element = UIElement('sidebar', **kwargs)
    return LayoutContainer(element)

def header(**kwargs) -> LayoutContainer:
    """Create a header container"""
    print(f"🔝 header() called")
    element = UIElement('header', **kwargs)
    return LayoutContainer(element)

def footer(**kwargs) -> LayoutContainer:
    """Create a footer container"""
    print(f"🔚 footer() called")
    element = UIElement('footer', **kwargs)
    return LayoutContainer(element)

def modal(title: str, visible: bool = False, 
          on_close: Optional[Callable] = None, **kwargs) -> LayoutContainer:
    """Create a modal dialog"""
    print(f"🪟 modal() called: '{title}', visible={visible}")
    element = UIElement('modal', title=title, visible=visible, **kwargs)
    
    if on_close:
        from ..server.app import EventRegistry
        handler_id = f"modal_close_{element.element_id}"
        EventRegistry.register_handler(handler_id, on_close)
        element.register_handler('close', handler_id)
    
    return LayoutContainer(element)

def dropdown(trigger_text: str, **kwargs) -> LayoutContainer:
    """Create a dropdown menu"""
    print(f"📥 dropdown() called: '{trigger_text}'")
    element = UIElement('dropdown', trigger_text=trigger_text, **kwargs)
    return LayoutContainer(element)

def separator(text: str = "", **kwargs) -> UIElement:
    """Render a visual separator/divider"""
    print(f"➖ separator() called: '{text}'")
    element = UIElement('separator', text=text, **kwargs)
    _add_to_current_container(element)
    return element

def spacer(height: str = "1rem", **kwargs) -> UIElement:
    """Render empty vertical space"""
    print(f"⬜ spacer() called: height={height}")
    element = UIElement('spacer', height=height, **kwargs)
    _add_to_current_container(element)
    return element