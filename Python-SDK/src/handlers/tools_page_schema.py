#####################################################################################  
#  
# PT_BR:  
# Página "tools_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes das ferramentas nas 6 teclas:  
#        Linha 1: PASS       - PRINT SCR - TERM  
#        Linha 2: Ctrl+C     - Ctrl+X    - Ctrl+V  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, executa a ação correspondente:  
#        KEY_1: Digita a senha armazenada em ~/.password via clipboard  
#        KEY_2: Captura de tela via Flameshot (Shift = delay de 1500ms)  
#        KEY_3: Toggle do terminal Guake  
#        KEY_4: Ctrl+C (copiar)  
#        KEY_5: Ctrl+X (recortar)  
#        KEY_6: Ctrl+V (colar)  
#  
# Dependências externas:  
#   - ydotool (simulação de teclas)  
#   - xclip (clipboard)  
#   - flameshot (screenshot)  
#   - guake (terminal drop-down)  
#   - gnome-extensions (controle do Pano clipboard manager)  
#  
# EN_US:  
# "tools_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays tool names on the device's 6 keys:  
#        Row 1: PASS       - PRINT SCR - TERM  
#        Row 2: Ctrl+C     - Ctrl+X    - Ctrl+V  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, executes the corresponding action:  
#        KEY_1: Types the password stored in ~/.password via clipboard  
#        KEY_2: Screenshot via Flameshot (Shift = 1500ms delay)  
#        KEY_3: Guake terminal toggle  
#        KEY_4: Ctrl+C (copy)  
#        KEY_5: Ctrl+X (cut)  
#        KEY_6: Ctrl+V (paste)  
#  
# External dependencies:  
#   - ydotool (key simulation)  
#   - xclip (clipboard)  
#   - flameshot (screenshot)  
#   - guake (drop-down terminal)  
#   - gnome-extensions (Pano clipboard manager control)  
#  
######################################################################################  
  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import ButtonKey  
import os  
import time  
import subprocess  
from utils.commands import run_cmd, run_cmd_no_snap  
from utils.image import render_keys_from_labels  
from utils.input_detection import is_shift_pressed  
from utils.keys import get_action_for_event, send_key  
  
  
######################################################################################  
#  
# PT_BR: MAPEAMENTO DE TECLAS  
#  
# KEY_LABELS: dicionário {índice_tecla: rótulo} com os nomes a exibir.  
#   Índices 1-3 = linha superior, 4-6 = linha inferior.  
#   Rótulos com "\n" são quebrados em duas linhas para caber em 64x64.  
#  
# EN_US: KEY MAPPING  
#  
# KEY_LABELS: dict {key_index: label} with the names to display.  
#   Indices 1-3 = top row, 4-6 = bottom row.  
#   Labels with "\n" are split into two lines to fit in 64x64.  
#  
######################################################################################  
  
