# Python-SDK/src/handlers/gnome_system_page_schema.py  
  
#####################################################################################  
#  
# PT_BR:  
# Página "gnome_system_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes dos utilitários/apps nas 6 teclas:  
#        Linha 1: BT        - GNM EXTS   - SYS MON  
#        Linha 2: IRIUN     - OBS        - LUTRS  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, lança o aplicativo correspondente:  
#        KEY_1: Gerenciador Bluetooth (gnome-control-center bluetooth)  
#        KEY_2: GNOME Extensions (gnome-extensions-app)  
#        KEY_3: GNOME System Monitor (gnome-system-monitor)  
#        KEY_4: Iriun Webcam (iriunwebcam)  
#        KEY_5: OBS Studio (obs)  
#        KEY_6: Lutris (lutris)  
#  
# Dependências externas:  
#   - gnome-control-center  
#   - gnome-extensions-app (GNOME 40+)  
#   - gnome-system-monitor  
#   - iriunwebcam  
#   - obs  
#   - lutris  
#  
# EN_US:  
# "gnome_system_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays utility/app names on the device's 6 keys:  
#        Row 1: BT        - GNM EXTS   - SYS MON  
#        Row 2: IRIUN     - OBS        - LUTRS  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, launches the corresponding application:  
#        KEY_1: Bluetooth Manager (gnome-control-center bluetooth)  
#        KEY_2: GNOME Extensions (gnome-extensions-app)  
#        KEY_3: GNOME System Monitor (gnome-system-monitor)  
#        KEY_4: Iriun Webcam (iriunwebcam)  
#        KEY_5: OBS Studio (obs)  
#        KEY_6: Lutris (lutris)  
#  
# External dependencies:  
#   - gnome-control-center  
#   - gnome-extensions-app (GNOME 40+)  
#   - gnome-system-monitor  
#   - iriunwebcam  
#   - obs  
#   - lutris  
#  
######################################################################################  
  
from PIL import Image, ImageDraw, ImageFont  
from StreamDock.ImageHelpers.PILHelper import create_key_image  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType, ButtonKey  
import os  
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
    1: "BT",              # Bluetooth Manager  
    2: "Gnm\nExts",       # GNOME Extensions  
    3: "Sys\nMon",        # GNOME System Monitor  
    4: "Iriun",           # Iriun Webcam  
    5: "OBS",             # OBS Studio  
    6: "Lutrs",           # Lutris  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES — EXECUÇÃO DE COMANDOS  
# EN_US: HELPER FUNCTIONS — COMMAND EXECUTION  
# =============================================================================  
  
def _run_cmd(cmd):  
    """  
    PT_BR: Executa comando de forma assíncrona (não-bloqueante).  
           Usa start_new_session=True para desacoplar o processo filho  
           do terminal/script pai (sobrevive ao encerramento do pai).  
    EN_US: Executes command asynchronously (non-blocking).  
           Uses start_new_session=True to detach the child process  
           from the parent terminal/script (survives parent termination).  
    """  
    try:  
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)  
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
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_gnome_system_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "gnome_system_page_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes dos utilitários GNOME e envia para o dispositivo.  
  
    Layout:  
        KEY_1: BT         KEY_2: GNM EXTS    KEY_3: SYS MON  
        KEY_4: IRIUN      KEY_5: OBS         KEY_6: LUTRS  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "gnome_system_page_schema" page to the K1Pro device.  
    Generates images with GNOME utility names and sends them to the device.  
  
    Layout:  
        KEY_1: BT         KEY_2: GNM EXTS    KEY_3: SYS MON  
        KEY_4: IRIUN      KEY_5: OBS         KEY_6: LUTRS  
  
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
# PT_BR: MAPEAMENTO DE TECLAS → COMANDOS DE LANÇAMENTO  
#  
# KEY_COMMANDS: dicionário {ButtonKey: list[str]} que mapeia cada tecla do K1Pro  
#   para o comando de lançamento do aplicativo (formato subprocess).  
#  
#   Layout:  
#     KEY_1: gnome-control-center bluetooth   KEY_2: gnome-extensions-app   KEY_3: gnome-system-monitor  
#     KEY_4: iriunwebcam                      KEY_5: obs                    KEY_6: lutris  
#  
# EN_US: KEY → LAUNCH COMMAND MAPPING  
#  
# KEY_COMMANDS: dict {ButtonKey: list[str]} mapping each K1Pro key  
#   to the application launch command (subprocess format).  
#  
#   Layout:  
#     KEY_1: gnome-control-center bluetooth   KEY_2: gnome-extensions-app   KEY_3: gnome-system-monitor  
#     KEY_4: iriunwebcam                      KEY_5: obs                    KEY_6: lutris  
#  
######################################################################################  
  
KEY_COMMANDS = {  
    ButtonKey.KEY_1: ["gnome-control-center", "bluetooth"],  
    ButtonKey.KEY_2: ["gnome-extensions-app"],  
    ButtonKey.KEY_3: ["gnome-system-monitor"],  
    ButtonKey.KEY_4: ["iriunwebcam"],  
    ButtonKey.KEY_5: ["obs"],  
    ButtonKey.KEY_6: ["lutris"],  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página gnome_system_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), lança o aplicativo  
    correspondente via subprocess.Popen (não-bloqueante, desacoplado).  
    Eventos de release (state == 0) são ignorados.  
  
    Aplicativos:  
        KEY_1: Gerenciador Bluetooth (gnome-control-center bluetooth)  
        KEY_2: GNOME Extensions (gnome-extensions-app)  
        KEY_3: GNOME System Monitor (gnome-system-monitor)  
        KEY_4: Iriun Webcam (iriunwebcam)  
        KEY_5: OBS Studio (obs)  
        KEY_6: Lutris (lutris)  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the gnome_system_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), launches the corresponding  
    application via subprocess.Popen (non-blocking, detached).  
    Release events (state == 0) are ignored.  
  
    Applications:  
        KEY_1: Bluetooth Manager (gnome-control-center bluetooth)  
        KEY_2: GNOME Extensions (gnome-extensions-app)  
        KEY_3: GNOME System Monitor (gnome-system-monitor)  
        KEY_4: Iriun Webcam (iriunwebcam)  
        KEY_5: OBS Studio (obs)  
        KEY_6: Lutris (lutris)  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Só age no pressionamento, ignora release  
    # EN_US: Only acts on press, ignores release  
    if event.state != 1:  
        return  
  
    # PT_BR: Busca o comando de lançamento correspondente  
    # EN_US: Looks up the corresponding launch command  
    cmd = KEY_COMMANDS.get(event.key)  
    if cmd is None:  
        print(f"Key {event.key} has no command mapped.", flush=True)  
        return  
  
    # PT_BR: Lança o aplicativo de forma assíncrona e desacoplada  
    # EN_US: Launches the application asynchronously and detached  
    _run_cmd(cmd)