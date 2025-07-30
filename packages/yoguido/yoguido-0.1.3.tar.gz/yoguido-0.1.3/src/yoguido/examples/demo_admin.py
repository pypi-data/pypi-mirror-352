"""
Professional Admin Portal with Sidebar Navigation
Enhanced layout with sidebar + top navigation
"""

import yoguido as hc
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

@hc.layout("admin_sidebar")
def admin_sidebar_layout(page_component):
    """Modern admin layout with sidebar navigation"""
    
    # Main container with sidebar layout
    with hc.container(class_name="min-h-screen bg-gray-50 flex"):
        
        # Sidebar
        render_sidebar()
        
        # Main content area
        with hc.container(class_name="flex-1 flex flex-col min-w-0"):
            
            # Top navigation bar
            render_top_nav()
            
            # Page content
            with hc.container(class_name="flex-1 p-6 overflow-auto"):
                
                # Breadcrumb
                render_breadcrumb()
                
                # Page content with spacing
                with hc.container(class_name="mt-6"):
                    page_component()

def render_sidebar():
    """Render the sidebar navigation"""
    with hc.container(class_name="w-64 bg-white shadow-lg flex flex-col"):
        
        # Logo/Brand section
        with hc.container(class_name="p-6 border-b border-gray-200"):
            with hc.container(class_name="flex items-center space-x-3"):
                hc.text("🧠", class_name="text-2xl")
                hc.title("AdminPro", level=2, class_name="text-xl font-bold text-purple-600 m-0")
        
        # Navigation menu
        with hc.container(class_name="flex-1 py-6"):
            with hc.container(class_name="px-3 space-y-1"):
                
                # Main navigation items
                sidebar_nav_item("📊", "Dashboard", "/admin")
                sidebar_nav_item("👥", "Users", "/admin/users")
                sidebar_nav_item("📦", "Products", "/admin/products")
                sidebar_nav_item("📈", "Analytics", "/admin/analytics")
                sidebar_nav_item("⚙️", "Settings", "/admin/settings")
                
                # Divider
                with hc.container(class_name="py-4"):
                    hc.separator(class_name="border-gray-200")
                
                # Secondary navigation
                hc.text("TOOLS", class_name="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2")
                sidebar_nav_item("📋", "Reports", "/admin/reports")
                sidebar_nav_item("🔔", "Notifications", "/admin/notifications")
                sidebar_nav_item("💬", "Support", "/admin/support")
        
        # Sidebar footer
        with hc.container(class_name="p-4 border-t border-gray-200"):
            with hc.container(class_name="flex items-center space-x-3"):
                # User avatar
                with hc.container(class_name="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center"):
                    hc.text("JD", class_name="text-sm font-medium text-white")
                
                # User info
                with hc.container(class_name="flex-1 min-w-0"):
                    hc.text("John Doe", class_name="text-sm font-medium text-gray-900 truncate")
                    hc.text("Admin", class_name="text-xs text-gray-500")
                
                # Settings button - fixed to navigate to settings page
                def user_settings():
                    print("⚙️ User settings clicked")
                    hc.navigate_to("/admin/settings")
                    return True
                
                if hc.button("⚙️", on_click=user_settings, 
                           class_name="text-gray-400 hover:text-gray-600 p-1"):
                    print("✅ User settings button clicked")

def sidebar_nav_item(icon: str, label: str, path: str):
    """Individual sidebar navigation item"""
    is_active = hc.is_current_page(path)
    
    def navigate():
        print(f"🎯 Navigation clicked: {path}")
        hc.navigate_to(path)
        return True
    
    # Style based on active state
    if is_active:
        item_class = "flex items-center space-x-3 px-3 py-2 text-sm font-medium text-purple-600 bg-purple-50 border-r-2 border-purple-600 rounded-l-md w-full text-left"
    else:
        item_class = "flex items-center space-x-3 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors w-full text-left"
    
    # Create button with icon and text inside
    button_text = f"{icon} {label}"
    clicked = hc.button(button_text, on_click=navigate, class_name=item_class)
    
    if clicked:
        print(f"✅ Button clicked for {label}")
        hc.alert(f"Navigating to {label}", type="info")

