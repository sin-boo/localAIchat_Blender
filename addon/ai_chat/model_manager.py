#!/usr/bin/env python3
"""
Ollama Model Manager for Blender Addon
Direct integration without external imports
"""

import subprocess
import os
import time
from pathlib import Path

def get_available_models():
    """Scan for available models"""
    models = []
    
    # Method 1: Check manifests directory
    manifests_dir = Path(r"F:\a_astitnet\ai mode\manifests\registry.ollama.ai\library")
    try:
        if manifests_dir.exists():
            for model_dir in manifests_dir.iterdir():
                if model_dir.is_dir():
                    model_name = model_dir.name
                    # Check for variants/sizes
                    for variant_dir in model_dir.iterdir():
                        if variant_dir.is_dir():
                            variant_name = variant_dir.name
                            full_model_name = f"{model_name}:{variant_name}"
                            models.append(full_model_name)
                            print(f"Found model: {full_model_name}")
    except Exception as e:
        print(f"Error scanning manifests: {e}")
    
    # Method 2: Try ollama list command
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
                    if model_name not in models:
                        models.append(model_name)
                        print(f"Found running model: {model_name}")
    except Exception as e:
        print(f"Could not run ollama list: {e}")
    
    # Fallback to defaults if none found
    if not models:
        models = ["qwen3:4b", "deepseek-r1:8b"]
        print("Using default models")
    
    print(f"Available models: {models}")
    return models

def stop_all_models():
    """Stop all running Ollama models/processes"""
    try:
        print("Stopping all Ollama models...")
        
        # Method 1: Try ollama stop (if it exists)
        try:
            subprocess.run(["ollama", "stop"], timeout=10, check=False, capture_output=True)
        except:
            pass
        
        # Method 2: Kill ollama processes
        if os.name == 'nt':  # Windows
            try:
                # Kill main ollama process
                result1 = subprocess.run(
                    ["taskkill", "/F", "/IM", "ollama.exe"], 
                    timeout=10, 
                    check=False,
                    capture_output=True
                )
                # Kill llama server process  
                result2 = subprocess.run(
                    ["taskkill", "/F", "/IM", "ollama_llama_server.exe"], 
                    timeout=10, 
                    check=False,
                    capture_output=True
                )
                # Kill any python processes running ollama
                subprocess.run(
                    ["taskkill", "/F", "/FI", "IMAGENAME eq python.exe", "/FI", "WINDOWTITLE eq *ollama*"], 
                    timeout=10, 
                    check=False,
                    capture_output=True
                )
                print("Windows processes terminated")
            except Exception as e:
                print(f"Windows process kill error: {e}")
        else:  # Linux/Mac
            try:
                subprocess.run(
                    ["pkill", "-f", "ollama"], 
                    timeout=10, 
                    check=False
                )
                print("Unix processes terminated")
            except Exception as e:
                print(f"Unix process kill error: {e}")
        
        print("✅ All Ollama models stopped")
        return True
        
    except Exception as e:
        print(f"❌ Error stopping models: {e}")
        return False

def start_model(model_name):
    """Start a specific model"""
    try:
        print(f"Starting model: {model_name}")
        
        # Start ollama serve first (in background)
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
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

def is_model_running(model_name):
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
