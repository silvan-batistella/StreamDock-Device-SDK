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
  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import ButtonKey  
from utils.commands import run_cmd  
from utils.image import render_keys_from_labels  
  
  
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
    render_keys_from_labels(device, KEY_LABELS)  
  
  
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
    run_cmd(cmd)