bl_info = {
    "name": "Simple Chat Launcher",
    "description": "One button to launch chat_with_portable_python.bat",
    "author": "Simple Fix",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Sidebar > Simple Chat",
    "category": "3D View",
}

import bpy
import subprocess
import os
from pathlib import Path
import time

# Global monitoring functions
def get_niout_directory():
    """Find the niout directory"""
    current = Path(__file__).parent
    
    for parent in [current] + list(current.parents):
        if parent.name.lower() == 'odin_grab':
            niout_dir = parent / 'a_astitnet' / 'niout'
            if niout_dir.exists():
                return niout_dir
        elif parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
            niout_dir = parent / 'niout'
            if niout_dir.exists():
                return niout_dir
    
    # Fallback
    return Path('F:/odin_grab/a_astitnet/niout')

def get_highest_response_number(niout_dir):
    """Get the highest numbered response file"""
    max_num = 0
    latest_file = None
    
    if niout_dir.exists():
        for file in niout_dir.glob('response_*.txt'):
            try:
                num_str = file.stem.replace('response_', '')
                num = int(num_str)
                if num > max_num:
                    max_num = num
                    latest_file = file
            except ValueError:
                continue
    
    return max_num, latest_file

def auto_refresh_monitor():
    """Monitor for new response files and auto-load them"""
    try:
        import bpy
        props = bpy.context.window_manager.simple_chat_props
        
        # Check if monitoring is enabled
        if not props.auto_refresh_enabled or not props.is_monitoring:
            props.monitoring_status = "Auto-refresh disabled"
            return None  # Stop timer
        
        niout_dir = get_niout_directory()
        current_max, latest_file = get_highest_response_number(niout_dir)
        
        # Check if we found a new file (higher number than we've seen)
        if current_max > props.last_known_max_number:
            # New file detected! Load it automatically
            props.last_known_max_number = current_max
            
            if latest_file and latest_file.exists():
                try:
                    # Load the new response
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    if content:
                        props.current_response = content
                        props.selected_response_file = latest_file.name
                        props.monitoring_status = f"📄 Auto-loaded {latest_file.name}"
                        
                        # Force UI update
                        for area in bpy.context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                        
                        print(f"Auto-Refresh: Loaded {latest_file.name}")
                        # Return 1 (new file found and loaded)
                        return 2.0  # Continue monitoring every 2 seconds
                    
                except Exception as e:
                    props.monitoring_status = f"Error loading {latest_file.name}: {e}"
                    print(f"Auto-Refresh Error: {e}")
        
        # Return 0 (no new files, continue watching)
        props.monitoring_status = f"👁️ Watching... (last: response_{current_max}.txt)" if current_max > 0 else "👁️ Watching..."
        return 2.0  # Continue monitoring every 2 seconds
        
    except Exception as e:
        print(f"Auto-Refresh Monitor Error: {e}")
        return None  # Stop on error

# Simple message storage
class SimpleChatProps(bpy.types.PropertyGroup):
    message: bpy.props.StringProperty(
        name="Message",
        description="Your message to AI",
        default="Hello, how are you?",
        maxlen=1000
    )
    
    # Response display - Increased maxlen for full responses
    current_response: bpy.props.StringProperty(
        name="Current Response",
        description="Currently displayed AI response",
        default="",
        maxlen=20000  # Much larger to show full responses
    )
    
    selected_response_file: bpy.props.StringProperty(
        name="Response File",
        description="Selected response file to display",
        default="response.txt"
    )
    
    # Auto-refresh system
    auto_refresh_enabled: bpy.props.BoolProperty(
        name="Auto Refresh",
        description="Automatically load new responses when they appear",
        default=True
    )
    
    # Internal monitoring state
    is_monitoring: bpy.props.BoolProperty(
        name="Is Monitoring",
        description="Currently monitoring for new responses",
        default=False
    )
    
    last_known_max_number: bpy.props.IntProperty(
        name="Last Known Max Number",
        description="Highest response number we've seen",
        default=0
    )
    
    monitoring_status: bpy.props.StringProperty(
        name="Monitoring Status",
        description="Current monitoring status message",
        default=""
    )

