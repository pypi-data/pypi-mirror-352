"""
YoGuido Debug Tools
Tools to diagnose button click issues in the YoGuido framework
"""

import yoguido as hc
import json

# ==================== DIAGNOSTIC FUNCTIONS ====================

def debug_button_registry():
    """Debug function to show all registered button handlers"""
    try:
        from yoguido.ui.basic_components import get_button_handlers
        handlers = get_button_handlers()
        print(f"🔍 BUTTON REGISTRY DEBUG:")
        print(f"   📊 Total handlers registered: {len(handlers)}")
        for handler_id, handler_func in handlers.items():
            print(f"   🎯 {handler_id}: {handler_func}")
        return handlers
    except Exception as e:
        print(f"❌ Error accessing button registry: {e}")
        return {}

def debug_component_tree():
    """Debug function to show the current component tree"""
    try:
        from yoguido.ui.basic_components import _get_component_tree
        tree = _get_component_tree()
        print(f"🔍 COMPONENT TREE DEBUG:")
        print(f"   📊 Total components: {len(tree)}")
        for i, component in enumerate(tree):
            print(f"   🧩 Component {i}: {component.get('type', 'unknown')} (id: {component.get('id', 'no-id')})")
            if component.get('handlers'):
                print(f"      🎯 Handlers: {component['handlers']}")
        return tree
    except Exception as e:
        print(f"❌ Error accessing component tree: {e}")
        return []

def debug_event_registry():
    """Debug function to show registered event handlers"""
    try:
        from yoguido.server.app import EventRegistry
        handlers = EventRegistry.handlers
        print(f"🔍 EVENT REGISTRY DEBUG:")
        print(f"   📊 Total event handlers: {len(handlers)}")
        for handler_id, handler_func in handlers.items():
            print(f"   🎯 {handler_id}: {handler_func}")
        return handlers
    except Exception as e:
        print(f"❌ Error accessing event registry: {e}")
        return {}

# ==================== DIAGNOSTIC PAGE ====================

