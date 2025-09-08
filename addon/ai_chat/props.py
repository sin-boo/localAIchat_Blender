import bpy
from pathlib import Path
import os

# Auto-detect odin_grab/a_astitnet directory structure
def find_a_astitnet_directory():
    """Find a_astitnet directory within Odin Grab structure"""
    # 0) Env var override
    env = os.environ.get("A_ASTITNET_PATH")
    if env:
        p = Path(env)
        if p.exists():
            return p

    current = Path(__file__).parent
    
    # Search up the directory tree for odin_grab/a_astitnet structure
    for parent in [current] + list(current.parents):
        # Look for odin_grab folder first
        if parent.name.lower() == 'odin_grab':
            a_astitnet_path = parent / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
        # Also check if we're already in a_astitnet under odin_grab
        if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
            return parent
        # Check for Odin Grab subdirectory
        og1 = parent / 'Odin Grab'
        if og1.exists():
            a_astitnet_path = og1 / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
        # Check for odin_grab as subdirectory
        og2 = parent / 'odin_grab'
        if og2.exists():
            a_astitnet_path = og2 / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
    
    # Desktop fallbacks
    desktop = Path.home() / 'Desktop' / 'Odin Grab' / 'a_astitnet'
    if desktop.exists():
        return desktop
    share_path = Path(r"C:\File\Desktop\Odin Grab\a_astitnet")
    if share_path.exists():
        return share_path
    
    # Fallback to original hardcoded path if not found
    return Path(r"F:\a_astitnet")

A_ASTITNET_PATH = find_a_astitnet_directory()
DEFAULT_INPUT_PATH = str(A_ASTITNET_PATH / "niout" / "input.txt")
DEFAULT_OUTPUT_PATH = str(A_ASTITNET_PATH / "niout" / "response.txt")

class AICHAT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__ if __package__ else "ai_chat"

    # Base directory for the whole system
    pref_base_path: bpy.props.StringProperty(
        name="Base Directory",
        subtype='DIR_PATH',
        default=str(Path(r"F:\odin_grab") / "a_astitnet")
    )

    # Stored preferences for persistence
    bl_idname = __package__ if __package__ else "ai_chat"

    # Stored preferences for persistence
    pref_input_path: bpy.props.StringProperty(
        name="Input File",
        subtype='FILE_PATH',
        default=DEFAULT_INPUT_PATH
    )
    pref_output_path: bpy.props.StringProperty(
        name="Output File",
        subtype='FILE_PATH',
        default=DEFAULT_OUTPUT_PATH
    )
    pref_ollama_script_path: bpy.props.StringProperty(
        name="Ollama Script",
        subtype='FILE_PATH',
        default=str(A_ASTITNET_PATH / "ollama_chat.py")
    )
    pref_auto_run_ollama: bpy.props.BoolProperty(
        name="Auto-run Script",
        default=True
    )
    pref_use_versioned: bpy.props.BoolProperty(
        name="Versioned Responses",
        default=True
    )
    pref_selected_model: bpy.props.StringProperty(
        name="Selected Model",
        default="qwen3:4b"
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="AI Chat Preferences")
        col.prop(self, "pref_base_path")
        col.prop(self, "pref_input_path")
        col.prop(self, "pref_output_path")
        col.prop(self, "pref_ollama_script_path")
        col.prop(self, "pref_auto_run_ollama")
        col.prop(self, "pref_use_versioned")
        col.prop(self, "pref_selected_model")

class AICHAT_Properties(bpy.types.PropertyGroup):
    # Base directory exposed in panel
    base_path: bpy.props.StringProperty(
        name="Base Directory",
        description="Root folder of AI Assistant (odin_grab/a_astitnet)",
        default=str(Path(r"F:\odin_grab") / "a_astitnet"),
        subtype='DIR_PATH'
    )
    """Main properties for AI Chat"""
    
    # User input message
    message: bpy.props.StringProperty(
        name="Message",
        description="Your message to send to AI",
        default="",
        maxlen=2000
    )
    
    # AI response text
    response: bpy.props.StringProperty(
        name="Response", 
        description="AI response text",
        default="No response yet..."
    )
    
    # Simple response monitoring
    waiting_for_response: bpy.props.BoolProperty(
        name="Waiting for Response",
        description="Whether we're currently waiting for a response",
        default=False
    )
    
    # File paths
    input_path: bpy.props.StringProperty(
        name="Input File",
        description="Path to input.txt file",
        default=DEFAULT_INPUT_PATH,
        subtype='FILE_PATH'
    )
    
    output_path: bpy.props.StringProperty(
        name="Output File", 
        description="Path to response.txt file",
        default=DEFAULT_OUTPUT_PATH,
        subtype='FILE_PATH'
    )
    
    # Versioned responses settings
    use_versioned_responses: bpy.props.BoolProperty(
        name="Versioned Responses",
        description="Save/read responses as response_1.txt, response_2.txt, ... while keeping response.txt updated",
        default=True
    )
    last_seen_index: bpy.props.IntProperty(
        name="Last Seen Index",
        description="Internal tracker for latest response_N seen",
        default=0
    )
    
    # Ollama script path
    ollama_script_path: bpy.props.StringProperty(
        name="Ollama Script",
        description="Path to ollama_chat.py script",
        default=str(A_ASTITNET_PATH / "ollama_chat.py"),
        subtype='FILE_PATH'
    )
    
    auto_run_ollama: bpy.props.BoolProperty(
        name="Auto-run Script",
        description="Automatically run Ollama script when Send is clicked",
        default=True
    )
    
    # Model management
    selected_model: bpy.props.StringProperty(
        name="Selected Model",
        description="Currently selected AI model (enter model name like 'qwen3:4b')",
        default="qwen3:4b"
    )
    
    # Model file path (for browsing to model files)
    model_file_path: bpy.props.StringProperty(
        name="Model File",
        description="Browse to select a model file",
        default=str(A_ASTITNET_PATH / "ai mode" / "manifests" / "registry.ollama.ai" / "library"),
        subtype='FILE_PATH'
    )
    

def register():
    bpy.utils.register_class(AICHAT_AddonPreferences)
    bpy.utils.register_class(AICHAT_Properties)
    
    # Add to window manager
    bpy.types.WindowManager.ai_chat = bpy.props.PointerProperty(
        type=AICHAT_Properties
    )

def unregister():
    del bpy.types.WindowManager.ai_chat
    bpy.utils.unregister_class(AICHAT_Properties)
    bpy.utils.unregister_class(AICHAT_AddonPreferences)
