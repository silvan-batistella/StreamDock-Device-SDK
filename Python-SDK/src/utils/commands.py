import os  
import subprocess  
  
  
def run_cmd(cmd):  
    """  
    PT_BR: Executa comando de forma assíncrona (não-bloqueante).  
    EN_US: Executes command asynchronously (non-blocking).  
    """  
    try:  
        subprocess.Popen(  
            cmd,  
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL,  
            start_new_session=True,  
        )  
    except Exception as e:  
        print(f"Command error: {e}", flush=True)  
  
  
def run_cmd_no_snap(cmd):  
    """  
    PT_BR: Executa comando com ambiente limpo de variáveis do snap.  
    EN_US: Executes command with snap-related environment variables removed.  
    """  
    clean_env = {}  
    for key, val in os.environ.items():  
        if "snap" in key.lower():  
            continue  
        if "/snap/" in val or "/snap:" in val:  
            continue  
        clean_env[key] = val  
  
    for var in ["LD_LIBRARY_PATH", "LD_PRELOAD"]:  
        clean_env.pop(var, None)  
  
    clean_env["LD_LIBRARY_PATH"] = (  
        "/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu:/usr/lib:/lib"  
    )  
  
    try:  
        subprocess.Popen(  
            cmd,  
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL,  
            env=clean_env,  
        )  
    except Exception as e:  
        print(f"Command error: {e}", flush=True)