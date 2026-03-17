"""  
PT_BR:  
Módulo centralizado para simulação de teclas via ydotool.  
  
O ydotool trabalha com keycodes numéricos do kernel Linux  
(definidos em linux/input-event-codes.h), no formato:  
    ydotool key <keycode>:1 <keycode>:0  
onde :1 = press e :0 = release.  
  
Para combos (ex: ctrl+shift+b), todos os modificadores são  
pressionados primeiro, depois a tecla principal, e o release  
acontece na ordem inversa.  
  
EN_US:  
Centralized module for key simulation via ydotool.  
  
ydotool uses numeric keycodes from the Linux kernel  
(defined in linux/input-event-codes.h), in the format:  
    ydotool key <keycode>:1 <keycode>:0  
where :1 = press and :0 = release.  
  
For combos (e.g., ctrl+shift+b), all modifiers are pressed  
first, then the main key, and release happens in reverse order.  
"""  
  
from utils.commands import run_cmd  
  
  
# ---------------------------------------------------------------------------  
# PT_BR: Mapeamento de nomes simbólicos → keycodes do kernel Linux  
#        Fonte: linux/input-event-codes.h  
# EN_US: Symbolic name → Linux kernel keycode mapping  
#        Source: linux/input-event-codes.h  
# ---------------------------------------------------------------------------  
KEYCODE_MAP = {  
    # --- Modificadores / Modifiers ---  
    "ctrl":       29,   # KEY_LEFTCTRL  
    "shift":      42,   # KEY_LEFTSHIFT  
    "alt":        56,   # KEY_LEFTALT  
    "super":     125,   # KEY_LEFTMETA  
  
    # --- Teclas de função / Function keys ---  
    "F1":         59,   # KEY_F1  
    "F2":         60,   # KEY_F2  
    "F3":         61,   # KEY_F3  
    "F4":         62,   # KEY_F4  
    "F5":         63,   # KEY_F5  
    "F6":         64,   # KEY_F6  
    "F7":         65,   # KEY_F7  
    "F8":         66,   # KEY_F8  
    "F9":         67,   # KEY_F9  
    "F10":        68,   # KEY_F10  
    "F11":        87,   # KEY_F11  
    "F12":        88,   # KEY_F12  
  
    # --- Navegação / Navigation ---  
    "Insert":    110,   # KEY_INSERT  
    "Delete":    111,   # KEY_DELETE  
    "Home":      102,   # KEY_HOME  
    "End":       107,   # KEY_END  
    "Page_Up":   104,   # KEY_PAGEUP  
    "Page_Down": 109,   # KEY_PAGEDOWN  
  
    # --- Letras / Letters ---  
    "a": 30, "b": 48, "c": 46, "d": 32, "e": 18, "f": 33,  
    "g": 34, "h": 35, "i": 23, "j": 36, "k": 37, "l": 38,  
    "m": 50, "n": 49, "o": 24, "p": 25, "q": 16, "r": 19,  
    "s": 31, "t": 20, "u": 22, "v": 47, "w": 17, "x": 45,  
    "y": 21, "z": 44,  
  
    # --- Números / Numbers ---  
    "0": 11, "1":  2, "2":  3, "3":  4, "4":  5,  
    "5":  6, "6":  7, "7":  8, "8":  9, "9": 10,  
  
    # --- Especiais / Special ---  
    "Return":     28,   # KEY_ENTER  
    "Escape":      1,   # KEY_ESC  
    "BackSpace":  14,   # KEY_BACKSPACE  
    "Tab":        15,   # KEY_TAB  
    "space":      57,   # KEY_SPACE  
    "Print":     210,   # KEY_PRINT (sysrq = 99, print = 210)  
}  
  
  
def send_key(key_combo: str):  
    """  
    PT_BR:  
    Simula pressionamento de tecla(s) via ydotool.  
  
    Aceita formato simbólico idêntico ao que era usado com xdotool:  
        "F8"              → tecla simples  
        "ctrl+shift+b"    → combo com modificadores  
        "Page_Up"         → tecla de navegação  
  
    Converte automaticamente para keycodes do kernel e monta a  
    sequência press(:1)/release(:0) na ordem correta.  
  
    Args:  
        key_combo: string no formato "tecla" ou "mod1+mod2+tecla"  
  
    EN_US:  
    Simulates key press(es) via ydotool.  
  
    Accepts symbolic format identical to what was used with xdotool:  
        "F8"              → single key  
        "ctrl+shift+b"    → combo with modifiers  
        "Page_Up"         → navigation key  
  
    Automatically converts to kernel keycodes and builds the  
    press(:1)/release(:0) sequence in the correct order.  
  
    Args:  
        key_combo: string in the format "key" or "mod1+mod2+key"  
    """  
    parts = key_combo.split("+")  
    keycodes = []  
  
    for part in parts:  
        kc = KEYCODE_MAP.get(part)  
        if kc is None:  
            print(f"[keys] Unknown key: '{part}' in combo '{key_combo}'", flush=True)  
            return  
        keycodes.append(kc)  
  
    # PT_BR: Monta sequência: press todos na ordem, release na ordem inversa  
    # EN_US: Builds sequence: press all in order, release in reverse order  
    args = [f"{kc}:1" for kc in keycodes] + [f"{kc}:0" for kc in reversed(keycodes)]  
  
    run_cmd(["ydotool", "key"] + args)  
  
  
def get_action_for_event(event, key_actions: dict):  
    """  
    PT_BR:  
    Extrai a ação do evento de botão.  
    Retorna None se for release (state != 1) ou tecla sem mapeamento.  
  
    Args:  
        event:       InputEvent com event_type == EventType.BUTTON  
        key_actions: dict {ButtonKey: str} com o mapeamento da página  
  
    Returns:  
        str ou None: a ação mapeada, ou None se ignorar  
  
    EN_US:  
    Extracts the action from a button event.  
    Returns None if release (state != 1) or unmapped key.  
  
    Args:  
        event:       InputEvent with event_type == EventType.BUTTON  
        key_actions: dict {ButtonKey: str} with the page mapping  
  
    Returns:  
        str or None: the mapped action, or None if ignored  
    """  
    if event.state != 1:  
        return None  
  
    action = key_actions.get(event.key)  
    if action is None:  
        print(f"Key {event.key} has no action mapped.", flush=True)  
    return action