"""
Reactive state management for YoGuido
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class StateChangeEvent:
    """Represents a state change event"""
    change_id: str
    state_id: str
    field_name: str
    old_value: Any
    new_value: Any
    timestamp: str
    component_id: Optional[str] = None

class StateManager:
    """Global state management with change tracking"""
    
    def __init__(self):
        self.state_instances: Dict[str, List[Any]] = {}
        self.change_log: List[StateChangeEvent] = []
        self.subscribers: List[callable] = []
    
    @classmethod
    def notify_change(cls, state_id: str, field_name: str, old_value: Any, new_value: Any):
        """Notify all subscribers of state changes"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        
        # Create change event
        event = StateChangeEvent(
            change_id=str(uuid.uuid4()),
            state_id=state_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Log the change
        cls._instance.change_log.append(event)
        
        # Notify subscribers (the server will send to frontend)
        for callback in cls._instance.subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"State change notification failed: {e}")
        
        print(f"🔄 State change: {state_id}.{field_name} = {new_value}")
    
    def register_state_instance(self, state_id: str, instance: Any):
        """Register a state instance (avoid duplicates)"""
        if state_id not in self.state_instances:
            self.state_instances[state_id] = []
        
        # FIXED: Don't add duplicate instances
        existing_instances = self.state_instances[state_id]
        if instance not in existing_instances:
            existing_instances.append(instance)
            print(f"📝 Registered new state instance for {state_id}")
        else:
            print(f"♻️ State instance already registered for {state_id}")
    
    def subscribe_to_changes(self, callback: callable):
        """Subscribe to state changes"""
        self.subscribers.append(callback)
    
    def get_change_history(self) -> List[Dict[str, Any]]:
        """Get all state changes as JSON"""
        return [asdict(event) for event in self.change_log]
    
    def get_current_state_snapshot(self) -> Dict[str, Any]:
        """Get current state of all instances"""
        snapshot = {}
        for state_id, instances in self.state_instances.items():
            if instances:
                # Get the first instance
                instance = instances[0]
                instance_data = {}
                
                # Get all non-private attributes
                for attr_name in dir(instance):
                    if not attr_name.startswith('_'):
                        try:
                            value = getattr(instance, attr_name)
                            if not callable(value):
                                instance_data[attr_name] = value
                        except:
                            pass
                
                snapshot[state_id] = instance_data
        
        return snapshot


# Add this to the top of yoguido/core/state.py
_state_instances_cache = {}

# Global state manager
state_manager = StateManager()

def use_state(state_class: Type, **initial_data) -> Any:
    """
    Hook to use a state class in components
    Returns the same instance across re-renders to maintain state
    """
    if not hasattr(state_class, '_yoguido_state'):
        raise ValueError(f"Class {state_class.__name__} is not a YoGuido state class")
    
    state_id = state_class._state_id
    
    # Return existing instance if it exists
    if state_id in _state_instances_cache:
        existing_instance = _state_instances_cache[state_id]
        print(f"🔄 Reusing existing state instance for {state_id}")
        return existing_instance
    
    # Create new instance only if none exists
    print(f"🆕 Creating new state instance for {state_id}")
    instance = state_class()  # This will call __init__ which should initialize data
    
    # Set initial data (override defaults if provided)
    for key, value in initial_data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    
    # Cache the instance
    _state_instances_cache[state_id] = instance
    
    # Register with state manager
    state_manager.register_state_instance(state_id, instance)
    
    return instance