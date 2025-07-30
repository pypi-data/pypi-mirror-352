"""
Fixed FastAPI server for YoGuido framework with router support
Replace your yoguido/server/app.py with this version
"""

import json
import uuid
from typing import Any, Callable, Dict, List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path

class EventRegistry:
    """Registry for event handlers"""
    
    handlers: Dict[str, Callable] = {}
    
    @classmethod
    def register_handler(cls, handler_id: str, callback: Callable):
        """Register an event handler"""
        cls.handlers[handler_id] = callback
        print(f"🎯 Registered handler: {handler_id}")
    
    @classmethod
    def execute_handler(cls, handler_id: str, *args, **kwargs) -> Any:
        """Execute an event handler"""
        if handler_id in cls.handlers:
            try:
                return cls.handlers[handler_id](*args, **kwargs)
            except Exception as e:
                print(f"❌ Handler {handler_id} failed: {e}")
                raise
        else:
            print(f"⚠️ Handler not found: {handler_id}")

class YoGuidoServer:
    """FastAPI server for YoGuido runtime with router support"""
    
    def __init__(self, build_dir: str = "./yoguido_build"):
        self.app = FastAPI(title="YoGuido Runtime")
        self.build_dir = Path(build_dir)
        self.setup_routes()
        self.setup_static_files()
    
    def setup_static_files(self):
        """Setup static file serving"""
        if self.build_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(self.build_dir)), name="static")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def serve_app():
            """Serve the main HTML file"""
            html_file = self.build_dir / "index.html"
            if html_file.exists():
                return html_file.read_text(encoding='utf-8')
            else:
                return """
                <html>
                    <body>
                        <h1>YoGuido App</h1>
                        <p>App not compiled yet. Run app.compile() first.</p>
                    </body>
                </html>
                """
        
        @self.app.get("/styles.css")
        async def serve_css():
            """Serve the CSS file"""
            css_file = self.build_dir / "styles.css"
            if css_file.exists():
                return Response(
                    content=css_file.read_text(encoding='utf-8'),
                    media_type="text/css"
                )
            return Response(
                content="/* CSS file not found */",
                media_type="text/css"
            )
        
        @self.app.get("/main.js")
        async def serve_js():
            """Serve the JavaScript file"""
            js_file = self.build_dir / "main.js"
            if js_file.exists():
                return Response(
                    content=js_file.read_text(encoding='utf-8'),
                    media_type="application/javascript"
                )
            return Response(
                content="// JavaScript file not found",
                media_type="application/javascript"
            )
        
        @self.app.post("/hcc")
        async def handle_component_communication(request: Request):
            """Handle component state changes from frontend"""
            try:
                data = await request.json()
                print(f"📡 HCC Request: {data}")
                
                event_type = data.get('event_type')
                handler_id = data.get('handler_id')
                
                response_data = {
                    "status": "success",
                    "timestamp": "2025-05-29T10:30:00Z"
                }
                
                # Handle button clicks
                if event_type == "click" and handler_id:
                    print(f"🔥 Executing handler: {handler_id}")
                    try:
                        result = EventRegistry.execute_handler(handler_id)
                        print(f"✅ Handler executed successfully: {result}")
                        response_data["handler_result"] = result
                    except Exception as e:
                        print(f"❌ Handler execution failed: {e}")
                        response_data["status"] = "error"
                        response_data["error"] = str(e)
                
                # Handle input changes
                elif event_type == "input":
                    field_name = data.get('field_name')
                    new_value = data.get('value')
                    print(f"📝 Input change: {field_name} = {new_value}")
                    response_data["field_updated"] = field_name
                    response_data["new_value"] = new_value
                
                # CRITICAL: Re-execute components after state changes
                print("🔄 Re-executing components after state change...")
                
                # Get updated component tree
                updated_tree = self._execute_app_components()
                
                response_data["component_tree"] = updated_tree
                
                return JSONResponse(content=response_data)
                
            except Exception as e:
                print(f"❌ HCC endpoint error: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/state")
        async def get_current_state():
            """Get current application state"""
            from ..core.state import state_manager
            
            return JSONResponse(content={
                "current_state": state_manager.get_current_state_snapshot(),
                "change_history": state_manager.get_change_history()
            })
        
        @self.app.post("/api/render")
        async def trigger_render():
            """Trigger a component re-render - FIXED for router support"""
            try:
                print("🎨 /api/render called - starting component execution")
                
                # Get updated component tree
                component_tree = self._execute_app_components()
                
                print(f"🌳 Component tree after execution: {len(component_tree)} components")
                
                # Debug: Print first component if exists
                if component_tree:
                    print(f"🔍 First component: {component_tree[0]}")
                else:
                    print("⚠️ Component tree is empty after execution!")
                
                return JSONResponse(content={
                    "status": "success",
                    "component_tree": component_tree
                })
                
            except Exception as e:
                print(f"❌ /api/render failed: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "framework": "yoguido-vanilla"}
    
    def _execute_app_components(self) -> List[Dict]:
        """
        FIXED: Execute app components with router support
        This method handles both traditional components and router-based apps
        """
        from ..ui.basic_components import _clear_component_tree, _get_component_tree
        
        # Clear previous component tree
        _clear_component_tree()
        print("🧹 Cleared component tree")
        
        # Try to get the current app to determine if router is enabled
        try:
            from ..core.runtime import get_current_app
            current_app = get_current_app()
            
            if current_app and current_app._router_enabled:
                print("🛣️ Router enabled - executing router component")
                try:
                    from ..pages.routing import router_component
                    router_component()
                    print("✅ Router component executed successfully")
                except Exception as e:
                    print(f"❌ Router component execution failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("🎨 Router not enabled - executing traditional components")
                # Execute traditional components
                from ..core.decorators import _registry
                components = _registry.get_all_components()
                print(f"📋 Found {len(components)} registered components")
                
                for comp_id, metadata in components.items():
                    try:
                        print(f"🎨 Executing component: {comp_id}")
                        metadata.function()
                        print(f"✅ Component {comp_id} executed successfully")
                    except Exception as e:
                        print(f"❌ Component {comp_id} execution failed: {e}")
                        import traceback
                        traceback.print_exc()
        
        except Exception as e:
            print(f"❌ App component execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Get the component tree AFTER execution
        component_tree = _get_component_tree()
        print(f"🌳 Final component tree: {len(component_tree)} components")
        
        return component_tree
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the server"""
        import uvicorn
        print(f"🚀 Starting YoGuido server at http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)