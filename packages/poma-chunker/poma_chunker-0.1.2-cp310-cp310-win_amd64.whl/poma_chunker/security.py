D=Exception
import os,sys,platform as B,threading as E,time as C,random as F
A=E.local()
def ensure_secure_environment():
	if not hasattr(A,'checked'):
		if not G():C.sleep(F.random()*2);sys.exit(1)
		A.checked=True
def G():
	G=C.time();E=0
	for H in range(1000):E=hash((E,H))&4294967295
	I=C.time()-G
	if I>.1:return False
	J=['PYTHONDEVMODE','PYTHONINSPECT','PYTHONDEBUG','PYDEVD_LOAD_VALUES_ASYNC']
	for K in J:
		if os.environ.get(K):return False
	for L in list(sys.modules.keys()):
		if any(A in L.lower()for A in['debugger','debug','pydevd','pdb','_pydev_']):return False
	if B.system()=='Windows':
		try:
			import ctypes as A
			if A.windll.kernel32.IsDebuggerPresent()!=0:return False
			M=A.windll.kernel32.GetCurrentProcess();F=A.c_bool();A.windll.kernel32.CheckRemoteDebuggerPresent(M,A.byref(F))
			if F.value:return False
		except D:pass
	elif B.system()=='Darwin':
		try:
			import subprocess as N;O=N.run(['sysctl','kern.proc.trace'],capture_output=True,text=True)
			if'0'not in O.stdout:return False
		except D:pass
	elif B.system()=='Linux':
		try:
			with open('/proc/self/status','r')as P:
				Q=P.read()
				if'TracerPid:\t0'not in Q:return False
		except D:pass
	return True