class SIMPLECHAT_OT_LaunchChat(bpy.types.Operator):
    """Launch chat_with_portable_python.bat"""
    bl_idname = "simplechat.launch_chat"
    bl_label = "Launch Chat with Portable Python"
    bl_description = "Start the chat_with_portable_python.bat file"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            # Get the message
            props = context.window_manager.simple_chat_props
            message = props.message.strip()
            
            if not message:
                self.report({'WARNING'}, "Please enter a message")
                return {'CANCELLED'}
            
            print(f"Simple Chat: Sending message: {message}")
            
            # Find the batch file
            current = Path(__file__).parent
            
            # Search for odin_grab structure
            batch_path = None
            for parent in [current] + list(current.parents):
                # Look for odin_grab folder
                if parent.name.lower() == 'odin_grab':
                    batch_path = parent / 'a_astitnet' / 'chat_with_portable_python.bat'
                    if batch_path.exists():
                        break
                # Check if we're in a_astitnet under odin_grab
                elif parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                    batch_path = parent / 'chat_with_portable_python.bat'
                    if batch_path.exists():
                        break
                # Check for odin_grab subdirectory
                elif (parent / 'odin_grab').exists():
                    batch_path = parent / 'odin_grab' / 'a_astitnet' / 'chat_with_portable_python.bat'
                    if batch_path.exists():
                        break
            
            # Fallback paths
            if not batch_path or not batch_path.exists():
                fallback_paths = [
                    Path('F:/odin_grab/a_astitnet/chat_with_portable_python.bat'),
                    Path.home() / 'Desktop' / 'Odin Grab' / 'a_astitnet' / 'chat_with_portable_python.bat',
                    Path('C:/File/Desktop/Odin Grab/a_astitnet/chat_with_portable_python.bat')
                ]
                for fallback in fallback_paths:
                    if fallback.exists():
                        batch_path = fallback
                        break
            
            if not batch_path or not batch_path.exists():
                self.report({'ERROR'}, "Could not find chat_with_portable_python.bat")
                print("Simple Chat: Batch file not found!")
                return {'CANCELLED'}
            
            print(f"Simple Chat: Found batch file: {batch_path}")
            
            # Write the message directly to input.txt (the working way)
            niout_dir = batch_path.parent / 'niout'
            niout_dir.mkdir(exist_ok=True)
            
            input_file = niout_dir / 'input.txt'
            model_config = niout_dir / 'model_config.txt'
            
            # Write input message
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(message)
            print(f"Simple Chat: Wrote message to {input_file}")
            
            # Write model config
            with open(model_config, 'w', encoding='utf-8') as f:
                f.write('qwen3:8b')
            print(f"Simple Chat: Set model to qwen3:8b")
            
            # Launch the simple batch file (no arguments needed)
            cmd_str = f'"{batch_path}"'
            print(f"Simple Chat: Running command: {cmd_str}")
            
            process = subprocess.Popen(
                cmd_str,
                cwd=str(batch_path.parent),
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print(f"Simple Chat: Launched batch file with PID: {process.pid}")
            
            # Clear the message after sending
            props.message = ""
            
            # Start auto-monitoring if enabled
            if props.auto_refresh_enabled:
                # Set up monitoring state
                niout_dir = get_niout_directory()
                current_max, _ = get_highest_response_number(niout_dir)
                props.last_known_max_number = current_max
                props.is_monitoring = True
                props.monitoring_status = "👁️ Starting to watch for response..."
                
                # Start the monitoring timer
                bpy.app.timers.register(auto_refresh_monitor, first_interval=3.0)
                print("Auto-Refresh: Started monitoring for new responses")
                
                self.report({'INFO'}, "Message sent! Watching for response...")
            else:
                self.report({'INFO'}, "Message sent! Check console window for AI processing.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to launch chat: {e}")
            print(f"Simple Chat Error: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class SIMPLECHAT_OT_LoadLatestResponse(bpy.types.Operator):
    """Load the latest response and show all available files"""
    bl_idname = "simplechat.load_latest_response"
    bl_label = "Load Latest Response"
    bl_description = "Load the latest AI response and show all available files"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.simple_chat_props
        
        try:
            # Find the niout directory
            current = Path(__file__).parent
            niout_dir = None
            
            for parent in [current] + list(current.parents):
                if parent.name.lower() == 'odin_grab':
                    niout_dir = parent / 'a_astitnet' / 'niout'
                    if niout_dir.exists():
                        break
                elif parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                    niout_dir = parent / 'niout'
                    if niout_dir.exists():
                        break
            
            if not niout_dir:
                niout_dir = Path('F:/odin_grab/a_astitnet/niout')
            
            # Find all response files and get the latest
            response_files = []
            max_num = 0
            latest_file = None
            
            if niout_dir.exists():
                # Check for regular response.txt
                if (niout_dir / 'response.txt').exists():
                    response_files.append('response.txt')
                
                # Find versioned files
                versioned = []
                for file in niout_dir.glob('response_*.txt'):
                    try:
                        num_str = file.stem.replace('response_', '')
                        num = int(num_str)
                        versioned.append((num, file.name))
                        # Track the highest number
                        if num > max_num:
                            max_num = num
                            latest_file = file
                    except ValueError:
                        continue
                
                # Sort versioned files by number and add to list
                versioned.sort(key=lambda x: x[0])
                response_files.extend([f[1] for f in versioned])
            
            # If no numbered files found, use regular response.txt
            if latest_file is None and response_files:
                regular_response = niout_dir / 'response.txt'
                if regular_response.exists():
                    latest_file = regular_response
            
            # Load the latest file
            if latest_file and latest_file.exists():
                # Update the selected file name
                props.selected_response_file = latest_file.name
                
                # Load the content - FIX: Increase maxlen to show full response
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    # Store full content (increase property maxlen if needed)
                    props.current_response = content
                    
                    # Report success with file list
                    if response_files:
                        files_str = ', '.join(response_files[-5:])  # Show last 5 files
                        if len(response_files) > 5:
                            files_str = "..." + files_str
                        self.report({'INFO'}, f"Loaded {latest_file.name} | Available: {files_str}")
                    else:
                        self.report({'INFO'}, f"Loaded {latest_file.name}")
                else:
                    props.current_response = "Response file is empty"
            else:
                props.current_response = "No response files found"
                self.report({'WARNING'}, "No response files found")
                
        except Exception as e:
            props.current_response = f"Error: {e}"
            self.report({'ERROR'}, f"Failed to load response: {e}")
        
        return {'FINISHED'}

class SIMPLECHAT_OT_ToggleMonitoring(bpy.types.Operator):
    """Toggle automatic response monitoring"""
    bl_idname = "simplechat.toggle_monitoring"
    bl_label = "Toggle Auto-Refresh"
    bl_description = "Turn automatic response monitoring on/off"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.simple_chat_props
        
        if props.is_monitoring:
            # Stop monitoring
            props.is_monitoring = False
            props.monitoring_status = "Auto-refresh stopped"
            self.report({'INFO'}, "Auto-refresh monitoring stopped")
        else:
            # Start monitoring
            if props.auto_refresh_enabled:
                niout_dir = get_niout_directory()
                current_max, _ = get_highest_response_number(niout_dir)
                props.last_known_max_number = current_max
                props.is_monitoring = True
                props.monitoring_status = "👁️ Auto-refresh started"
                
                bpy.app.timers.register(auto_refresh_monitor, first_interval=1.0)
                self.report({'INFO'}, "Auto-refresh monitoring started")
            else:
                self.report({'WARNING'}, "Auto-refresh is disabled. Enable it first.")
        
        return {'FINISHED'}

class SIMPLECHAT_PT_Panel(bpy.types.Panel):
    """Simple Chat Panel"""
    bl_label = "Simple Chat"
    bl_idname = "SIMPLECHAT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Simple Chat"
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.simple_chat_props
        
        # Message input section
        box = layout.box()
        box.label(text="Send Message:", icon='OUTLINER_DATA_FONT')
        box.prop(props, "message", text="")
        
        # Launch button
        row = box.row()
        row.scale_y = 1.5
        row.operator("simplechat.launch_chat", text="🚀 Launch Chat", icon='CONSOLE')
        
        layout.separator()
        
        # Response section
        box = layout.box()
        box.label(text="AI Responses:", icon='FILE_TEXT')
        
        # Auto-refresh controls
        row = box.row(align=True)
        row.prop(props, "auto_refresh_enabled", text="Auto-Refresh")
        if props.is_monitoring:
            row.operator("simplechat.toggle_monitoring", text="Stop", icon='PAUSE')
        else:
            row.operator("simplechat.toggle_monitoring", text="Start", icon='PLAY')
        
        # Monitoring status
        if props.monitoring_status:
            status_box = box.box()
            status_box.scale_y = 0.8
            status_box.label(text=props.monitoring_status, icon='INFO')
        
        # Simple file selector (shows what's loaded)
        row = box.row()
        row.prop(props, "selected_response_file", text="Current")
        
        # Load latest button (manual override)
        row = box.row()
        row.scale_y = 1.2
        row.operator("simplechat.load_latest_response", text="⭐ Load Latest (Manual)", icon='SORT_DESC')
        
        # Response display area - Show more lines and longer lines
        if props.current_response:
            box.separator()
            box.label(text="Response:", icon='WORDWRAP_ON')
            
            # Create a text area for the response (multi-line)
            col = box.column(align=True)
            
            # Split response into lines and display MORE lines with LONGER text
            lines = props.current_response.split('\n')
            for i, line in enumerate(lines[:20]):  # Show 20 lines instead of 10
                if line.strip() or i == 0:  # Show empty lines in the middle but not at start
                    # Show longer lines (120 chars instead of 80)
                    if len(line) > 120:
                        col.label(text=line[:120] + "...")
                    else:
                        col.label(text=line)
            
            if len(lines) > 20:
                box.label(text=f"... ({len(lines)-20} more lines - full text in file)", icon='INFO')

def register():
    bpy.utils.register_class(SimpleChatProps)
    bpy.utils.register_class(SIMPLECHAT_OT_LaunchChat)
    bpy.utils.register_class(SIMPLECHAT_OT_LoadLatestResponse)
    bpy.utils.register_class(SIMPLECHAT_OT_ToggleMonitoring)
    bpy.utils.register_class(SIMPLECHAT_PT_Panel)
    bpy.types.WindowManager.simple_chat_props = bpy.props.PointerProperty(type=SimpleChatProps)
    print("Simple Chat Launcher registered")

def unregister():
    del bpy.types.WindowManager.simple_chat_props
    bpy.utils.unregister_class(SIMPLECHAT_PT_Panel)
    bpy.utils.unregister_class(SIMPLECHAT_OT_ToggleMonitoring)
    bpy.utils.unregister_class(SIMPLECHAT_OT_LoadLatestResponse)
    bpy.utils.unregister_class(SIMPLECHAT_OT_LaunchChat)
    bpy.utils.unregister_class(SimpleChatProps)
    print("Simple Chat Launcher unregistered")

if __name__ == "__main__":
    register()
