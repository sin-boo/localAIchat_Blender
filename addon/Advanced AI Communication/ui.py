import bpy

def draw_text_multiline(layout, text, width=50):
    """Draw text with word wrapping (from original ai_chat)"""
    if not text:
        return
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > width and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Display lines using dynamic height from Simple Chat
    props = bpy.context.window_manager.advanced_ai_props
    max_lines = getattr(props, 'panel_height', 15)  # Use panel height slider
    
    for line in lines[:max_lines]:
        layout.label(text=line)
    
    if len(lines) > max_lines:
        layout.label(text=f"... ({len(lines) - max_lines} more lines - use Copy to get full text)")

class ADVANCEDAI_PT_MainPanel(bpy.types.Panel):
    """Main Advanced AI Panel - Enhanced version of ai_chat"""
    bl_label = "Advanced AI Communication"
    bl_idname = "ADVANCEDAI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Advanced AI"
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.advanced_ai_props
        
        # === TOP CONTROLS (Panel Height & Settings) from Simple Chat ===
        top_row = layout.row(align=True)
        top_row.scale_y = 0.8
        top_row.prop(props, "panel_height", text="Panel Height", slider=True)
        top_row.operator("advanced_ai.save_settings", text="💾", icon='FILE_TICK')
        
        layout.separator(factor=0.5)
        
        # === OLLAMA CONTROL SECTION ===
        ollama_box = layout.box()
        
        # Model directory display (extended width)
        dir_row = ollama_box.row(align=True)
        dir_row.scale_y = 0.8
        # Extended model directory path display
        dir_col = dir_row.column(align=True)
        dir_col.label(text="Model Directory:", icon='FOLDER_REDIRECT')
        dir_col.label(text=props.model_directory_path)
        
        # Header with current model
        header_row = ollama_box.row(align=True)
        header_row.label(text=f"AI Model: {props.current_model_display}", icon='PREFERENCES')
        
        # Ollama status and controls
        status_row = ollama_box.row(align=True)
        status_row.label(text=props.ollama_status)
        
        controls_row = ollama_box.row(align=True)
        controls_row.operator("advanced_ai.start_ollama", text="Launch Ollama App", icon='PLAY')
        controls_row.operator("advanced_ai.stop_ollama", text="Stop App", icon='PAUSE')
        
        layout.separator(factor=0.5)
        
        # === MESSAGE INPUT SECTION (Enhanced from ai_chat) ===
        input_box = layout.box()
        input_box.label(text="Message:", icon='EDITMODE_HLT')
        
        col = input_box.column(align=True)
        col.prop(props, "message", text="")
        
        # Buttons row
        row = col.row(align=True)
        row.operator("advanced_ai.send_message", text="Send", icon='RIGHTARROW_THIN')
        row.operator("advanced_ai.clear_message", text="Clear", icon='X')
        
        # Auto-refresh controls from Simple Chat
        layout.separator(factor=1.0)
        
        # === RESPONSE SECTION (Hybrid of both) ===
        response_box = layout.box()
        
        # Header with monitoring controls
        header_row = response_box.row(align=True)
        if props.waiting_for_response or props.is_monitoring:
            header_row.label(text="🤖 AI Response (processing...):", icon='TIME')
        else:
            header_row.label(text="🤖 AI Response:", icon='TEXT')
        
        # Auto-refresh toggle
        header_row.prop(props, "auto_refresh_enabled", text="Auto", icon='AUTO')
        
        # Controls row
        controls_row = response_box.row(align=True)
        controls_row.scale_y = 0.9
        
        # Monitor toggle
        if props.is_monitoring:
            controls_row.operator("advanced_ai.toggle_monitoring", text="⏸️ Stop", icon='PAUSE')
        else:
            controls_row.operator("advanced_ai.toggle_monitoring", text="▶️ Start", icon='PLAY')
        
        # Manual refresh and copy
        controls_row.operator("advanced_ai.refresh_response", text="🔄", icon='FILE_REFRESH')
        controls_row.operator("advanced_ai.copy_response", text="📋", icon='COPYDOWN')
        controls_row.operator("advanced_ai.clear_responses", text="🗑️", icon='TRASH')
        
        # Load latest and file selector
        file_row = response_box.row(align=True)
        file_row.prop(props, "selected_response_file", text="")
        file_row.operator("advanced_ai.load_latest_response", text="Load Latest", icon='SORT_DESC')
        
        # Monitoring status from Simple Chat
        if props.monitoring_status:
            status_row = response_box.row()
            status_row.scale_y = 0.7
            status_row.label(text=props.monitoring_status, icon='INFO')
        
        # Response display area using multiline function with dynamic height
        response_display = response_box.box()
        response_display.scale_y = 0.8
        
        if props.response:
            # Use the enhanced word-wrapping with dynamic height
            draw_text_multiline(response_display, props.response, width=50)
        else:
            response_display.label(text="No response yet...")

