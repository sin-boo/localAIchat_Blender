# 🤖 AI Chat System - Portable Release

**EXACT same structure as your original setup, but within odin_grab folder!**

## 📁 **Directory Structure:**
```
odin_grab/
└── a_astitnet/            # Main AI Chat folder
    ├── addon/ai_chat/      # Blender addon files
    ├── ai mode/            # AI model files & manifests
    │   ├── blobs/          # Model data files
    │   └── manifests/      # Model manifests
    ├── niout/              # Chat files
    │   ├── input.txt       # Your messages
    │   ├── response.txt    # AI responses
    │   └── model_config.txt # Selected model
    ├── python_portable/    # Portable Python (auto-created)
    ├── INSTALL_PYTHON.bat  # Double-click installer
    ├── TEST_AI_CHAT.bat    # System tester
    ├── chat.bat            # Quick chat script
    ├── model_manager.py    # Model management
    └── ollama_chat.py      # Main chat script
```
```

## 🚀 **Setup (3 Steps):**

### 1. Extract anywhere:
- Desktop/odin_grab/ ✓
- Documents/odin_grab/ ✓  
- USB/odin_grab/ ✓
- Any location works!
- System finds odin_grab/a_astitnet automatically!

### 2. Install Blender Addon:
1. Open Blender → Edit → Preferences → Add-ons
2. Click "Install..." → Browse to `addon/ai_chat` folder
3. Enable "AI Chat" addon

### 3. Install Ollama:
- Download: https://ollama.ai/
- Install model: `ollama pull qwen3:4b`

## ✨ **Features:**
- **EXACT same structure** - identical to your original setup
- **Auto path detection** - finds a_astitnet folder from any location
- **All your files included** - input.txt, response.txt, model files, etc.
- **Model management** - browse, start, stop models with file browser
- **Complete AI models** - deepseek-r1:8b, qwen3:4b with full data
- **Cross-platform** - works on any PC

## 🎮 **Usage:**
1. Type message in AI Chat panel
2. Click "Send" 
3. Response appears automatically!

## 🔧 **Troubleshooting:**

### **Problem: "Failed to start librery gama 1b"**
**Solutions:**
1. Use correct model name: `gemma:1b` (not "librery gama 1b")
2. Click "Load" button after browsing to model file
3. Try typing exact name: `gemma:1b`, `llama:7b`, etc.

### **Problem: "Don't have Python but they have 3.10"**
**Solutions:**
1. **SUPER EASY: Double-click `INSTALL_PYTHON.bat`**
   - Just double-click the file - that's it!
   - Downloads Python 3.11 automatically (~15MB)
   - Installs to `a_astitnet/python_portable/`
   - Completely isolated - won't mess with your system
   - Includes requests module automatically
   - Ready to use immediately!
2. **Also easy: Click "Install Python (Portable)"** in Blender addon Settings
3. **Check existing: Run `check_python.bat`** to test current setup
4. **Manual install:** Download Python from python.org

### **Problem: Models not found**
**Solutions:**
1. Install model: `ollama pull gemma:1b`
2. Check Ollama is running: `ollama serve`
3. Use exact model names in addon

**Works from any location with zero configuration!** ✨
