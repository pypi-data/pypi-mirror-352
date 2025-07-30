"""
Fixed YoGuido Admin Portal for Debugging Button Clicks
Ensures all buttons render properly and work correctly
"""

import yoguido as hc

# ==================== TEST DATA ====================

users_data = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@company.com", "role": "Admin", "status": "Active"},
    {"id": 2, "name": "Bob Smith", "email": "bob@company.com", "role": "Editor", "status": "Active"},
    {"id": 3, "name": "Carol Wilson", "email": "carol@company.com", "role": "Viewer", "status": "Inactive"},
]

# ==================== STATE CLASS (DEFINE FIRST) ====================

@hc.state
class CounterState:
    """Simple counter state for testing"""
    def __init__(self):
        self.count = 0

# ==================== SIMPLE LAYOUT ====================

@hc.layout("debug_layout")
def debug_layout(page_component):
    """Simple layout for debugging"""
    
    # Simple container
    with hc.container(class_name="min-h-screen bg-gray-50 p-8"):
        
        # Simple header
        with hc.container(class_name="bg-white rounded-lg shadow p-6 mb-8"):
            hc.title("YoGuido Button Debug", level=1, class_name="text-2xl font-bold text-gray-900")
            hc.text("Testing button click functionality", class_name="text-gray-600")
        
        # Page content
        page_component()

# ==================== TEST PAGES ====================

