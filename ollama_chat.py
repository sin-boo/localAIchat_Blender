#!/usr/bin/env python3
"""
Ollama Text File Interface
Reads from niout/input.txt, sends to local Ollama model, writes response to niout/response.txt
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen3:4b"

# Auto-detect odin_grab/a_astitnet directory structure
def find_a_astitnet_directory():
    """Find a_astitnet directory within odin_grab structure"""
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
        # Check for odin_grab as subdirectory
        odin_grab_path = parent / 'odin_grab'
        if odin_grab_path.exists():
            a_astitnet_path = odin_grab_path / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
    
    # Also try current working directory
    current_dir = Path.cwd()
    for parent in [current_dir] + list(current_dir.parents):
        # Look for odin_grab folder first
        if parent.name.lower() == 'odin_grab':
            a_astitnet_path = parent / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
        # Check for odin_grab as subdirectory
        odin_grab_path = parent / 'odin_grab'
        if odin_grab_path.exists():
            a_astitnet_path = odin_grab_path / 'a_astitnet'
            if a_astitnet_path.exists():
                return a_astitnet_path
    
    # Fallback to original hardcoded path
    return Path(r"F:\a_astitnet")

# Get paths based on a_astitnet location
A_ASTITNET_PATH = find_a_astitnet_directory()
INPUT_FILE = A_ASTITNET_PATH / "niout" / "input.txt"
OUTPUT_FILE = A_ASTITNET_PATH / "niout" / "response.txt"
MODEL_CONFIG_FILE = A_ASTITNET_PATH / "niout" / "model_config.txt"

def get_current_model():
    """Get the currently selected model from config file or use default"""
    try:
        if os.path.exists(MODEL_CONFIG_FILE):
            with open(MODEL_CONFIG_FILE, 'r') as f:
                model = f.read().strip()
                if model:
                    return model
    except Exception as e:
        print(f"Could not read model config: {e}")
    return DEFAULT_MODEL

def read_input_file():
    """Read the input file and return its content as the prompt"""
    try:
        # Try reading with different encodings
        encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(INPUT_FILE, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("Error: Could not read file with any encoding")
            return None
            
        if not content:
            print("Input file is empty")
            return None
            
        return content
    
    except FileNotFoundError:
        print(f"Input file {INPUT_FILE} not found!")
        return None
    except Exception as e:
        print(f"Error reading input file: {e}")
        return None

def send_to_ollama(prompt):
    """Send prompt to local Ollama model and get response"""
    try:
        current_model = get_current_model()
        payload = {
            "model": current_model,
            "prompt": prompt,
            "stream": False
        }
        
        print(f"Using model: {current_model}")
        print(f"Sending request to Ollama...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response received')
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure it's running on localhost:11434"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The model might be taking too long to respond."
    except Exception as e:
        return f"Error: {str(e)}"

def clean_response(response_text):
    """Clean up the response by removing thinking process and numbered formatting"""
    lines = response_text.split('\n')
    cleaned_lines = []
    in_thinking = False
    
    for line in lines:
        # Remove numbered prefixes like "1|", "2|", etc.
        if '|' in line and line.strip():
            parts = line.split('|', 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                line = parts[1].strip()
        
        # Skip thinking process
        if '<think>' in line:
            in_thinking = True
            continue
        elif '</think>' in line:
            in_thinking = False
            continue
        elif in_thinking:
            continue
        
        # Skip empty lines at the start, but keep them in the middle/end
        if line.strip() or cleaned_lines:
            cleaned_lines.append(line)
    
    # Join lines and clean up extra whitespace
    result = '\n'.join(cleaned_lines).strip()
    return result

def get_next_response_number():
    """Find the next response file number by checking existing files"""
    niout_dir = A_ASTITNET_PATH / "niout"
    max_num = 0
    
    if niout_dir.exists():
        for file in niout_dir.glob("response_*.txt"):
            try:
                # Extract number from filename like "response_5.txt"
                num_str = file.stem.replace("response_", "")
                num = int(num_str)
                if num > max_num:
                    max_num = num
            except (ValueError, AttributeError):
                continue
    
    return max_num + 1

def write_response_file(response_text):
    """Write the response to output file as clean plain text with versioning"""
    try:
        # Clean up the response first
        cleaned_response = clean_response(response_text)
        
        # Write main response file (for compatibility)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(cleaned_response)
        print(f"Response written to {OUTPUT_FILE}")
        
        # Also write versioned response file
        next_num = get_next_response_number()
        versioned_file = A_ASTITNET_PATH / "niout" / f"response_{next_num}.txt"
        
        with open(versioned_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_response)
        print(f"Versioned response written to {versioned_file}")
        
    except Exception as e:
        print(f"Error writing response file: {e}")

def main():
    """Main function"""
    print("Ollama Text File Interface")
    print("=" * 30)
    
    # Check if Ollama is running
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code != 200:
            print("Warning: Ollama might not be running properly")
    except:
        print("Error: Cannot connect to Ollama. Make sure it's running!")
        print("Start Ollama with: ollama serve")
        return
    
    # Read input
    prompt = read_input_file()
    if not prompt:
        print("No prompt found in input file or file is empty")
        return
    
    print(f"Found prompt: {prompt}")
    
    # Send to Ollama
    print("Processing with Ollama...")
    response = send_to_ollama(prompt)
    
    # Write response
    write_response_file(response)
    print("Done!")

if __name__ == "__main__":
    main()
