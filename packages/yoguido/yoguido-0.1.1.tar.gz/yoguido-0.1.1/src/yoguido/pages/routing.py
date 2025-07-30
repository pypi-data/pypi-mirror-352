"""
Fixed page system and routing for YoGuido framework
Replace your yoguido/pages/routing.py with this fixed version
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

@dataclass
class Page:
    """Page definition"""
    path: str
    title: str
    component: Callable
    layout: Optional[str] = None
    auth_required: bool = False
    permissions: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

class Router:
    """Fixed client-side router for YoGuido apps"""
    
    def __init__(self):
        self.pages: Dict[str, Page] = {}
        self.current_page: Optional[str] = None
        self.layouts: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self._auto_render = True
        print("🛣️ Router initialized")
    
    def register_page(self, path: str, title: str, component: Callable, 
                     layout: Optional[str] = None, **kwargs) -> Page:
        """Register a page route"""
        page = Page(
            path=path,
            title=title,
            component=component,
            layout=layout,
            permissions=kwargs.get('permissions', []),
            auth_required=kwargs.get('auth_required', False),
            meta=kwargs.get('meta', {})
        )
        
        self.pages[path] = page
        print(f"🛣️ Registered page: {path} -> {component.__name__}")
        
        # FIXED: Auto-set first page as current if none set
        if self.current_page is None:
            self.current_page = path
            print(f"🎯 Set {path} as initial current page")
        
        return page
    
    def register_layout(self, name: str, layout_component: Callable):
        """Register a layout component"""
        self.layouts[name] = layout_component
        print(f"🏗️ Registered layout: {name}")
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware function"""
        self.middleware.append(middleware_func)
        print(f"🔌 Added middleware: {middleware_func.__name__}")
    
    def navigate_to(self, path: str):
        """Navigate to a specific page"""
        print(f"🧭 navigate_to called with path: {path}")
        print(f"🔍 Available pages: {list(self.pages.keys())}")
        
        if path in self.pages:
            old_page = self.current_page
            self.current_page = path
            print(f"✅ Successfully navigated from {old_page} to: {path}")
            
            # FIXED: Trigger re-render after navigation
            if self._auto_render:
                print("🔄 Auto-triggering re-render after navigation")
                self._trigger_rerender()
        else:
            print(f"❌ Page not found: {path}")
            print(f"🔍 Available pages: {list(self.pages.keys())}")
    
    def get_current_page(self) -> Optional[Page]:
        """Get the current page"""
        print(f"🔍 get_current_page called, current_page: {self.current_page}")
        if self.current_page and self.current_page in self.pages:
            page = self.pages[self.current_page]
            print(f"✅ Found page: {page.path} -> {page.component.__name__}")
            return page
        print(f"❌ No current page found")
        return None
    
    def render_current_page(self):
        """Render the current page with its layout"""
        print(f"🎨 render_current_page called")
        print(f"📍 Current page: {self.current_page}")
        print(f"🔍 Available pages: {list(self.pages.keys())}")
        
        current = self.get_current_page()
        if not current:
            print("❌ No current page found, rendering 404")
            self._render_404()
            return
        
        print(f"✅ Rendering page: {current.path} with layout: {current.layout}")
        
        # Apply middleware
        for middleware in self.middleware:
            try:
                if not middleware(current):
                    print(f"🛑 Middleware blocked rendering")
                    return  # Middleware blocked rendering
            except Exception as e:
                print(f"❌ Middleware error: {e}")
        
        # Render with layout if specified
        if current.layout and current.layout in self.layouts:
            layout_component = self.layouts[current.layout]
            print(f"🏗️ Using layout: {current.layout}")
            try:
                layout_component(current.component)  # Pass the page component as argument
                print(f"✅ Layout rendered successfully")
            except Exception as e:
                print(f"❌ Layout error: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to rendering page directly
                print("📄 Falling back to direct page render")
                try:
                    current.component()
                except Exception as e2:
                    print(f"❌ Page component fallback also failed: {e2}")
        else:
            # Render page component directly
            print(f"📄 Rendering page directly (no layout): {current.layout}")
            try:
                current.component()
                print(f"✅ Page rendered successfully")
            except Exception as e:
                print(f"❌ Page component error: {e}")
                import traceback
                traceback.print_exc()
    
    def _render_404(self):
        """Render a 404 page"""
        from ..ui.basic_components import title, text
        title("404 - Page Not Found", level=1)
        text("The requested page could not be found.")
        text(f"Current page: {self.current_page}")
        text(f"Available pages: {list(self.pages.keys())}")
    
    def _trigger_rerender(self):
        """Trigger a component re-render (for navigation)"""
        try:
            # Clear component tree and re-execute
            from ..ui.basic_components import _clear_component_tree
            _clear_component_tree()
            
            # Re-render current page
            self.render_current_page()
            
        except Exception as e:
            print(f"❌ Rerender failed: {e}")
            import traceback
            traceback.print_exc()

# Global router instance
router = Router()

# ==================== PAGE DECORATORS ====================

def page(path: str, title: str = "", layout: str = None, **kwargs):
    """Decorator to register a page component"""
    def decorator(func: Callable):
        page_title = title or func.__name__.replace('_', ' ').title()
        router.register_page(path, page_title, func, layout, **kwargs)
        
        # IMPORTANT: Don't double-register as component
        # The page will be called by the router, not by the component system
        return func  # Return original function, not wrapped
    return decorator

def layout(name: str):
    """Decorator to register a layout component"""
    def decorator(func: Callable):
        router.register_layout(name, func)
        return func  # Don't wrap in @component
    return decorator

# ==================== CORE ROUTER COMPONENT ====================

def router_component():
    """
    Main router component that should be called by your app
    This is what actually renders the current page
    """
    print("🎯 router_component() called - rendering current page")
    router.render_current_page()

# ==================== UTILITY FUNCTIONS ====================

def navigate_to(path: str):
    """Navigate to a page (can be used in event handlers)"""
    router.navigate_to(path)

def get_current_path() -> Optional[str]:
    """Get current page path"""
    return router.current_page

def get_current_page_title() -> str:
    """Get current page title"""
    current = router.get_current_page()
    return current.title if current else "YoGuido App"

def is_current_page(path: str) -> bool:
    """Check if given path is the current page"""
    return router.current_page == path

# ==================== MIDDLEWARE EXAMPLES ====================

def auth_middleware(page: Page) -> bool:
    """Example authentication middleware"""
    if page.auth_required:
        # Check if user is authenticated
        user_authenticated = check_user_authentication()
        if not user_authenticated:
            navigate_to("/login")
            return False
    return True

def permission_middleware(page: Page) -> bool:
    """Example permission checking middleware"""
    if page.permissions:
        user_permissions = get_user_permissions()
        for required_permission in page.permissions:
            if required_permission not in user_permissions:
                from ..ui.basic_components import title, text
                title("Access Denied", level=1)
                text("You don't have permission to access this page.")
                return False
    return True

def check_user_authentication() -> bool:
    """Placeholder for authentication check"""
    return True

def get_user_permissions() -> List[str]:
    """Placeholder for getting user permissions"""
    return ["read", "write", "admin"]

# ==================== DEBUG FUNCTIONS ====================

def debug_router_state():
    """Debug the router state"""
    print("\n" + "="*50)
    print("🔍 ROUTER DEBUG INFORMATION")
    print("="*50)
    
    print(f"📍 Current page: {router.current_page}")
    print(f"🔍 Available pages: {list(router.pages.keys())}")
    print(f"🏗️ Available layouts: {list(router.layouts.keys())}")
    
    if router.current_page:
        current = router.get_current_page()
        if current:
            print(f"✅ Current page details:")
            print(f"   Path: {current.path}")
            print(f"   Title: {current.title}")
            print(f"   Component: {current.component.__name__}")
            print(f"   Layout: {current.layout}")
        else:
            print(f"❌ Current page not found in registry")
    else:
        print(f"❌ No current page set")
    
    print("="*50 + "\n")