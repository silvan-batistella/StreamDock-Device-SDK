#####################################################################################  
#  
# PT_BR:  
# Página "default_keyboard_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes das teclas padrão do teclado nas 6 teclas:  
#        Linha 1: INSERT  - HOME - PAGE UP  
#        Linha 2: DELETE  - END  - PAGE DOWN  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, simula a tecla de teclado  
#      correspondente via ydotool.  
#  
# EN_US:  
# "default_keyboard_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays standard keyboard key names on the device's 6 keys:  
#        Row 1: INSERT  - HOME - PAGE UP  
#        Row 2: DELETE  - END  - PAGE DOWN  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, simulates the corresponding keyboard  
#      key via ydotool.  
#  
######################################################################################  
  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import ButtonKey  
from utils.image import render_keys_from_labels  
from utils.keys import send_key, get_action_for_event  
  
  
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
    1: "INS",  
    2: "HOME",  
    3: "PG\nUP",  
    4: "DEL",  
    5: "END",  
    6: "PG\nDN",  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_default_keyboard_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "default_keyboard_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes das teclas padrão e envia para o dispositivo.  
  
    Layout:  
        KEY_1: INSERT    KEY_2: HOME    KEY_3: PAGE UP  
        KEY_4: DELETE    KEY_5: END     KEY_6: PAGE DN  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "default_keyboard_schema" page to the K1Pro device.  
    Generates images with standard key names and sends them to the device.  
  
    Layout:  
        KEY_1: INSERT    KEY_2: HOME    KEY_3: PAGE UP  
        KEY_4: DELETE    KEY_5: END     KEY_6: PAGE DN  
  
    Args:  
        device: K1Pro instance already opened and initialized.  
    """  
    render_keys_from_labels(device, KEY_LABELS)  
  
  
######################################################################################  
#  
# PT_BR: MAPEAMENTO DE TECLAS → AÇÕES DE TECLADO  
#  
# KEY_ACTIONS: dicionário {ButtonKey: str} que mapeia cada tecla do K1Pro  
#   para o nome da tecla de teclado no formato simbólico aceito por send_key.  
#  
#   Layout:  
#     KEY_1: Insert    KEY_2: Home    KEY_3: Page_Up  
#     KEY_4: Delete    KEY_5: End     KEY_6: Page_Down  
#  
# EN_US: KEY → KEYBOARD ACTION MAPPING  
#  
# KEY_ACTIONS: dict {ButtonKey: str} mapping each K1Pro key  
#   to the keyboard key name in symbolic format accepted by send_key.  
#  
#   Layout:  
#     KEY_1: Insert    KEY_2: Home    KEY_3: Page_Up  
#     KEY_4: Delete    KEY_5: End     KEY_6: Page_Down  
#  
######################################################################################  
  
KEY_ACTIONS = {  
    ButtonKey.KEY_1: "Insert",  
    ButtonKey.KEY_2: "Home",  
    ButtonKey.KEY_3: "Page_Up",  
    ButtonKey.KEY_4: "Delete",  
    ButtonKey.KEY_5: "End",  
    ButtonKey.KEY_6: "Page_Down",  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página default_keyboard_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), simula a tecla  
    de teclado correspondente usando ydotool (via utils.keys.send_key).  
    Eventos de release (state == 0) são ignorados.  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the default_keyboard_schema page.  
  
    When a K1Pro key is pressed (state == 1), simulates the corresponding  
    keyboard key using ydotool (via utils.keys.send_key).  
    Release events (state == 0) are ignored.  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Extrai a ação; retorna None se release ou tecla sem mapeamento  
    # EN_US: Extracts the action; returns None if release or unmapped key  
    action = get_action_for_event(event, KEY_ACTIONS)  
    if action is None:  
        return  
  
    # PT_BR: Simula o pressionamento da tecla via ydotool  
    # EN_US: Simulates the key press via ydotool  
    send_key(action)