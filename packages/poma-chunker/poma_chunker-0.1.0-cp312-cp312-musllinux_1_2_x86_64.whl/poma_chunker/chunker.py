from importlib.util import spec_from_file_location, module_from_spec
import os
import sys
import platform
import hashlib
import threading
import time
import random

# Thread-local storage for security checks
_security_tls = threading.local()

def _check_environment():
    """Check for suspicious environment variables or debugger presence"""
    # Add a timing check to detect debugger-induced slowdowns
    start_time = time.time()
    
    # Compute a simple hash to add some delay
    hash_val = 0
    for i in range(1000):
        hash_val = hash((hash_val, i)) & 0xFFFFFFFF
    
    # Check execution time - debuggers typically slow this down
    elapsed = time.time() - start_time
    if elapsed > 0.1:  # Suspiciously slow execution
        return False
    
    # Check for common debugging environment variables
    suspicious_vars = ['PYTHONDEVMODE', 'PYTHONINSPECT', 'PYTHONDEBUG', 'PYDEVD_LOAD_VALUES_ASYNC']
    for var in suspicious_vars:
        if os.environ.get(var):
            return False
    
    # Check for debugger modules in loaded modules
    for module_name in list(sys.modules.keys()):
        if any(dbg in module_name.lower() for dbg in ['debugger', 'debug', 'pydevd', 'pdb', '_pydev_']):
            return False
    
    # Platform-specific debugger checks
    if platform.system() == 'Windows':
        # Check for Windows debugger using IsDebuggerPresent
        try:
            import ctypes
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                return False
            # Also check CheckRemoteDebuggerPresent
            h_process = ctypes.windll.kernel32.GetCurrentProcess()
            debug_present = ctypes.c_bool()
            ctypes.windll.kernel32.CheckRemoteDebuggerPresent(h_process, ctypes.byref(debug_present))
            if debug_present.value:
                return False
        except Exception:
            pass
    elif platform.system() == 'Darwin':
        # Check for macOS debugger using sysctl
        try:
            import subprocess
            result = subprocess.run(['sysctl', 'kern.proc.trace'], capture_output=True, text=True)
            if '0' not in result.stdout:
                return False
        except Exception:
            pass
    elif platform.system() == 'Linux':
        # Check for Linux debugger using status
        try:
            with open('/proc/self/status', 'r') as f:
                content = f.read()
                if 'TracerPid:\t0' not in content:
                    return False
        except Exception:
            pass
    
    return True

def _load_native(name):
    """Load native extension with security checks"""
    # Security check - only run once per thread
    if not hasattr(_security_tls, 'checked'):
        if not _check_environment():
            # If debugger detected, delay and exit
            time.sleep(random.random() * 2)  # Random delay to confuse timing analysis
            sys.exit(1)
        _security_tls.checked = True
    
    # Simple extension suffix based on platform
    ext = "pyd" if platform.system().lower() == "windows" else "so"
    suffix = f"{name}.cpython-{sys.version_info.major}{sys.version_info.minor}-{platform.system().lower()}.{ext}"
    path = os.path.join(os.path.dirname(__file__), suffix)
    
    # Verify file exists
    if not os.path.exists(path):
        raise ImportError(f"Cannot load native module: {name}")
    
    # Load the module
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    return mod

_chunker = _load_native("chunker_core")
process = _chunker.process
__all__ = ["process"]