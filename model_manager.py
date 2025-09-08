#!/usr/bin/env python3
"""
Ollama Model Manager
Manages starting, stopping, and listing AI models
"""

import subprocess
import os
import json
import time
from pathlib import Path

# Auto-detect odin_grab/a_astitnet directory structure for model path
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
    
    # Fallback to original hardcoded path
    return Path(r"F:\a_astitnet")

# Model directory path
A_ASTITNET_PATH = find_a_astitnet_directory()
MODEL_MANIFESTS_DIR = A_ASTITNET_PATH / "ai mode" / "manifests" / "registry.ollama.ai" / "library"

class OllamaModelManager:
    """Manages Ollama AI models"""
    
    def __init__(self):
        self.models = []
        self.scan_models()
    
    def scan_models(self):
        """Scan for available models in the manifests directory"""
        self.models = []
        
        try:
            if MODEL_MANIFESTS_DIR.exists():
                for model_dir in MODEL_MANIFESTS_DIR.iterdir():
                    if model_dir.is_dir():
                        model_name = model_dir.name
                        # Check for variants/sizes
                        for variant_dir in model_dir.iterdir():
                            if variant_dir.is_dir():
                                variant_name = variant_dir.name
                                full_model_name = f"{model_name}:{variant_name}"
                                self.models.append(full_model_name)
                                print(f"Found model: {full_model_name}")
            
            # Also try to get models from ollama list command
            try:
                result = subprocess.run(
                    ["ollama", "list"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            model_name = line.split()[0]  # First column is model name
                            if model_name not in self.models:
                                self.models.append(model_name)
                                print(f"Found running model: {model_name}")
            except subprocess.TimeoutExpired:
                print("Ollama list command timed out")
            except Exception as e:
                print(f"Could not run ollama list: {e}")
        
        except Exception as e:
            print(f"Error scanning models: {e}")
        
        if not self.models:
            # Fallback to default models
            self.models = ["qwen3:4b", "deepseek-r1:8b"]
            print("Using default models")
        
        print(f"Available models: {self.models}")
        return self.models
    
    def get_available_models(self):
        """Get list of available models"""
        return self.models
    
    def stop_all_models(self):
        """Stop all running Ollama models/processes"""
        try:
            print("Stopping all Ollama models...")
            
            # Method 1: Try ollama stop (if it exists)
            try:
                subprocess.run(["ollama", "stop"], timeout=10, check=False)
            except:
                pass
            
            # Method 2: Kill ollama processes
            if os.name == 'nt':  # Windows
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "ollama.exe"], 
                        timeout=10, 
                        check=False,
                        capture_output=True
                    )
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "ollama_llama_server.exe"], 
                        timeout=10, 
                        check=False,
                        capture_output=True
                    )
                except Exception as e:
                    print(f"Windows process kill error: {e}")
            else:  # Linux/Mac
                try:
                    subprocess.run(
                        ["pkill", "-f", "ollama"], 
                        timeout=10, 
                        check=False
                    )
                except Exception as e:
                    print(f"Unix process kill error: {e}")
            
            print("✅ All Ollama models stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping models: {e}")
            return False
    
    def start_model(self, model_name):
        """Start a specific model"""
        try:
            print(f"Starting model: {model_name}")
            
            # Start ollama serve first (in background)
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                time.sleep(2)  # Give it time to start
            except Exception as e:
                print(f"Ollama serve might already be running: {e}")
            
            # Pull/start the specific model
            result = subprocess.run(
                ["ollama", "run", model_name, "Hello"], 
                timeout=30,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Model {model_name} started successfully")
                return True
            else:
                print(f"❌ Error starting {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout starting model {model_name}")
            return False
        except Exception as e:
            print(f"❌ Error starting model {model_name}: {e}")
            return False
    
    def is_model_running(self, model_name):
        """Check if a specific model is running"""
        try:
            result = subprocess.run(
                ["ollama", "ps"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return model_name in result.stdout
        except:
            return False

def main():
    """Main function for testing"""
    manager = OllamaModelManager()
    
    print("Available models:")
    for model in manager.get_available_models():
        print(f"  - {model}")
    
    # Example usage
    # manager.stop_all_models()
    # manager.start_model("qwen3:4b")

if __name__ == "__main__":
    main()
