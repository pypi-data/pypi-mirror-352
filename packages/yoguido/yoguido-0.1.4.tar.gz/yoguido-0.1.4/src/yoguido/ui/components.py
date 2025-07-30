"""
UI components for YoGuido framework
"""

import uuid
from typing import Any, Callable, Dict, List, Optional, Union

# Global component tree being built
_component_tree = []
_current_container = None

class UIElement:
    """Base class for all UI elements"""
    
    def __init__(self, element_type: str, **props):
        self.element_type = element_type
        self.element_id = props.get('id', f"hc_{uuid.uuid4().hex[:8]}")
        self.props = props
        self.children: List['UIElement'] = []
        self.event_handlers: Dict[str, str] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.element_type,
            'id': self.element_id,
            'props': self.props,
            'children': [child.to_dict() for child in self.children],
            'handlers': self.event_handlers
        }
    
    def add_child(self, child: 'UIElement'):
        """Add a child element"""
        self.children.append(child)
    
    def register_handler(self, event_type: str, handler_id: str):
        """Register an event handler"""
        self.event_handlers[event_type] = handler_id

def _add_to_current_container(element: UIElement):
    """Add element to current container or global tree"""
    global _current_container, _component_tree
    
    if _current_container:
        print(f"📦 Adding {element.element_type} to container {_current_container.element_type}")
        _current_container.add_child(element)
    else:
        print(f"🌳 Adding {element.element_type} to global tree (tree size: {len(_component_tree)})")
        _component_tree.append(element)
        print(f"🌳 Global tree now has {len(_component_tree)} components")

def _get_component_tree() -> List[Dict[str, Any]]:
    """Get the current component tree as JSON"""
    global _component_tree
    print(f"🔍 _get_component_tree called: {len(_component_tree)} components in tree")
    return [element.to_dict() for element in _component_tree]

def _clear_component_tree():
    """Clear the component tree (for new renders)"""
    global _component_tree
    old_size = len(_component_tree)
    _component_tree = []
    print(f"🧹 Cleared component tree (was {old_size}, now {len(_component_tree)})")

# ==================== BASIC COMPONENTS ====================

def title(text: str, level: int = 1, **kwargs) -> UIElement:
    """Render a title/heading"""
    print(f"📝 title() called: '{text}' (level {level})")
    element = UIElement('title', text=text, level=level, **kwargs)
    _add_to_current_container(element)
    print(f"✅ title element created and added")
    return element

def text(content: str, **kwargs) -> UIElement:
    """Render text content"""
    print(f"📝 text() called: '{content}'")
    element = UIElement('text', content=content, **kwargs)
    _add_to_current_container(element)
    print(f"✅ text element created and added")
    return element

def button(label: str, on_click: Optional[Callable] = None, **kwargs) -> bool:
    """
    Render a button with click handler
    Returns True if button was clicked in this render cycle
    """
    print(f"🔘 button() called: '{label}' with on_click: {on_click is not None}")
    element = UIElement('button', label=label, **kwargs)
    
    # Generate handler ID and register if callback provided
    if on_click:
        from ..server.app import EventRegistry
        handler_id = f"btn_{element.element_id}"
        EventRegistry.register_handler(handler_id, on_click)
        element.register_handler('click', handler_id)
        print(f"🎯 Registered click handler: {handler_id}")
    
    _add_to_current_container(element)
    print(f"✅ button element created and added")
    
    # Check if this button was clicked (simplified - real implementation would check request)
    # For now, return False - actual click detection happens in server
    return False

def input_text(placeholder: str = "", value: str = "", **kwargs) -> str:
    """
    Render a text input field
    Returns the current value
    """
    print(f"📝 input_text() called: placeholder='{placeholder}', value='{value}'")
    element = UIElement('input_text', placeholder=placeholder, value=value, **kwargs)
    _add_to_current_container(element)
    print(f"✅ input_text element created and added")
    
    # In real implementation, this would get the current value from request
    return value

def input_number(placeholder: str = "", value: Union[int, float] = 0, 
                min_val: Optional[Union[int, float]] = None,
                max_val: Optional[Union[int, float]] = None, **kwargs) -> Union[int, float]:
    """
    Render a number input field
    Returns the current value
    """
    print(f"📝 input_number() called: placeholder='{placeholder}', value={value}")
    element = UIElement('input_number', 
                       placeholder=placeholder, 
                       value=value,
                       min=min_val,
                       max=max_val,
                       **kwargs)
    _add_to_current_container(element)
    print(f"✅ input_number element created and added")
    return value

def select(options: List[Union[str, Dict[str, Any]]], value: str = "", **kwargs) -> str:
    """
    Render a select dropdown
    Returns the selected value
    """
    print(f"📝 select() called: {len(options)} options, value='{value}'")
    # Normalize options
    normalized_options = []
    for option in options:
        if isinstance(option, str):
            normalized_options.append({"label": option, "value": option})
        else:
            normalized_options.append(option)
    
    element = UIElement('select', options=normalized_options, value=value, **kwargs)
    _add_to_current_container(element)
    print(f"✅ select element created and added")
    return value

def checkbox(label: str, checked: bool = False, **kwargs) -> bool:
    """
    Render a checkbox
    Returns the checked state
    """
    print(f"📝 checkbox() called: label='{label}', checked={checked}")
    element = UIElement('checkbox', label=label, checked=checked, **kwargs)
    _add_to_current_container(element)
    print(f"✅ checkbox element created and added")
    return checked

def slider(min_val: Union[int, float] = 0, max_val: Union[int, float] = 100,
          value: Union[int, float] = 50, **kwargs) -> Union[int, float]:
    """
    Render a slider
    Returns the current value
    """
    print(f"📝 slider() called: min={min_val}, max={max_val}, value={value}")
    element = UIElement('slider', min=min_val, max=max_val, value=value, **kwargs)
    _add_to_current_container(element)
    print(f"✅ slider element created and added")
    return value

# ==================== LAYOUT COMPONENTS ====================

class LayoutContainer:
    """Context manager for layout containers"""
    
    def __init__(self, element: UIElement):
        self.element = element
        self.prev_container = None
        print(f"📦 LayoutContainer created for {element.element_type}")
    
    def __enter__(self):
        global _current_container
        print(f"📦 Entering {self.element.element_type} container")
        
        # FIXED: Add container to current context FIRST
        _add_to_current_container(self.element)
        
        # THEN set it as the new current container
        self.prev_container = _current_container
        _current_container = self.element
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _current_container
        print(f"📦 Exiting {self.element.element_type} container")
        _current_container = self.prev_container

def container(**kwargs) -> LayoutContainer:
    """Create a basic container"""
    print(f"📦 container() called")
    element = UIElement('container', **kwargs)
    return LayoutContainer(element)

def flex(direction: str = "row", justify: str = "start", align: str = "start", **kwargs) -> LayoutContainer:
    """Create a flex container"""
    print(f"📦 flex() called: direction={direction}, justify={justify}, align={align}")
    element = UIElement('flex', 
                       direction=direction,
                       justify=justify, 
                       align=align,
                       **kwargs)
    return LayoutContainer(element)

def grid(columns: str = "1fr", rows: str = "auto", gap: str = "1rem", **kwargs) -> LayoutContainer:
    """Create a grid container"""
    print(f"📦 grid() called: columns={columns}, rows={rows}, gap={gap}")
    element = UIElement('grid',
                       columns=columns,
                       rows=rows,
                       gap=gap,
                       **kwargs)
    return LayoutContainer(element)