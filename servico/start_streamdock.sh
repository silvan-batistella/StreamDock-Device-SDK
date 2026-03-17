#!/bin/bash  
set -e  
  
# Inicia ydotoold em background  
ydotoold &  
YDOTOOL_PID=$!  
  
# Garante cleanup ao sair  
cleanup() {  
    kill "$YDOTOOL_PID" 2>/dev/null || true  
    wait "$YDOTOOL_PID" 2>/dev/null || true  
}  
trap cleanup EXIT INT TERM  
  
# Aguarda o socket ficar disponível  
for i in $(seq 1 20); do  
    if [ -e "/tmp/.ydotool_socket" ] || [ -e "/run/user/$(id -u)/.ydotool_socket" ]; then  
        break  
    fi  
    sleep 0.25  
done  
  
# Inicia o script Python (foreground — systemd monitora este processo)  
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"  
cd "$SCRIPT_DIR/../Python-SDK/src" 
exec python3 k1_pro.py