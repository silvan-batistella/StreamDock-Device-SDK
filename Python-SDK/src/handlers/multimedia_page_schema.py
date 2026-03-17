#####################################################################################  
#  
# PT_BR:  
# Página "multimedia_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes dos controles de mídia nas 6 teclas:  
#        Linha 1: RTHMB     - PLAY/PAUSE - SHFFL  
#        Linha 2: PREV      - STOP       - NEXT  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, executa a ação correspondente:  
#        KEY_1: Abre/foca o Rhythmbox  
#        KEY_2: Play/Pause via playerctl  
#        KEY_3: Toggle shuffle via playerctl  
#        KEY_4: Faixa anterior via playerctl  
#        KEY_5: Parar reprodução via playerctl  
#        KEY_6: Próxima faixa via playerctl  
#  
# Dependências externas:  
#   - playerctl (controle de mídia via MPRIS2)  
#   - rhythmbox (player de música)  
#   - wmctrl (foco de janela)  
#  
# EN_US:  
# "multimedia_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays media control names on the device's 6 keys:  
#        Row 1: RTHMB     - PLAY/PAUSE - SHFFL  
#        Row 2: PREV      - STOP       - NEXT  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, executes the corresponding action:  
#        KEY_1: Opens/focuses Rhythmbox  
#        KEY_2: Play/Pause via playerctl  
#        KEY_3: Toggle shuffle via playerctl  
#        KEY_4: Previous track via playerctl  
#        KEY_5: Stop playback via playerctl  
#        KEY_6: Next track via playerctl  
#  
# External dependencies:  
#   - playerctl (media control via MPRIS2)  
#   - rhythmbox (music player)  
#   - wmctrl (window focus)  
#  
######################################################################################  
  
import subprocess  
import time  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import ButtonKey  
from utils.commands import run_cmd  
from utils.image import render_keys_from_labels  
from utils.keys import get_action_for_event  
  
  
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
    1: "Rthmb",           # Rhythmbox  
    2: "Play\nPause",     # Play/Pause  
    3: "Shffl",           # Shuffle toggle  
    4: "Prev",            # Previous track  
    5: "Stop",            # Stop  
    6: "Next",            # Next track  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — RHYTHMBOX  
# EN_US: HELPER FUNCTIONS — RHYTHMBOX  
# =============================================================================  
  
def _is_rhythmbox_running() -> bool:  
    """  
    PT_BR: Verifica se o Rhythmbox já está rodando via pgrep.  
    EN_US: Checks if Rhythmbox is already running via pgrep.  
    """  
    try:  
        result = subprocess.run(  
            ["pgrep", "-x", "rhythmbox"],  
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL,  
        )  
        return result.returncode == 0  
    except Exception:  
        return False  
  
  
def _open_rhythmbox():  
    """  
    PT_BR:  
    Garante que o Rhythmbox está rodando e foca a janela.  
    Se o Rhythmbox não estiver ativo, inicia o processo e aguarda.  
  
    EN_US:  
    Ensures Rhythmbox is running and focuses the window.  
    If Rhythmbox is not active, starts the process and waits.  
    """  
    if not _is_rhythmbox_running():  
        print("Rhythmbox não está rodando. Iniciando...", flush=True)  
        run_cmd(["rhythmbox"])  
  
        # PT_BR: Aguarda o Rhythmbox subir (máx ~3s)  
        # EN_US: Waits for Rhythmbox to start (max ~3s)  
        retries = 10  
        while retries > 0 and not _is_rhythmbox_running():  
            time.sleep(0.3)  
            retries -= 1  
  
        if not _is_rhythmbox_running():  
            print("Falha ao iniciar o Rhythmbox.", flush=True)  
            return  
  
    # PT_BR: Foca a janela do Rhythmbox via wmctrl  
    # EN_US: Focuses the Rhythmbox window via wmctrl  
    run_cmd(["wmctrl", "-a", "Rhythmbox"])  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_multimedia_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "multimedia_page_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes dos controles de mídia e envia para o dispositivo.  
  
    Layout:  
        KEY_1: RTHMB     KEY_2: PLAY/PAUSE   KEY_3: SHFFL  
        KEY_4: PREV      KEY_5: STOP         KEY_6: NEXT  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "multimedia_page_schema" page to the K1Pro device.  
    Generates images with media control names and sends them to the device.  
  
    Layout:  
        KEY_1: RTHMB     KEY_2: PLAY/PAUSE   KEY_3: SHFFL  
        KEY_4: PREV      KEY_5: STOP         KEY_6: NEXT  
  
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
#     KEY_1: rhythmbox      KEY_2: play_pause    KEY_3: shuffle  
#     KEY_4: prev           KEY_5: stop          KEY_6: next  
#  
# EN_US: KEY → ACTION MAPPING  
#  
# KEY_ACTIONS: dict {ButtonKey: str} mapping each K1Pro key  
#   to the corresponding action.  
#  
#   Layout:  
#     KEY_1: rhythmbox      KEY_2: play_pause    KEY_3: shuffle  
#     KEY_4: prev           KEY_5: stop          KEY_6: next  
#  
######################################################################################  
  
KEY_ACTIONS = {  
    ButtonKey.KEY_1: "rhythmbox",  
    ButtonKey.KEY_2: "play_pause",  
    ButtonKey.KEY_3: "shuffle",  
    ButtonKey.KEY_4: "prev",  
    ButtonKey.KEY_5: "stop",  
    ButtonKey.KEY_6: "next",  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página multimedia_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), executa a ação  
    de mídia correspondente.  
    Eventos de release (state == 0) são ignorados.  
  
    Ações:  
        KEY_1: Abre/foca o Rhythmbox  
        KEY_2: Play/Pause (playerctl play-pause)  
        KEY_3: Toggle shuffle (playerctl shuffle Toggle)  
        KEY_4: Faixa anterior (playerctl previous)  
        KEY_5: Parar reprodução (playerctl stop)  
        KEY_6: Próxima faixa (playerctl next)  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the multimedia_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), executes the corresponding  
    media action.  
    Release events (state == 0) are ignored.  
  
    Actions:  
        KEY_1: Opens/focuses Rhythmbox  
        KEY_2: Play/Pause (playerctl play-pause)  
        KEY_3: Toggle shuffle (playerctl shuffle Toggle)  
        KEY_4: Previous track (playerctl previous)  
        KEY_5: Stop playback (playerctl stop)  
        KEY_6: Next track (playerctl next)  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Extrai a ação; retorna None se release ou tecla sem mapeamento  
    # EN_US: Extracts the action; returns None if release or unmapped key  
    action = get_action_for_event(event, KEY_ACTIONS)  
    if action is None:  
        return  
  
    if action == "rhythmbox":  
        _open_rhythmbox()  
    elif action == "play_pause":  
        run_cmd(["playerctl", "play-pause"])  
    elif action == "shuffle":  
        run_cmd(["playerctl", "shuffle", "Toggle"])  
    elif action == "prev":  
        run_cmd(["playerctl", "previous"])  
    elif action == "stop":  
        run_cmd(["playerctl", "stop"])  
    elif action == "next":  
        run_cmd(["playerctl", "next"])