KEY_LABELS = {  
    1: "Pass\nWD",        # Macro de senha / Password macro  
    2: "Prnt\nScrn",     # PrintScreen  
    3: "Term",          # Terminal (Guake)  
    4: "Ctrl\nC",       # Copy  
    5: "Ctrl\nX",       # Cut  
    6: "Ctrl\nV",       # Paste  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — GUAKE (TERMINAL)  
# EN_US: HELPER FUNCTIONS — GUAKE (TERMINAL)  
# =============================================================================  
  
def _is_guake_running() -> bool:  
    """  
    PT_BR: Verifica se o Guake já está rodando via pgrep.  
    EN_US: Checks if Guake is already running via pgrep.  
    """  
    try:  
        result = subprocess.run(  
            ["pgrep", "-x", "guake"],  
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL,  
        )  
        return result.returncode == 0  
    except Exception:  
        return False  
  
  
def _open_guake():  
    """  
    PT_BR:  
    Garante que o Guake está rodando e faz toggle.  
    Se o Guake não estiver ativo, inicia o processo e aguarda antes do toggle.  
  
    EN_US:  
    Ensures Guake is running and toggles it.  
    If Guake is not active, starts the process and waits before toggling.  
    """  
    if not _is_guake_running():  
        print("Guake não está rodando. Iniciando...", flush=True)  
        run_cmd(["guake"])  
  
        # PT_BR: Aguarda o Guake subir antes de fazer toggle  
        # EN_US: Waits for Guake to start before toggling  
        retries = 10  
        while retries > 0 and not _is_guake_running():  
            time.sleep(0.3)  
            retries -= 1  
  
        if not _is_guake_running():  
            print("Falha ao iniciar o Guake.", flush=True)  
            return  
  
    run_cmd(["guake-toggle"])  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — FLAMESHOT (SCREENSHOT)  
# EN_US: HELPER FUNCTIONS — FLAMESHOT (SCREENSHOT)  
# =============================================================================  
  
def _is_flameshot_running() -> bool:  
    """  
    PT_BR: Verifica se o daemon do Flameshot está rodando via pgrep.  
    EN_US: Checks if the Flameshot daemon is running via pgrep.  
    """  
    try:  
        result = subprocess.run(  
            ["pgrep", "-x", "flameshot"],  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
        )  
        return result.returncode == 0  
    except Exception:  
        return False  
  
  
def _take_screenshot():  
    """  
    PT_BR:  
    Captura screenshot via Flameshot.  
    Garante que o daemon está rodando antes de abrir o GUI.  
    Se Shift estiver pressionado no teclado, adiciona delay de 1500ms.  
    Usa run_cmd_no_snap para evitar conflitos com bibliotecas do snap.  
  
    EN_US:  
    Takes a screenshot via Flameshot.  
    Ensures the daemon is running before opening the GUI.  
    If Shift is pressed on the keyboard, adds a 1500ms delay.  
    Uses run_cmd_no_snap to avoid snap library conflicts.  
    """  
    if not _is_flameshot_running():  
        print("Flameshot daemon não está rodando. Iniciando...", flush=True)  
        run_cmd_no_snap(["flameshot"])  
  
        # PT_BR: Aguarda o daemon subir (máx ~4.5s)  
        # EN_US: Waits for the daemon to start (max ~4.5s)  
        retries = 15  
        while retries > 0 and not _is_flameshot_running():  
            time.sleep(0.3)  
            retries -= 1  
  
        if not _is_flameshot_running():  
            print("FALHA: Flameshot daemon não iniciou.", flush=True)  
            return  
  
        # PT_BR: Espera extra para o daemon estabilizar (evita tela preta)  
        # EN_US: Extra wait for daemon to stabilize (avoids black screen)  
        time.sleep(1.0)  
  
    # PT_BR: Monta o comando; Shift adiciona delay de 1500ms  
    # EN_US: Builds the command; Shift adds a 1500ms delay  
    cmd = ["flameshot", "gui"]  
    if is_shift_pressed():  
        cmd.extend(["-d", "1500"])  
  
    run_cmd_no_snap(cmd)  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — SENHA / CLIPBOARD  
# EN_US: HELPER FUNCTIONS — PASSWORD / CLIPBOARD  
# =============================================================================  
  
def _read_password() -> str:  
    """  
    PT_BR:  
    Lê a senha do arquivo ~/.password.  
    Retorna a primeira linha do arquivo (sem newline).  
    O arquivo deve ter permissão 600 (chmod 600 ~/.password).  
  
    EN_US:  
    Reads the password from the ~/.password file.  
    Returns the first line of the file (without newline).  
    The file should have permission 600 (chmod 600 ~/.password).  
    """  
    password_file = os.path.expanduser("~/.password")  
    try:  
        with open(password_file, "r") as f:  
            return f.readline().strip()  
    except FileNotFoundError:  
        print(f"Arquivo de senha não encontrado: {password_file}", flush=True)  
        return ""  
    except Exception as e:  
        print(f"Erro ao ler senha: {e}", flush=True)  
        return ""  
  
def _pause_pano():  
    """  
    PT_BR: Desabilita a extensão Pano (clipboard manager) temporariamente.  
    EN_US: Temporarily disables the Pano extension (clipboard manager).  
    """  
    subprocess.run(  
        ["gnome-extensions", "disable", "pano@elhan.io"],  
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  
    )  
  
  
def _resume_pano():  
    """  
    PT_BR: Reabilita a extensão Pano (clipboard manager).  
    EN_US: Re-enables the Pano extension (clipboard manager).  
    """  
    subprocess.run(  
        ["gnome-extensions", "enable", "pano@elhan.io"],  
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  
    )  
  
  
def _type_password():  
    """  
    PT_BR:  
    Lê a senha de ~/.password e copia para o clipboard via xclip.  
    O usuário cola manualmente (Ctrl+V) onde desejar.  
    Não faz paste automático nem pressiona Enter.  
  
    Fluxo:  
        1. Lê a senha do arquivo  
        2. Copia a senha para o clipboard via xclip  
  
    EN_US:  
    Reads the password from ~/.password and copies it to the clipboard  
    via xclip. The user pastes manually (Ctrl+V) wherever needed.  
    Does not auto-paste or press Enter.  
  
    Flow:  
        1. Reads the password from file  
        2. Copies the password to clipboard via xclip  
    """  
    password = _read_password()  
    if not password:  
        return  
  
    # PT_BR: Copia a senha para o clipboard via xclip  
    # EN_US: Copies the password to clipboard via xclip  
    proc = subprocess.Popen(  
        ["xclip", "-selection", "clipboard"],  
        stdin=subprocess.PIPE,  
        stdout=subprocess.DEVNULL,  
        stderr=subprocess.DEVNULL,  
    )  
    proc.communicate(password.encode())  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_tools_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "tools_page_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes das ferramentas e envia para o dispositivo.  
  
    Layout:  
        KEY_1: PASS      KEY_2: PRINT SCR   KEY_3: TERM  
        KEY_4: Ctrl+C    KEY_5: Ctrl+X      KEY_6: Ctrl+V  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "tools_page_schema" page to the K1Pro device.  
    Generates images with tool names and sends them to the device.  
  
    Layout:  
        KEY_1: PASS      KEY_2: PRINT SCR   KEY_3: TERM  
        KEY_4: Ctrl+C    KEY_5: Ctrl+X      KEY_6: Ctrl+V  
  
    Args:  
        device: K1Pro instance already opened and initialized.  
    """  
    render_keys_from_labels(device, KEY_LABELS)  
  
  
######################################################################################  
#  
# PT_BR: MAPEAMENTO DE TECLAS → AÇÕES  
#  
# KEY_ACTIONS: dicionário {ButtonKey: str} que mapeia cada tecla do K1Pro  
#   para a ação correspondente.  
#  
#   Layout:  
#     KEY_1: password_macro   KEY_2: Print        KEY_3: terminal  
#     KEY_4: ctrl+c           KEY_5: ctrl+x       KEY_6: ctrl+v  
#  
# EN_US: KEY → ACTION MAPPING  
#  
# KEY_ACTIONS: dict {ButtonKey: str} mapping each K1Pro key  
#   to the corresponding action.  
#  
#   Layout:  
#     KEY_1: password_macro   KEY_2: Print        KEY_3: terminal  
#     KEY_4: ctrl+c           KEY_5: ctrl+x       KEY_6: ctrl+v  
#  
######################################################################################  
  
KEY_ACTIONS = {  
    ButtonKey.KEY_1: "password_macro",  
    ButtonKey.KEY_2: "Print",  
    ButtonKey.KEY_3: "terminal",  
    ButtonKey.KEY_4: "ctrl+c",  
    ButtonKey.KEY_5: "ctrl+x",  
    ButtonKey.KEY_6: "ctrl+v",  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página tools_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), executa a ação  
    correspondente. Eventos de release (state == 0) são ignorados.  
  
    Ações:  
        password_macro: digita a senha de ~/.password via clipboard  
        Print:          captura de tela via Flameshot  
        terminal:       toggle do Guake  
        ctrl+c/x/v:    simula Ctrl+C, Ctrl+X ou Ctrl+V via ydotool  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the tools_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), executes the corresponding  
    action. Release events (state == 0) are ignored.  
  
    Actions:  
        password_macro: types the password from ~/.password via clipboard  
        Print:          screenshot via Flameshot  
        terminal:       Guake toggle  
        ctrl+c/x/v:    simulates Ctrl+C, Ctrl+X or Ctrl+V via ydotool  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Extrai a ação; retorna None se release ou tecla sem mapeamento  
    # EN_US: Extracts the action; returns None if release or unmapped key  
    action = get_action_for_event(event, KEY_ACTIONS)  
    if action is None:  
        return  
  
    if action == "password_macro":  
        # PT_BR: Digita a senha via clipboard  
        # EN_US: Types the password via clipboard  
        _type_password()  
  
    elif action == "Print":  
        # PT_BR: Captura de tela via Flameshot (Shift = delay)  
        # EN_US: Screenshot via Flameshot (Shift = delay)  
        _take_screenshot()  
  
    elif action == "terminal":  
        # PT_BR: Toggle do terminal Guake  
        # EN_US: Guake terminal toggle  
        _open_guake()  
  
    else:  
        # PT_BR: Simula atalho de teclado via ydotool (ctrl+c, ctrl+x, ctrl+v)  
        # EN_US: Simulates keyboard shortcut via ydotool (ctrl+c, ctrl+x, ctrl+v)  
        send_key(action)