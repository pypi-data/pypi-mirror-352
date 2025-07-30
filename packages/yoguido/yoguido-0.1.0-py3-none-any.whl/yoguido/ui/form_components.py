"""
Form components for YoGuido framework
Add to: yoguido/ui/form_components.py
"""

import uuid
from typing import Any, Callable, Dict, List, Optional, Union
from .components import UIElement, _add_to_current_container, LayoutContainer

def textarea(placeholder: str = "", value: str = "", rows: int = 4, **kwargs) -> str:
    """Render a textarea input"""
    print(f"📝 textarea() called: {rows} rows")
    element = UIElement('textarea', 
                       placeholder=placeholder, 
                       value=value,
                       rows=rows,
                       **kwargs)
    _add_to_current_container(element)
    return value

def date_picker(value: str = "", label: str = "", **kwargs) -> str:
    """Render a date picker input"""
    print(f"📅 date_picker() called: value='{value}'")
    element = UIElement('date_picker', value=value, label=label, **kwargs)
    _add_to_current_container(element)
    return value

def file_upload(accept: str = "*", multiple: bool = False, 
                label: str = "Choose file", **kwargs) -> List[str]:
    """Render a file upload input"""
    print(f"📁 file_upload() called: accept='{accept}', multiple={multiple}")
    element = UIElement('file_upload',
                       accept=accept,
                       multiple=multiple,
                       label=label,
                       **kwargs)
    _add_to_current_container(element)
    return []  # Return list of uploaded file names

def radio_group(options: List[Union[str, Dict[str, Any]]], 
                value: str = "", name: str = "", **kwargs) -> str:
    """Render a radio button group"""
    print(f"📻 radio_group() called: {len(options)} options")
    
    # Normalize options
    normalized_options = []
    for option in options:
        if isinstance(option, str):
            normalized_options.append({"label": option, "value": option})
        else:
            normalized_options.append(option)
    
    element = UIElement('radio_group',
                       options=normalized_options,
                       value=value,
                       name=name or f"radio_{uuid.uuid4().hex[:8]}",
                       **kwargs)
    _add_to_current_container(element)
    return value

def form(**kwargs) -> LayoutContainer:
    """Create a form container"""
    print(f"📋 form() called")
    element = UIElement('form', **kwargs)
    return LayoutContainer(element)

def form_field(label: str, required: bool = False, 
               help_text: str = "", **kwargs) -> LayoutContainer:
    """Create a form field with label and help text"""
    print(f"📝 form_field() called: '{label}'")
    element = UIElement('form_field',
                       label=label,
                       required=required,
                       help_text=help_text,
                       **kwargs)
    return LayoutContainer(element)