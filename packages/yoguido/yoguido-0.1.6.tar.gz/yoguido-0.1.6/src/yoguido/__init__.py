# ==================== yoguido/__init__.py (Updated for hc.* style) ====================
"""
Main YoGuido framework - supports both import styles:
1. from yoguido import *           # Direct imports  
2. import yoguido as hc           # Module-style imports (hc.component, hc.state, etc.)
"""

# Core framework
from .core.runtime import YoGuidoApp
from .core.decorators import component, state, computed
from .core.state import use_state

# Basic UI components
from .ui.basic_components import (
    title, text, button, 
    input_text, input_number, select, checkbox, slider,
    container, flex, grid
)

# Extended UI components
from .ui.data_components import (
    table, card, stats_card, progress_bar, 
    badge, alert, loading_spinner
)

from .ui.form_components import (
    textarea, date_picker, file_upload, radio_group,
    form, form_field
)

from .ui.navigation_components import (
    breadcrumb, tabs, pagination
)

from .ui.layout_components import (
    sidebar, header, footer, modal, dropdown,
    separator, spacer
)

from .ui.chart_components import (
    line_chart, bar_chart, pie_chart
)

# Page system
from .pages.routing import (
    page, layout, router, navigate_to,
    get_current_path, get_current_page_title, is_current_page
)

# Export everything for both import styles
__all__ = [
    # Core
    'YoGuidoApp', 'component', 'state', 'computed', 'use_state',
    
    # Basic UI
    'title', 'text', 'button', 'input_text', 'input_number', 
    'select', 'checkbox', 'slider',
    
    # Layout
    'container', 'flex', 'grid', 'sidebar', 'header', 'footer',
    'modal', 'dropdown', 'separator', 'spacer',
    
    # Data display
    'table', 'card', 'stats_card', 'progress_bar', 'badge', 
    'alert', 'loading_spinner',
    
    # Forms
    'form', 'form_field', 'textarea', 'date_picker', 
    'file_upload', 'radio_group',
    
    # Navigation
    'breadcrumb', 'tabs', 'pagination',
    
    # Charts
    'line_chart', 'bar_chart', 'pie_chart',
    
    # Pages
    'page', 'layout', 'router', 'navigate_to',
    'get_current_path', 'get_current_page_title', 'is_current_page'
]