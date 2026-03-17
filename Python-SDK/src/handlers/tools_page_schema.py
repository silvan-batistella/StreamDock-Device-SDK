# Python-SDK/src/handlers/tools_page_schema.py  
  
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
#   - xdotool (simulação de teclas)  
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
#   - xdotool (key simulation)  
#   - xclip (clipboard)  
#   - flameshot (screenshot)  
#   - guake (drop-down terminal)  
#   - gnome-extensions (Pano clipboard manager control)  
#  
######################################################################################  
  
from PIL import Image, ImageDraw, ImageFont  
from StreamDock.ImageHelpers.PILHelper import create_key_image  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType, ButtonKey  
import os  
import time  
import ctypes  
import ctypes.util  
import random  
import subprocess  
  
  
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
# PT_BR: FUNÇÕES AUXILIARES — EXECUÇÃO DE COMANDOS  
# EN_US: HELPER FUNCTIONS — COMMAND EXECUTION  
# =============================================================================  
  
def _run_cmd(cmd):  
    """  
    PT_BR: Executa comando de forma assíncrona (não-bloqueante).  
    EN_US: Executes command asynchronously (non-blocking).  
    """  
    try:  
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)  
    except Exception as e:  
        print(f"Command error: {e}", flush=True)  
  
  
def _run_cmd_no_snap(cmd):  
    """  
    PT_BR:  
    Executa comando com ambiente limpo de variáveis do snap.  
    Remove variáveis com "snap" no nome ou "/snap/" no valor,  
    e força os paths de biblioteca do sistema no LD_LIBRARY_PATH.  
    Necessário para executar aplicações nativas (ex: flameshot) quando  
    o processo pai herda ambiente contaminado pelo snap (ex: terminal do VS Code).  
  
    EN_US:  
    Executes command with snap-related environment variables removed.  
    Removes variables with "snap" in the name or "/snap/" in the value,  
    and forces system library paths in LD_LIBRARY_PATH.  
    Required to run native applications (e.g., flameshot) when the parent  
    process inherits a snap-contaminated environment (e.g., VS Code terminal).  
    """  
    clean_env = {}  
  
    for key, val in os.environ.items():  
        # PT_BR: Remove variáveis com "snap" no nome (ex: SNAP_*, *_VSCODE_SNAP_ORIG)  
        # EN_US: Removes variables with "snap" in the name (e.g., SNAP_*, *_VSCODE_SNAP_ORIG)  
        if "snap" in key.lower():  
            continue  
        # PT_BR: Remove variáveis com paths do snap no valor  
        # EN_US: Removes variables with snap paths in the value  
        if "/snap/" in val or "/snap:" in val:  
            continue  
        clean_env[key] = val  
  
    # PT_BR: Remove LD_LIBRARY_PATH e LD_PRELOAD herdados e força paths do sistema  
    # EN_US: Removes inherited LD_LIBRARY_PATH and LD_PRELOAD, forces system paths  
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
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — GERAÇÃO DE IMAGENS  
# EN_US: HELPER FUNCTIONS — IMAGE GENERATION  
# =============================================================================  
  
def _generate_label_image(device: K1Pro, label: str) -> str:  
    """  
    PT_BR:  
    Gera uma imagem 64x64 com o texto centralizado e salva como JPEG temporário.  
    Retorna o path do arquivo temporário gerado.  
  
    Args:  
        device: instância do K1Pro (usada para obter o formato da tecla).  
        label:  texto a ser renderizado na imagem.  
  
    Returns:  
        str: caminho do arquivo JPEG temporário.  
  
    EN_US:  
    Generates a 64x64 image with centered text and saves it as a temporary JPEG.  
    Returns the path of the generated temporary file.  
  
    Args:  
        device: K1Pro instance (used to get the key image format).  
        label:  text to render on the image.  
  
    Returns:  
        str: path to the temporary JPEG file.  
    """  
    # PT_BR: Cria imagem preta no tamanho da tecla (64x64)  
    # EN_US: Creates a black image in the key size (64x64)  
    img = create_key_image(device, background="black")  
    draw = ImageDraw.Draw(img)  
  
    # PT_BR: Tenta carregar fonte do sistema; fallback para fonte padrão do PIL  
    # EN_US: Tries to load system font; falls back to PIL default font  
    try:  
        font = ImageFont.truetype(  
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11  
        )  
    except (IOError, OSError):  
        font = ImageFont.load_default()  
  
    # PT_BR: Calcula posição centralizada do texto na imagem  
    # EN_US: Calculates centered text position on the image  
    bbox = draw.textbbox((0, 0), label, font=font)  
    text_w = bbox[2] - bbox[0]  
    text_h = bbox[3] - bbox[1]  
    x = (img.width - text_w) // 2  
    y = (img.height - text_h) // 2  
  
    # PT_BR: Desenha o texto branco centralizado  
    # EN_US: Draws the centered white text  
    draw.text((x, y), label, fill="white", font=font, align="center")  
  
    # PT_BR: Salva como JPEG temporário com nome aleatório para evitar colisões  
    # EN_US: Saves as temporary JPEG with random name to avoid collisions  
    temp_path = f"key_label_{random.randint(9999, 999999)}.jpg"  
    img.save(temp_path, "JPEG")  
    return temp_path  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — DETECÇÃO DE ESTADO DO TECLADO  
