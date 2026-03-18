#!/bin/bash  
set -e  
  
# PT_BR: Inicia o script Python (foreground — systemd monitora este processo)  
#        A simulação de teclas é feita via python-evdev (uinput),  
#        sem necessidade de daemons externos.  
# EN_US: Starts the Python script (foreground — systemd monitors this process)  
#        Key simulation is done via python-evdev (uinput),  
#        no external daemons needed.  
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"  
cd "$SCRIPT_DIR/../Python-SDK/src"  
exec python3 k1_pro.py