# Python-SDK/src/handlers/multimedia_page_schema.py  
  
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
#        KEY_2: Play/Pause via XF86AudioPlay  
#        KEY_3: Toggle shuffle via playerctl  
#        KEY_4: Faixa anterior via XF86AudioPrev  
#        KEY_5: Parar reprodução via XF86AudioStop  
#        KEY_6: Próxima faixa via XF86AudioNext  
#  
# Dependências externas:  
#   - xdotool (simulação de teclas de mídia)  
#   - playerctl (controle de shuffle via MPRIS2)  
#   - rhythmbox (player de música)  
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
#        KEY_2: Play/Pause via XF86AudioPlay  
#        KEY_3: Toggle shuffle via playerctl  
#        KEY_4: Previous track via XF86AudioPrev  
#        KEY_5: Stop playback via XF86AudioStop  
#        KEY_6: Next track via XF86AudioNext  
#  
# External dependencies:  
#   - xdotool (media key simulation)  
#   - playerctl (shuffle control via MPRIS2)  
#   - rhythmbox (music player)  
#  
######################################################################################  
  
from PIL import Image, ImageDraw, ImageFont  
from StreamDock.ImageHelpers.PILHelper import create_key_image  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType, ButtonKey  
import os  
import time  
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
    1: "Rthmb",           # Rhythmbox  
    2: "Play\nPause",     # Play/Pause  
    3: "Shffl",           # Shuffle toggle  
    4: "Prev",            # Previous track  
    5: "Stop",            # Stop  
    6: "Next",            # Next track  
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
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  
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
        _run_cmd(["rhythmbox"])  
  
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
    _run_cmd(["wmctrl", "-a", "Rhythmbox"])  
  
  
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
    if event.state != 1:  
        return  
  
    action = KEY_ACTIONS.get(event.key)  
    if action is None:  
        print(f"Key {event.key} has no action mapped.", flush=True)  
        return  
  
    if action == "rhythmbox":  
        _open_rhythmbox()  
    elif action == "play_pause":  
        _run_cmd(["playerctl", "play-pause"])  
    elif action == "shuffle":  
        _run_cmd(["playerctl", "shuffle", "Toggle"])  
    elif action == "prev":  
        _run_cmd(["playerctl", "previous"])  
    elif action == "stop":  
        _run_cmd(["playerctl", "stop"])  
    elif action == "next":  
        _run_cmd(["playerctl", "next"])