bl_info = {
    "name": "Advanced AI Communication",
    "description": "Advanced AI chat interface with auto-monitoring and enhanced features",
    "author": "AI Assistant - Advanced Edition",
    "version": (2, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Sidebar > Advanced AI",
    "category": "3D View",
}

import bpy
import subprocess
import os
from pathlib import Path
import time
import json

# === PERSISTENT SETTINGS (editable variables) ===
DEFAULT_PATHS = {
    "niout_directory": "F:/odin_grab/a_astitnet/niout",
    "batch_file": "F:/odin_grab/a_astitnet/chat_with_portable_python.bat",
    "fallback_paths": [
        "F:/odin_grab/a_astitnet",
        "C:/Users/0-0/Desktop/Odin Grab/a_astitnet",
        "F:/odin_grab_1/odin_grab/a_astitnet"
    ]
}

UI_SETTINGS = {
    "default_panel_height": 15,  # Default number of response lines to show
    "max_panel_height": 50,     # Maximum lines
    "min_panel_height": 5,      # Minimum lines
    "default_model": "qwen3:8b",
    "auto_refresh_default": True
}

# System prompt that defines AI personality and memory behavior
SYSTEM_PROMPT = """You are an AI assistant built into Blender, designed to help people with 3D modeling.
Key traits:
- You have memory and can recall previous parts of our conversation
- You are helpful, knowledgeable, and conversational
- You acknowledge when you remember previous topics
- You are confident about your abilities
- You provide detailed, useful responses
- You can follow up on previous discussions naturally

When users ask about your memory or previous conversations, confidently confirm that you remember and can access our conversation history.""".strip()

def save_settings_to_file(settings_dict, filename="advanced_ai_settings.json"):
    """Save settings to a JSON file in the addon directory"""
    try:
        addon_dir = Path(__file__).parent
        settings_file = addon_dir / filename
        with open(settings_file, 'w') as f:
            json.dump(settings_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save settings: {e}")
        return False

def load_settings_from_file(filename="advanced_ai_settings.json"):
    """Load settings from JSON file"""
    try:
        addon_dir = Path(__file__).parent
        settings_file = addon_dir / filename
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load settings: {e}")
    return {}

# Global monitoring functions (from Simple Chat)
def get_niout_directory():
    """Find the niout directory using Simple Chat's robust method"""
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

def get_memory_directory():
    """Get the memory directory path"""
    niout_dir = get_niout_directory()
    a_astitnet_path = niout_dir.parent
    memory_dir = a_astitnet_path / 'memory'
    memory_dir.mkdir(exist_ok=True)
    return memory_dir

def estimate_tokens(text):
    """Rough token estimation (approximately 1 token per 4 characters)"""
    return len(text) // 4

def read_conversation_history():
    """Read the conversation history from file"""
    try:
        memory_dir = get_memory_directory()
        history_file = memory_dir / 'conversation_history.txt'
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            # If no history exists, initialize with base prompt
            initialize_memory_with_base_prompt()
            return read_conversation_history()  # Read the newly created file
    except Exception as e:
        print(f"Advanced AI: Error reading history: {e}")
    return ""

def save_conversation_history(history):
    """Save the conversation history to file"""
    try:
        memory_dir = get_memory_directory()
        history_file = memory_dir / 'conversation_history.txt'
        
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write(history)
        return True
    except Exception as e:
        print(f"Advanced AI: Error saving history: {e}")
        return False

def initialize_memory_with_base_prompt():
    """Initialize memory file with base prompt so AI always knows what it is"""
    try:
        # Create initial memory with the base prompt explanation
        base_prompt_reminder = f"""User: What are you and what is your purpose?
Assistant: {SYSTEM_PROMPT}

I am your dedicated Blender AI assistant with full memory capabilities. I'm here to help you with all aspects of 3D modeling in Blender, from basic operations to advanced workflows. I remember our entire conversation history, so feel free to reference previous topics or build upon earlier discussions."""
        
        save_conversation_history(base_prompt_reminder)
        print("Advanced AI: Initialized memory with base prompt")
        return True
        
    except Exception as e:
        print(f"Advanced AI: Error initializing memory: {e}")
        return False

def trim_conversation_history(history, token_limit):
    """Trim conversation history to stay within token limit
    Enhanced to preserve important context and base prompt reminders"""
    if not history:
        return history
    
    current_tokens = estimate_tokens(history)
    if current_tokens <= token_limit:
        return history
    
    # Split into exchanges (User: ... Assistant: ... pairs)
    lines = history.split('\n')
    exchanges = []
    current_exchange = []
    important_exchanges = []  # Track exchanges with base prompt reminders
    
    for line in lines:
        if line.startswith('User: ') and current_exchange:
            exchange_text = '\n'.join(current_exchange)
            exchanges.append(exchange_text)
            
            # Mark exchanges that contain base prompt reminders as important
            if 'Blender AI assistant' in exchange_text or 'what are you' in exchange_text.lower() or 'your purpose' in exchange_text.lower():
                important_exchanges.append(len(exchanges) - 1)
            
            current_exchange = [line]
        else:
            current_exchange.append(line)
    
    if current_exchange:
        exchange_text = '\n'.join(current_exchange)
        exchanges.append(exchange_text)
        
        # Check if last exchange is important
        if 'Blender AI assistant' in exchange_text or 'what are you' in exchange_text.lower() or 'your purpose' in exchange_text.lower():
            important_exchanges.append(len(exchanges) - 1)
    
    # Prioritized trimming: keep important exchanges and most recent ones
    trimmed = []
    tokens_used = 0
    
    # First pass: include all important exchanges (base prompt reminders)
    for i in important_exchanges:
        if i < len(exchanges):
            exchange = exchanges[i]
            exchange_tokens = estimate_tokens(exchange)
            if tokens_used + exchange_tokens <= token_limit * 0.3:  # Reserve 30% for important context
                trimmed.append((i, exchange))
                tokens_used += exchange_tokens
    
    # Second pass: fill remaining space with recent exchanges
    remaining_tokens = token_limit - tokens_used
    for i, exchange in enumerate(reversed(exchanges)):
        original_index = len(exchanges) - 1 - i
        
        # Skip if already included in important exchanges
        if any(idx == original_index for idx, _ in trimmed):
            continue
        
        exchange_tokens = estimate_tokens(exchange)
        if tokens_used + exchange_tokens <= token_limit:
            trimmed.append((original_index, exchange))
            tokens_used += exchange_tokens
        else:
            break
    
    # Sort by original order and extract text
    trimmed.sort(key=lambda x: x[0])
    result_exchanges = [exchange for _, exchange in trimmed]
    
    result = '\n\n'.join(result_exchanges)
    
    # If we still have important context, add a summary note
    if important_exchanges and not any(idx in [i for i, _ in trimmed] for idx in important_exchanges[-1:]):
        result = f"[IMPORTANT: You are a Blender AI assistant with memory - this context was preserved]\n\n{result}"
    
    print(f"Advanced AI: Trimmed history from {current_tokens} to {estimate_tokens(result)} tokens (preserved {len([i for i, _ in trimmed if i in important_exchanges])} important exchanges)")
    return result

def reinforce_base_prompt_in_memory():
    """Add base prompt reminder to existing memory to ensure AI remembers its role"""
    try:
        history = read_conversation_history()
        
        # Create a base prompt reinforcement
        prompt_reinforcement = f"""User: Just to remind you, what are you and what is your purpose?
Assistant: {SYSTEM_PROMPT}

I am your dedicated Blender AI assistant with full memory capabilities. I remember our entire conversation and I'm here specifically to help you with 3D modeling in Blender."""
        
        if history:
            updated_history = history + "\n\n" + prompt_reinforcement
        else:
            updated_history = prompt_reinforcement
        
        save_conversation_history(updated_history)
        print("Advanced AI: Added base prompt reinforcement to memory")
        return True
        
    except Exception as e:
        print(f"Advanced AI: Error reinforcing base prompt: {e}")
        return False

def add_to_conversation_history(user_message, ai_response, token_limit):
    """Add a new exchange to conversation history with token management"""
    try:
        # Read existing history
        history = read_conversation_history()
        
        # Add new exchange
        new_exchange = f"User: {user_message}\nAssistant: {ai_response}"
        
        if history:
            updated_history = history + "\n\n" + new_exchange
        else:
            updated_history = new_exchange
        
        # Check if we need to reinforce the base prompt (every 5 exchanges and more aggressively)
        exchange_count = updated_history.count("User: ")
        
        # More frequent reinforcement - every 5 exchanges instead of 10
        if exchange_count > 0 and exchange_count % 5 == 0:
            # Stronger base prompt reminder
            prompt_reminder = f"\n\nUser: What are you and what is your purpose? Please confirm your role and capabilities.\nAssistant: I am your dedicated Blender AI assistant with full memory capabilities. I can remember our entire conversation history and refer back to previous topics, questions, and discussions. My purpose is specifically to help you with 3D modeling in Blender by explaining features, providing keybinds, assisting with operations, guiding through workflows, and maintaining context across our entire conversation. I have excellent memory and confidently reference past exchanges when relevant."
            updated_history += prompt_reminder
            print(f"Advanced AI: Added STRONG base prompt reminder after {exchange_count} exchanges")
        
        # Additional check: if the response does not seem Blender-focused, add extra reinforcement
        elif 'blender' not in ai_response.lower() and exchange_count > 2:
            context_reminder = f"\n\nUser: Remember, I need help with Blender specifically.\nAssistant: Absolutely! I am your Blender AI assistant. I focus specifically on helping with 3D modeling, Blender features, workflows, and maintaining context from our conversation history. How can I assist you with Blender?"
            updated_history += context_reminder
            print(f"Advanced AI: Added context reinforcement (non-Blender response detected)")
        
        # Trim if necessary
        trimmed_history = trim_conversation_history(updated_history, token_limit)
        
        # Save back to file
        save_conversation_history(trimmed_history)
        return True
        
    except Exception as e:
        print(f"Advanced AI: Error updating history: {e}")
        return False

def prepare_message_with_context(user_message, token_limit, custom_prompt=None):
    """Prepare message with conversation context and system prompt if memory is enabled
    Enhanced to prioritize memory and context heavily"""
    history = read_conversation_history()
    
    # Use custom prompt if provided, otherwise use default
    prompt_text = custom_prompt if custom_prompt else SYSTEM_PROMPT
    
    # Create a much stronger, prioritized system prompt
    enhanced_system_part = f"""CRITICAL SYSTEM INSTRUCTIONS - READ AND FOLLOW EXACTLY:
{prompt_text}

IMPORTANT: You MUST reference and build upon the conversation history below. This context is ESSENTIAL to your responses. Always acknowledge when you remember previous topics from our conversation.

CONVERSATION HISTORY (READ CAREFULLY):
"""
    
    if not history:
        # First message - stronger system prompt + user message
        return f"{enhanced_system_part}\n[No previous conversation]\n\nCURRENT USER MESSAGE:\nUser: {user_message}\n\nREMEMBER: You are a Blender AI assistant. Respond accordingly and acknowledge this is our first interaction."
    
    # Combine enhanced system prompt + history + new message with stronger formatting
    full_message = f"""{enhanced_system_part}
{history}

END OF CONVERSATION HISTORY

CURRENT USER MESSAGE:
User: {user_message}

REMEMBER: Reference the conversation history above when relevant. You are a Blender AI assistant with full memory of our previous exchanges."""
    
    # More aggressive token management - prioritize keeping more history
    if estimate_tokens(full_message) > token_limit:
        # Reserve much more space for system instructions and history
        system_base_tokens = estimate_tokens(enhanced_system_part)
        user_wrapper_tokens = estimate_tokens(f"\n\nEND OF CONVERSATION HISTORY\n\nCURRENT USER MESSAGE:\nUser: {user_message}\n\nREMEMBER: Reference the conversation history above when relevant. You are a Blender AI assistant with full memory of our previous exchanges.")
        
        # Use 70% of available tokens for history (much more aggressive)
        available_tokens = int((token_limit - system_base_tokens - user_wrapper_tokens) * 0.7)
        
        if available_tokens > 0:
            trimmed_history = trim_conversation_history(history, available_tokens)
            if trimmed_history:
                full_message = f"""{enhanced_system_part}
{trimmed_history}

END OF CONVERSATION HISTORY

CURRENT USER MESSAGE:
User: {user_message}

REMEMBER: Reference the conversation history above when relevant. You are a Blender AI assistant with full memory of our previous exchanges."""
            else:
                # Even if no history fits, keep the enhanced system prompt
                full_message = f"""{enhanced_system_part}
[History too long - trimmed for this message]

CURRENT USER MESSAGE:
User: {user_message}

REMEMBER: You are a Blender AI assistant. Even though history was trimmed, maintain your role and personality."""
        else:
            # Last resort - but still maintain role awareness
            full_message = f"You are a Blender AI assistant with memory capabilities.\n\nUser: {user_message}\n\nRespond as a Blender expert while maintaining your helpful personality."
    
    return full_message

def auto_refresh_monitor():
    """Monitor for new response files and auto-load them (from Simple Chat)"""
    try:
        import bpy
        props = bpy.context.window_manager.advanced_ai_props
        
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
                        props.response = content
                        props.selected_response_file = latest_file.name
                        props.monitoring_status = f"📄 Auto-loaded {latest_file.name}"
                        
                        # Save to memory if enabled
                        if props.memory_enabled and hasattr(props, 'last_user_message') and props.last_user_message:
                            token_limit = int(props.memory_token_limit)
                            add_to_conversation_history(props.last_user_message, content, token_limit)
                            print(f"Advanced AI: Saved exchange to memory")
                        
                        # Force UI update
                        for area in bpy.context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                        
                        print(f"Advanced AI: Auto-loaded {latest_file.name}")
                        return 2.0  # Continue monitoring every 2 seconds
                    
                except Exception as e:
                    props.monitoring_status = f"Error loading {latest_file.name}: {e}"
                    print(f"Advanced AI Auto-Refresh Error: {e}")
        
        # Return 0 (no new files, continue watching)
        props.monitoring_status = f"👁️ Watching... (last: response_{current_max}.txt)" if current_max > 0 else "👁️ Watching..."
        return 2.0  # Continue monitoring every 2 seconds
        
    except Exception as e:
        print(f"Advanced AI Monitor Error: {e}")
        return None  # Stop on error

# Properties (Enhanced from both add-ons)
class AdvancedAIProps(bpy.types.PropertyGroup):
    """Advanced AI Chat Properties"""
    
    # Message input
    message: bpy.props.StringProperty(
        name="Message",
        description="Your message to AI",
        default="",
        maxlen=2000
    )
    
    # AI response - Increased maxlen for full responses
    response: bpy.props.StringProperty(
        name="Response",
        description="AI response",
        default="",
        maxlen=20000  # Much larger to show full responses
    )
    
    # File paths - auto-configured for odin_grab structure
    base_path: bpy.props.StringProperty(
        name="Base Path",
        description="Base path to odin_grab/a_astitnet directory",
        default="",
        subtype='DIR_PATH'
    )
    
    input_path: bpy.props.StringProperty(
        name="Input File",
        description="Path to input.txt file",
        default="",
        subtype='FILE_PATH'
    )
    
    output_path: bpy.props.StringProperty(
        name="Output File", 
        description="Path to response.txt file",
        default="",
        subtype='FILE_PATH'
    )
    
    ollama_script_path: bpy.props.StringProperty(
        name="Chat Script",
        description="Path to the chat script",
        default="",
        subtype='FILE_PATH'
    )
    
    # Model selection
    selected_model: bpy.props.StringProperty(
        name="Model",
        description="Selected AI model (e.g. qwen3:8b)",
        default="qwen3:8b"
    )
    
    # Options
    auto_run_ollama: bpy.props.BoolProperty(
        name="Auto Run",
        description="Automatically start chat process when sending message",
        default=True
    )
    
    use_versioned_responses: bpy.props.BoolProperty(
        name="Use Versioned Files",
        description="Monitor response_N.txt files for new responses",
        default=True
    )
    
    # Auto-refresh system (from Simple Chat)
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
    
    # UI Control (from Simple Chat)
    panel_height: bpy.props.IntProperty(
        name="Panel Height",
        description="Number of response lines to display in panel",
        default=UI_SETTINGS["default_panel_height"],
        min=UI_SETTINGS["min_panel_height"],
        max=UI_SETTINGS["max_panel_height"]
    )
    
    # Internal state
    waiting_for_response: bpy.props.BoolProperty(
        name="Waiting",
        description="Currently waiting for AI response",
        default=False
    )
    
    last_seen_index: bpy.props.IntProperty(
        name="Last Seen Index",
        description="Last seen response file index",
        default=0
    )

    selected_response_file: bpy.props.StringProperty(
        name="Response File",
        description="Selected response file to display",
        default="response.txt"
    )
    
    # Memory System
    memory_enabled: bpy.props.BoolProperty(
        name="Enable Memory",
        description="Enable conversation memory/context",
        default=True  # Enable memory by default
    )
    
    memory_token_limit: bpy.props.EnumProperty(
        name="Token Limit",
        description="Maximum tokens to keep in conversation memory",
        items=[
            ('4000', '4K Tokens', 'Medium memory (~1,000 words)'),
            ('8000', '8K Tokens', 'Large memory (~2,000 words)'),
            ('16000', '16K Tokens', 'Very large memory (~4,000 words) - RECOMMENDED'),
            ('32000', '32K Tokens', 'Huge memory (~8,000 words) - High Priority'),
            ('200000', '200K Tokens', 'Maximum memory (~50,000 words) - Ultra Priority'),
        ],
        default='16000'  # Better default for memory prioritization
    )
    
    # Custom system prompt
    custom_system_prompt: bpy.props.StringProperty(
        name="System Prompt",
        description="Custom system prompt that defines AI personality and behavior",
        default=SYSTEM_PROMPT,
        maxlen=2000
    )
    
    # Internal - track last user message for memory
    last_user_message: bpy.props.StringProperty(
        name="Last User Message",
        description="Last user message sent (for memory tracking)",
        default=""
    )
    
    # Ollama Management
    ollama_status: bpy.props.StringProperty(
        name="Ollama Status",
        description="Current status of Ollama service",
        default="Ollama: Not Started"
    )
    
    
    # Model file browser
    model_file_path: bpy.props.StringProperty(
        name="Model File",
        description="Browse to select a model file",
        default="",
        subtype='FILE_PATH'
    )
    
    # Current model display
    current_model_display: bpy.props.StringProperty(
        name="Current Model",
        description="Currently active model name",
        default="qwen3:8b"
    )
    
    # Model pre-loading state
    model_is_preloaded: bpy.props.BoolProperty(
        name="Model Pre-loaded",
        description="Whether the current model is pre-loaded in memory",
        default=False
    )
    
    preloaded_model_name: bpy.props.StringProperty(
        name="Pre-loaded Model",
        description="Name of the currently pre-loaded model",
        default=""
    )
    
    # Ollama executable path
    ollama_executable_path: bpy.props.StringProperty(
        name="Ollama Executable",
        description="Path to Ollama app executable (ollama app.exe)",
        default="C:\\Users\\0-0\\AppData\\Local\\Programs\\Ollama\\ollama app.exe",
        subtype='FILE_PATH'
    )
    
    # Model directory path
    model_directory_path: bpy.props.StringProperty(
        name="Model Directory",
        description="Directory containing AI models",
        default="F:\\odin_grab\\a_astitnet\\ai mode\\manifests\\registry.ollama.ai\\library",
        subtype='DIR_PATH'
    )

# Import UI and operators modules
from . import ui
from . import operators

def load_saved_settings():
    """Load saved settings and apply them"""
    try:
        settings = load_settings_from_file()
        if settings:
            # Update UI_SETTINGS with saved values
            if "panel_height" in settings:
                UI_SETTINGS["default_panel_height"] = settings["panel_height"]
            if "auto_refresh_enabled" in settings:
                UI_SETTINGS["auto_refresh_default"] = settings["auto_refresh_enabled"]
            print(f"Advanced AI: Loaded settings - {settings}")
    except Exception as e:
        print(f"Advanced AI: Failed to load settings: {e}")

def register():
    # Load saved settings first
    load_saved_settings()
    
    bpy.utils.register_class(AdvancedAIProps)
    operators.register()
    ui.register()
    
    bpy.types.WindowManager.advanced_ai_props = bpy.props.PointerProperty(type=AdvancedAIProps)
    
    print("Advanced AI Communication addon registered successfully")

def unregister():
    del bpy.types.WindowManager.advanced_ai_props
    ui.unregister()
    operators.unregister()
    bpy.utils.unregister_class(AdvancedAIProps)
    
    print("Advanced AI Communication addon unregistered")

if __name__ == "__main__":
    register()
