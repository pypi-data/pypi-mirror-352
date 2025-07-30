# YoGuido 🚀

## The Python UI Framework with Pure Vanilla JS

YoGuido is a lightweight, powerful Python web framework designed to create modern web applications without the bloat. Build reactive web UIs with Python's simplicity and the performance of vanilla JavaScript - no dependencies, no complications.

![PyPI version](https://img.shields.io/pypi/v/yoguido.svg)
![Python versions](https://img.shields.io/pypi/pyversions/yoguido.svg)
![License](https://img.shields.io/pypi/l/yoguido.svg)

## ✨ Features

- **Zero JavaScript Dependencies** - Pure vanilla JS for maximum performance
- **Pure Python UI Logic** - Build your entire UI in Python
- **Instant Hot Reloading** - See changes immediately
- **Component-Based Architecture** - Reusable, composable UI elements
- **Reactive Data Binding** - Automatic UI updates when data changes
- **Built on FastAPI** - Leverage the speed and simplicity of FastAPI
- **Lightweight & Fast** - Minimal overhead for maximum performance
- **Software Sovereign** - Own your stack with zero external dependencies

## 📦 Installation

```bash
pip install yoguido
```

## 🧩 Core Concepts

### Layout

Determine a layout that can be used in a page

```python
import yoguido as yog
@yog.layout("name_of_layout")
def dashboard(components):
    # Build up layout and components owned by the layout.
    # ...

    # Render your components
    components()
```

### Pages

Create interactive pages that can be navigated to with "yog.navigate_to(...url...)".

```python
import yoguido as yog
@yog.page("/url", title="Your page title", layout="name_of_layout")
def dashboard():
    # Render components
    with yog.container(class_name="text-center py-16"):
        yog.text("💬", class_name="text-6xl mb-4")
        yog.title("Support", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        yog.text("Support system coming soon!", class_name="text-lg text-gray-600")
```

### State Management

Manage application state simply with Python:

```python
import yoguido as yog

# Define a Class to hold state with a property to keep state accross backend and frontend.
@yog.state
class CounterState:
    """Simple counter state for testing"""
    def __init__(self):
        self.count = 0

# Define a page, the instance of the class with the initial count value.
@yog.page("/admin", title="Your page title", layout="name_of_layout")
def dashboard():

    # Define a counter_state
    counter_state = yog.use_state(CounterState, count=0)

    # Define the action attached to the button.
    def increment_counter():
        print(f"🎯 TEST: Counter button clicked! Current: {counter_state.count}")
        counter_state.count += 1
        return True
    
    # Create a button on the page that will increase count.
    counter_button = yog.button(f"Count: {counter_state.count}", on_click=increment_counter,
                                class_name="bg-purple-500 text-white px-4 py-2 rounded")
    
```


## 🚀 Quick Start

Create a full blown application in minutes.
Here is an example of an admin portal you can use.
A single document you can easily split up.

```python
"""
Professional Admin Portal with Sidebar Navigation
Enhanced layout with sidebar + top navigation
"""

import yoguido as yog
from datetime import datetime

# ==================== SAMPLE DATA ====================

users_data = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@company.com", "role": "Admin", "status": "Active", "last_login": "2024-01-15"},
    {"id": 2, "name": "Bob Smith", "email": "bob@company.com", "role": "Editor", "status": "Active", "last_login": "2024-01-14"},
    {"id": 3, "name": "Carol Wilson", "email": "carol@company.com", "role": "Viewer", "status": "Inactive", "last_login": "2024-01-10"},
    {"id": 4, "name": "David Brown", "email": "david@company.com", "role": "Editor", "status": "Active", "last_login": "2024-01-15"},
    {"id": 5, "name": "Emma Davis", "email": "emma@company.com", "role": "Admin", "status": "Active", "last_login": "2024-01-15"},
]

analytics_data = [
    {"month": "Jan", "users": 1200, "revenue": 45000},
    {"month": "Feb", "users": 1350, "revenue": 52000},
    {"month": "Mar", "users": 1100, "revenue": 48000},
    {"month": "Apr", "users": 1450, "revenue": 58000},
    {"month": "May", "users": 1600, "revenue": 62000},
]

dashboard_stats = {
    'total_users': len(users_data),
    'active_users': len([u for u in users_data if u["status"] == "Active"]),
    'admin_users': len([u for u in users_data if u["role"] == "Admin"]),
    'total_revenue': sum(d["revenue"] for d in analytics_data),
    'avg_revenue': sum(d["revenue"] for d in analytics_data) / len(analytics_data)
}

recent_activity = [
    {"action": "👤 New user registered", "description": "Emma Davis joined 2 minutes ago", "time": "2m"},
    {"action": "💰 Payment received", "description": "$299.99 from Enterprise client", "time": "5m"},
    {"action": "📦 Product updated", "description": "Premium Plan pricing changed", "time": "12m"},
    {"action": "🎫 Support ticket", "description": "Priority ticket #1234 resolved", "time": "15m"},
    {"action": "📊 Report generated", "description": "Monthly analytics report ready", "time": "1h"}
]

# ==================== SIDEBAR LAYOUT SYSTEM ====================

@yog.layout("admin_sidebar")
def admin_sidebar_layout(page_component):
    """Modern admin layout with sidebar navigation"""
    
    # Main container with sidebar layout
    with yog.container(class_name="min-h-screen bg-gray-50 flex"):
        
        # Sidebar
        render_sidebar()
        
        # Main content area
        with yog.container(class_name="flex-1 flex flex-col min-w-0"):
            
            # Top navigation bar
            render_top_nav()
            
            # Page content
            with yog.container(class_name="flex-1 p-6 overflow-auto"):
                
                # Breadcrumb
                render_breadcrumb()
                
                # Page content with spacing
                with yog.container(class_name="mt-6"):
                    page_component()

def render_sidebar():
    """Render the sidebar navigation"""
    with yog.container(class_name="w-64 bg-white shadow-lg flex flex-col"):
        
        # Logo/Brand section
        with yog.container(class_name="p-6 border-b border-gray-200"):
            with yog.container(class_name="flex items-center space-x-3"):
                yog.text("🧠", class_name="text-2xl")
                yog.title("AdminPro", level=2, class_name="text-xl font-bold text-purple-600 m-0")
        
        # Navigation menu
        with yog.container(class_name="flex-1 py-6"):
            with yog.container(class_name="px-3 space-y-1"):
                
                # Main navigation items
                sidebar_nav_item("📊", "Dashboard", "/admin")
                sidebar_nav_item("👥", "Users", "/admin/users")
                sidebar_nav_item("📦", "Products", "/admin/products")
                sidebar_nav_item("📈", "Analytics", "/admin/analytics")
                sidebar_nav_item("⚙️", "Settings", "/admin/settings")
                
                # Divider
                with yog.container(class_name="py-4"):
                    yog.separator(class_name="border-gray-200")
                
                # Secondary navigation
                yog.text("TOOLS", class_name="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2")
                sidebar_nav_item("📋", "Reports", "/admin/reports")
                sidebar_nav_item("🔔", "Notifications", "/admin/notifications")
                sidebar_nav_item("💬", "Support", "/admin/support")
        
        # Sidebar footer
        with yog.container(class_name="p-4 border-t border-gray-200"):
            with yog.container(class_name="flex items-center space-x-3"):
                # User avatar
                with yog.container(class_name="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center"):
                    yog.text("JD", class_name="text-sm font-medium text-white")
                
                # User info
                with yog.container(class_name="flex-1 min-w-0"):
                    yog.text("John Doe", class_name="text-sm font-medium text-gray-900 truncate")
                    yog.text("Admin", class_name="text-xs text-gray-500")
                
                # Settings button - fixed to navigate to settings page
                def user_settings():
                    print("⚙️ User settings clicked")
                    yog.navigate_to("/admin/settings")
                    return True
                
                if yog.button("⚙️", on_click=user_settings, 
                           class_name="text-gray-400 hover:text-gray-600 p-1"):
                    print("✅ User settings button clicked")

def sidebar_nav_item(icon: str, label: str, path: str):
    """Individual sidebar navigation item"""
    is_active = yog.is_current_page(path)
    
    def navigate():
        print(f"🎯 Navigation clicked: {path}")
        yog.navigate_to(path)
        return True
    
    # Style based on active state
    if is_active:
        item_class = "flex items-center space-x-3 px-3 py-2 text-sm font-medium text-purple-600 bg-purple-50 border-r-2 border-purple-600 rounded-l-md w-full text-left"
    else:
        item_class = "flex items-center space-x-3 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors w-full text-left"
    
    # Create button with icon and text inside
    button_text = f"{icon} {label}"
    clicked = yog.button(button_text, on_click=navigate, class_name=item_class)
    
    if clicked:
        print(f"✅ Button clicked for {label}")
        yog.alert(f"Navigating to {label}", type="info")

def render_top_nav():
    """Render the top navigation bar"""
    with yog.container(class_name="bg-white shadow-sm border-b border-gray-200 px-6 py-4"):
        with yog.container(class_name="flex items-center justify-between"):
            
            # Left side - Page actions or search
            with yog.container(class_name="flex items-center space-x-4"):
                # Mobile menu button (for responsive design)
                def toggle_mobile_menu():
                    print("🔄 Mobile menu toggled")
                    yog.alert("Mobile menu would toggle", type="info")
                    return True
                
                yog.button("☰", on_click=toggle_mobile_menu, 
                         class_name="lg:hidden p-2 text-gray-400 hover:text-gray-600")
                
                # Search bar
                with yog.container(class_name="hidden md:block"):
                    search_value = yog.input_text(placeholder="Search...", 
                                               class_name="w-80 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent")
            
            # Right side - Actions and notifications
            with yog.container(class_name="flex items-center space-x-4"):
                
                # Quick actions
                def add_item():
                    print("➕ Quick add clicked")
                    yog.alert("Quick add menu would open", type="info")
                    return True
                
                if yog.button("➕", on_click=add_item,
                           class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                    print("✅ Quick add button clicked")
                
                # Notifications
                def show_notifications():
                    print("🔔 Notifications clicked")
                    yog.alert("Notifications panel would open", type="info")
                    return True
                
                with yog.container(class_name="relative"):
                    if yog.button("🔔", on_click=show_notifications,
                               class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                        print("✅ Notifications button clicked")
                    
                    # Notification badge
                    with yog.container(class_name="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center"):
                        yog.text("3", class_name="text-xs text-white font-medium")
                
                # Profile dropdown
                def profile_menu():
                    print("👤 Profile menu clicked")
                    yog.alert("Profile menu would open", type="info")
                    return True
                
                if yog.button("👤", on_click=profile_menu,
                           class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                    print("✅ Profile button clicked")

def render_breadcrumb():
    """Render breadcrumb navigation"""
    current_path = yog.get_current_path()
    
    breadcrumb_data = {
        "/admin": [{"label": "Dashboard"}],
        "/admin/users": [{"label": "Dashboard", "url": "/admin"}, {"label": "Users"}],
        "/admin/products": [{"label": "Dashboard", "url": "/admin"}, {"label": "Products"}],
        "/admin/analytics": [{"label": "Dashboard", "url": "/admin"}, {"label": "Analytics"}],
        "/admin/settings": [{"label": "Dashboard", "url": "/admin"}, {"label": "Settings"}],
        "/admin/reports": [{"label": "Dashboard", "url": "/admin"}, {"label": "Reports"}],
        "/admin/notifications": [{"label": "Dashboard", "url": "/admin"}, {"label": "Notifications"}],
        "/admin/support": [{"label": "Dashboard", "url": "/admin"}, {"label": "Support"}]
    }
    
    items = breadcrumb_data.get(current_path, [{"label": "Dashboard"}])
    
    with yog.container(class_name="bg-white rounded-lg border border-gray-200 px-4 py-3"):
        with yog.container(class_name="flex items-center space-x-2 text-sm"):
            # Home icon
            yog.text("🏠", class_name="text-gray-400")
            
            for i, item in enumerate(items):
                # Add separator if not first item
                if i > 0:
                    yog.text("/", class_name="text-gray-400 mx-2")
                
                # Create breadcrumb item
                if "url" in item:
                    # Clickable breadcrumb item
                    def navigate_to_item(url=item["url"]):
                        yog.navigate_to(url)
                        return True
                    
                    if yog.button(item["label"], on_click=navigate_to_item,
                               class_name="text-purple-600 hover:text-purple-800 hover:underline bg-transparent border-0 p-0 font-medium"):
                        yog.alert(f"Navigating to {item['label']}", type="info")
                else:
                    # Current page (non-clickable)
                    yog.text(item["label"], class_name="text-gray-900 font-medium")

# ==================== ENHANCED COMPONENTS ====================

def stats_card(title: str, value: str, change: str = None, trend: str = "neutral", icon: str = "📊"):
    """Professional statistics card"""
    
    trend_colors = {
        "up": "bg-green-50 border-green-200",
        "down": "bg-red-50 border-red-200", 
        "neutral": "bg-blue-50 border-blue-200"
    }
    
    card_class = f"bg-white rounded-lg border-2 {trend_colors.get(trend, 'border-gray-200')} p-6 hover:shadow-md transition-shadow"
    
    with yog.container(class_name=card_class):
        with yog.container(class_name="flex items-center justify-between"):
            with yog.container():
                yog.text(title, class_name="text-sm font-medium text-gray-600 mb-1")
                yog.text(value, class_name="text-2xl font-bold text-gray-900 mb-2")
                
                if change:
                    change_color = "text-green-600" if trend == "up" else "text-red-600" if trend == "down" else "text-gray-600"
                    yog.text(change, class_name=f"text-sm {change_color} font-medium")
            
            yog.text(icon, class_name="text-3xl text-purple-600")

def professional_button(label: str, on_click=None, variant: str = "primary", icon: str = "", size: str = "md"):
    """Professional button component"""
    
    base_classes = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
    
    variant_classes = {
        "primary": "bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500",
        "secondary": "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
        "danger": "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
        "success": "bg-green-600 text-white hover:bg-green-700 focus:ring-green-500"
    }
    
    size_classes = {
        "sm": "px-3 py-2 text-sm",
        "md": "px-4 py-2 text-sm",
        "lg": "px-6 py-3 text-base"
    }
    
    button_class = f"{base_classes} {variant_classes.get(variant, variant_classes['primary'])} {size_classes.get(size, size_classes['md'])}"
    display_text = f"{icon} {label}" if icon else label
    
    return yog.button(display_text, on_click=on_click, class_name=button_class)

def data_table(data, columns, title="Data Table", actions=None):
    """Professional data table component"""
    with yog.container(class_name="bg-white rounded-lg border border-gray-200 overflow-hidden"):
        # Table header
        with yog.container(class_name="px-6 py-4 border-b border-gray-200 bg-gray-50"):
            yog.title(title, level=3, class_name="text-lg font-semibold text-gray-900 m-0")
        
        # Table content
        with yog.container(class_name="overflow-x-auto"):
            yog.table(data, columns=columns, actions=actions, 
                    class_name="w-full divide-y divide-gray-200")

def activity_feed_item(action: str, description: str, time: str):
    """Activity feed item component"""
    with yog.container(class_name="flex items-start space-x-3 py-4 border-b border-gray-100 last:border-b-0"):
        # Activity indicator
        with yog.container(class_name="flex-shrink-0 mt-1.5"):
            with yog.container(class_name="w-2 h-2 bg-purple-500 rounded-full"):
                pass
        
        # Activity content
        with yog.container(class_name="flex-1 min-w-0"):
            yog.text(action, class_name="text-sm font-medium text-gray-900")
            yog.text(description, class_name="text-sm text-gray-500 mt-1")
        
        # Timestamp
        yog.text(time, class_name="flex-shrink-0 text-xs text-gray-400 mt-1.5")

def quick_action_card(title: str, description: str, icon: str, on_click=None):
    """Quick action card component"""
    def handle_click():
        print(f"🎯 Quick action clicked: {title}")
        if on_click:
            result = on_click()
            print(f"✅ Quick action executed: {result}")
            return result
        return True
    
    # Use a simple button approach
    button_content = f"{icon} {title}\n{description}"
    
    clicked = yog.button(button_content, on_click=handle_click, 
                       class_name="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer w-full text-left")
    
    return clicked

# ==================== ADMIN PAGES ====================

@yog.page("/admin", title="Dashboard", layout="admin_sidebar")
def sidebar_dashboard():
    """Dashboard with sidebar layout"""
    
    # Page header
    with yog.container(class_name="mb-8"):
        yog.title("Dashboard", level=1, class_name="text-3xl font-bold text-gray-900")
        yog.text("Welcome back! Here's what's happening with your business today.", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Key metrics
    with yog.container(class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Users", str(dashboard_stats['total_users']), "+12%", "up", "👥")
        stats_card("Revenue", f"${dashboard_stats['total_revenue']:,}", "+8.2%", "up", "💰")
        stats_card("Active Users", str(dashboard_stats['active_users']), "+5%", "up", "✅")
        stats_card("Growth Rate", "23.4%", "+2.1%", "up", "📈")
    
    # Main content grid
    with yog.container(class_name="grid grid-cols-1 lg:grid-cols-3 gap-8"):
        
        # Recent activity (spans 2 columns)
        with yog.container(class_name="lg:col-span-2"):
            with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
                with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                    yog.title("Recent Activity", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
                
                with yog.container(class_name="p-6"):
                    for activity in recent_activity:
                        activity_feed_item(
                            activity["action"], 
                            activity["description"], 
                            activity["time"]
                        )
                    
                    # View all button
                    with yog.container(class_name="pt-4 border-t border-gray-200 mt-4"):
                        def view_all_activity():
                            yog.navigate_to("/admin/analytics")
                            return True
                        
                        if professional_button("View All Activity", on_click=view_all_activity, 
                                             variant="secondary", icon="📊", size="sm"):
                            yog.alert("Loading activity log...", type="info")
        
        # Quick actions (1 column)
        with yog.container():
            with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
                with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                    yog.title("Quick Actions", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
                
                with yog.container(class_name="p-6 space-y-4"):
                    
                    def add_user():
                        print("👤 Add user clicked")
                        yog.navigate_to("/admin/users")
                        return True
                    
                    def add_product():
                        print("📦 Add product clicked")
                        yog.navigate_to("/admin/products")
                        return True
                    
                    def view_analytics():
                        print("📊 View analytics clicked")
                        yog.navigate_to("/admin/analytics")
                        return True
                    
                    def open_settings():
                        print("⚙️ Open settings clicked")
                        yog.navigate_to("/admin/settings")
                        return True
                    
                    if quick_action_card("Add User", "Create new user account", "👤", add_user):
                        yog.alert("Opening user management...", type="success")
                    
                    if quick_action_card("Add Product", "Create new product", "📦", add_product):
                        yog.alert("Opening product management...", type="success")
                    
                    if quick_action_card("View Reports", "Access analytics dashboard", "📊", view_analytics):
                        yog.alert("Loading analytics...", type="success")
                    
                    if quick_action_card("Settings", "Configure system settings", "⚙️", open_settings):
                        yog.alert("Opening settings...", type="success")
                
                # System status
                with yog.container(class_name="px-6 py-4 border-t border-gray-200 bg-gray-50"):
                    with yog.container(class_name="flex items-center justify-between"):
                        yog.text("System Status", class_name="text-sm font-medium text-gray-600")
                        yog.badge("Online", variant="success")
                    yog.text("Last backup: 2 hours ago", class_name="text-xs text-gray-500 mt-1")

@yog.page("/admin/users", title="Users", layout="admin_sidebar")
def sidebar_users():
    """User management with sidebar layout"""
    
    # Page header with action
    with yog.container(class_name="mb-8"):
        with yog.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            with yog.container():
                yog.title("User Management", level=1, class_name="text-3xl font-bold text-gray-900")
                yog.text("Manage user accounts, roles, and permissions", 
                        class_name="text-lg text-gray-600 mt-2")
            
            def add_user():
                yog.alert("Add user modal would open", type="info")
                return True
            
            if professional_button("Add User", on_click=add_user, variant="primary", icon="➕"):
                yog.alert("Opening user creation form...", type="success")
    
    # User statistics
    with yog.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"):
        stats_card("Total Users", str(dashboard_stats['total_users']), "+5", "up", "👥")
        stats_card("Active Users", str(dashboard_stats['active_users']), "+3", "up", "✅")
        stats_card("Admin Users", str(dashboard_stats['admin_users']), "0", "neutral", "🔐")
    
    # Search and filters
    with yog.container(class_name="bg-white rounded-lg border border-gray-200 p-4 mb-6"):
        with yog.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            # Search and filters
            with yog.container(class_name="flex flex-col sm:flex-row gap-4"):
                yog.input_text(placeholder="Search users...", 
                             class_name="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500")
                yog.select(options=["All Roles", "Admin", "Editor", "Viewer"], 
                         value="All Roles", class_name="px-3 py-2 border border-gray-300 rounded-lg")
                yog.select(options=["All Status", "Active", "Inactive"], 
                         value="All Status", class_name="px-3 py-2 border border-gray-300 rounded-lg")
            
            # Action buttons
            with yog.container(class_name="flex gap-2"):
                def export_users():
                    yog.alert("Exporting users...", type="success")
                    return True
                
                def bulk_actions():
                    yog.alert("Bulk actions available", type="info")
                    return True
                
                if professional_button("Export", on_click=export_users, variant="secondary", icon="📤", size="sm"):
                    yog.alert("User data exported!", type="success")
                
                if professional_button("Bulk Actions", on_click=bulk_actions, variant="secondary", icon="⚡", size="sm"):
                    yog.alert("Bulk action menu opened", type="info")
    
    # Users table
    data_table(users_data, ["name", "email", "role", "status", "last_login"], "All Users")

@yog.page("/admin/analytics", title="Analytics", layout="admin_sidebar")
def sidebar_analytics():
    """Analytics with sidebar layout"""
    
    # Page header
    with yog.container(class_name="mb-8"):
        yog.title("Analytics & Reports", level=1, class_name="text-3xl font-bold text-gray-900")
        yog.text("Track performance metrics and generate detailed reports", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Key metrics
    with yog.container(class_name="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Revenue", f"${dashboard_stats['total_revenue']:,}", "+15.3%", "up", "💰")
        stats_card("Avg Monthly", f"${dashboard_stats['avg_revenue']:,.0f}", "+12.1%", "up", "📊")
        stats_card("Growth Rate", "23.4%", "+2.1%", "up", "📈")
        stats_card("Conversion", "3.24%", "-0.5%", "down", "🎯")
    
    # Charts section
    with yog.container(class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8"):
        
        # Revenue chart
        with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
            with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                yog.title("Revenue Trend", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with yog.container(class_name="p-6"):
                yog.line_chart(data=analytics_data, x_key="month", y_key="revenue", 
                             title="Monthly Revenue")
        
        # User growth chart
        with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
            with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                yog.title("User Growth", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with yog.container(class_name="p-6"):
                yog.bar_chart(data=analytics_data, x_key="month", y_key="users", 
                            title="Monthly Active Users")
    
    # Report generation
    with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
        with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
            yog.title("Generate Reports", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
        
        with yog.container(class_name="p-6"):
            with yog.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-4"):
                
                def generate_monthly():
                    yog.alert("Monthly report generated!", type="success")
                    return True
                
                def generate_quarterly():
                    yog.alert("Quarterly report generated!", type="success")
                    return True
                
                def generate_annual():
                    yog.alert("Annual report generated!", type="success")
                    return True
                
                if professional_button("Monthly Report", on_click=generate_monthly, 
                                     variant="primary", icon="📅"):
                    yog.alert("Generating monthly report...", type="info")
                
                if professional_button("Quarterly Report", on_click=generate_quarterly, 
                                     variant="secondary", icon="📊"):
                    yog.alert("Generating quarterly report...", type="info")
                
                if professional_button("Annual Report", on_click=generate_annual, 
                                     variant="secondary", icon="📈"):
                    yog.alert("Generating annual report...", type="info")

# ==================== ADDITIONAL PAGES ====================

@yog.page("/admin/products", title="Products", layout="admin_sidebar")
def sidebar_products():
    """Products page with sidebar layout"""
    
    # Page header
    with yog.container(class_name="mb-8"):
        with yog.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            with yog.container():
                yog.title("Product Management", level=1, class_name="text-3xl font-bold text-gray-900")
                yog.text("Manage your product catalog and inventory", 
                        class_name="text-lg text-gray-600 mt-2")
            
            def add_product():
                yog.alert("Add product modal would open", type="info")
                return True
            
            if professional_button("Add Product", on_click=add_product, variant="primary", icon="📦"):
                yog.alert("Opening product creation form...", type="success")
    
    # Product stats
    with yog.container(class_name="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Products", "45", "+8", "up", "📦")
        stats_card("Active Products", "42", "+5", "up", "✅")
        stats_card("Categories", "12", "+1", "up", "🏷️")
        stats_card("Out of Stock", "3", "-2", "down", "⚠️")
    
    # Coming soon placeholder
    with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
        with yog.container(class_name="p-12 text-center"):
            yog.text("📦", class_name="text-6xl mb-4")
            yog.title("Product Management", level=2, class_name="text-2xl font-semibold text-gray-900 mb-2")
            yog.text("Advanced product management features coming soon!", 
                    class_name="text-gray-600 mb-6")
            
            def notify_me():
                yog.alert("You'll be notified when this feature is ready!", type="success")
                return True
            
            if professional_button("Notify Me", on_click=notify_me, variant="secondary", icon="🔔"):
                yog.alert("Notification preferences updated!", type="success")

@yog.page("/admin/settings", title="Settings", layout="admin_sidebar")
def sidebar_settings():
    """Settings page with sidebar layout"""
    
    # Page header
    with yog.container(class_name="mb-8"):
        yog.title("Settings", level=1, class_name="text-3xl font-bold text-gray-900")
        yog.text("Configure your application preferences and system settings", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Settings grid
    with yog.container(class_name="grid grid-cols-1 lg:grid-cols-2 gap-8"):
        
        # General settings
        with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
            with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                yog.title("General Settings", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with yog.container(class_name="p-6 space-y-6"):
                with yog.container():
                    yog.text("Application Name", class_name="block text-sm font-medium text-gray-700 mb-2")
                    yog.input_text(value="AdminPro", 
                                 class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500")
                
                with yog.container():
                    yog.text("Time Zone", class_name="block text-sm font-medium text-gray-700 mb-2")
                    yog.select(options=["UTC", "EST", "PST", "GMT"], value="UTC", 
                             class_name="w-full px-3 py-2 border border-gray-300 rounded-lg")
                
                with yog.container(class_name="space-y-3"):
                    yog.checkbox("Enable notifications", checked=True, 
                               class_name="flex items-center space-x-2")
                    yog.checkbox("Auto-save changes", checked=False,
                               class_name="flex items-center space-x-2")
                
                def save_general():
                    yog.alert("General settings saved!", type="success")
                    return True
                
                if professional_button("Save Settings", on_click=save_general, variant="primary", icon="💾"):
                    yog.alert("Saving general settings...", type="info")
        
        # Security settings
        with yog.container(class_name="bg-white rounded-lg border border-gray-200"):
            with yog.container(class_name="px-6 py-4 border-b border-gray-200"):
                yog.title("Security Settings", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with yog.container(class_name="p-6 space-y-6"):
                with yog.container():
                    yog.text("Session Timeout", class_name="block text-sm font-medium text-gray-700 mb-2")
                    yog.select(options=["15 minutes", "30 minutes", "1 hour", "4 hours"], 
                             value="30 minutes", 
                             class_name="w-full px-3 py-2 border border-gray-300 rounded-lg")
                
                with yog.container(class_name="space-y-3"):
                    yog.checkbox("Enable two-factor authentication", checked=True,
                               class_name="flex items-center space-x-2")
                    yog.checkbox("Require strong passwords", checked=True,
                               class_name="flex items-center space-x-2")
                    yog.checkbox("Log security events", checked=False,
                               class_name="flex items-center space-x-2")
                
                def save_security():
                    yog.alert("Security settings updated!", type="success")
                    return True
                
                if professional_button("Update Security", on_click=save_security, variant="danger", icon="🔐"):
                    yog.alert("Updating security settings...", type="info")

# Additional placeholder pages for sidebar navigation
@yog.page("/admin/reports", title="Reports", layout="admin_sidebar")
def sidebar_reports():
    """Reports page"""
    with yog.container(class_name="text-center py-16"):
        yog.text("📋", class_name="text-6xl mb-4")
        yog.title("Reports", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        yog.text("Advanced reporting features coming soon!", class_name="text-lg text-gray-600")

@yog.page("/admin/notifications", title="Notifications", layout="admin_sidebar")
def sidebar_notifications():
    """Notifications page"""
    with yog.container(class_name="text-center py-16"):
        yog.text("🔔", class_name="text-6xl mb-4")
        yog.title("Notifications", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        yog.text("Notification management coming soon!", class_name="text-lg text-gray-600")

@yog.page("/admin/support", title="Support", layout="admin_sidebar")
def sidebar_support():
    """Support page"""
    with yog.container(class_name="text-center py-16"):
        yog.text("💬", class_name="text-6xl mb-4")
        yog.title("Support", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        yog.text("Support system coming soon!", class_name="text-lg text-gray-600")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    
    print("🚀 Starting Professional Admin Portal with Sidebar Navigation...")
    print("=" * 70)
    
    # Create app
    app = yog.YoGuidoApp("Professional Admin Portal - Sidebar", debug=True)
    app.enable_router()
    
    # Set initial page
    yog.navigate_to("/admin")
    
    # Show debug info
    app.debug_info()
    
    # Compile and run
    print("🔨 Compiling with Tailwind CSS...")
    app.compile(force=True)
    
    print("🌐 Starting server...")
    print("✨ Open: http://127.0.0.1:8000/admin")
    print("🎨 Features:")
    print("   - Sidebar navigation with icons")
    print("   - Top navigation bar with search")
    print("   - User profile in sidebar footer")
    print("   - Secondary navigation section")
    print("   - Professional layout structure")
    print("   - Responsive design")
    print("=" * 70)
    
    app.run(host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
```

## 🛠️ Advanced Features

- **Server-Side Rendering** - Fast initial page loads
- **Client-Side Hydration** - Smooth interactivity after load
- **Form Validation** - Built-in validation helpers
- **Routing** - Simple yet powerful routing system
- **API Integration** - Seamless backend communication

## 📚 Documentation

Visit [docs.yoguido.com](https://docs.yoguido.com) for complete documentation.

## 🤝 Contributing

Contributions are welcome! Check out the [contribution guidelines](CONTRIBUTING.md).

## 📄 License

YoGuido is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

YoGuido was inspired by modern UI frameworks but designed to be simpler, more performant, and with zero external dependencies.

---

Made with ❤️ by the YoGuido Team | [yoguido.com](https://www.yoguido.com)