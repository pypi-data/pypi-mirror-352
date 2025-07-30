"""
Fixed YoGuido Compiler with Working Button Events
Replace your yoguido/core/compiler.py with this version
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class YoGuidoCompiler:
    """
    Fixed Vanilla JavaScript compiler for YoGuido framework
    """
    
    def __init__(self, output_dir: str = "./yoguido_build"):
        self.output_dir = Path(output_dir)
        self.components = {}
        self.state_classes = {}
        self.css_built = False

    def compile_project(self, app_title: str = "YoGuido App"):
        """Compile entire project with CSS build integration"""
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"🔨 Compiling YoGuido app: {app_title}")
        
        # 1. Try to build Tailwind CSS
        self._try_build_css()
        
        # 2. Analyze registered components
        self._analyze_components()
        
        # 3. Generate HTML file
        self._generate_html(app_title)
        
        # 4. Generate JavaScript
        self._generate_javascript()
        
        # 5. Generate CSS (fallback if not already built)
        if not self.css_built:
            self._generate_fallback_css()
        
        print(f"✅ Compilation complete!")
        print(f"   📁 Output directory: {self.output_dir}")
        print(f"   🌐 Open: {self.output_dir}/index.html")
        
        # Show CSS info
        css_file = self.output_dir / "styles.css"
        if css_file.exists():
            size_kb = css_file.stat().st_size / 1024
            print(f"   📏 CSS file size: {size_kb:.1f} KB")

    def _try_build_css(self):
        """Try to build Tailwind CSS, don't fail if it doesn't work"""
        css_file = self.output_dir / "styles.css"
        
        # Check if we need to build
        if css_file.exists():
            print("✅ CSS file already exists")
            self.css_built = True
            return
        
        # Try to build Tailwind CSS
        if self._build_tailwind_css():
            self.css_built = True
        else:
            print("⚠️ Tailwind CSS build failed, will use fallback")
            self.css_built = False

    def _build_tailwind_css(self) -> bool:
        """Try to build Tailwind CSS"""
        css_input = Path("src/input.css")
        css_output = self.output_dir / "styles.css"
        
        # Check if input files exist
        if not css_input.exists():
            print("ℹ️ No src/input.css found, skipping Tailwind build")
            return False
        
        if not Path("tailwind.config.js").exists():
            print("ℹ️ No tailwind.config.js found, skipping Tailwind build")
            return False
        
        # Try different build methods
        build_methods = [
            (["npx", "tailwindcss"], "npx tailwindcss"),
            (["npx", "@tailwindcss/cli"], "npx @tailwindcss/cli"),
            (["tailwindcss"], "global tailwindcss")
        ]
        
        for base_cmd, method_name in build_methods:
            try:
                print(f"🎨 Trying to build CSS with {method_name}...")
                
                cmd = base_cmd + [
                    "-i", str(css_input),
                    "-o", str(css_output),
                    "--minify"
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                
                if result.returncode == 0 and css_output.exists():
                    size_kb = css_output.stat().st_size / 1024
                    print(f"✅ CSS built successfully with {method_name}! ({size_kb:.1f} KB)")
                    return True
                else:
                    print(f"❌ {method_name} failed")
                    
            except subprocess.TimeoutExpired:
                print(f"❌ {method_name} timed out")
            except FileNotFoundError:
                print(f"❌ {method_name} not found")
            except Exception as e:
                print(f"❌ {method_name} error: {e}")
        
        print("❌ All CSS build methods failed")
        return False

    def _analyze_components(self):
        """Analyze registered components"""
        try:
            from .decorators import _registry
            self.components = _registry.get_all_components()
            self.state_classes = _registry.get_all_state_classes()
        except ImportError:
            print("⚠️ Could not import component registry")
            self.components = {}
            self.state_classes = {}
        
        print(f"📊 Found {len(self.components)} components")
        print(f"📊 Found {len(self.state_classes)} state classes")

    def _generate_html(self, app_title: str):
        """Generate main HTML file with proper element IDs"""
        
        # Get CSS link
        css_link = self._get_css_link()
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_title}</title>
    
    {css_link}
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Meta tags -->
    <meta name="description" content="{app_title} - Built with YoGuido Framework">
    <meta name="theme-color" content="#7c3aed">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔧</text></svg>">
    
    <style>
        /* Base styles before CSS loads */
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9fafb;
            color: #111827;
            line-height: 1.5;
        }}
        
        /* Loading animation */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .loading-animation {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        /* Loading screen styles */
        .loading-screen {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #f9fafb;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50;
        }}
        
        .loading-content {{
            text-align: center;
            max-width: 400px;
            padding: 2rem;
        }}
        
        .spinner {{
            width: 3rem;
            height: 3rem;
            border: 4px solid #e5e7eb;
            border-top: 4px solid #7c3aed;
            border-radius: 50%;
            margin: 0 auto 1rem;
            animation: spin 1s linear infinite;
        }}
        
        .loading-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
            margin: 0 0 0.5rem 0;
        }}
        
        .loading-subtitle {{
            color: #6b7280;
            margin: 0 0 1rem 0;
        }}
        
        .loading-status {{
            font-size: 0.875rem;
            color: #6b7280;
            margin-top: 1rem;
        }}
        
        /* App content */
        .app-content {{
            min-height: 100vh;
            display: none;
        }}
        
        /* State management */
        .yoguido-loading .app-content {{
            display: none;
        }}
        
        .yoguido-loaded .loading-screen {{
            display: none;
        }}
        
        .yoguido-loaded .app-content {{
            display: block;
        }}
        
        /* Error display */
        .error-display {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 50;
            max-width: 28rem;
        }}
        
        .error-content {{
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            color: #991b1b;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: flex-start;
        }}
        
        .error-icon {{
            flex-shrink: 0;
            margin-right: 0.75rem;
        }}
        
        .error-text {{
            flex: 1;
            min-width: 0;
        }}
        
        .error-title {{
            font-weight: 500;
            margin: 0 0 0.25rem 0;
        }}
        
        .error-message {{
            font-size: 0.875rem;
            margin: 0;
        }}
        
        .error-close {{
            background: none;
            border: none;
            color: currentColor;
            opacity: 0.5;
            cursor: pointer;
            padding: 0;
            margin-left: 1rem;
        }}
        
        .error-close:hover {{
            opacity: 0.75;
        }}
        
        /* Utilities */
        .hidden {{
            display: none !important;
        }}
        
        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }}
    </style>
</head>

<body class="yoguido-loading">
    <!-- Skip to main content -->
    <a href="#app-content" class="sr-only">Skip to main content</a>
    
    <!-- Main application container -->
    <div id="yoguido-app">
        
        <!-- Loading screen -->
        <div id="loading" class="loading-screen">
            <div class="loading-content">
                <div class="loading-animation">
                    <div class="spinner"></div>
                </div>
                <h2 class="loading-title">Loading {app_title}</h2>
                <p class="loading-subtitle">Powered by YoGuido Framework</p>
                <div class="loading-status">
                    {'✅ Using local Tailwind CSS' if self.css_built else '⚠️ Using fallback CSS'}
                </div>
            </div>
        </div>
        
        <!-- Main app content with correct ID -->
        <div id="app-content" class="app-content">
            <!-- Components will be rendered here by JavaScript -->
        </div>
        
        <!-- Error display -->
        <div id="error-display" class="error-display hidden">
            <div class="error-content">
                <div class="error-icon">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="error-text">
                    <h4 class="error-title">Application Error</h4>
                    <p id="error-message" class="error-message"></p>
                </div>
                <button id="close-error" class="error-close">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Notification container -->
        <div id="notification-container"></div>
        
        <!-- Accessibility live region -->
        <div aria-live="polite" aria-atomic="true" class="sr-only" id="live-region"></div>
    </div>
    
    <!-- JavaScript application -->
    <script src="main.js"></script>
    
    <!-- Initialize app -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Mark app as loaded
            document.body.classList.remove('yoguido-loading');
            document.body.classList.add('yoguido-loaded');
            
            // Setup error close handler
            const closeErrorBtn = document.getElementById('close-error');
            const errorDisplay = document.getElementById('error-display');
            
            if (closeErrorBtn && errorDisplay) {{
                closeErrorBtn.addEventListener('click', function() {{
                    errorDisplay.classList.add('hidden');
                }});
            }}
            
            console.log('🎉 YoGuido app initialized successfully!');
            console.log('📊 CSS Method: {("Local Tailwind" if self.css_built else "Fallback")}');
        }});
        
        // Global error handler
        window.addEventListener('error', function(event) {{
            console.error('Global error:', event.error);
            
            const errorDisplay = document.getElementById('error-display');
            const errorMessage = document.getElementById('error-message');
            
            if (errorDisplay && errorMessage) {{
                errorMessage.textContent = event.error.message || 'An unexpected error occurred';
                errorDisplay.classList.remove('hidden');
            }}
        }});
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', function(event) {{
            console.error('Unhandled promise rejection:', event.reason);
        }});
    </script>
</body>
</html>'''
        
        # Write HTML file
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("📄 Generated index.html with proper element IDs")

    def _get_css_link(self) -> str:
        """Get the appropriate CSS link (local or CDN fallback)"""
        css_file = self.output_dir / "styles.css"
        
        if css_file.exists() and self.css_built:
            return '''<!-- Local Tailwind CSS -->
    <link rel="stylesheet" href="styles.css">'''
        else:
            return '''<!-- Tailwind CSS CDN Fallback -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        purple: {{
                            50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff',
                            300: '#d8b4fe', 400: '#c084fc', 500: '#a855f7',
                            600: '#9333ea', 700: '#7c3aed', 800: '#6b21a8', 900: '#581c87'
                        }}
                    }}
                }}
            }}
        }}
    </script>'''

    def _generate_fallback_css(self):
        """Generate a basic fallback CSS file if Tailwind build failed"""
        if self.css_built:
            return
        
        print("🎨 Generating fallback CSS...")
        
        fallback_css = '''/* YoGuido Fallback CSS */

/* Reset and base styles */
* {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f9fafb;
    color: #111827;
    line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    color: #111827;
    margin-top: 0;
    margin-bottom: 0.5rem;
}

/* Button styles */
.btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    background-color: #9333ea;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.btn-primary:hover {
    background-color: #7c3aed;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    background-color: white;
    color: #374151;
    font-weight: 600;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.btn-secondary:hover {
    background-color: #f9fafb;
}

/* Card styles */
.card {
    background-color: white;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    overflow: hidden;
}

.card-elevated {
    background-color: white;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: box-shadow 0.3s ease;
}

.card-elevated:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Navigation styles */
.nav-item {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
    text-decoration: none;
}

.nav-item-active {
    background-color: #ede9fe;
    color: #7c3aed;
}

.nav-item-inactive {
    color: #6b7280;
}

.nav-item-inactive:hover {
    color: #374151;
    background-color: #f3f4f6;
}

/* Header styles */
.header {
    background-color: white;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    border-bottom: 1px solid #e5e7eb;
}

.header-content {
    max-width: 80rem;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 4rem;
}

/* Container styles */
.container-wide {
    max-width: 80rem;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Utility styles */
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.space-x-4 > * + * { margin-left: 1rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.grid { display: grid; }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
.gap-6 { gap: 1.5rem; }
.gap-8 { gap: 2rem; }
.mb-8 { margin-bottom: 2rem; }
.mt-6 { margin-top: 1.5rem; }
.p-6 { padding: 1.5rem; }
.py-8 { padding-top: 2rem; padding-bottom: 2rem; }
.text-2xl { font-size: 1.5rem; }
.text-3xl { font-size: 1.875rem; }
.font-bold { font-weight: 700; }
.text-gray-600 { color: #4b5563; }
.text-gray-900 { color: #111827; }

/* Responsive */
@media (min-width: 768px) {
    .md\\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
    .md\\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 1024px) {
    .lg\\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
    .lg\\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
    .lg\\:col-span-2 { grid-column: span 2; }
}
'''
        
        with open(self.output_dir / "styles.css", 'w', encoding='utf-8') as f:
            f.write(fallback_css)
        
        print("✅ Generated fallback CSS")

    def _generate_javascript(self):
        """Generate the main JavaScript file with FIXED button event handling"""
        
        js_content = '''// FIXED YoGuido JavaScript Runtime with Working Button Events
console.log("🚀 YoGuido JavaScript is loading...");

class YoGuidoApp {
    constructor() {
        console.log("🏗️ YoGuidoApp constructor called");
        this.state = {};
        this.eventHandlers = {};
        this.componentTree = [];
        this.buttonHandlers = new Map();
    }
    
    async init() {
        console.log("🎬 YoGuidoApp.init() called");
        
        // Hide loading, show app
        const loading = document.getElementById('loading');
        const appContent = document.getElementById('app-content');
        
        if (loading) {
            loading.style.display = 'none';
            console.log("✅ Hidden loading div");
        }
        
        if (appContent) {
            appContent.style.display = 'block';
            console.log("✅ Showed app content div");
        } else {
            console.log("❌ Could not find app-content div");
            return;
        }
        
        // Initial render
        console.log("🎨 Calling initial render...");
        await this.render();
    }
    
    async render() {
        try {
            console.log("🎨 Starting render...");
            
            const response = await fetch('/api/render', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            console.log("📡 /api/render response status:", response.status);
            
            if (!response.ok) {
                throw new Error(`Render failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log("📊 Render response data:", data);
            
            this.componentTree = data.component_tree || [];
            console.log("🌳 Component tree:", this.componentTree);
            
            this.renderComponentTree();
            
        } catch (error) {
            console.error("❌ Render error:", error);
            this.showError(error.message);
        }
    }
    
    renderComponentTree() {
        console.log("🖼️ Rendering component tree with", this.componentTree.length, "components");
        
        const container = document.getElementById('app-content');
        if (!container) {
            console.error("❌ Could not find app-content container!");
            return;
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Clear existing button handlers
        this.buttonHandlers.clear();
        
        // Render each component
        this.componentTree.forEach((component, index) => {
            console.log(`🧩 Rendering component ${index}: ${component.type}`);
            try {
                const element = this.createElement(component);
                container.appendChild(element);
            } catch (error) {
                console.error(`❌ Failed to render component ${index}:`, error);
            }
        });
        
        console.log("✅ Component tree rendering complete");
        console.log(`🎯 Registered ${this.buttonHandlers.size} button handlers`);
    }
    
    createElement(componentData) {
        const { type, id, props, handlers } = componentData;
        
        switch (type) {
            case 'title':
                return this.createTitle(id, props);
            case 'text':
                return this.createText(id, props);
            case 'button':
                return this.createButton(id, props, handlers);
            case 'container':
                return this.createContainer(id, props, componentData.children || []);
            case 'input_text':
                return this.createInputText(id, props);
            case 'select':
                return this.createSelect(id, props);
            case 'checkbox':
                return this.createCheckbox(id, props);
            case 'table':
                return this.createTable(id, props);
            default:
                console.warn(`Unknown component type: ${type}`);
                const div = document.createElement('div');
                div.textContent = `Unknown component: ${type}`;
                return div;
        }
    }
    
    createTitle(id, props) {
        const level = props.level || 1;
        const element = document.createElement(`h${level}`);
        element.id = id;
        element.textContent = props.text || '';
        element.className = props.class_name || 'text-2xl font-bold text-gray-900 mb-4';
        return element;
    }
    
    createText(id, props) {
        const element = document.createElement('p');
        element.id = id;
        element.textContent = props.content || '';
        element.className = props.class_name || 'text-gray-600 mb-2';
        return element;
    }
    
    createButton(id, props, handlers) {
        console.log(`🔘 Creating button: ${id}`, props, handlers);
        
        const element = document.createElement('button');
        element.id = id;
        element.textContent = props.label || 'Button';
        element.className = props.class_name || 'bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors';
        
        // CRITICAL FIX: Add click handler if it exists
        if (handlers && handlers.click) {
            const handlerId = handlers.click;
            console.log(`🎯 Registering click handler for button ${id}: ${handlerId}`);
            
            // Store handler reference
            this.buttonHandlers.set(id, handlerId);
            
            // Add click event listener
            element.addEventListener('click', async (event) => {
                console.log(`🔥 Button clicked: ${id} -> ${handlerId}`);
                event.preventDefault();
                
                try {
                    // Send event to backend
                    await this.sendButtonClick(id, handlerId);
                } catch (error) {
                    console.error(`❌ Button click failed for ${id}:`, error);
                }
            });
            
            console.log(`✅ Click handler registered for button ${id}`);
        } else {
            console.log(`⚠️ No click handler for button ${id}`);
        }
        
        return element;
    }
    
    async sendButtonClick(buttonId, handlerId) {
        console.log(`📡 Sending button click: ${buttonId} -> ${handlerId}`);
        
        try {
            const response = await fetch('/hcc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: 'click',
                    element_id: buttonId,
                    handler_id: handlerId,
                    timestamp: new Date().toISOString()
                })
            });
            
            console.log(`📡 Button click response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`📊 Button click response:`, data);
            
            // If server returns updated component tree, re-render
            if (data.component_tree) {
                console.log("🔄 Re-rendering after button click...");
                this.componentTree = data.component_tree;
                this.renderComponentTree();
            }
            
            // Show any alerts or notifications
            if (data.status === 'success') {
                console.log("✅ Button click processed successfully");
            }
            
        } catch (error) {
            console.error(`❌ Failed to send button click:`, error);
            this.showError(`Button click failed: ${error.message}`);
        }
    }
    
    createContainer(id, props, children) {
        const element = document.createElement('div');
        element.id = id;
        element.className = props.class_name || 'p-6';
        
        children.forEach(child => {
            element.appendChild(this.createElement(child));
        });
        
        return element;
    }
    
    createInputText(id, props) {
        const element = document.createElement('input');
        element.type = 'text';
        element.id = id;
        element.placeholder = props.placeholder || '';
        element.value = props.value || '';
        element.className = props.class_name || 'border border-gray-300 rounded px-3 py-2';
        
        // Add input change handler
        element.addEventListener('input', async (event) => {
            await this.sendInputChange(id, event.target.value);
        });
        
        return element;
    }
    
    async sendInputChange(inputId, value) {
        try {
            const response = await fetch('/hcc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: 'input',
                    element_id: inputId,
                    value: value,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`📝 Input change processed:`, data);
            }
        } catch (error) {
            console.error(`❌ Failed to send input change:`, error);
        }
    }
    
    createSelect(id, props) {
        const element = document.createElement('select');
        element.id = id;
        element.className = props.class_name || 'border border-gray-300 rounded px-3 py-2';
        
        (props.options || []).forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value || option;
            optionElement.textContent = option.label || option;
            if (props.value === optionElement.value) {
                optionElement.selected = true;
            }
            element.appendChild(optionElement);
        });
        
        // Add change handler
        element.addEventListener('change', async (event) => {
            await this.sendInputChange(id, event.target.value);
        });
        
        return element;
    }
    
    createCheckbox(id, props) {
        const wrapper = document.createElement('div');
        wrapper.className = props.class_name || 'flex items-center space-x-2';
        
        const element = document.createElement('input');
        element.type = 'checkbox';
        element.id = id;
        element.checked = props.checked || false;
        element.className = 'rounded';
        
        const label = document.createElement('label');
        label.htmlFor = id;
        label.textContent = props.label || '';
        label.className = 'text-sm font-medium text-gray-700';
        
        wrapper.appendChild(element);
        wrapper.appendChild(label);
        
        // Add change handler
        element.addEventListener('change', async (event) => {
            await this.sendInputChange(id, event.target.checked);
        });
        
        return wrapper;
    }
    
    createTable(id, props) {
        const wrapper = document.createElement('div');
        wrapper.className = 'overflow-x-auto';
        
        const table = document.createElement('table');
        table.id = id;
        table.className = props.class_name || 'w-full divide-y divide-gray-200';
        
        // Create header
        if (props.columns && props.columns.length > 0) {
            const thead = document.createElement('thead');
            thead.className = 'bg-gray-50';
            
            const headerRow = document.createElement('tr');
            props.columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column.charAt(0).toUpperCase() + column.slice(1);
                th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // Create body
        const tbody = document.createElement('tbody');
        tbody.className = 'bg-white divide-y divide-gray-200';
        
        (props.data || []).forEach((row, rowIndex) => {
            const tr = document.createElement('tr');
            tr.className = rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            
            (props.columns || Object.keys(row)).forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column] || '';
                td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        wrapper.appendChild(table);
        
        return wrapper;
    }
    
    showError(message) {
        console.error("🚨 Showing error:", message);
        const errorDisplay = document.getElementById('error-display');
        const errorMessage = document.getElementById('error-message');
        
        if (errorDisplay && errorMessage) {
            errorMessage.textContent = message;
            errorDisplay.classList.remove('hidden');
        }
    }
    
    // Debug method to inspect current state
    debugState() {
        console.log("🔍 DEBUG STATE:");
        console.log("   Component tree:", this.componentTree);
        console.log("   Button handlers:", this.buttonHandlers);
        console.log("   State:", this.state);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("📄 DOM loaded, initializing YoGuido app...");
    const app = new YoGuidoApp();
    app.init();
    
    // Make app globally available for debugging
    window.yoguidoApp = app;
    console.log("🌍 App available globally as window.yoguidoApp");
    
    // Add debug helper
    window.debugYoGuido = () => {
        app.debugState();
    };
    console.log("🔍 Debug helper available as window.debugYoGuido()");
});

console.log("✅ YoGuido JavaScript loaded successfully");'''
        
        with open(self.output_dir / "main.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print("📄 Generated main.js with FIXED button event handling")