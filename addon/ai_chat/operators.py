import bpy
import subprocess
import os
import re
from pathlib import Path

class AICHAT_OT_SendMessage(bpy.types.Operator):
    """Send message to AI"""
    bl_idname = "ai_chat.send_message"
    bl_label = "Send Message"
    bl_description = "Send your message to AI"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.ai_chat
        
        # Get message
        message = props.message.strip()
        if not message:
            self.report({'WARNING'}, "Please enter a message")
            return {'CANCELLED'}
        
        try:
            # Ensure paths point to odin_grab/a_astitnet/niout
            try:
                print("AI Chat: Send clicked — preparing paths and launch...")
                current = Path(__file__).parent
                a_astitnet_path = None

                # 1) Prefer base_path if valid
                if props.base_path:
                    bp = Path(props.base_path)
                    if bp.exists():
                        a_astitnet_path = bp
                        print(f"AI Chat: Using base_path from UI: {a_astitnet_path}")

                # 2) Search up for odin_grab/a_astitnet from this file
                if not a_astitnet_path:
                    for parent in [current] + list(current.parents):
                        if parent.name.lower() == 'odin_grab':
                            cand = parent / 'a_astitnet'
                            if cand.exists():
                                a_astitnet_path = cand
                                break
                        if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                            a_astitnet_path = parent
                            break
                        og = parent / 'odin_grab'
                        if og.exists():
                            cand = og / 'a_astitnet'
                            if cand.exists():
                                a_astitnet_path = cand
                                break

                # 3) Desktop fallbacks
                if not a_astitnet_path:
                    desktop = Path.home() / 'Desktop' / 'Odin Grab' / 'a_astitnet'
                    if desktop.exists():
                        a_astitnet_path = desktop
                        print(f"AI Chat: Found a_astitnet on Desktop: {a_astitnet_path}")
                if not a_astitnet_path:
                    share_path = Path('C:/File/Desktop/Odin Grab/a_astitnet')
                    if share_path.exists():
                        a_astitnet_path = share_path
                        print(f"AI Chat: Found shared a_astitnet: {a_astitnet_path}")

                if a_astitnet_path and a_astitnet_path.exists():
                    # Update props paths to match this base
                    desired_input = a_astitnet_path / 'niout' / 'input.txt'
                    desired_output = a_astitnet_path / 'niout' / 'response.txt'
                    if Path(props.input_path) != desired_input:
                        props.input_path = str(desired_input)
                        print(f"AI Chat: Auto-set input_path to {desired_input}")
                    if Path(props.output_path) != desired_output:
                        props.output_path = str(desired_output)
                        print(f"AI Chat: Auto-set output_path to {desired_output}")
                    if not props.base_path:
                        props.base_path = str(a_astitnet_path)
                    print(f"AI Chat: Using niout dir: {a_astitnet_path / 'niout'}")
                else:
                    print("AI Chat: Could not resolve a_astitnet path via UI, parents, or Desktop fallbacks")
            except Exception as e:
                print(f"AI Chat: Path auto-correct failed: {e}")
            
            # Do not create input file here; the launcher batch will handle it
            print(f"AI Chat: Skipping input file write (launcher will create niout/input.txt)")
            
            # Do not write model_config here; the launcher will handle it
            print(f"AI Chat: Selected model for launcher: {props.selected_model}")
            
            # Clear input and set waiting message
            props.message = ""
            props.response = "Processing your request..."
            
            # Auto-run Ollama script if enabled
            if props.auto_run_ollama:
                try:
                    launched = False
                    # Prefer launching the portable chat batch (non-interactive)
                    current = Path(__file__).parent
                    a_astitnet_path = None
                    for parent in [current] + list(current.parents):
                        if parent.name.lower() == 'odin_grab':
                            a_astitnet_path = parent / 'a_astitnet'
                            break
                        if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                            a_astitnet_path = parent
                            break
                        og = parent / 'odin_grab'
                        if og.exists():
                            a_astitnet_path = og / 'a_astitnet'
                            break
                    if (not a_astitnet_path or not a_astitnet_path.exists()) and props.base_path:
                        bp = Path(props.base_path)
                        if bp.exists():
                            a_astitnet_path = bp
                            print(f"AI Chat: Using base_path fallback: {a_astitnet_path}")
                    if a_astitnet_path and a_astitnet_path.exists():
                        print(f"AI Chat: Launch directory set to {a_astitnet_path}")
                        print(f"AI Chat: Message length {len(message)}; model '{props.selected_model}'")
                        
                        # Look specifically for chat_with_portable_python.bat first
                        batch = a_astitnet_path / "chat_with_portable_python.bat"
                        print(f"AI Chat: Checking for batch file: {batch}")
                        print(f"AI Chat: Directory contents: {list(a_astitnet_path.glob('*.bat'))}")
                        print(f"AI Chat: Batch file exists: {batch.exists()}")
                        
                        if batch.exists():
                            try:
                                # Launch the batch file with proper arguments
                                if os.name == 'nt':
                                    cmd = [str(batch), "-p", message, "-m", props.selected_model]
                                    print(f"AI Chat: Launching with command: {cmd} (cwd={a_astitnet_path})")
                                    print(f"AI Chat: Working directory: {os.getcwd()}")
                                    
                                    # Use shell=True to properly execute batch file
                                    process = subprocess.Popen(
                                        cmd, 
                                        cwd=str(a_astitnet_path), 
                                        shell=True,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE
                                    )
                                    print(f"AI Chat: Batch file started with PID: {process.pid}")
                                    
                                    # Give it a moment to start
                                    import time
                                    time.sleep(1)
                                    
                                    # Check if process is still running
                                    poll_result = process.poll()
                                    if poll_result is None:
                                        print(f"AI Chat: Process is running (PID: {process.pid})")
                                    else:
                                        print(f"AI Chat: Process exited quickly with code: {poll_result}")
                                else:
                                    # For non-Windows, try bash
                                    cmd = ["bash", str(batch), "-p", message, "-m", props.selected_model]
                                    print(f"AI Chat: Launching with command: {cmd} (cwd={a_astitnet_path})")
                                    subprocess.Popen(cmd, cwd=str(a_astitnet_path))
                                
                                print(f"AI Chat: Successfully launched {batch.name}")
                                launched = True
                                
                            except Exception as e:
                                print(f"AI Chat: Failed to launch {batch.name}: {e}")
                        else:
                            print(f"AI Chat: Batch file not found: {batch}")
                        # If batch file not found, try additional fallback names
                        if not launched:
                            fallback_names = ["chat_portable.bat", "chat with Portable Python.bat", "Chat with Portable Python.bat"]
                            print("AI Chat: Primary batch not found, trying fallbacks...")
                            
                            for fallback_name in fallback_names:
                                fallback_batch = a_astitnet_path / fallback_name
                                print(f"AI Chat: Checking fallback: {fallback_batch}")
                                
                                if fallback_batch.exists():
                                    try:
                                        if os.name == 'nt':
                                            cmd = [str(fallback_batch), "-p", message, "-m", props.selected_model]
                                            print(f"AI Chat: Launching fallback with command: {cmd}")
                                            process = subprocess.Popen(
                                                cmd, 
                                                cwd=str(a_astitnet_path), 
                                                shell=True,
                                                creationflags=subprocess.CREATE_NEW_CONSOLE
                                            )
                                            print(f"AI Chat: Fallback batch started with PID: {process.pid}")
                                        else:
                                            cmd = ["bash", str(fallback_batch), "-p", message, "-m", props.selected_model]
                                            subprocess.Popen(cmd, cwd=str(a_astitnet_path))
                                        
                                        print(f"AI Chat: Successfully launched fallback {fallback_name}")
                                        launched = True
                                        break
                                        
                                    except Exception as e:
                                        print(f"AI Chat: Failed to launch fallback {fallback_name}: {e}")
                    if not launched:
                        # Fallback: verify/correct the python script path and launch it
                        script_path_str = props.ollama_script_path.strip()
                        script_path = Path(script_path_str) if script_path_str else None
                        if not script_path or not script_path.exists():
                            detected = None
                            for parent in [current] + list(current.parents):
                                if parent.name.lower() == 'odin_grab':
                                    cand = parent / 'a_astitnet' / 'ollama_chat.py'
                                    if cand.exists():
                                        detected = cand
                                        break
                                if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                                    cand = parent / 'ollama_chat.py'
                                    if cand.exists():
                                        detected = cand
                                        break
                                og = parent / 'odin_grab'
                                if og.exists():
                                    cand = og / 'a_astitnet' / 'ollama_chat.py'
                                    if cand.exists():
                                        detected = cand
                                        break
                            if detected:
                                props.ollama_script_path = str(detected)
                                print(f"AI Chat: Auto-set ollama_script_path to {detected}")
                        # Start script (run_ollama_script does its own Python detection)
                        print(f"AI Chat: Falling back to Python script: {props.ollama_script_path}")
                        self.run_ollama_script(props.ollama_script_path)
                        launched = True
                    if launched:
                        self.report({'INFO'}, "Message sent! Chat started.")
                    else:
                        self.report({'WARNING'}, "Message sent, but could not start chat process.")
                except Exception as e:
                    self.report({'WARNING'}, f"Message sent, but failed to start script: {e}")
            else:
                self.report({'INFO'}, "Message sent! Run Ollama script manually.")
            
            # Prepare versioned response tracking
            if props.use_versioned_responses:
                try:
                    niout_dir = Path(props.output_path).parent
                    max_idx = 0
                    pattern = re.compile(r"response_(\d+)\.txt$")
                    if niout_dir.exists():
                        for p in niout_dir.iterdir():
                            if p.is_file():
                                m = pattern.match(p.name)
                                if m:
                                    idx = int(m.group(1))
                                    if idx > max_idx:
                                        max_idx = idx
                    props.last_seen_index = max_idx
                    print(f"AI Chat: Initialized last_seen_index={max_idx}")
                except Exception as e:
                    print(f"AI Chat: init version tracking failed: {e}")
            
            # Set up monitoring for response
            props.waiting_for_response = True
            
            # Register a simple timer to check after 3 seconds
            bpy.app.timers.register(
                lambda: self.check_and_update_response(context),
                first_interval=3.0
            )
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to send message: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def run_ollama_script(self, script_path):
        """Run the Ollama script in the background"""
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Ollama script not found: {script_path}")
        
        # Get the directory containing the script
        script_dir = script_path.parent
        
        # Run the script in the background - try different python commands
        python_commands = []
        
        # Check for portable Python in odin_grab/a_astitnet structure
        try:
            current = Path(__file__).parent
            for parent in [current] + list(current.parents):
                # Look for odin_grab folder first
                if parent.name.lower() == 'odin_grab':
                    portable_python = parent / 'a_astitnet' / "python_portable" / "python.exe"
                    if portable_python.exists():
                        python_commands.insert(0, str(portable_python))
                        print(f"AI Chat: Found portable Python: {portable_python}")
                    break
                # Check if we're already in a_astitnet under odin_grab
                if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                    portable_python = parent / "python_portable" / "python.exe"
                    if portable_python.exists():
                        python_commands.insert(0, str(portable_python))
                        print(f"AI Chat: Found portable Python: {portable_python}")
                    break
                # Check for odin_grab as subdirectory
                odin_grab_path = parent / 'odin_grab'
                if odin_grab_path.exists():
                    portable_python = odin_grab_path / 'a_astitnet' / "python_portable" / "python.exe"
                    if portable_python.exists():
                        python_commands.insert(0, str(portable_python))
                        print(f"AI Chat: Found portable Python: {portable_python}")
                    break
        except Exception as e:
            print(f"AI Chat: Error checking for portable Python: {e}")
        
        # Add system Python commands
        if os.name == 'nt':  # Windows
            python_commands.extend(["python", "py", "python3", "python.exe"])
        else:  # Linux/Mac
            python_commands.extend(["python3", "python"])
        
        script_started = False
        for python_cmd in python_commands:
            try:
                if os.name == 'nt':  # Windows
                    subprocess.Popen(
                        [python_cmd, str(script_path)], 
                        cwd=str(script_dir),
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        [python_cmd, str(script_path)], 
                        cwd=str(script_dir)
                    )
                script_started = True
                print(f"AI Chat: Started script with {python_cmd}")
                break
            except FileNotFoundError:
                continue
        
        if not script_started:
            raise FileNotFoundError("No Python interpreter found. Portable Python not found; tried python, py, python3")
    
    def check_and_update_response(self, context):
        """Check for response and update UI - called by timer"""
        props = context.window_manager.ai_chat
        
        try:
            if props.use_versioned_responses:
                # Look for newest response_N.txt greater than last_seen_index
                niout_dir = Path(props.output_path).parent
                max_idx = props.last_seen_index
                latest_file = None
                pattern = re.compile(r"response_(\d+)\.txt$")
                if niout_dir.exists():
                    for p in niout_dir.iterdir():
                        if p.is_file():
                            m = pattern.match(p.name)
                            if m:
                                idx = int(m.group(1))
                                if idx > max_idx:
                                    max_idx = idx
                                    latest_file = p
                if latest_file is not None:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        props.response = content
                        props.last_seen_index = max_idx
                        props.waiting_for_response = False
                        # Force UI redraw
                        for area in context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                        print(f"AI Chat: Loaded {latest_file.name} (max_idx={max_idx})")
                        return None  # Stop timer
                else:
                    print(f"AI Chat: Scanned niout — max_idx={max_idx}, last_seen={props.last_seen_index}; no new response_N yet")
                    # Fallback: if no versioned file detected, try response.txt
                    output_path = Path(props.output_path)
                    if output_path.exists():
                        with open(output_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        if content:
                            props.response = content
                            props.waiting_for_response = False
                            for area in context.screen.areas:
                                if area.type == 'VIEW_3D':
                                    area.tag_redraw()
                            print("AI Chat: Fallback loaded response.txt")
                            return None
                # keep waiting
                if props.waiting_for_response:
                    print("AI Chat: Waiting for response_N.txt, checking again in 2s")
                    return 2.0
            else:
                output_path = Path(props.output_path)
                if output_path.exists():
                    # Read the response file
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        # Update response and stop waiting
                        props.response = content
                        props.waiting_for_response = False
                        # Force UI redraw
                        for area in context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                        print(f"AI Chat: Response loaded successfully")
                        return None  # Stop timer
                # keep waiting
                if props.waiting_for_response:
                    print("AI Chat: Still waiting for response, checking again in 2 seconds")
                    return 2.0  # Check again in 2 seconds
        except Exception as e:
            props.response = f"Error reading response: {e}"
            props.waiting_for_response = False
            print(f"AI Chat: Error: {e}")
        
        return None  # Stop timer

class AICHAT_OT_ClearMessage(bpy.types.Operator):
    """Clear the input message"""
    bl_idname = "ai_chat.clear_message"
    bl_label = "Clear"
    bl_description = "Clear the input message"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        context.window_manager.ai_chat.message = ""
        return {'FINISHED'}

class AICHAT_OT_RefreshResponse(bpy.types.Operator):
    """Manually refresh response"""
    bl_idname = "ai_chat.refresh_response"
    bl_label = "Refresh"
    bl_description = "Manually check for new response"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.ai_chat
        
        try:
            output_path = Path(props.output_path)
            
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
            props.response = f"Error reading response: {e}"
            self.report({'ERROR'}, f"Failed to refresh: {e}")
        
        return {'FINISHED'}

class AICHAT_OT_StopAllModels(bpy.types.Operator):
    """Stop all running AI models"""
    bl_idname = "ai_chat.stop_all_models"
    bl_label = "Stop All Models"
    bl_description = "Stop all running Ollama AI models"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            from . import model_manager
            
            success = model_manager.stop_all_models()
            
            if success:
                self.report({'INFO'}, "✅ All AI models stopped successfully")
            else:
                self.report({'WARNING'}, "⚠️ Some models may still be running")
                
        except Exception as e:
            self.report({'ERROR'}, f"❌ Failed to stop models: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class AICHAT_OT_StartSelectedModel(bpy.types.Operator):
    """Start the selected AI model"""
    bl_idname = "ai_chat.start_selected_model"
    bl_label = "Start Selected Model"
    bl_description = "Start the currently selected AI model"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.ai_chat
        model_name = props.selected_model.strip()
        
        if not model_name:
            self.report({'WARNING'}, "⚠️ No model selected")
            return {'CANCELLED'}
        
        # If it's a file path, extract model name from it
        if model_name.endswith('.bin') or '\\' in model_name or '/' in model_name:
            model_path = Path(model_name)
            if model_path.exists():
                # For file paths, we need to get model name differently
                # For now, let user type the model name instead
                self.report({'WARNING'}, f"📁 Please enter model name (like 'qwen3:4b') not file path")
                return {'CANCELLED'}
        
        try:
            from . import model_manager
            
            success = model_manager.start_model(model_name)
            
            if success:
                self.report({'INFO'}, f"✅ Model {model_name} started successfully")
            else:
                self.report({'ERROR'}, f"❌ Failed to start model {model_name}")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"❌ Failed to start model: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class AICHAT_OT_BrowseModel(bpy.types.Operator):
    """Browse for model file and extract model name"""
    bl_idname = "ai_chat.browse_model"
    bl_label = "Browse Model"
    bl_description = "Browse to a model file and extract its name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.ai_chat
        model_path = props.model_file_path.strip()
        
        if not model_path:
            self.report({'WARNING'}, "📁 Please browse to select a model file first")
            return {'CANCELLED'}
        
        try:
            model_path_obj = Path(model_path)
            
            if not model_path_obj.exists():
                self.report({'ERROR'}, f"❌ Model file not found: {model_path}")
                return {'CANCELLED'}
            
            # Extract model name from path
            # Look for patterns like deepseek-r1/8b or qwen3/4b in the path
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
                        # Also check for versions like "v1.5", "3.1"
                        elif variant.replace('.', '').replace('v', '').isdigit():
                            model_name = f"{part}:{variant}"
                            break
            
            # Fallback: try to guess from filename or parent folders
            if not model_name:
                # Look at parent directory names
                parent_name = model_path_obj.parent.name
                grandparent_name = model_path_obj.parent.parent.name
                
                if ':' not in parent_name and grandparent_name:
                    # Try combining grandparent:parent
                    model_name = f"{grandparent_name}:{parent_name}"
                else:
                    model_name = parent_name
            
            if model_name:
                props.selected_model = model_name
                self.report({'INFO'}, f"✅ Model set to: {model_name}")
            else:
                self.report({'WARNING'}, "⚠️ Could not determine model name from path. Please enter manually.")
                
        except Exception as e:
            self.report({'ERROR'}, f"❌ Error processing model file: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class AICHAT_OT_InstallDependencies(bpy.types.Operator):
    """Install portable Python and dependencies"""
    bl_idname = "ai_chat.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Install portable Python and required modules (isolated)"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        import subprocess
        import sys
        from pathlib import Path
        
        try:
            # Find the a_astitnet directory within odin_grab structure
            current = Path(__file__).parent
            
            # Search up for odin_grab/a_astitnet structure
            a_astitnet_path = None
            for parent in [current] + list(current.parents):
                # Look for odin_grab folder first
                if parent.name.lower() == 'odin_grab':
                    a_astitnet_path = parent / 'a_astitnet'
                    if a_astitnet_path.exists():
                        break
                # Check if we're already in a_astitnet under odin_grab
                if parent.name == 'a_astitnet' and parent.parent.name.lower() == 'odin_grab':
                    a_astitnet_path = parent
                    break
                # Check for odin_grab as subdirectory
                odin_grab_path = parent / 'odin_grab'
                if odin_grab_path.exists():
                    a_astitnet_path = odin_grab_path / 'a_astitnet'
                    if a_astitnet_path.exists():
                        break
            
            if not a_astitnet_path:
                self.report({'ERROR'}, "❌ Could not find a_astitnet directory")
                return {'CANCELLED'}
            
            # Path to install script
            install_script = a_astitnet_path / "install_python.py"
            
            if not install_script.exists():
                self.report({'ERROR'}, f"❌ Install script not found: {install_script}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "📅 Starting portable Python installation...")
            
            # Run the installer with Blender's Python (fallback)
            # This will download and setup a completely separate Python
            result = subprocess.run(
                [sys.executable, str(install_script)],
                cwd=str(a_astitnet_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                self.report({'INFO'}, "✅ Portable Python installed successfully! You can now use AI Chat.")
            else:
                self.report({'WARNING'}, "⚠️ Installation completed with warnings. Check the console.")
                
        except Exception as e:
            self.report({'ERROR'}, f"❌ Installation failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class AICHAT_OT_ClearResponses(bpy.types.Operator):
    """Delete all versioned response_N.txt files and reset state"""
    bl_idname = "ai_chat.clear_responses"
    bl_label = "Clear Responses"
    bl_description = "Delete response_*.txt files and clear output"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.window_manager.ai_chat
        try:
            niout_dir = Path(props.output_path).parent
            pattern = re.compile(r"response_(\d+)\.txt$")
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
                out = Path(props.output_path)
                if out.exists():
                    out.unlink()
            except Exception:
                pass
            props.last_seen_index = 0
            props.response = ""
            props.waiting_for_response = False
            self.report({'INFO'}, f"Cleared {deleted} response files")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear responses: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}

class AICHAT_OT_SaveSettings(bpy.types.Operator):
    """Save current settings to Blender preferences"""
    bl_idname = "ai_chat.save_settings"
    bl_label = "Save Settings"
    bl_description = "Save file paths and options to Blender preferences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            addon_id = __package__ if __package__ else "ai_chat"
            prefs = context.preferences.addons[addon_id].preferences
            props = context.window_manager.ai_chat
            
            prefs.pref_base_path = props.base_path
            prefs.pref_input_path = props.input_path
            prefs.pref_output_path = props.output_path
            prefs.pref_ollama_script_path = props.ollama_script_path
            prefs.pref_auto_run_ollama = props.auto_run_ollama
            prefs.pref_use_versioned = props.use_versioned_responses
            prefs.pref_selected_model = props.selected_model
            
            # Try to persist to disk
            try:
                bpy.ops.wm.save_userpref()
            except Exception:
                pass
            
            self.report({'INFO'}, "Settings saved to preferences")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save settings: {e}")
            return {'CANCELLED'}

class AICHAT_OT_LoadSettings(bpy.types.Operator):
    """Load settings from Blender preferences"""
    bl_idname = "ai_chat.load_settings"
    bl_label = "Load Settings"
    bl_description = "Load file paths and options from Blender preferences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            addon_id = __package__ if __package__ else "ai_chat"
            prefs = context.preferences.addons[addon_id].preferences
            props = context.window_manager.ai_chat
            
            # Only overwrite if prefs have values
            if prefs.pref_base_path:
                props.base_path = prefs.pref_base_path
            if prefs.pref_input_path:
                props.input_path = prefs.pref_input_path
            if prefs.pref_output_path:
                props.output_path = prefs.pref_output_path
            if prefs.pref_ollama_script_path:
                props.ollama_script_path = prefs.pref_ollama_script_path
            props.auto_run_ollama = prefs.pref_auto_run_ollama
            props.use_versioned_responses = prefs.pref_use_versioned
            if prefs.pref_selected_model:
                props.selected_model = prefs.pref_selected_model
            
            self.report({'INFO'}, "Settings loaded from preferences")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load settings: {e}")
            return {'CANCELLED'}

class AICHAT_OT_RefreshModels(bpy.types.Operator):
    """Refresh available models list"""
    bl_idname = "ai_chat.refresh_models"
    bl_label = "Refresh Models"
    bl_description = "Scan for available AI models"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            from . import model_manager
            
            models = model_manager.get_available_models()
            self.report({'INFO'}, f"🔍 Found {len(models)} models: {', '.join(models)}")
            
            # Optionally set first model as selected if none selected
            props = context.window_manager.ai_chat
            if not props.selected_model and models:
                props.selected_model = models[0]
                
        except Exception as e:
            self.report({'ERROR'}, f"❌ Failed to refresh models: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AICHAT_OT_SendMessage)
    bpy.utils.register_class(AICHAT_OT_ClearMessage)
    bpy.utils.register_class(AICHAT_OT_RefreshResponse)
    bpy.utils.register_class(AICHAT_OT_StopAllModels)
    bpy.utils.register_class(AICHAT_OT_StartSelectedModel)
    bpy.utils.register_class(AICHAT_OT_BrowseModel)
    bpy.utils.register_class(AICHAT_OT_InstallDependencies)
    bpy.utils.register_class(AICHAT_OT_ClearResponses)
    bpy.utils.register_class(AICHAT_OT_SaveSettings)
    bpy.utils.register_class(AICHAT_OT_LoadSettings)
    bpy.utils.register_class(AICHAT_OT_RefreshModels)

def unregister():
    bpy.utils.unregister_class(AICHAT_OT_RefreshModels)
    bpy.utils.unregister_class(AICHAT_OT_LoadSettings)
    bpy.utils.unregister_class(AICHAT_OT_SaveSettings)
    bpy.utils.unregister_class(AICHAT_OT_ClearResponses)
    bpy.utils.unregister_class(AICHAT_OT_InstallDependencies)
    bpy.utils.unregister_class(AICHAT_OT_BrowseModel)
    bpy.utils.unregister_class(AICHAT_OT_StartSelectedModel)
    bpy.utils.unregister_class(AICHAT_OT_StopAllModels)
    bpy.utils.unregister_class(AICHAT_OT_RefreshResponse)
    bpy.utils.unregister_class(AICHAT_OT_ClearMessage)
    bpy.utils.unregister_class(AICHAT_OT_SendMessage)
