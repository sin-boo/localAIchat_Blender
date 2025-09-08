#!/usr/bin/env python3
"""
Portable Python Installer for AI Chat System
Downloads and installs a minimal Python environment locally
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
from pathlib import Path

# Configuration
PYTHON_VERSION = "3.11.9"

# Auto-detect odin_grab/a_astitnet structure
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
    
    # Fallback to current directory
    return current

CURRENT_DIR = find_a_astitnet_directory()
PYTHON_DIR = CURRENT_DIR / "python_portable"
PYTHON_EXE = PYTHON_DIR / "python.exe"

def download_portable_python():
    """Download portable Python from python.org"""
    print("📥 Downloading portable Python...")
    
    # Windows embeddable Python URL
    if os.name == 'nt':  # Windows
        url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
        zip_path = CURRENT_DIR / "python_portable.zip"
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            print(f"✅ Downloaded: {zip_path}")
            return zip_path
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    else:
        print("❌ Portable Python installer only supports Windows currently")
        return None

def extract_python(zip_path):
    """Extract Python to local directory"""
    print("📂 Extracting Python...")
    
    try:
        # Create python directory
        PYTHON_DIR.mkdir(exist_ok=True)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PYTHON_DIR)
        
        print(f"✅ Extracted to: {PYTHON_DIR}")
        
        # Clean up zip file
        zip_path.unlink()
        
        return True
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def setup_pip():
    """Setup pip for the portable Python"""
    print("🔧 Setting up pip...")
    
    try:
        # Download get-pip.py
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = PYTHON_DIR / "get-pip.py"
        
        urllib.request.urlretrieve(get_pip_url, get_pip_path)
        
        # Run get-pip.py with our portable python
        result = subprocess.run(
            [str(PYTHON_EXE), str(get_pip_path)],
            cwd=str(PYTHON_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Pip installed successfully")
            
            # Clean up
            get_pip_path.unlink()
            return True
        else:
            print(f"❌ Pip installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Pip setup failed: {e}")
        return False

def install_requests():
    """Install requests module"""
    print("📦 Installing requests module...")
    
    try:
        pip_exe = PYTHON_DIR / "Scripts" / "pip.exe"
        if not pip_exe.exists():
            pip_exe = PYTHON_EXE  # fallback
            
        result = subprocess.run(
            [str(pip_exe), "install", "requests"],
            cwd=str(PYTHON_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Requests module installed")
            return True
        else:
            print(f"❌ Requests installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Requests installation failed: {e}")
        return False

def test_installation():
    """Test the portable Python installation"""
    print("🧪 Testing installation...")
    
    try:
        # Test basic Python
        result = subprocess.run(
            [str(PYTHON_EXE), "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Python version: {result.stdout.strip()}")
        else:
            print("❌ Python test failed")
            return False
        
        # Test requests module
        result = subprocess.run(
            [str(PYTHON_EXE), "-c", "import requests; print('Requests module OK')"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Requests module test passed")
            return True
        else:
            print("❌ Requests module test failed")
            return False
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def create_launcher_script():
    """Create a script that uses the portable Python"""
    print("📝 Creating launcher script...")
    
    launcher_content = f'''@echo off
REM Portable Python launcher for AI Chat
set PYTHON_PATH={PYTHON_DIR.absolute()}
set PATH=%PYTHON_PATH%;%PYTHON_PATH%\\Scripts;%PATH%

REM Run ollama_chat.py with portable Python
"%PYTHON_PATH%\\python.exe" "%~dp0ollama_chat.py" %*
'''
    
    launcher_path = CURRENT_DIR / "chat_portable.bat"
    try:
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        print(f"✅ Created launcher: {launcher_path}")
        return True
    except Exception as e:
        print(f"❌ Launcher creation failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🐍 AI Chat Portable Python Installer")
    print("=" * 40)
    
    # Check if already installed
    if PYTHON_EXE.exists():
        print("✅ Portable Python already installed!")
        if test_installation():
            print("🎊 Installation is working correctly!")
            return True
        else:
            print("⚠️ Reinstalling due to test failures...")
            # Remove and reinstall
            import shutil
            shutil.rmtree(PYTHON_DIR, ignore_errors=True)
    
    # Download Python
    zip_path = download_portable_python()
    if not zip_path:
        return False
    
    # Extract Python
    if not extract_python(zip_path):
        return False
    
    # Setup pip
    if not setup_pip():
        print("⚠️ Pip setup failed, but Python should still work")
    
    # Install requests
    if not install_requests():
        print("⚠️ Requests installation failed, you may need to install manually")
    
    # Test everything
    if not test_installation():
        print("⚠️ Some tests failed, but installation may still work")
    
    # Create launcher
    if not create_launcher_script():
        print("⚠️ Launcher creation failed")
    
    print("\n🎊 Portable Python installation complete!")
    print(f"📁 Location: {PYTHON_DIR}")
    print(f"🐍 Python: {PYTHON_EXE}")
    print("🚀 You can now use the AI Chat system!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed!")
        print("Please check your internet connection and try again.")
    
    input("\nPress Enter to continue...")