def render_top_nav():
    """Render the top navigation bar"""
    with hc.container(class_name="bg-white shadow-sm border-b border-gray-200 px-6 py-4"):
        with hc.container(class_name="flex items-center justify-between"):
            
            # Left side - Page actions or search
            with hc.container(class_name="flex items-center space-x-4"):
                # Mobile menu button (for responsive design)
                def toggle_mobile_menu():
                    print("🔄 Mobile menu toggled")
                    hc.alert("Mobile menu would toggle", type="info")
                    return True
                
                hc.button("☰", on_click=toggle_mobile_menu, 
                         class_name="lg:hidden p-2 text-gray-400 hover:text-gray-600")
                
                # Search bar
                with hc.container(class_name="hidden md:block"):
                    search_value = hc.input_text(placeholder="Search...", 
                                               class_name="w-80 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent")
            
            # Right side - Actions and notifications
            with hc.container(class_name="flex items-center space-x-4"):
                
                # Quick actions
                def add_item():
                    print("➕ Quick add clicked")
                    hc.alert("Quick add menu would open", type="info")
                    return True
                
                if hc.button("➕", on_click=add_item,
                           class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                    print("✅ Quick add button clicked")
                
                # Notifications
                def show_notifications():
                    print("🔔 Notifications clicked")
                    hc.alert("Notifications panel would open", type="info")
                    return True
                
                with hc.container(class_name="relative"):
                    if hc.button("🔔", on_click=show_notifications,
                               class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                        print("✅ Notifications button clicked")
                    
                    # Notification badge
                    with hc.container(class_name="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center"):
                        hc.text("3", class_name="text-xs text-white font-medium")
                
                # Profile dropdown
                def profile_menu():
                    print("👤 Profile menu clicked")
                    hc.alert("Profile menu would open", type="info")
                    return True
                
                if hc.button("👤", on_click=profile_menu,
                           class_name="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"):
                    print("✅ Profile button clicked")

def render_breadcrumb():
    """Render breadcrumb navigation"""
    current_path = hc.get_current_path()
    
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
    
    with hc.container(class_name="bg-white rounded-lg border border-gray-200 px-4 py-3"):
        with hc.container(class_name="flex items-center space-x-2 text-sm"):
            # Home icon
            hc.text("🏠", class_name="text-gray-400")
            
            for i, item in enumerate(items):
                # Add separator if not first item
                if i > 0:
                    hc.text("/", class_name="text-gray-400 mx-2")
                
                # Create breadcrumb item
                if "url" in item:
                    # Clickable breadcrumb item
                    def navigate_to_item(url=item["url"]):
                        hc.navigate_to(url)
                        return True
                    
                    if hc.button(item["label"], on_click=navigate_to_item,
                               class_name="text-purple-600 hover:text-purple-800 hover:underline bg-transparent border-0 p-0 font-medium"):
                        hc.alert(f"Navigating to {item['label']}", type="info")
                else:
                    # Current page (non-clickable)
                    hc.text(item["label"], class_name="text-gray-900 font-medium")

# ==================== ENHANCED COMPONENTS ====================

def stats_card(title: str, value: str, change: str = None, trend: str = "neutral", icon: str = "📊"):
    """Professional statistics card"""
    
    trend_colors = {
        "up": "bg-green-50 border-green-200",
        "down": "bg-red-50 border-red-200", 
        "neutral": "bg-blue-50 border-blue-200"
    }
    
    card_class = f"bg-white rounded-lg border-2 {trend_colors.get(trend, 'border-gray-200')} p-6 hover:shadow-md transition-shadow"
    
    with hc.container(class_name=card_class):
        with hc.container(class_name="flex items-center justify-between"):
            with hc.container():
                hc.text(title, class_name="text-sm font-medium text-gray-600 mb-1")
                hc.text(value, class_name="text-2xl font-bold text-gray-900 mb-2")
                
                if change:
                    change_color = "text-green-600" if trend == "up" else "text-red-600" if trend == "down" else "text-gray-600"
                    hc.text(change, class_name=f"text-sm {change_color} font-medium")
            
            hc.text(icon, class_name="text-3xl text-purple-600")

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
    
    return hc.button(display_text, on_click=on_click, class_name=button_class)

def data_table(data, columns, title="Data Table", actions=None):
    """Professional data table component"""
    with hc.container(class_name="bg-white rounded-lg border border-gray-200 overflow-hidden"):
        # Table header
        with hc.container(class_name="px-6 py-4 border-b border-gray-200 bg-gray-50"):
            hc.title(title, level=3, class_name="text-lg font-semibold text-gray-900 m-0")
        
        # Table content
        with hc.container(class_name="overflow-x-auto"):
            hc.table(data, columns=columns, actions=actions, 
                    class_name="w-full divide-y divide-gray-200")

def activity_feed_item(action: str, description: str, time: str):
    """Activity feed item component"""
    with hc.container(class_name="flex items-start space-x-3 py-4 border-b border-gray-100 last:border-b-0"):
        # Activity indicator
        with hc.container(class_name="flex-shrink-0 mt-1.5"):
            with hc.container(class_name="w-2 h-2 bg-purple-500 rounded-full"):
                pass
        
        # Activity content
        with hc.container(class_name="flex-1 min-w-0"):
            hc.text(action, class_name="text-sm font-medium text-gray-900")
            hc.text(description, class_name="text-sm text-gray-500 mt-1")
        
        # Timestamp
        hc.text(time, class_name="flex-shrink-0 text-xs text-gray-400 mt-1.5")

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
    
    clicked = hc.button(button_content, on_click=handle_click, 
                       class_name="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer w-full text-left")
    
    return clicked

# ==================== ADMIN PAGES ====================

@hc.page("/admin", title="Dashboard", layout="admin_sidebar")
def sidebar_dashboard():
    """Dashboard with sidebar layout"""
    
    # Page header
    with hc.container(class_name="mb-8"):
        hc.title("Dashboard", level=1, class_name="text-3xl font-bold text-gray-900")
        hc.text("Welcome back! Here's what's happening with your business today.", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Key metrics
    with hc.container(class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Users", str(dashboard_stats['total_users']), "+12%", "up", "👥")
        stats_card("Revenue", f"${dashboard_stats['total_revenue']:,}", "+8.2%", "up", "💰")
        stats_card("Active Users", str(dashboard_stats['active_users']), "+5%", "up", "✅")
        stats_card("Growth Rate", "23.4%", "+2.1%", "up", "📈")
    
    # Main content grid
    with hc.container(class_name="grid grid-cols-1 lg:grid-cols-3 gap-8"):
        
        # Recent activity (spans 2 columns)
        with hc.container(class_name="lg:col-span-2"):
            with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
                with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                    hc.title("Recent Activity", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
                
                with hc.container(class_name="p-6"):
                    for activity in recent_activity:
                        activity_feed_item(
                            activity["action"], 
                            activity["description"], 
                            activity["time"]
                        )
                    
                    # View all button
                    with hc.container(class_name="pt-4 border-t border-gray-200 mt-4"):
                        def view_all_activity():
                            hc.navigate_to("/admin/analytics")
                            return True
                        
                        if professional_button("View All Activity", on_click=view_all_activity, 
                                             variant="secondary", icon="📊", size="sm"):
                            hc.alert("Loading activity log...", type="info")
        
        # Quick actions (1 column)
        with hc.container():
            with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
                with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                    hc.title("Quick Actions", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
                
                with hc.container(class_name="p-6 space-y-4"):
                    
                    def add_user():
                        print("👤 Add user clicked")
                        hc.navigate_to("/admin/users")
                        return True
                    
                    def add_product():
                        print("📦 Add product clicked")
                        hc.navigate_to("/admin/products")
                        return True
                    
                    def view_analytics():
                        print("📊 View analytics clicked")
                        hc.navigate_to("/admin/analytics")
                        return True
                    
                    def open_settings():
                        print("⚙️ Open settings clicked")
                        hc.navigate_to("/admin/settings")
                        return True
                    
                    if quick_action_card("Add User", "Create new user account", "👤", add_user):
                        hc.alert("Opening user management...", type="success")
                    
                    if quick_action_card("Add Product", "Create new product", "📦", add_product):
                        hc.alert("Opening product management...", type="success")
                    
                    if quick_action_card("View Reports", "Access analytics dashboard", "📊", view_analytics):
                        hc.alert("Loading analytics...", type="success")
                    
                    if quick_action_card("Settings", "Configure system settings", "⚙️", open_settings):
                        hc.alert("Opening settings...", type="success")
                
                # System status
                with hc.container(class_name="px-6 py-4 border-t border-gray-200 bg-gray-50"):
                    with hc.container(class_name="flex items-center justify-between"):
                        hc.text("System Status", class_name="text-sm font-medium text-gray-600")
                        hc.badge("Online", variant="success")
                    hc.text("Last backup: 2 hours ago", class_name="text-xs text-gray-500 mt-1")

@hc.page("/admin/users", title="Users", layout="admin_sidebar")
def sidebar_users():
    """User management with sidebar layout"""
    
    # Page header with action
    with hc.container(class_name="mb-8"):
        with hc.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            with hc.container():
                hc.title("User Management", level=1, class_name="text-3xl font-bold text-gray-900")
                hc.text("Manage user accounts, roles, and permissions", 
                        class_name="text-lg text-gray-600 mt-2")
            
            def add_user():
                hc.alert("Add user modal would open", type="info")
                return True
            
            if professional_button("Add User", on_click=add_user, variant="primary", icon="➕"):
                hc.alert("Opening user creation form...", type="success")
    
    # User statistics
    with hc.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"):
        stats_card("Total Users", str(dashboard_stats['total_users']), "+5", "up", "👥")
        stats_card("Active Users", str(dashboard_stats['active_users']), "+3", "up", "✅")
        stats_card("Admin Users", str(dashboard_stats['admin_users']), "0", "neutral", "🔐")
    
    # Search and filters
    with hc.container(class_name="bg-white rounded-lg border border-gray-200 p-4 mb-6"):
        with hc.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            # Search and filters
            with hc.container(class_name="flex flex-col sm:flex-row gap-4"):
                hc.input_text(placeholder="Search users...", 
                             class_name="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500")
                hc.select(options=["All Roles", "Admin", "Editor", "Viewer"], 
                         value="All Roles", class_name="px-3 py-2 border border-gray-300 rounded-lg")
                hc.select(options=["All Status", "Active", "Inactive"], 
                         value="All Status", class_name="px-3 py-2 border border-gray-300 rounded-lg")
            
            # Action buttons
            with hc.container(class_name="flex gap-2"):
                def export_users():
                    hc.alert("Exporting users...", type="success")
                    return True
                
                def bulk_actions():
                    hc.alert("Bulk actions available", type="info")
                    return True
                
                if professional_button("Export", on_click=export_users, variant="secondary", icon="📤", size="sm"):
                    hc.alert("User data exported!", type="success")
                
                if professional_button("Bulk Actions", on_click=bulk_actions, variant="secondary", icon="⚡", size="sm"):
                    hc.alert("Bulk action menu opened", type="info")
    
    # Users table
    data_table(users_data, ["name", "email", "role", "status", "last_login"], "All Users")

@hc.page("/admin/analytics", title="Analytics", layout="admin_sidebar")
def sidebar_analytics():
    """Analytics with sidebar layout"""
    
    # Page header
    with hc.container(class_name="mb-8"):
        hc.title("Analytics & Reports", level=1, class_name="text-3xl font-bold text-gray-900")
        hc.text("Track performance metrics and generate detailed reports", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Key metrics
    with hc.container(class_name="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Revenue", f"${dashboard_stats['total_revenue']:,}", "+15.3%", "up", "💰")
        stats_card("Avg Monthly", f"${dashboard_stats['avg_revenue']:,.0f}", "+12.1%", "up", "📊")
        stats_card("Growth Rate", "23.4%", "+2.1%", "up", "📈")
        stats_card("Conversion", "3.24%", "-0.5%", "down", "🎯")
    
    # Charts section
    with hc.container(class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8"):
        
        # Revenue chart
        with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
            with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                hc.title("Revenue Trend", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with hc.container(class_name="p-6"):
                hc.line_chart(data=analytics_data, x_key="month", y_key="revenue", 
                             title="Monthly Revenue")
        
        # User growth chart
        with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
            with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                hc.title("User Growth", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with hc.container(class_name="p-6"):
                hc.bar_chart(data=analytics_data, x_key="month", y_key="users", 
                            title="Monthly Active Users")
    
    # Report generation
    with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
        with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
            hc.title("Generate Reports", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
        
        with hc.container(class_name="p-6"):
            with hc.container(class_name="grid grid-cols-1 md:grid-cols-3 gap-4"):
                
                def generate_monthly():
                    hc.alert("Monthly report generated!", type="success")
                    return True
                
                def generate_quarterly():
                    hc.alert("Quarterly report generated!", type="success")
                    return True
                
                def generate_annual():
                    hc.alert("Annual report generated!", type="success")
                    return True
                
                if professional_button("Monthly Report", on_click=generate_monthly, 
                                     variant="primary", icon="📅"):
                    hc.alert("Generating monthly report...", type="info")
                
                if professional_button("Quarterly Report", on_click=generate_quarterly, 
                                     variant="secondary", icon="📊"):
                    hc.alert("Generating quarterly report...", type="info")
                
                if professional_button("Annual Report", on_click=generate_annual, 
                                     variant="secondary", icon="📈"):
                    hc.alert("Generating annual report...", type="info")

# ==================== ADDITIONAL PAGES ====================

@hc.page("/admin/products", title="Products", layout="admin_sidebar")
def sidebar_products():
    """Products page with sidebar layout"""
    
    # Page header
    with hc.container(class_name="mb-8"):
        with hc.container(class_name="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"):
            with hc.container():
                hc.title("Product Management", level=1, class_name="text-3xl font-bold text-gray-900")
                hc.text("Manage your product catalog and inventory", 
                        class_name="text-lg text-gray-600 mt-2")
            
            def add_product():
                hc.alert("Add product modal would open", type="info")
                return True
            
            if professional_button("Add Product", on_click=add_product, variant="primary", icon="📦"):
                hc.alert("Opening product creation form...", type="success")
    
    # Product stats
    with hc.container(class_name="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"):
        stats_card("Total Products", "45", "+8", "up", "📦")
        stats_card("Active Products", "42", "+5", "up", "✅")
        stats_card("Categories", "12", "+1", "up", "🏷️")
        stats_card("Out of Stock", "3", "-2", "down", "⚠️")
    
    # Coming soon placeholder
    with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
        with hc.container(class_name="p-12 text-center"):
            hc.text("📦", class_name="text-6xl mb-4")
            hc.title("Product Management", level=2, class_name="text-2xl font-semibold text-gray-900 mb-2")
            hc.text("Advanced product management features coming soon!", 
                    class_name="text-gray-600 mb-6")
            
            def notify_me():
                hc.alert("You'll be notified when this feature is ready!", type="success")
                return True
            
            if professional_button("Notify Me", on_click=notify_me, variant="secondary", icon="🔔"):
                hc.alert("Notification preferences updated!", type="success")

@hc.page("/admin/settings", title="Settings", layout="admin_sidebar")
def sidebar_settings():
    """Settings page with sidebar layout"""
    
    # Page header
    with hc.container(class_name="mb-8"):
        hc.title("Settings", level=1, class_name="text-3xl font-bold text-gray-900")
        hc.text("Configure your application preferences and system settings", 
                class_name="text-lg text-gray-600 mt-2")
    
    # Settings grid
    with hc.container(class_name="grid grid-cols-1 lg:grid-cols-2 gap-8"):
        
        # General settings
        with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
            with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                hc.title("General Settings", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with hc.container(class_name="p-6 space-y-6"):
                with hc.container():
                    hc.text("Application Name", class_name="block text-sm font-medium text-gray-700 mb-2")
                    hc.input_text(value="AdminPro", 
                                 class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500")
                
                with hc.container():
                    hc.text("Time Zone", class_name="block text-sm font-medium text-gray-700 mb-2")
                    hc.select(options=["UTC", "EST", "PST", "GMT"], value="UTC", 
                             class_name="w-full px-3 py-2 border border-gray-300 rounded-lg")
                
                with hc.container(class_name="space-y-3"):
                    hc.checkbox("Enable notifications", checked=True, 
                               class_name="flex items-center space-x-2")
                    hc.checkbox("Auto-save changes", checked=False,
                               class_name="flex items-center space-x-2")
                
                def save_general():
                    hc.alert("General settings saved!", type="success")
                    return True
                
                if professional_button("Save Settings", on_click=save_general, variant="primary", icon="💾"):
                    hc.alert("Saving general settings...", type="info")
        
        # Security settings
        with hc.container(class_name="bg-white rounded-lg border border-gray-200"):
            with hc.container(class_name="px-6 py-4 border-b border-gray-200"):
                hc.title("Security Settings", level=3, class_name="text-lg font-semibold text-gray-900 m-0")
            
            with hc.container(class_name="p-6 space-y-6"):
                with hc.container():
                    hc.text("Session Timeout", class_name="block text-sm font-medium text-gray-700 mb-2")
                    hc.select(options=["15 minutes", "30 minutes", "1 hour", "4 hours"], 
                             value="30 minutes", 
                             class_name="w-full px-3 py-2 border border-gray-300 rounded-lg")
                
                with hc.container(class_name="space-y-3"):
                    hc.checkbox("Enable two-factor authentication", checked=True,
                               class_name="flex items-center space-x-2")
                    hc.checkbox("Require strong passwords", checked=True,
                               class_name="flex items-center space-x-2")
                    hc.checkbox("Log security events", checked=False,
                               class_name="flex items-center space-x-2")
                
                def save_security():
                    hc.alert("Security settings updated!", type="success")
                    return True
                
                if professional_button("Update Security", on_click=save_security, variant="danger", icon="🔐"):
                    hc.alert("Updating security settings...", type="info")

# Additional placeholder pages for sidebar navigation
@hc.page("/admin/reports", title="Reports", layout="admin_sidebar")
def sidebar_reports():
    """Reports page"""
    with hc.container(class_name="text-center py-16"):
        hc.text("📋", class_name="text-6xl mb-4")
        hc.title("Reports", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        hc.text("Advanced reporting features coming soon!", class_name="text-lg text-gray-600")

@hc.page("/admin/notifications", title="Notifications", layout="admin_sidebar")
def sidebar_notifications():
    """Notifications page"""
    with hc.container(class_name="text-center py-16"):
        hc.text("🔔", class_name="text-6xl mb-4")
        hc.title("Notifications", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        hc.text("Notification management coming soon!", class_name="text-lg text-gray-600")

@hc.page("/admin/support", title="Support", layout="admin_sidebar")
def sidebar_support():
    """Support page"""
    with hc.container(class_name="text-center py-16"):
        hc.text("💬", class_name="text-6xl mb-4")
        hc.title("Support", level=1, class_name="text-3xl font-bold text-gray-900 mb-4")
        hc.text("Support system coming soon!", class_name="text-lg text-gray-600")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    
    print("🚀 Starting Professional Admin Portal with Sidebar Navigation...")
    print("=" * 70)
    
    # Create app
    app = hc.YoGuidoApp("Professional Admin Portal - Sidebar", debug=True)
    app.enable_router()
    
    # Set initial page
    hc.navigate_to("/admin")
    
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