@hc.page("/diagnostic", title="YoGuido Diagnostics", layout="debug_layout")
def diagnostic_page():
    """Comprehensive diagnostic page"""
    
    print("🔍 === DIAGNOSTIC PAGE RENDERING ===")
    
    # Registry debugging
    button_handlers = debug_button_registry()
    component_tree = debug_component_tree()
    event_handlers = debug_event_registry()
    
    with hc.container(class_name="space-y-8"):
        
        # Diagnostic header
        with hc.container(class_name="bg-white rounded-lg shadow p-6"):
            hc.title("YoGuido Framework Diagnostics", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
            hc.text("This page helps diagnose button click and event handling issues", class_name="text-gray-600")
        
        # Button Test Section
        with hc.container(class_name="bg-white rounded-lg shadow p-6"):
            hc.title("Live Button Tests", level=2, class_name="text-xl font-semibold mb-4")
            
            # Create test buttons with different approaches
            
            # Test 1: Minimal button
            def minimal_test():
                print("🟢 MINIMAL TEST: Button clicked!")
                return True
            
            minimal_clicked = hc.button("Minimal Test", on_click=minimal_test)
            if minimal_clicked:
                print("✅ Minimal button click detected!")
                hc.alert("Minimal button works!", type="success")
            
            # Test 2: Button with classes
            def styled_test():
                print("🟡 STYLED TEST: Button clicked!")
                return True
            
            styled_clicked = hc.button("Styled Test", on_click=styled_test, 
                                     class_name="bg-blue-500 text-white px-4 py-2 rounded ml-4")
            if styled_clicked:
                print("✅ Styled button click detected!")
                hc.alert("Styled button works!", type="info")
            
            # Test 3: Button with unique ID
            def unique_test():
                print("🟣 UNIQUE TEST: Button clicked!")
                return True
            
            unique_clicked = hc.button("Unique ID Test", on_click=unique_test,
                                     id="unique-test-button",
                                     class_name="bg-purple-500 text-white px-4 py-2 rounded ml-4")
            if unique_clicked:
                print("✅ Unique ID button click detected!")
                hc.alert("Unique ID button works!", type="warning")
        
        # Registry Information
        with hc.container(class_name="bg-white rounded-lg shadow p-6"):
            hc.title("Registry Information", level=2, class_name="text-xl font-semibold mb-4")
            
            with hc.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-6"):
                
                # Button handlers count
                with hc.container(class_name="bg-blue-50 rounded-lg p-4"):
                    hc.text("Button Handlers", class_name="text-sm font-medium text-blue-600")
                    hc.text(str(len(button_handlers)), class_name="text-2xl font-bold text-blue-900")
                
                # Component tree count
                with hc.container(class_name="bg-green-50 rounded-lg p-4"):
                    hc.text("Components", class_name="text-sm font-medium text-green-600")
                    hc.text(str(len(component_tree)), class_name="text-2xl font-bold text-green-900")
                
                # Event handlers count
                with hc.container(class_name="bg-purple-50 rounded-lg p-4"):
                    hc.text("Event Handlers", class_name="text-sm font-medium text-purple-600")
                    hc.text(str(len(event_handlers)), class_name="text-2xl font-bold text-purple-900")
        
        # Detailed Registry Info
        with hc.container(class_name="bg-white rounded-lg shadow p-6"):
            hc.title("Detailed Registry Information", level=2, class_name="text-xl font-semibold mb-4")
            
            # Button handlers details
            if button_handlers:
                hc.title("Button Handlers:", level=3, class_name="text-lg font-medium mb-2")
                for handler_id, handler_func in button_handlers.items():
                    hc.text(f"• {handler_id}: {handler_func}", class_name="text-sm text-gray-600 ml-4")
            else:
                hc.text("❌ No button handlers found in registry", class_name="text-red-600")
            
            # Event handlers details  
            if event_handlers:
                hc.title("Event Handlers:", level=3, class_name="text-lg font-medium mb-2 mt-4")
                for handler_id, handler_func in event_handlers.items():
                    hc.text(f"• {handler_id}: {handler_func}", class_name="text-sm text-gray-600 ml-4")
            else:
                hc.text("❌ No event handlers found in registry", class_name="text-red-600")
        
        # JavaScript Debug Section
        with hc.container(class_name="bg-white rounded-lg shadow p-6"):
            hc.title("JavaScript Debug Instructions", level=2, class_name="text-xl font-semibold mb-4")
            
            with hc.container(class_name="space-y-4"):
                hc.text("🔍 Open browser console (F12) and check for:", class_name="font-medium")
                hc.text("• JavaScript errors on page load", class_name="text-sm text-gray-600 ml-4")
                hc.text("• Network requests to /hcc when clicking buttons", class_name="text-sm text-gray-600 ml-4")
                hc.text("• YoGuidoApp initialization messages", class_name="text-sm text-gray-600 ml-4")
                hc.text("• Button click event registrations", class_name="text-sm text-gray-600 ml-4")
                
                hc.text("🎯 Expected console output when buttons work:", class_name="font-medium mt-4")
                hc.text("• 'YoGuidoApp constructor called'", class_name="text-sm text-gray-600 ml-4")
                hc.text("• 'YoGuidoApp.init() called'", class_name="text-sm text-gray-600 ml-4")
                hc.text("• Network POST to /hcc on button clicks", class_name="text-sm text-gray-600 ml-4")
        
        # Manual Test Section
        with hc.container(class_name="bg-yellow-50 rounded-lg border border-yellow-200 p-6"):
            hc.title("Manual Testing Steps", level=2, class_name="text-xl font-semibold mb-4")
            
            with hc.container(class_name="space-y-2"):
                hc.text("1. Click each test button above", class_name="text-sm")
                hc.text("2. Watch terminal for 'TEST:' messages", class_name="text-sm")
                hc.text("3. Check browser console for errors", class_name="text-sm")
                hc.text("4. Look at Network tab for /hcc requests", class_name="text-sm")
                hc.text("5. If no requests appear, the JavaScript runtime isn't working", class_name="text-sm text-red-600")

# ==================== LAYOUT FOR DIAGNOSTIC ====================

@hc.layout("debug_layout")
def debug_layout(page_component):
    """Simple layout for debugging"""
    
    with hc.container(class_name="min-h-screen bg-gray-50 p-8"):
        
        # Simple header with navigation
        with hc.container(class_name="bg-white rounded-lg shadow p-6 mb-8"):
            hc.title("YoGuido Debug Suite", level=1, class_name="text-2xl font-bold text-gray-900")
            
            # Navigation buttons
            with hc.container(class_name="flex space-x-4 mt-4"):
                
                def nav_debug():
                    print("🧭 Navigating to debug page")
                    hc.navigate_to("/debug")
                    return True
                
                def nav_diagnostic():
                    print("🧭 Navigating to diagnostic page")
                    hc.navigate_to("/diagnostic")
                    return True
                
                hc.button("Basic Tests", on_click=nav_debug, 
                         class_name="bg-blue-500 text-white px-4 py-2 rounded")
                hc.button("Diagnostics", on_click=nav_diagnostic,
                         class_name="bg-green-500 text-white px-4 py-2 rounded")
        
        # Page content
        page_component()

# ==================== MAIN DEBUG APPLICATION ====================

def main_debug():
    """Main debug application"""
    
    print("🐛" * 20)
    print("🔍 HYPERCODE BUTTON CLICK DEBUGGING SESSION")
    print("🐛" * 20)
    print()
    print("📋 This debug session will help identify why buttons aren't clicking")
    print()
    print("🎯 Pages available:")
    print("   /debug - Basic button tests")
    print("   /diagnostic - Comprehensive diagnostics")
    print()
    print("🔍 What to look for:")
    print("   • Terminal messages starting with 'TEST:' or '✅'")
    print("   • Browser console errors (F12)")
    print("   • Network requests to /hcc endpoint")
    print("   • Registry information on diagnostic page")
    print()
    
    # Create debug app
    app = hc.YoGuidoApp("YoGuido Debug Suite", debug=True)
    app.enable_router()
    
    # Set initial page
    hc.navigate_to("/diagnostic")
    
    # Show debug info
    app.debug_info()
    
    # Compile and run
    print("🔨 Compiling debug version...")
    app.compile(force=True)
    
    print("\n🌐 Debug server starting...")
    print("✨ Open: http://127.0.0.1:8000/diagnostic")
    print()
    
    app.run(host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main_debug()