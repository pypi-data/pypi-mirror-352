"""
Core decorators for YoGuido framework
"""

import inspect
import uuid
from functools import wraps
from typing import Dict, List, Any, Callable, Type
from dataclasses import dataclass

@dataclass
class ComponentMetadata:
    """Metadata for registered components"""
    component_id: str
    function: Callable
    source_code: str
    audit_enabled: bool = False

@dataclass 
class StateMetadata:
    """Metadata for registered state classes"""
    state_id: str
    state_class: Type
    fields: Dict[str, Any]

class ComponentRegistry:
    """Global registry for components and state classes"""
    
    def __init__(self):
        self.components: Dict[str, ComponentMetadata] = {}
        self.state_classes: Dict[str, StateMetadata] = {}
        self.current_render_context = []
    
    def register_component(self, func: Callable, **kwargs) -> str:
        """Register a component function"""
        component_id = f"{func.__module__}.{func.__name__}"
        
        try:
            source_code = inspect.getsource(func)
        except:
            source_code = "# Source unavailable"
        
        metadata = ComponentMetadata(
            component_id=component_id,
            function=func,
            source_code=source_code,
            audit_enabled=kwargs.get('audit', False)
        )
        
        self.components[component_id] = metadata
        print(f"📝 Registered component: {func.__name__}")
        return component_id
    
    def register_state(self, cls: Type) -> str:
        """Register a state class"""
        state_id = f"{cls.__module__}.{cls.__name__}"
        
        # Analyze class fields
        fields = {}
        for name, annotation in getattr(cls, '__annotations__', {}).items():
            if not name.startswith('_'):
                fields[name] = annotation
        
        metadata = StateMetadata(
            state_id=state_id,
            state_class=cls,
            fields=fields
        )
        
        self.state_classes[state_id] = metadata
        print(f"📊 Registered state: {cls.__name__}")
        return state_id
    
    def get_all_components(self) -> Dict[str, ComponentMetadata]:
        return self.components.copy()
    
    def get_all_state_classes(self) -> Dict[str, StateMetadata]:
        return self.state_classes.copy()

# Global registry instance
_registry = ComponentRegistry()

def component(audit: bool = False):
    """
    Decorator to mark a function as a UI component
    
    Args:
        audit: Enable audit logging for this component
    """
    def decorator(func: Callable):
        component_id = _registry.register_component(func, audit=audit)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add to render context
            _registry.current_render_context.append(component_id)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Remove from render context
                if _registry.current_render_context:
                    _registry.current_render_context.pop()
        
        wrapper._yoguido_component = True
        wrapper._component_id = component_id
        return wrapper
    
    return decorator

def state(cls: Type):
    """
    Decorator to mark a class as application state
    Enables reactive updates and state synchronization
    """
    state_id = _registry.register_state(cls)
    
    # Store original __setattr__ to wrap it
    original_setattr = cls.__setattr__ if hasattr(cls, '__setattr__') else object.__setattr__
    
    def reactive_setattr(self, name: str, value: Any):
        """Enhanced __setattr__ with reactive capabilities"""
        old_value = getattr(self, name, None)
        original_setattr(self, name, value)
        
        # Trigger state change notification if value changed
        if old_value != value:
            from .state import StateManager
            StateManager.notify_change(state_id, name, old_value, value)
    
    # Add reactive capabilities
    cls.__setattr__ = reactive_setattr
    cls._yoguido_state = True
    cls._state_id = state_id
    
    return cls

def computed(func: Callable):
    """
    Decorator for computed properties that automatically update
    when their dependencies change
    """
    @wraps(func)
    def wrapper(self):
        # Simple caching - could be enhanced
        cache_key = f"{id(self)}_{func.__name__}"
        
        # For now, just compute every time
        # In production, would implement proper dependency tracking
        return func(self)
    
    wrapper._yoguido_computed = True
    return wrapper