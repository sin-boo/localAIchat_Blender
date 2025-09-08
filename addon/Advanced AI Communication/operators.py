import bpy
import subprocess
import os
import re
from pathlib import Path

# Import from main module
from . import get_niout_directory, get_highest_response_number, auto_refresh_monitor, save_settings_to_file, UI_SETTINGS
from . import prepare_message_with_context, add_to_conversation_history, save_conversation_history, reinforce_base_prompt_in_memory

class ADVANCEDAI_OT_SendMessage(bpy.types.Operator):
    """Send message to AI using Simple Chat's superior system"""
    bl_idname = "advanced_ai.send_message"
    bl_label = "Send Message"
    bl_description = "Send your message to AI"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        # Get message
        message = props.message.strip()
        if not message:
            self.report({'WARNING'}, "Please enter a message")
            return {'CANCELLED'}
        
        try:
            # Auto-detect and configure paths using Simple Chat's method
            self.auto_configure_paths(props)
            
            # Prepare message with memory context if enabled
            if props.memory_enabled:
                token_limit = int(props.memory_token_limit)
                custom_prompt = props.custom_system_prompt if props.custom_system_prompt.strip() else None
                final_message = prepare_message_with_context(message, token_limit, custom_prompt)
                print(f"Advanced AI: Memory enabled - using {len(final_message)} characters with context")
            else:
                final_message = message
                print(f"Advanced AI: Memory disabled - using message as-is")
            
            # Write message and model config using Simple Chat's direct method
            niout_dir = get_niout_directory()
            niout_dir.mkdir(exist_ok=True)
            
            input_file = niout_dir / 'input.txt'
            model_config = niout_dir / 'model_config.txt'
            
            # Write input message (with context if memory enabled)
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(final_message)
            print(f"Advanced AI: Wrote message to {input_file}")
            
            # Write model config using selected model
            model_name = props.selected_model if props.selected_model else 'qwen3:8b'
            with open(model_config, 'w', encoding='utf-8') as f:
                f.write(model_name)
            print(f"Advanced AI: Set model to {model_name}")
            
            # Update current model display
            props.current_model_display = model_name
            
            # Launch the batch file using Simple Chat's method
            self.launch_batch_file(niout_dir.parent)
            
            # Store the original user message for memory
            props.last_user_message = message
            
            # Clear input and set waiting message
            props.message = ""
            props.response = "Processing your request..."
            
            # Start auto-monitoring if enabled (Simple Chat's feature)
            if props.auto_refresh_enabled:
                # Set up monitoring state
                current_max, _ = get_highest_response_number(niout_dir)
                props.last_known_max_number = current_max
                props.is_monitoring = True
                props.monitoring_status = "👁️ Starting to watch for response..."
                
                # Start the monitoring timer
                bpy.app.timers.register(auto_refresh_monitor, first_interval=3.0)
                print("Advanced AI: Started monitoring for new responses")
                
                self.report({'INFO'}, "Message sent! Watching for response...")
            else:
                self.report({'INFO'}, "Message sent! Check console window for AI processing.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to send message: {e}")
            print(f"Advanced AI Error: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def auto_configure_paths(self, props):
        """Auto-configure paths using Simple Chat's robust system"""
        niout_dir = get_niout_directory()
        a_astitnet_path = niout_dir.parent
        
        if a_astitnet_path.exists():
            props.base_path = str(a_astitnet_path)
            props.input_path = str(niout_dir / 'input.txt')
            props.output_path = str(niout_dir / 'response.txt')
            
            # Find chat script
            script_candidates = [
                a_astitnet_path / 'chat_with_portable_python.bat',
                a_astitnet_path / 'ollama_chat.py',
                a_astitnet_path / 'chat.py'
            ]
            for script in script_candidates:
                if script.exists():
                    props.ollama_script_path = str(script)
                    break
    
    def launch_batch_file(self, base_path):
        """Launch batch file using Simple Chat's reliable method"""
        batch_file = base_path / 'chat_with_portable_python.bat'
        
        if batch_file.exists():
            try:
                cmd_str = f'"{batch_file}"'
                print(f"Advanced AI: Running command: {cmd_str}")
                
                process = subprocess.Popen(
                    cmd_str,
                    cwd=str(base_path),
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                print(f"Advanced AI: Batch file started with PID: {process.pid}")
                
            except Exception as e:
                print(f"Advanced AI: Failed to launch batch file: {e}")
                raise e
        else:
            raise FileNotFoundError(f"Batch file not found: {batch_file}")

class ADVANCEDAI_OT_ClearMessage(bpy.types.Operator):
    """Clear the input message"""
    bl_idname = "advanced_ai.clear_message"
    bl_label = "Clear"
    bl_description = "Clear the input message"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        context.window_manager.advanced_ai_props.message = ""
        return {'FINISHED'}

class ADVANCEDAI_OT_RefreshResponse(bpy.types.Operator):
    """Manually refresh response"""
    bl_idname = "advanced_ai.refresh_response"
    bl_label = "Refresh"
    bl_description = "Check for new AI response"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            output_path = Path(props.output_path) if props.output_path else get_niout_directory() / 'response.txt'
            
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    props.response = content
                    props.waiting_for_response = False
                    self.report({'INFO'}, "Response refreshed!")
                else:
                    props.response = "Response file is empty"
            else:
                props.response = "Response file not found"
                
        except Exception as e:
            props.response = f"Error: {e}"
            self.report({'ERROR'}, f"Failed to refresh: {e}")
        
        return {'FINISHED'}

class ADVANCEDAI_OT_LoadLatestResponse(bpy.types.Operator):
    """Load the latest response and show all available files (from Simple Chat)"""
    bl_idname = "advanced_ai.load_latest_response"
    bl_label = "Load Latest Response"
    bl_description = "Load the latest AI response and show all available files"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            niout_dir = get_niout_directory()
            
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
                
                # Load the content
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    props.response = content
                    
                    # Report success with file list
                    if response_files:
                        files_str = ', '.join(response_files[-5:])  # Show last 5 files
                        if len(response_files) > 5:
                            files_str = "..." + files_str
                        self.report({'INFO'}, f"Loaded {latest_file.name} | Available: {files_str}")
                    else:
                        self.report({'INFO'}, f"Loaded {latest_file.name}")
                else:
                    props.response = "Response file is empty"
            else:
                props.response = "No response files found"
                self.report({'WARNING'}, "No response files found")
                
        except Exception as e:
            props.response = f"Error: {e}"
            self.report({'ERROR'}, f"Failed to load response: {e}")
        
        return {'FINISHED'}

class ADVANCEDAI_OT_ToggleMonitoring(bpy.types.Operator):
    """Toggle automatic response monitoring (from Simple Chat)"""
    bl_idname = "advanced_ai.toggle_monitoring"
    bl_label = "Toggle Auto-Refresh"
    bl_description = "Turn automatic response monitoring on/off"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
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

class ADVANCEDAI_OT_CopyResponse(bpy.types.Operator):
    """Copy the current AI response to clipboard (from Simple Chat)"""
    bl_idname = "advanced_ai.copy_response"
    bl_label = "Copy Response"
    bl_description = "Copy the current AI response to clipboard"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        if not props.response:
            self.report({'WARNING'}, "No response to copy")
            return {'CANCELLED'}
        
        try:
            # Copy to system clipboard using Blender's built-in clipboard
            context.window_manager.clipboard = props.response
            self.report({'INFO'}, f"✅ Copied {len(props.response)} characters to clipboard")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to copy: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_SaveSettings(bpy.types.Operator):
    """Save current settings to file (from Simple Chat)"""
    bl_idname = "advanced_ai.save_settings"
    bl_label = "Save Settings"
    bl_description = "Save current panel settings to file"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        # Gather current settings
        settings = {
            "panel_height": props.panel_height,
            "auto_refresh_enabled": props.auto_refresh_enabled,
            "selected_model": UI_SETTINGS["default_model"]
        }
        
        if save_settings_to_file(settings):
            self.report({'INFO'}, "✅ Settings saved")
        else:
            self.report({'ERROR'}, "❌ Failed to save settings")
        
        return {'FINISHED'}

class ADVANCEDAI_OT_ClearResponses(bpy.types.Operator):
    """Delete all versioned response_N.txt files and reset state"""
    bl_idname = "advanced_ai.clear_responses"
    bl_label = "Clear Responses"
    bl_description = "Delete response_*.txt files and clear output"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        try:
            niout_dir = get_niout_directory()
            pattern = re.compile(r"response_(\\d+)\\.txt$")
            deleted = 0
            
            if niout_dir.exists():
                for p in list(niout_dir.iterdir()):
                    if p.is_file() and pattern.match(p.name):
                        try:
                            p.unlink()
                            deleted += 1
                        except Exception:
                            pass
            
            # Optionally clear response.txt as well
            try:
                out = niout_dir / 'response.txt'
                if out.exists():
                    out.unlink()
            except Exception:
                pass
                
            props.last_seen_index = 0
            props.last_known_max_number = 0
            props.response = ""
            props.waiting_for_response = False
            
            self.report({'INFO'}, f"Cleared {deleted} response files")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear responses: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_ClearMemory(bpy.types.Operator):
    """Clear conversation memory/history"""
    bl_idname = "advanced_ai.clear_memory"
    bl_label = "Clear Memory"
    bl_description = "Clear all conversation history from memory"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            # Clear the conversation history
            save_conversation_history("")
            self.report({'INFO'}, "🧠 Memory cleared successfully")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear memory: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_ReinforcePrompt(bpy.types.Operator):
    """Reinforce base prompt in memory so AI remembers its role"""
    bl_idname = "advanced_ai.reinforce_prompt"
    bl_label = "Reinforce AI Role"
    bl_description = "Add base prompt reminder to memory so AI remembers it's a Blender assistant"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            reinforce_base_prompt_in_memory()
            self.report({'INFO'}, "Base prompt reinforced - AI will remember its Blender role")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to reinforce prompt: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StartOllama(bpy.types.Operator):
    """Launch Ollama App"""
    bl_idname = "advanced_ai.start_ollama"
    bl_label = "Launch Ollama App"
    bl_description = "Launch the Ollama App"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            import subprocess
            
            # Simple: just run the ollama app.exe
            subprocess.Popen(["C:\\Users\\0-0\\AppData\\Local\\Programs\\Ollama\\ollama app.exe"])
            
            props.ollama_status = "Ollama App: Launched"
            self.report({'INFO'}, "Ollama App launched")
            
        except Exception as e:
            props.ollama_status = "Ollama App: Error"
            self.report({'ERROR'}, f"Failed to launch: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StopOllama(bpy.types.Operator):
    """Stop Ollama App and service"""
    bl_idname = "advanced_ai.stop_ollama"
    bl_label = "Stop Ollama App"
    bl_description = "Stop the Ollama App and service"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            import subprocess
            import platform
            
            # Stop Ollama processes
            if platform.system() == "Windows":
                # Kill both ollama.exe and ollama app.exe processes on Windows
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    print("Advanced AI: Stopped ollama.exe")
                except:
                    pass
                
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "ollama app.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    print("Advanced AI: Stopped ollama app.exe")
                except:
                    pass
            else:
                # Kill ollama processes on Linux/Mac
                subprocess.run(["pkill", "-f", "ollama"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                print("Advanced AI: Stopped ollama processes")
            
            props.ollama_status = "Ollama: Stopped"
            self.report({'INFO'}, "Ollama App stopped")
            
        except Exception as e:
            self.report({'WARNING'}, f"Error stopping Ollama: {e}")
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StartSelectedModel(bpy.types.Operator):
    """Start the selected AI model"""
    bl_idname = "advanced_ai.start_selected_model"
    bl_label = "Start Selected Model"
    bl_description = "Start the currently selected AI model using Ollama"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_name = props.selected_model.strip()
        
        if not model_name:
            self.report({'WARNING'}, "No model selected")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Get Ollama executable path
            ollama_path = Path(props.ollama_executable_path)
            
            if not ollama_path.exists():
                self.report({'ERROR'}, f"Ollama executable not found: {ollama_path}")
                return {'CANCELLED'}
            
            # Start the model using ollama run
            print(f"Advanced AI: Starting model {model_name} with Ollama")
            subprocess.Popen([str(ollama_path), "run", model_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            props.current_model_display = model_name
            self.report({'INFO'}, f"Started model: {model_name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_TerminateAllModels(bpy.types.Operator):
    """Terminate all running AI models"""
    bl_idname = "advanced_ai.terminate_all_models"
    bl_label = "Terminate All Models"
    bl_description = "Stop all running AI models and Ollama processes"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            import subprocess
            import platform
            from pathlib import Path
            
            # Try multiple methods to stop Ollama and models
            success_count = 0
            
            # Method 1: Try using ollama CLI if available
            try:
                ollama_path = Path(props.ollama_executable_path)
                if ollama_path.exists():
                    # Try running stop command
                    result = subprocess.run([str(ollama_path), "stop"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        success_count += 1
                        print(f"Advanced AI: Ollama stop command succeeded")
            except Exception as e:
                print(f"Advanced AI: Ollama stop command failed: {e}")
            
            # Method 2: Kill Ollama processes (more aggressive)
            try:
                if platform.system() == "Windows":
                    # Kill both ollama.exe and ollama app.exe processes
                    subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    subprocess.run(["taskkill", "/F", "/IM", "ollama app.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    success_count += 1
                    print(f"Advanced AI: Killed Ollama processes")
                else:
                    # Kill ollama processes on Linux/Mac
                    subprocess.run(["pkill", "-f", "ollama"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    success_count += 1
            except Exception as e:
                print(f"Advanced AI: Process kill failed: {e}")
            
            # Update addon state
            props.model_is_preloaded = False
            props.preloaded_model_name = ""
            props.ollama_status = "Ollama: Stopped"
            
            if success_count > 0:
                self.report({'INFO'}, "All models and Ollama processes terminated")
            else:
                self.report({'WARNING'}, "Could not terminate models - check console")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error terminating models: {e}")
        
        return {'FINISHED'}

class ADVANCEDAI_OT_SetModel(bpy.types.Operator):
    """Set model without pre-loading (config only)"""
    bl_idname = "advanced_ai.set_model"
    bl_label = "Set Model"
    bl_description = "Set the model for next message (no pre-loading)"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_name = props.selected_model.strip()
        
        if not model_name:
            self.report({'WARNING'}, "No model selected")
            return {'CANCELLED'}
        
        # Update model config without pre-loading
        props.current_model_display = model_name
        
        self.report({'INFO'}, f"Model set to: {model_name} (will load on next message)")
        return {'FINISHED'}

class ADVANCEDAI_OT_SetAndPreloadModel(bpy.types.Operator):
    """Set model and pre-load it into memory"""
    bl_idname = "advanced_ai.set_and_preload_model"
    bl_label = "Set & Pre-load Model"
    bl_description = "Set the model and pre-load it into memory for faster responses"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_name = props.selected_model.strip()
        
        if not model_name:
            self.report({'WARNING'}, "No model selected")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Get Ollama executable path
            ollama_path = Path(props.ollama_executable_path)
            
            if not ollama_path.exists():
                self.report({'ERROR'}, f"Ollama executable not found: {ollama_path}")
                return {'CANCELLED'}
            
            # Stop previous model if one is loaded
            if props.model_is_preloaded and props.preloaded_model_name:
                print(f"Advanced AI: Stopping previous model: {props.preloaded_model_name}")
                subprocess.run([str(ollama_path), "stop", props.preloaded_model_name], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            
            # Pre-load the new model
            print(f"Advanced AI: Pre-loading model {model_name}")
            subprocess.Popen([str(ollama_path), "run", model_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Update state
            props.current_model_display = model_name
            props.model_is_preloaded = True
            props.preloaded_model_name = model_name
            
            self.report({'INFO'}, f"Pre-loading model: {model_name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to pre-load model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_LoadNewModel(bpy.types.Operator):
    """Load new model and replace the current one"""
    bl_idname = "advanced_ai.load_new_model"
    bl_label = "Load Model"
    bl_description = "Load new model and stop the previous one"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_name = props.selected_model.strip()
        
        if not model_name:
            self.report({'WARNING'}, "No model selected")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Get Ollama executable path
            ollama_path = Path(props.ollama_executable_path)
            
            if not ollama_path.exists():
                self.report({'ERROR'}, f"Ollama executable not found: {ollama_path}")
                return {'CANCELLED'}
            
            # Stop all models first (clean slate)
            print(f"Advanced AI: Stopping all models before loading new one")
            subprocess.run([str(ollama_path), "stop"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            
            # Load the new model
            print(f"Advanced AI: Loading new model {model_name}")
            subprocess.Popen([str(ollama_path), "run", model_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Update state
            props.current_model_display = model_name
            props.model_is_preloaded = True
            props.preloaded_model_name = model_name
            
            self.report({'INFO'}, f"Loading model: {model_name} (replacing previous)")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StartPreloadedModel(bpy.types.Operator):
    """Start/resume the pre-loaded model"""
    bl_idname = "advanced_ai.start_preloaded_model"
    bl_label = "Start Pre-loaded"
    bl_description = "Start the pre-loaded model"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        if not props.preloaded_model_name:
            self.report({'WARNING'}, "No pre-loaded model found")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Get Ollama executable path
            ollama_path = Path(props.ollama_executable_path)
            
            if not ollama_path.exists():
                self.report({'ERROR'}, f"Ollama executable not found: {ollama_path}")
                return {'CANCELLED'}
            
            # Start the pre-loaded model
            model_name = props.preloaded_model_name
            print(f"Advanced AI: Starting pre-loaded model {model_name}")
            subprocess.Popen([str(ollama_path), "run", model_name], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            props.model_is_preloaded = True
            
            self.report({'INFO'}, f"Started pre-loaded model: {model_name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start pre-loaded model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_TestModelConnection(bpy.types.Operator):
    """Test if the current model responds via Ollama API"""
    bl_idname = "advanced_ai.test_model_connection"
    bl_label = "Test Model"
    bl_description = "Send a test message to verify the model is working"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        try:
            import requests
            import json
            
            # Test connection to Ollama API
            model_name = props.current_model_display
            test_prompt = "Hello, please respond with just 'OK' to confirm you're working."
            
            payload = {
                "model": model_name,
                "prompt": test_prompt,
                "stream": False
            }
            
            print(f"Advanced AI: Testing model {model_name}...")
            
            # Send test request
            response = requests.post("http://localhost:11434/api/generate", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'No response')
                
                # Show first part of response
                preview = ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
                
                if props.model_is_preloaded:
                    self.report({'INFO'}, f"Pre-loaded model {model_name} responded: {preview}")
                else:
                    self.report({'INFO'}, f"Model {model_name} responded: {preview}")
                
            else:
                self.report({'ERROR'}, f"API Error: HTTP {response.status_code}")
                return {'CANCELLED'}
            
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, "Cannot connect to Ollama API. Is Ollama running?")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Test failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StopPreloadedModel(bpy.types.Operator):
    """Stop the pre-loaded model"""
    bl_idname = "advanced_ai.stop_preloaded_model"
    bl_label = "Stop Pre-loaded"
    bl_description = "Stop the pre-loaded model"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        if not props.preloaded_model_name:
            self.report({'WARNING'}, "No pre-loaded model found")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Get Ollama executable path
            ollama_path = Path(props.ollama_executable_path)
            
            if not ollama_path.exists():
                self.report({'ERROR'}, f"Ollama executable not found: {ollama_path}")
                return {'CANCELLED'}
            
            # Stop the pre-loaded model
            model_name = props.preloaded_model_name
            print(f"Advanced AI: Stopping pre-loaded model {model_name}")
            subprocess.run([str(ollama_path), "stop", model_name], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            
            props.model_is_preloaded = False
            
            self.report({'INFO'}, f"Stopped pre-loaded model: {model_name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to stop pre-loaded model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_LaunchMonitor(bpy.types.Operator):
    """Launch the AI usage monitor"""
    bl_idname = "advanced_ai.launch_monitor"
    bl_label = "Launch Monitor"
    bl_description = "Open AI usage monitoring window (separate from addon)"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            import subprocess
            from pathlib import Path
            
            # Find the ai_monitor.bat file
            niout_dir = get_niout_directory()
            monitor_file = niout_dir.parent / "ai_monitor.bat"
            
            if monitor_file.exists():
                # Launch monitor in new console window
                subprocess.Popen([str(monitor_file)], 
                               cwd=str(niout_dir.parent),
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                self.report({'INFO'}, "AI Monitor launched in separate window")
            else:
                self.report({'ERROR'}, f"Monitor file not found: {monitor_file}")
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to launch monitor: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_BrowseModelDirectory(bpy.types.Operator):
    """Browse model directory and list available models"""
    bl_idname = "advanced_ai.browse_model_directory"
    bl_label = "Browse Models"
    bl_description = "Browse the model directory and show available models"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_dir = props.model_directory_path.strip()
        
        if not model_dir:
            self.report({'WARNING'}, "Model directory path not set")
            return {'CANCELLED'}
        
        try:
            from pathlib import Path
            model_dir_obj = Path(model_dir)
            
            if not model_dir_obj.exists():
                self.report({'ERROR'}, f"Model directory not found: {model_dir}")
                return {'CANCELLED'}
            
            # List available models in directory
            models_found = []
            
            # Search for model directories
            for item in model_dir_obj.iterdir():
                if item.is_dir():
                    # Check if it contains model variants
                    for variant in item.iterdir():
                        if variant.is_dir():
                            # Format as model:variant
                            model_name = f"{item.name}:{variant.name}"
                            models_found.append(model_name)
            
            if models_found:
                # Set first model as selected if none selected
                if not props.selected_model:
                    props.selected_model = models_found[0]
                    props.current_model_display = models_found[0]
                
                models_str = ', '.join(models_found[:5])  # Show first 5
                if len(models_found) > 5:
                    models_str += f" and {len(models_found) - 5} more"
                
                self.report({'INFO'}, f"Found models: {models_str}")
            else:
                self.report({'WARNING'}, "No models found in directory")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error browsing models: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_BrowseModel(bpy.types.Operator):
    """Browse for specific model file and set model name"""
    bl_idname = "advanced_ai.browse_model"
    bl_label = "Browse Model File"
    bl_description = "Browse to a specific model file and extract its name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        model_path = props.model_file_path.strip()
        
        if not model_path:
            self.report({'WARNING'}, "Please browse to select a model file first")
            return {'CANCELLED'}
        
        try:
            from pathlib import Path
            model_path_obj = Path(model_path)
            
            if not model_path_obj.exists():
                self.report({'ERROR'}, f"Model file not found: {model_path}")
                return {'CANCELLED'}
            
            # Extract model name from path
            path_parts = model_path_obj.parts
            model_name = ""
            
            # Search for model name patterns in path
            for i, part in enumerate(path_parts):
                # Check for common model names
                model_names = ['deepseek-r1', 'qwen3', 'llama', 'llama2', 'llama3', 'mistral', 'codellama', 'gemma', 'phi', 'vicuna']
                if part.lower() in [m.lower() for m in model_names] or any(m in part.lower() for m in ['llama', 'gemma', 'phi']):
                    if i + 1 < len(path_parts):
                        variant = path_parts[i + 1]
                        # Check for size patterns like "8b", "4b", "1b", "13b", "70b"
                        if variant.lower().endswith('b') and variant[:-1].replace('.', '').isdigit():
                            model_name = f"{part}:{variant}"
                            break
                        elif variant.replace('.', '').replace('v', '').isdigit():
                            model_name = f"{part}:{variant}"
                            break
            
            # Fallback: try to guess from filename or parent folders
            if not model_name:
                parent_name = model_path_obj.parent.name
                grandparent_name = model_path_obj.parent.parent.name
                
                if ':' not in parent_name and grandparent_name:
                    model_name = f"{grandparent_name}:{parent_name}"
                else:
                    model_name = parent_name
            
            if model_name:
                props.selected_model = model_name
                props.current_model_display = model_name
                self.report({'INFO'}, f"Model set to: {model_name}")
            else:
                self.report({'WARNING'}, "Could not determine model name from path. Please enter manually.")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error processing model file: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_CloseAllModels(bpy.types.Operator):
    """Close all running models"""
    bl_idname = "advanced_ai.close_all_models"
    bl_label = "Close All Models"
    bl_description = "Close all currently running AI models"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            import subprocess
            import platform
            
            # Simple approach - just kill all ollama processes
            if platform.system() == "Windows":
                # Kill both ollama.exe and ollama app.exe processes
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    print("Advanced AI: Stopped ollama.exe")
                except:
                    pass
                
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "ollama app.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    print("Advanced AI: Stopped ollama app.exe")
                except:
                    pass
            else:
                # Kill ollama processes on Linux/Mac
                subprocess.run(["pkill", "-f", "ollama"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                print("Advanced AI: Stopped ollama processes")
            
            self.report({'INFO'}, "All models closed")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error closing models: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class ADVANCEDAI_OT_StartCurrentModel(bpy.types.Operator):
    """Start the model based on the file browser selection"""
    bl_idname = "advanced_ai.start_current_model"
    bl_label = "Start Current Model"
    bl_description = "Start the model selected in the file browser"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.advanced_ai_props
        
        # Get the model name from the file browser selection
        model_path = props.model_file_path.strip()
        if not model_path:
            self.report({'WARNING'}, "Please browse and select a model file first")
            return {'CANCELLED'}
        
        try:
            import subprocess
            from pathlib import Path
            
            # Extract model name from the file path
            model_path_obj = Path(model_path)
            
            if not model_path_obj.exists():
                self.report({'ERROR'}, f"Model file not found: {model_path}")
                return {'CANCELLED'}
            
            # Get model name (same logic as browse_model operator)
            path_parts = model_path_obj.parts
            model_name = ""
            
            # Search for model name patterns in path
            for i, part in enumerate(path_parts):
                model_names = ['deepseek-r1', 'qwen3', 'llama', 'llama2', 'llama3', 'mistral', 'codellama', 'gemma', 'phi', 'vicuna']
                if part.lower() in [m.lower() for m in model_names] or any(m in part.lower() for m in ['llama', 'gemma', 'phi']):
                    if i + 1 < len(path_parts):
                        variant = path_parts[i + 1]
                        if variant.lower().endswith('b') and variant[:-1].replace('.', '').isdigit():
                            model_name = f"{part}:{variant}"
                            break
                        elif variant.replace('.', '').replace('v', '').isdigit():
                            model_name = f"{part}:{variant}"
                            break
            
            # Fallback
            if not model_name:
                parent_name = model_path_obj.parent.name
                grandparent_name = model_path_obj.parent.parent.name
                if ':' not in parent_name and grandparent_name:
                    model_name = f"{grandparent_name}:{parent_name}"
                else:
                    model_name = parent_name
            
            if not model_name:
                self.report({'ERROR'}, "Could not determine model name from file path")
                return {'CANCELLED'}
            
            # Start the model using simple subprocess call
            print(f"Advanced AI: Starting model {model_name}")
            subprocess.Popen(["C:\\Users\\0-0\\AppData\\Local\\Programs\\Ollama\\ollama.exe", "run", model_name])
            
            # Update the current model display
            props.current_model_display = model_name
            props.selected_model = model_name
            
            self.report({'INFO'}, f"Starting model: {model_name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ADVANCEDAI_OT_SendMessage)
    bpy.utils.register_class(ADVANCEDAI_OT_ClearMessage)
    bpy.utils.register_class(ADVANCEDAI_OT_RefreshResponse)
    bpy.utils.register_class(ADVANCEDAI_OT_LoadLatestResponse)
    bpy.utils.register_class(ADVANCEDAI_OT_ToggleMonitoring)
    bpy.utils.register_class(ADVANCEDAI_OT_CopyResponse)
    bpy.utils.register_class(ADVANCEDAI_OT_SaveSettings)
    bpy.utils.register_class(ADVANCEDAI_OT_ClearResponses)
    bpy.utils.register_class(ADVANCEDAI_OT_ClearMemory)
    bpy.utils.register_class(ADVANCEDAI_OT_ReinforcePrompt)
    bpy.utils.register_class(ADVANCEDAI_OT_StartOllama)
    bpy.utils.register_class(ADVANCEDAI_OT_StopOllama)
    bpy.utils.register_class(ADVANCEDAI_OT_StartSelectedModel)
    bpy.utils.register_class(ADVANCEDAI_OT_TerminateAllModels)
    bpy.utils.register_class(ADVANCEDAI_OT_SetModel)
    bpy.utils.register_class(ADVANCEDAI_OT_SetAndPreloadModel)
    bpy.utils.register_class(ADVANCEDAI_OT_LoadNewModel)
    bpy.utils.register_class(ADVANCEDAI_OT_StartPreloadedModel)
    bpy.utils.register_class(ADVANCEDAI_OT_StopPreloadedModel)
    bpy.utils.register_class(ADVANCEDAI_OT_BrowseModelDirectory)
    bpy.utils.register_class(ADVANCEDAI_OT_BrowseModel)
    bpy.utils.register_class(ADVANCEDAI_OT_TestModelConnection)
    bpy.utils.register_class(ADVANCEDAI_OT_LaunchMonitor)
    bpy.utils.register_class(ADVANCEDAI_OT_CloseAllModels)
    bpy.utils.register_class(ADVANCEDAI_OT_StartCurrentModel)

def unregister():
    bpy.utils.unregister_class(ADVANCEDAI_OT_StartCurrentModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_CloseAllModels)
    bpy.utils.unregister_class(ADVANCEDAI_OT_LaunchMonitor)
    bpy.utils.unregister_class(ADVANCEDAI_OT_TestModelConnection)
    bpy.utils.unregister_class(ADVANCEDAI_OT_BrowseModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_BrowseModelDirectory)
    bpy.utils.unregister_class(ADVANCEDAI_OT_StopPreloadedModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_StartPreloadedModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_LoadNewModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_SetAndPreloadModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_SetModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_TerminateAllModels)
    bpy.utils.unregister_class(ADVANCEDAI_OT_StartSelectedModel)
    bpy.utils.unregister_class(ADVANCEDAI_OT_StopOllama)
    bpy.utils.unregister_class(ADVANCEDAI_OT_StartOllama)
    bpy.utils.unregister_class(ADVANCEDAI_OT_ReinforcePrompt)
    bpy.utils.unregister_class(ADVANCEDAI_OT_ClearMemory)
    bpy.utils.unregister_class(ADVANCEDAI_OT_ClearResponses)
    bpy.utils.unregister_class(ADVANCEDAI_OT_SaveSettings)
    bpy.utils.unregister_class(ADVANCEDAI_OT_CopyResponse)
    bpy.utils.unregister_class(ADVANCEDAI_OT_ToggleMonitoring)
    bpy.utils.unregister_class(ADVANCEDAI_OT_LoadLatestResponse)
    bpy.utils.unregister_class(ADVANCEDAI_OT_RefreshResponse)
    bpy.utils.unregister_class(ADVANCEDAI_OT_ClearMessage)
    bpy.utils.unregister_class(ADVANCEDAI_OT_SendMessage)
