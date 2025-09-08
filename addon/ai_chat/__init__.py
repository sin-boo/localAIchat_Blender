bl_info = {
    "name": "AI Chat",
    "description": "Simple AI chat interface with streaming text effect",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Sidebar > AI Chat",
    "category": "3D View",
}

import bpy

# Import modules
from . import props
from . import operators
from . import ui

def _apply_prefs_to_props():
    try:
        import bpy
        addon_id = __package__ if __package__ else "ai_chat"
        if addon_id not in bpy.context.preferences.addons:
            print("AI Chat: Preferences not found on startup")
            return None
        prefs = bpy.context.preferences.addons[addon_id].preferences
        wm = bpy.context.window_manager if hasattr(bpy.context, 'window_manager') else None
        if not wm or not hasattr(wm, 'ai_chat'):
            # try again shortly until WindowManager.ai_chat is ready
            return 0.5
        props = wm.ai_chat
        # Copy prefs into runtime properties
        if getattr(prefs, 'pref_base_path', None):
            props.base_path = prefs.pref_base_path
        if getattr(prefs, 'pref_input_path', None):
            props.input_path = prefs.pref_input_path
        if getattr(prefs, 'pref_output_path', None):
            props.output_path = prefs.pref_output_path
        if getattr(prefs, 'pref_ollama_script_path', None):
            props.ollama_script_path = prefs.pref_ollama_script_path
        if hasattr(prefs, 'pref_auto_run_ollama'):
            props.auto_run_ollama = prefs.pref_auto_run_ollama
        if hasattr(prefs, 'pref_use_versioned'):
            props.use_versioned_responses = prefs.pref_use_versioned
        if getattr(prefs, 'pref_selected_model', None):
            props.selected_model = prefs.pref_selected_model
        print("AI Chat: Preferences applied on startup")
    except Exception as e:
        print(f"AI Chat: Failed to apply preferences on startup: {e}")
    return None


def register():
    props.register()
    operators.register()
    ui.register()

    # Apply saved preferences to runtime properties shortly after register
    import bpy
    bpy.app.timers.register(_apply_prefs_to_props, first_interval=0.5)
    
    print("AI Chat addon registered successfully")

def unregister():
    ui.unregister()
    operators.unregister()
    props.unregister()
    
    print("AI Chat addon unregistered")

if __name__ == "__main__":
    register()