class ADVANCEDAI_PT_SettingsPanel(bpy.types.Panel):
    """Settings Panel - Enhanced from ai_chat with Simple Chat features"""
    bl_label = "Settings"
    bl_idname = "ADVANCEDAI_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Advanced AI"
    bl_parent_id = "ADVANCEDAI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.advanced_ai_props
        
        # File Paths (auto-configured)
        box = layout.box()
        box.label(text="📁 File Paths (Auto-configured):", icon='FOLDER_REDIRECT')
        
        col = box.column(align=True)
        col.scale_y = 0.8
        col.prop(props, "base_path", text="Base")
        col.prop(props, "input_path", text="Input")
        col.prop(props, "output_path", text="Output")
        col.prop(props, "ollama_script_path", text="Script")
        
        # Auto-refresh settings from Simple Chat
        layout.separator()
        box = layout.box()
        box.label(text="🔄 Auto-Refresh Settings:", icon='AUTO')
        
        col = box.column(align=True)
        col.prop(props, "auto_refresh_enabled", text="Enable Auto-Refresh")
        col.prop(props, "use_versioned_responses", text="Versioned responses (_1, _2, ...)")
        
        if props.is_monitoring:
            col.label(text="Status: Monitoring active", icon='CHECKMARK')
        else:
            col.label(text="Status: Monitoring stopped", icon='X')
        
        col.label(text=f"Last seen index: {props.last_known_max_number}")
        
        # Ollama Configuration
        layout.separator()
        box = layout.box()
        box.label(text="Ollama Configuration:", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.prop(props, "ollama_executable_path", text="Ollama Exe")
        col.prop(props, "model_directory_path", text="Model Dir")
        
        # Model Management
        layout.separator()
        box = layout.box()
        box.label(text="Model Management:", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.prop(props, "selected_model", text="Model Name")
        
        # Browse models in directory
        col.separator()
        browse_row = col.row(align=True)
        browse_row.operator("advanced_ai.browse_model_directory", text="Browse Models", icon='FOLDER_REDIRECT')
        
        # Extended file path browser for specific model files
        col.separator()
        col.label(text="Browse to specific model file:", icon='FILE')
        
        # Extended file path display (full width)
        file_col = col.column(align=True)
        file_col.scale_y = 1.2  # Make it taller
        file_col.prop(props, "model_file_path", text="")
        
        # Browse model button
        browse_file_row = col.row(align=True)
        browse_file_row.operator("advanced_ai.browse_model", text="Extract Model Name from File", icon='IMPORT')
        
        # Model control buttons
        col.separator()
        model_control_row = col.row(align=True)
        model_control_row.scale_y = 1.2
        model_control_row.operator("advanced_ai.start_current_model", text="Start Current Model", icon='PLAY')
        model_control_row.operator("advanced_ai.close_all_models", text="Close All Models", icon='X')
        
        # Current model display info
        col.separator()
        info_row = col.row(align=True)
        info_row.scale_y = 0.8
        info_row.label(text=f"Current: {props.current_model_display}", icon='PREFERENCES')
        
        col.prop(props, "auto_run_ollama", text="Auto-run script")
        
        # UI Settings from Simple Chat
        layout.separator()
        box = layout.box()
        box.label(text="🎨 Display Settings:", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.prop(props, "panel_height", text="Response Lines", slider=True)
        col.label(text=f"Currently showing: {props.panel_height} lines max")
        
        row = col.row(align=True)
        row.operator("advanced_ai.save_settings", text="Save Settings", icon='FILE_TICK')

class ADVANCEDAI_PT_HelpPanel(bpy.types.Panel):
    """Help Panel - Enhanced from ai_chat"""
    bl_label = "How to Use"
    bl_idname = "ADVANCEDAI_PT_help_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Advanced AI"
    bl_parent_id = "ADVANCEDAI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 0.8
        
        col.label(text="📝 Basic Usage:")
        col.label(text="1. Type your message")
        col.label(text="2. Click 'Send'")
        col.label(text="3. Response appears automatically")
        col.label(text="4. Use 'Copy' to copy full text")
        
        col.separator()
        col.label(text="🚀 Advanced Features:")
        col.label(text="• Auto-refresh monitoring")
        col.label(text="• Versioned response files")
        col.label(text="• Dynamic panel height control")
        col.label(text="• One-click copy to clipboard")
        col.label(text="• Persistent settings")
        
        col.separator()
        col.label(text="⚡ From Simple Chat:")
        col.label(text="• Robust path detection")
        col.label(text="• Background monitoring")
        col.label(text="• Better file handling")
        col.label(text="• Enhanced UI controls")

class ADVANCEDAI_PT_MemoryPanel(bpy.types.Panel):
    """Memory Panel - New conversation memory system"""
    bl_label = "Memory"
    bl_idname = "ADVANCEDAI_PT_memory_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Advanced AI"
    bl_parent_id = "ADVANCEDAI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.advanced_ai_props
        
        # Memory Enable/Disable
        box = layout.box()
        header_row = box.row(align=True)
        header_row.prop(props, "memory_enabled", text="Enable Memory", icon='MEMORY' if props.memory_enabled else 'ORPHAN_DATA')
        
        if props.memory_enabled:
            header_row.label(text="🧠 ON", icon='CHECKMARK')
        else:
            header_row.label(text="OFF", icon='X')
        
        # Memory settings (only show when enabled)
        if props.memory_enabled:
            col = box.column(align=True)
            col.separator()
            col.label(text="Token Limit:", icon='SETTINGS')
            col.prop(props, "memory_token_limit", text="")
            
            # Memory info
            col.separator()
            col.scale_y = 0.8
            
            if props.memory_token_limit == '4000':
                col.label(text="- Medium memory (~1,000 words)")
            elif props.memory_token_limit == '8000':
                col.label(text="- Large memory (~2,000 words)")
            elif props.memory_token_limit == '16000':
                col.label(text="- Very large memory (~4,000 words)")
                col.label(text="- RECOMMENDED for Blender work", icon='CHECKMARK')
            elif props.memory_token_limit == '32000':
                col.label(text="- Huge memory (~8,000 words)")
                col.label(text="- HIGH PRIORITY mode", icon='ERROR')
            elif props.memory_token_limit == '200000':
                col.label(text="- Maximum memory (~50,000 words)")
                col.label(text="- ULTRA PRIORITY mode", icon='ERROR')
            
            # Memory management buttons
            col.separator()
            
            # Reinforce prompt button
            reinforce_row = col.row()
            reinforce_row.scale_y = 1.1
            reinforce_row.operator("advanced_ai.reinforce_prompt", text="Reinforce AI Role", icon='PINNED')
            
            # Clear memory button
            clear_row = col.row()
            clear_row.scale_y = 1.2
            clear_row.operator("advanced_ai.clear_memory", text="Clear Memory", icon='TRASH')
            
        else:
            # Show help when disabled
            col = box.column(align=True)
            col.scale_y = 0.8
            col.label(text="Memory allows AI to remember")
            col.label(text="previous parts of the conversation")
            col.label(text="Enable to maintain context across messages")

def register():
    bpy.utils.register_class(ADVANCEDAI_PT_MainPanel)
    bpy.utils.register_class(ADVANCEDAI_PT_SettingsPanel)
    bpy.utils.register_class(ADVANCEDAI_PT_MemoryPanel)
    bpy.utils.register_class(ADVANCEDAI_PT_HelpPanel)

def unregister():
    bpy.utils.unregister_class(ADVANCEDAI_PT_HelpPanel)
    bpy.utils.unregister_class(ADVANCEDAI_PT_MemoryPanel)
    bpy.utils.unregister_class(ADVANCEDAI_PT_SettingsPanel)
    bpy.utils.unregister_class(ADVANCEDAI_PT_MainPanel)
