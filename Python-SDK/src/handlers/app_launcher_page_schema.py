#####################################################################################  
#  
# PT_BR:  
# Página "app_launcher_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes dos aplicativos nas 6 teclas:  
#        Linha 1: FERDIUM   - CHR SOCIN  - CHR BTL  
#        Linha 2: ECLIPSE   - INTELLIJ   - DBEAVER  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, lança o aplicativo correspondente:  
#        KEY_1: Ferdium (mensageiro unificado)  
#        KEY_2: Google Chrome — perfil "Profile 1" (Socin)  
#        KEY_3: Google Chrome — perfil "Default" (Btl)  
#        KEY_4: Eclipse IDE  
#        KEY_5: IntelliJ IDEA Community  
#        KEY_6: DBeaver Community Edition  
#  
# Dependências externas:  
#   - ferdium  
#   - google-chrome  
#   - /xpto/dev/ide/eclipse/eclipse  
#   - intellij-idea-community  
#   - dbeaver-ce  
#  
# EN_US:  
# "app_launcher_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays application names on the device's 6 keys:  
#        Row 1: FERDIUM   - CHR SOCIN  - CHR BTL  
#        Row 2: ECLIPSE   - INTELLIJ   - DBEAVER  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, launches the corresponding application:  
#        KEY_1: Ferdium (unified messenger)  
#        KEY_2: Google Chrome — profile "Profile 1" (Socin)  
#        KEY_3: Google Chrome — profile "Default" (Btl)  
#        KEY_4: Eclipse IDE  
#        KEY_5: IntelliJ IDEA Community  
#        KEY_6: DBeaver Community Edition  
#  
# External dependencies:  
#   - ferdium  
#   - google-chrome  
#   - /xpto/dev/ide/eclipse/eclipse  
#   - intellij-idea-community  
#   - dbeaver-ce  
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
    1: "Frdm",            # Ferdium  
    2: "Chrm\nSCN",      # Chrome — Profile 1 (Socin)  
    3: "Chrm\nBtl",        # Chrome — Default (Btl)  
    4: "Eclps",           # Eclipse IDE  
    5: "Intlj",           # IntelliJ IDEA Community  
    6: "DBvr",            # DBeaver CE  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_app_launcher_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "app_launcher_page_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes dos aplicativos e envia para o dispositivo.  
  
    Layout:  
        KEY_1: FRDM      KEY_2: CHR SOCIN   KEY_3: CHR BTL  
        KEY_4: ECLPS      KEY_5: INTLJ       KEY_6: DBVR  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "app_launcher_page_schema" page to the K1Pro device.  
    Generates images with application names and sends them to the device.  
  
    Layout:  
        KEY_1: FRDM      KEY_2: CHR SOCIN   KEY_3: CHR BTL  
        KEY_4: ECLPS      KEY_5: INTLJ       KEY_6: DBVR  
  
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
#     KEY_1: ferdium                          KEY_2: chrome (Profile 1)   KEY_3: chrome (Default)  
#     KEY_4: eclipse                          KEY_5: intellij             KEY_6: dbeaver  
#  
# EN_US: KEY → LAUNCH COMMAND MAPPING  
#  
# KEY_COMMANDS: dict {ButtonKey: list[str]} mapping each K1Pro key  
#   to the application launch command (subprocess format).  
#  
#   Layout:  
#     KEY_1: ferdium                          KEY_2: chrome (Profile 1)   KEY_3: chrome (Default)  
#     KEY_4: eclipse                          KEY_5: intellij             KEY_6: dbeaver  
#  
######################################################################################  
  
KEY_COMMANDS = {  
    ButtonKey.KEY_1: ["ferdium"],  
    ButtonKey.KEY_2: ["google-chrome", "--profile-directory=Profile 1"],  
    ButtonKey.KEY_3: ["google-chrome", "--profile-directory=Default"],  
    ButtonKey.KEY_4: ["/xpto/dev/ide/eclipse/eclipse/eclipse"],  
    ButtonKey.KEY_5: ["intellij-idea-community"],  
    ButtonKey.KEY_6: ["dbeaver-ce"],  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página app_launcher_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), lança o aplicativo  
    correspondente via subprocess.Popen (não-bloqueante).  
    Eventos de release (state == 0) são ignorados.  
  
    Aplicativos:  
        KEY_1: Ferdium (mensageiro unificado)  
        KEY_2: Google Chrome — perfil "Profile 1" (Socin)  
        KEY_3: Google Chrome — perfil "Default" (Btl)  
        KEY_4: Eclipse IDE (/xpto/dev/ide/eclipse/eclipse)  
        KEY_5: IntelliJ IDEA Community  
        KEY_6: DBeaver Community Edition  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the app_launcher_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), launches the corresponding  
    application via subprocess.Popen (non-blocking).  
    Release events (state == 0) are ignored.  
  
    Applications:  
        KEY_1: Ferdium (unified messenger)  
        KEY_2: Google Chrome — profile "Profile 1" (Socin)  
        KEY_3: Google Chrome — profile "Default" (Btl)  
        KEY_4: Eclipse IDE (/xpto/dev/ide/eclipse/eclipse)  
        KEY_5: IntelliJ IDEA Community  
        KEY_6: DBeaver Community Edition  
  
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
  
    # PT_BR: Lança o aplicativo de forma assíncrona  
    # EN_US: Launches the application asynchronously  
    run_cmd(cmd)