@hc.page("/debug", title="Debug Dashboard", layout="debug_layout")
def debug_dashboard():
    """Simple dashboard for testing buttons"""
    
    print("🔍 Debug dashboard rendering...")
    
    # FIXED: Get state instance once at the top
    counter_state = hc.use_state(CounterState, count=0)
    print(f"📊 Counter state initialized: {counter_state.count}")
    
    # Test Section 1: Basic Buttons
    with hc.container(class_name="bg-white rounded-lg shadow p-6 mb-8"):
        hc.title("Basic Button Tests", level=2, class_name="text-xl font-semibold mb-4")
        
        # FIXED: Create buttons separately and check results individually
        
        # Test button 1 - Simple navigation
        def test_navigate():
            print("🎯 TEST: Navigation button clicked!")
            hc.navigate_to("/debug/users")
            return True
        
        print("🔨 Creating navigation button...")
        navigation_button = hc.button("Navigate to Users", on_click=test_navigate, 
                                    class_name="bg-blue-500 text-white px-4 py-2 rounded mr-4")
        print(f"✅ Navigation button created: {navigation_button}")
        
        if navigation_button:
            print("✅ Navigation button was clicked!")
            hc.alert("Navigation successful!", type="success")
        
        # Test button 2 - Simple alert
        def test_alert():
            print("🎯 TEST: Alert button clicked!")
            hc.alert("Hello from button click!", type="info")
            return True
        
        print("🔨 Creating alert button...")
        alert_button = hc.button("Show Alert", on_click=test_alert,
                                class_name="bg-green-500 text-white px-4 py-2 rounded mr-4")
        print(f"✅ Alert button created: {alert_button}")
        
        if alert_button:
            print("✅ Alert button was clicked!")
        
        # Test button 3 - Counter button with state
        def increment_counter():
            print(f"🎯 TEST: Counter button clicked! Current: {counter_state.count}")
            counter_state.count += 1
            print(f"✅ Counter incremented to: {counter_state.count}")
            return True
        
        print("🔨 Creating counter button...")
        counter_button = hc.button(f"Count: {counter_state.count}", on_click=increment_counter,
                                 class_name="bg-purple-500 text-white px-4 py-2 rounded")
        print(f"✅ Counter button created: {counter_button}")
        
        if counter_button:
            print("✅ Counter button was clicked!")
    
    # Test Section 2: Container with buttons
    with hc.container(class_name="bg-white rounded-lg shadow p-6 mb-8"):
        hc.title("Container Button Tests", level=2, class_name="text-xl font-semibold mb-4")
        
        # FIXED: Create container and buttons with proper spacing
        with hc.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-4"):
            
            # Test 1 button
            def test_1():
                print("🔥 Container Test 1 clicked!")
                hc.alert("Container Test 1 works!", type="success")
                return True
            
            print("🔨 Creating container test 1 button...")
            test1_button = hc.button("Test 1", on_click=test_1, 
                                   class_name="bg-red-500 text-white px-4 py-2 rounded")
            print(f"✅ Test 1 button created: {test1_button}")
            
            if test1_button:
                print("✅ Container Test 1 clicked!")
            
            # Test 2 button
            def test_2():
                print("🔥 Container Test 2 clicked!")
                hc.alert("Container Test 2 works!", type="warning")
                return True
            
            print("🔨 Creating container test 2 button...")
            test2_button = hc.button("Test 2", on_click=test_2, 
                                   class_name="bg-yellow-500 text-white px-4 py-2 rounded")
            print(f"✅ Test 2 button created: {test2_button}")
            
            if test2_button:
                print("✅ Container Test 2 clicked!")
            
            # Test 3 button
            def test_3():
                print("🔥 Container Test 3 clicked!")
                hc.alert("Container Test 3 works!", type="error")
                return True
            
            print("🔨 Creating container test 3 button...")
            test3_button = hc.button("Test 3", on_click=test_3, 
                                   class_name="bg-pink-500 text-white px-4 py-2 rounded")
            print(f"✅ Test 3 button created: {test3_button}")
            
            if test3_button:
                print("✅ Container Test 3 clicked!")
    
    # Test Section 3: Simple buttons without containers
    with hc.container(class_name="bg-white rounded-lg shadow p-6 mb-8"):
        hc.title("Simple Button Tests", level=2, class_name="text-xl font-semibold mb-4")
        
        # Simple button 1
        def simple_1():
            print("🟢 Simple button 1 clicked!")
            return True
        
        print("🔨 Creating simple button 1...")
        simple1 = hc.button("Simple 1", on_click=simple_1)
        print(f"✅ Simple button 1 created: {simple1}")
        
        # Simple button 2  
        def simple_2():
            print("🟡 Simple button 2 clicked!")
            return True
        
        print("🔨 Creating simple button 2...")
        simple2 = hc.button("Simple 2", on_click=simple_2)
        print(f"✅ Simple button 2 created: {simple2}")
        
        # Simple button 3
        def simple_3():
            print("🔵 Simple button 3 clicked!")
            return True
        
        print("🔨 Creating simple button 3...")
        simple3 = hc.button("Simple 3", on_click=simple_3)
        print(f"✅ Simple button 3 created: {simple3}")
    
    # Debug info
    with hc.container(class_name="bg-gray-100 rounded-lg p-6"):
        hc.title("Debug Info", level=2, class_name="text-xl font-semibold mb-4")
        hc.text(f"Current counter value: {counter_state.count}", class_name="text-sm text-gray-600")
        hc.text("Check your terminal for button click logs", class_name="text-sm text-gray-600")
        hc.text("Watch for browser console errors (F12)", class_name="text-sm text-red-600")
        
        # Component tree debug
        def show_debug_info():
            print("🔍 DEBUG INFO REQUESTED")
            try:
                from yoguido.ui.basic_components import _get_component_tree
                tree = _get_component_tree()
                print(f"📊 Component tree has {len(tree)} components")
                for i, comp in enumerate(tree):
                    print(f"   {i}: {comp.get('type', 'unknown')} (id: {comp.get('id', 'no-id')})")
                    if comp.get('handlers'):
                        print(f"      Handlers: {comp['handlers']}")
            except Exception as e:
                print(f"❌ Debug info error: {e}")
            return True
        
        debug_button = hc.button("Show Debug Info", on_click=show_debug_info,
                                class_name="bg-gray-500 text-white px-4 py-2 rounded")
        
        if debug_button:
            print("✅ Debug button was clicked!")

