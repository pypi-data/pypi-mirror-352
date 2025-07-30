"""
Fixed main runtime for YoGuido applications
Replace your yoguido/core/runtime.py with this version
"""

import asyncio
import threading
from pathlib import Path
from typing import List, Optional

from .compiler import YoGuidoCompiler
from .state import state_manager
from ..server.app import YoGuidoServer

class YoGuidoApp:
    """
    Fixed main application class for YoGuido apps
    Handles compilation, server management, and component registration
    """
    
    def __init__(self, title: str = "YoGuido App", debug: bool = False):
        self.title = title
        self.debug = debug
        self.build_dir = "./yoguido_build"
        self.compiler = YoGuidoCompiler(self.build_dir)
        self.server = YoGuidoServer(self.build_dir)
        self.components: List[callable] = []
        self._compiled = False
        self._router_enabled = False
    
    def add_component(self, component_func: callable):
        """Add a component function to the app"""
        if not hasattr(component_func, '_yoguido_component'):
            print(f"⚠️ Warning: {component_func.__name__} is not a @component decorated function")
        
        self.components.append(component_func)
        print(f"➕ Added component: {component_func.__name__}")
    
    def enable_router(self):
        """Enable the page routing system"""
        self._router_enabled = True
        print("🛣️ Router enabled - pages will be rendered automatically")
    
    def compile(self, force: bool = False):
        """Compile the application to vanilla web assets"""
        if self._compiled and not force:
            print("✅ App already compiled (use force=True to recompile)")
            return
        
        print(f"🔨 Compiling YoGuido app: {self.title}")
        
        # Compile to vanilla web assets
        self.compiler.compile_project(self.title)
        self._compiled = True
        
        print("✅ Compilation complete!")
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, auto_compile: bool = True):
        """Run the application"""
        if auto_compile:
            self.compile()
        
        # FIXED: Set this as the current app so server can access it
        set_current_app(self)
        
        # Setup state change notifications to trigger re-renders
        def on_state_change(event):
            """Handle state changes by triggering component re-renders"""
            if self.debug:
                print(f"🔄 State changed: {event.state_id}.{event.field_name}")
            
            # Execute all registered components to rebuild component tree
            self._execute_components()
        
        state_manager.subscribe_to_changes(on_state_change)
        
        # Initial component execution
        self._execute_components()
        
        print(f"🚀 Starting YoGuido app: {self.title}")
        print(f"   Server: http://{host}:{port}")
        print(f"   Components: {len(self.components)}")
        print(f"   Router enabled: {self._router_enabled}")
        print(f"   Debug mode: {self.debug}")
        
        # Run the server
        self.server.run(host=host, port=port)
    
    def _execute_components(self):
        """Execute all registered components to build component tree"""
        from ..ui.basic_components import _clear_component_tree
        
        # Clear previous component tree
        _clear_component_tree()
        
        if self._router_enabled:
            # FIXED: If router is enabled, render through router
            print("🛣️ Router enabled - rendering current page")
            try:
                from ..pages.routing import router_component
                router_component()
                print("✅ Router component executed successfully")
            except Exception as e:
                print(f"❌ Router component failed: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
        else:
            # Execute traditional components
            print(f"🎨 Executing {len(self.components)} traditional components")
            for component_func in self.components:
                try:
                    if self.debug:
                        print(f"🎨 Executing component: {component_func.__name__}")
                    component_func()
                except Exception as e:
                    print(f"❌ Component {component_func.__name__} failed: {e}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()
    
    def get_component_tree(self):
        """Get the current component tree (for debugging)"""
        from ..ui.basic_components import _get_component_tree
        return _get_component_tree()
    
    def get_state_snapshot(self):
        """Get current state snapshot (for debugging)"""
        return state_manager.get_current_state_snapshot()
    
    def hot_reload(self):
        """Hot reload the application (recompile and restart)"""
        print("🔥 Hot reloading...")
        self.compile(force=True)
        self._execute_components()
        print("✅ Hot reload complete!")
    
    def debug_info(self):
        """Print debug information about the app state"""
        print("\n" + "="*60)
        print("🔍 HYPERCODE APP DEBUG INFORMATION")
        print("="*60)
        
        print(f"📱 App Title: {self.title}")
        print(f"🔧 Debug Mode: {self.debug}")
        print(f"📁 Build Directory: {self.build_dir}")
        print(f"✅ Compiled: {self._compiled}")
        print(f"🛣️ Router Enabled: {self._router_enabled}")
        print(f"🎨 Components Registered: {len(self.components)}")
        
        if self.components:
            print("   Components:")
            for i, comp in enumerate(self.components, 1):
                print(f"   {i}. {comp.__name__}")
        
        # Show component tree
        tree = self.get_component_tree()
        print(f"🌳 Current Component Tree: {len(tree)} elements")
        if tree:
            for i, element in enumerate(tree, 1):
                print(f"   {i}. {element.get('type', 'unknown')} (id: {element.get('id', 'no-id')})")
        
        # Show router state if enabled
        if self._router_enabled:
            from ..pages.routing import debug_router_state
            debug_router_state()
        
        print("="*60 + "\n")

# Global app instance for convenience
_current_app: Optional[YoGuidoApp] = None

def get_current_app() -> Optional[YoGuidoApp]:
    """Get the currently running app instance"""
    return _current_app

def set_current_app(app: YoGuidoApp):
    """Set the current app instance"""
    global _current_app
    _current_app = app