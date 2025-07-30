import os
import sys
import platform
import threading
import time
import random

_security_tls = threading.local()

def ensure_secure_environment():
    if not hasattr(_security_tls, 'checked'):
        if not _check_environment():
            time.sleep(random.random() * 2)
            sys.exit(1)
        _security_tls.checked = True

def _check_environment():
    start_time = time.time()
    hash_val = 0
    for i in range(1000):
        hash_val = hash((hash_val, i)) & 0xFFFFFFFF
    elapsed = time.time() - start_time
    if elapsed > 0.1:
        return False
    suspicious_vars = ['PYTHONDEVMODE', 'PYTHONINSPECT', 'PYTHONDEBUG', 'PYDEVD_LOAD_VALUES_ASYNC']
    for var in suspicious_vars:
        if os.environ.get(var):
            return False
    for module_name in list(sys.modules.keys()):
        if any(dbg in module_name.lower() for dbg in ['debugger', 'debug', 'pydevd', 'pdb', '_pydev_']):
            return False
    if platform.system() == 'Windows':
        try:
            import ctypes
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                return False
            h_process = ctypes.windll.kernel32.GetCurrentProcess()
            debug_present = ctypes.c_bool()
            ctypes.windll.kernel32.CheckRemoteDebuggerPresent(h_process, ctypes.byref(debug_present))
            if debug_present.value:
                return False
        except Exception:
            pass
    elif platform.system() == 'Darwin':
        try:
            import subprocess
            result = subprocess.run(['sysctl', 'kern.proc.trace'], capture_output=True, text=True)
            if '0' not in result.stdout:
                return False
        except Exception:
            pass
    elif platform.system() == 'Linux':
        try:
            with open('/proc/self/status', 'r') as f:
                content = f.read()
                if 'TracerPid:\t0' not in content:
                    return False
        except Exception:
            pass
    return True
