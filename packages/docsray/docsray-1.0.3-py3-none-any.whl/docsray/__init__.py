"""
DocsRay - PDF Question-Answering System with MCP Integration
"""

__version__ = "1.0.3"
__author__ = "Taehoon Kim"

import os
import sys

# Suppress logs
os.environ["LLAMA_LOG_LEVEL"] = "40"
os.environ["GGML_LOG_LEVEL"] = "error"
os.environ["LLAMA_CPP_LOG_LEVEL"] = "ERROR"

# Import config
from .config import FAST_MODE, FULL_FEATURE_MODE, MAX_TOKENS, DOCSRAY_HOME, DATA_DIR, MODEL_DIR, CACHE_DIR

# Check if llama-cpp-python needs update (for post-install message)
def check_llama_cpp_python():
    """Check if llama-cpp-python needs the hotfix"""
    try:
        import llama_cpp
        # Check if this is the forked version by trying to import Gemma3ChatHandler
        try:
            from llama_cpp.llama_chat_format import Gemma3ChatHandler
            return True  # Hotfix already applied
        except ImportError:
            return False  # Need hotfix
    except ImportError:
        return None  # Not installed at all

# Display post-install message if needed
def display_hotfix_message():
    """Display hotfix message for Gemma3 support"""
    llama_status = check_llama_cpp_python()
    
    if llama_status is False:
        print("\n" + "="*70)
        print("🔧 DocsRay Post-Install Setup")
        print("="*70)
        print("\n# 1-1. Hotfix (Temporary)")
        print("# Hotfix: Use the forked version of llama-cpp-python for Gemma3 Support")
        print("# Note: This is a temporary fix until the official library supports Gemma3")
        print("# Install the forked version of llama-cpp-python")
        print("\npip install git+https://github.com/kossum/llama-cpp-python.git@main\n")
        print("="*70 + "\n")

# Check if this is the first run after installation
def check_first_run():
    """Check if this is the first run after installation"""
    first_run_flag = DOCSRAY_HOME / ".first_run_complete"
    if not first_run_flag.exists():
        # First run - show message
        display_hotfix_message()
        # Create flag file
        try:
            first_run_flag.touch()
        except:
            pass

# Always check on import
check_first_run()

__all__ = [
    "__version__", 
    "DOCSRAY_HOME", 
    "DATA_DIR", 
    "MODEL_DIR", 
    "CACHE_DIR",
    "FAST_MODE",
    "FULL_FEATURE_MODE", 
    "MAX_TOKENS"
]