@hc.page("/debug/users", title="Debug Users", layout="debug_layout")
def debug_users():
    """Simple users page for testing navigation"""
    
    print("🔍 Debug users page rendering...")
    
    with hc.container(class_name="bg-white rounded-lg shadow p-6"):
        hc.title("Users Page", level=2, class_name="text-xl font-semibold mb-4")
        hc.text("✅ Navigation worked! You're on the users page.", class_name="text-green-600 mb-4")
        
        # Back button
        def go_back():
            print("🎯 Back button clicked!")
            hc.navigate_to("/debug")
            return True
        
        print("🔨 Creating back button...")
        back_button = hc.button("← Back to Dashboard", on_click=go_back,
                               class_name="bg-gray-500 text-white px-4 py-2 rounded mb-4")
        print(f"✅ Back button created: {back_button}")
        
        if back_button:
            print("✅ Back button was clicked!")
        
        # Simple table
        print("🔨 Creating table...")
        hc.table(users_data, columns=["name", "email", "role", "status"])
        print("✅ Table created")

# ==================== DIAGNOSTIC PAGE ====================

@hc.page("/debug/diagnostic", title="Diagnostic", layout="debug_layout") 
def diagnostic_page():
    """Diagnostic page to check component registration"""
    
    print("🔍 Diagnostic page rendering...")
    
    with hc.container(class_name="bg-white rounded-lg shadow p-6"):
        hc.title("Component Diagnostic", level=2, class_name="text-xl font-semibold mb-4")
        
        # Check component tree
        try:
            from yoguido.ui.basic_components import _get_component_tree
            tree = _get_component_tree()
            hc.text(f"Total components in tree: {len(tree)}", class_name="text-lg mb-4")
            
            for i, comp in enumerate(tree):
                comp_info = f"Component {i}: {comp.get('type', 'unknown')} (id: {comp.get('id', 'no-id')})"
                if comp.get('handlers'):
                    comp_info += f" - Handlers: {list(comp['handlers'].keys())}"
                hc.text(comp_info, class_name="text-sm text-gray-600")
                
        except Exception as e:
            hc.text(f"Error accessing component tree: {e}", class_name="text-red-600")
        
        # Navigation back
        def nav_back():
            print("🎯 Diagnostic nav back clicked!")
            hc.navigate_to("/debug")
            return True
        
        hc.button("← Back to Debug", on_click=nav_back,
                 class_name="bg-blue-500 text-white px-4 py-2 rounded mt-4")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application for debugging button clicks"""
    
    print("🐛 Starting YoGuido Button Debug Session...")
    print("=" * 60)
    print("🎯 Focus: Testing basic button click functionality")
    print("📋 Test Plan:")
    print("   1. Simple navigation buttons")
    print("   2. Alert buttons") 
    print("   3. State-changing buttons")
    print("   4. Container-based buttons")
    print("   5. Component tree diagnostic")
    print("=" * 60)
    
    # Create app
    app = hc.YoGuidoApp("Button Debug Session", debug=True)
    app.enable_router()
    
    # Set initial page
    hc.navigate_to("/debug")
    
    # Show debug info
    app.debug_info()
    
    # Compile and run
    print("\n🔨 Compiling debug version...")
    app.compile(force=True)
    
    print("\n🌐 Debug server starting...")
    print("✨ URLs available:")
    print("   http://127.0.0.1:8000/debug - Main test page")
    print("   http://127.0.0.1:8000/debug/users - Navigation test")
    print("   http://127.0.0.1:8000/debug/diagnostic - Component diagnostic")
    print()
    print("🔍 Debug Instructions:")
    print("   1. Click each button on the page")
    print("   2. Watch terminal for 'TEST:' and '✅' messages") 
    print("   3. Check browser console (F12) for errors")
    print("   4. Look for network requests to /hcc endpoint")
    print("   5. Use diagnostic page to check component registration")
    print("=" * 60)
    
    app.run(host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()