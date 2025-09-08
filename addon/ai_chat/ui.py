import bpy

def draw_text_multiline(layout, text, width=50):
    """Draw text with word wrapping"""
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
    
    # Display lines (limit to prevent UI lag)
    for line in lines[:15]:  # Show max 15 lines
        layout.label(text=line)
    
    if len(lines) > 15:
        layout.label(text="... (text truncated)")

class AICHAT_PT_MainPanel(bpy.types.Panel):
    """Main AI Chat Panel"""
    bl_label = "AI Chat"
    bl_idname = "AICHAT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Chat"
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.ai_chat
        
        # Input Section
        box = layout.box()
        box.label(text="💬 Message:", icon='EDITMODE_HLT')
        
        col = box.column(align=True)
        col.prop(props, "message", text="")
        
        # Buttons
        row = col.row(align=True)
        row.operator("ai_chat.send_message", text="Send", icon='RIGHTARROW_THIN')
        row.operator("ai_chat.clear_message", text="Clear", icon='X')
        
        
        # Auto-run status
        row = col.row(align=True)
        if props.auto_run_ollama:
            row.label(text="✅ Auto-run: ON", icon='CHECKMARK')
        else:
            row.label(text="❌ Auto-run: OFF", icon='X')
        
        # Response Section
        layout.separator()
        box = layout.box()
        
        # Header with waiting indicator
        row = box.row(align=True)
        if props.waiting_for_response:
            row.label(text="🤖 AI Response (processing...):", icon='TIME')
        else:
            row.label(text="🤖 AI Response:", icon='TEXT')
        
        row.operator("ai_chat.refresh_response", text="", icon='FILE_REFRESH')
        row.operator("ai_chat.clear_responses", text="", icon='TRASH')
        
        # Response text
        response_box = box.box()
        response_box.scale_y = 0.8
        
        if props.response:
            draw_text_multiline(response_box, props.response, width=50)
        else:
            response_box.label(text="No response yet...")

class AICHAT_PT_SettingsPanel(bpy.types.Panel):
    """Settings Panel"""
    bl_label = "Settings"
    bl_idname = "AICHAT_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Chat"
    bl_parent_id = "AICHAT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.ai_chat
        
        box = layout.box()
        box.label(text="📁 File Paths:", icon='FOLDER_REDIRECT')
        
        # Base directory first
        col = box.column(align=True)
        col.prop(props, "base_path", text="Base")
        
        col = box.column(align=True)
        col.prop(props, "input_path", text="Input")
        col.prop(props, "output_path", text="Output")
        
        row = col.row(align=True)
        row.operator("ai_chat.save_settings", text="Save Settings", icon='FOLDER_REDIRECT')
        row.operator("ai_chat.load_settings", text="Load Settings", icon='FILE_FOLDER')
        
        # Ollama Script Settings
        layout.separator()
        box = layout.box()
        box.label(text="🤖 Ollama Script:", icon='SCRIPT')
        
        col = box.column(align=True)
        col.prop(props, "auto_run_ollama")
        col.prop(props, "ollama_script_path", text="Script Path")
        
        # Dependencies section
        layout.separator()
        box = layout.box()
        box.label(text="🛠️ Dependencies:", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.label(text="If you don't have Python installed:")
        col.operator("ai_chat.install_dependencies", text="Install Python (Portable)", icon='IMPORT')
        col.separator()
        col.scale_y = 0.8
        col.label(text="• Downloads Python 3.11 (~15MB)")
        col.label(text="• Installs to a_astitnet/python_portable/")
        col.label(text="• Completely isolated - won't affect your system")
        col.label(text="• Includes requests module automatically")
        
        # Response behavior
        layout.separator()
        box = layout.box()
        box.label(text="📄 Responses:", icon='TEXT')
        col = box.column(align=True)
        col.prop(props, "use_versioned_responses", text="Versioned responses (_1, _2, ...)")
        col.label(text=f"Last seen index: {props.last_seen_index}")
        
        # Model Management
        layout.separator()
        box = layout.box()
        row = box.row(align=True)
        row.label(text="🎯 Model Control:", icon='PREFERENCES')
        row.operator("ai_chat.refresh_models", text="", icon='FILE_REFRESH')
        
        col = box.column(align=True)
        
        # Model name input
        col.prop(props, "selected_model", text="Model Name")
        
        # File browser method
        col.separator()
        col.label(text="Or browse to model file:", icon='FOLDER_REDIRECT')
        row = col.row(align=True)
        row.prop(props, "model_file_path", text="")
        row.operator("ai_chat.browse_model", text="Load", icon='IMPORT')
        
        # Model control buttons
        col.separator()
        row = col.row(align=True)
        row.operator("ai_chat.start_selected_model", text="Start Model", icon='PLAY')
        row.operator("ai_chat.stop_all_models", text="Stop All", icon='PAUSE')

class AICHAT_PT_HelpPanel(bpy.types.Panel):
    """Help Panel"""
    bl_label = "How to Use"
    bl_idname = "AICHAT_PT_help_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Chat"
    bl_parent_id = "AICHAT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 0.8
        
        col.label(text="1. Type your message")
        col.label(text="2. Click 'Send'")
        col.label(text="3. Script runs automatically")
        col.label(text="4. Response appears when ready")
        col.label(text="5. Use 'Refresh' if needed")
        col.separator()
        col.label(text="✨ Features:")
        col.label(text="• Auto-run Ollama script")
        col.label(text="• Model management")
        col.label(text="• File browser for models")
        col.label(text="• Cross-platform support")
        col.separator()
        col.label(text="⚠️ Troubleshooting:")
        col.label(text="• Install Python 3.10+")
        col.label(text="• Install: pip install requests")
        col.label(text="• Check model names (like 'gemma:1b')")
        col.label(text="• Restart Ollama if models fail")

def register():
    bpy.utils.register_class(AICHAT_PT_MainPanel)
    bpy.utils.register_class(AICHAT_PT_SettingsPanel)
    bpy.utils.register_class(AICHAT_PT_HelpPanel)

def unregister():
    bpy.utils.unregister_class(AICHAT_PT_HelpPanel)
    bpy.utils.unregister_class(AICHAT_PT_SettingsPanel)
    bpy.utils.unregister_class(AICHAT_PT_MainPanel)