# EN_US: HELPER FUNCTIONS — KEYBOARD STATE DETECTION  
# =============================================================================  
  
def _is_shift_pressed() -> bool:  
    """  
    PT_BR:  
    Verifica se a tecla Shift (esquerda ou direita) está pressionada  
    no teclado físico, consultando o XQueryKeymap do X11.  
    Funciona apenas em X11 (não Wayland).  
  
    Keycodes padrão:  
        Shift_L = 50  
        Shift_R = 62  
  
    Returns:  
        bool: True se Shift estiver pressionado.  
  
    EN_US:  
    Checks if the Shift key (left or right) is pressed on the physical  
    keyboard by querying X11's XQueryKeymap.  
    Works only on X11 (not Wayland).  
  
    Default keycodes:  
        Shift_L = 50  
        Shift_R = 62  
  
    Returns:  
        bool: True if Shift is pressed.  
    """  
    try:  
        x11_path = ctypes.util.find_library("X11")  
        if not x11_path:  
            print("libX11 não encontrada.", flush=True)  
            return False  
  
        x11 = ctypes.cdll.LoadLibrary(x11_path)  
  
        # PT_BR: Define tipos corretos para evitar segfault em sistemas 64-bit  
        # EN_US: Sets correct types to avoid segfault on 64-bit systems  
        x11.XOpenDisplay.restype = ctypes.c_void_p  
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]  
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]  
        x11.XQueryKeymap.argtypes = [ctypes.c_void_p, ctypes.c_char * 32]  
  
        display = x11.XOpenDisplay(None)  
        if not display:  
            print("Não foi possível abrir display X11.", flush=True)  
            return False  
  
        try:  
            keymap = (ctypes.c_char * 32)()  
            x11.XQueryKeymap(display, keymap)  
  
            def is_key_pressed(keycode):  
                byte_index = keycode // 8  
                bit_index = keycode % 8  
                return bool(keymap[byte_index][0] & (1 << bit_index))  
  
            return is_key_pressed(50) or is_key_pressed(62)  
        finally:  
            x11.XCloseDisplay(display)  
  
    except Exception as e:  
        print(f"Erro ao verificar Shift: {e}", flush=True)  
        return False  
  
  
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
        _run_cmd(["guake"])  
  
        # PT_BR: Aguarda o Guake subir antes de fazer toggle  
        # EN_US: Waits for Guake to start before toggling  
        retries = 10  
        while retries > 0 and not _is_guake_running():  
            time.sleep(0.3)  
            retries -= 1  
  
        if not _is_guake_running():  
            print("Falha ao iniciar o Guake.", flush=True)  
            return  
  
    _run_cmd(["guake-toggle"])  
  
  
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
    Usa _run_cmd_no_snap para evitar conflitos com bibliotecas do snap.  
  
    EN_US:  
    Takes a screenshot via Flameshot.  
    Ensures the daemon is running before opening the GUI.  
    If Shift is pressed on the keyboard, adds a 1500ms delay.  
    Uses _run_cmd_no_snap to avoid snap library conflicts.  
    """  
    if not _is_flameshot_running():  
        print("Flameshot daemon não está rodando. Iniciando...", flush=True)  
        _run_cmd_no_snap(["flameshot"])  
  
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
    if _is_shift_pressed():  
        cmd.extend(["-d", "1500"])  
  
    _run_cmd_no_snap(cmd)  
  
  
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
    Lê a senha de ~/.password, cola no campo focado via clipboard e pressiona Enter.  
    Pausa o Pano clipboard manager durante a operação para que a senha  
    não fique armazenada no histórico do clipboard.  
  
    Fluxo:  
        1. Lê a senha do arquivo  
        2. Pausa o Pano  
        3. Copia a senha para o clipboard via xclip  
        4. Cola com Ctrl+V  
        5. Pressiona Enter  
        6. Limpa o clipboard  
        7. Reativa o Pano  
  
    EN_US:  
    Reads the password from ~/.password, pastes it into the focused field  
    via clipboard and presses Enter.  
    Pauses the Pano clipboard manager during the operation so the password  
    is not stored in the clipboard history.  
  
    Flow:  
        1. Reads the password from file  
        2. Pauses Pano  
        3. Copies the password to clipboard via xclip  
        4. Pastes with Ctrl+V  
        5. Presses Enter  
        6. Clears the clipboard  
        7. Re-enables Pano  
    """  
    password = _read_password()  
    if not password:  
        return  
  
    # PT_BR: Pausa o Pano para não capturar a senha no histórico  
    # EN_US: Pauses Pano to prevent capturing the password in history  
    _pause_pano()  
  
    # PT_BR: Copia a senha para o clipboard via xclip  
    # EN_US: Copies the password to clipboard via xclip  
    proc = subprocess.Popen(  
        ["xclip", "-selection", "clipboard"],  
        stdin=subprocess.PIPE,  
        stdout=subprocess.DEVNULL,  
        stderr=subprocess.DEVNULL,  
    )  
    proc.communicate(password.encode())  
    time.sleep(0.05)  
  
    # PT_BR: Cola com Ctrl+V e pressiona Enter  
    # EN_US: Pastes with Ctrl+V and presses Enter  
    subprocess.run(  
        ["xdotool", "key", "--clearmodifiers", "ctrl+v"],  
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  
    )  
    subprocess.run(  
        ["xdotool", "key", "--clearmodifiers", "Return"],  
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  
    )  
  
    # PT_BR: Limpa o clipboard e reativa o Pano  
    # EN_US: Clears the clipboard and re-enables Pano  
    time.sleep(0.05)  
    proc = subprocess.Popen(  
        ["xclip", "-selection", "clipboard"],  
        stdin=subprocess.PIPE,  
        stdout=subprocess.DEVNULL,  
        stderr=subprocess.DEVNULL,  
    )  
    proc.communicate(b"")  
  
    _resume_pano()  
  
  
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
    for key_index, label in KEY_LABELS.items():  
        # PT_BR: Gera imagem temporária com o rótulo da tecla  
        # EN_US: Generates temporary image with the key label  
        temp_path = _generate_label_image(device, label)  
        try:  
            # PT_BR: Envia a imagem para o dispositivo e atualiza a tela  
            # EN_US: Sends the image to the device and refreshes the display  
            device.set_key_image(key_index, temp_path)  
            device.refresh()  
        finally:  
            # PT_BR: Remove o arquivo temporário mesmo em caso de erro  
            # EN_US: Removes the temporary file even on error  
            if os.path.exists(temp_path):  
                os.remove(temp_path)  
  
  
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
        ctrl+c/x/v:    simula Ctrl+C, Ctrl+X ou Ctrl+V via xdotool  
  
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
        ctrl+c/x/v:    simulates Ctrl+C, Ctrl+X or Ctrl+V via xdotool  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Só age no pressionamento, ignora release  
    # EN_US: Only acts on press, ignores release  
    if event.state != 1:  
        return  
  
    action = KEY_ACTIONS.get(event.key)  
    if action is None:  
        print(f"Key {event.key} has no action mapped.", flush=True)  
        return  
  
    if action == "password_macro":  
        # PT_BR: Digita a senha via clipboard com Pano pausado  
        # EN_US: Types the password via clipboard with Pano paused  
        _type_password()  
  
    elif action == "Print":  
        # PT_BR: Captura de tela via Flameshot (Shift = delay)  
        # EN_US: Screenshot via Flameshot (Shift = delay)  
        _take_screenshot()  
  
    elif action == "terminal":  
        # PT_BR: Toggle do terminal Guake  
        # EN_US: Guake terminal toggle  
        _open_guake()  
  
    elif action.startswith("ctrl+"):  
        # PT_BR: Simula Ctrl+C, Ctrl+X ou Ctrl+V via xdotool  
        # EN_US: Simulates Ctrl+C, Ctrl+X or Ctrl+V via xdotool  
        key = action.split("+")[1]  
        _run_cmd(["xdotool", "key", "--clearmodifiers", f"ctrl+{key}"])