#####################################################################################  
#  
# PT_BR:  
# Página "eclipse_debug_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os nomes dos atalhos de debug do Eclipse nas 6 teclas:  
#        Linha 1: BRKPT       - RESUME     - INSPT  
#        Linha 2: STEP INTO   - STEP OVER  - DROP FRM  
#      Cada tecla recebe uma imagem 64x64 com o nome centralizado em fundo preto.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, simula o atalho de teclado  
#      correspondente via ydotool:  
#        KEY_1: Ctrl+Shift+B  (Toggle Breakpoint)  
#        KEY_2: F8            (Resume)  
#        KEY_3: Ctrl+Shift+I  (Inspect)  
#        KEY_4: F5            (Step Into)  
#        KEY_5: F6            (Step Over)  
#        KEY_6: F9            (Drop to Frame)  
#  
# Dependências externas:  
#   - ydotool (simulação de teclas)  
#  
# EN_US:  
# "eclipse_debug_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays Eclipse debug shortcut names on the device's 6 keys:  
#        Row 1: BRKPT       - RESUME     - INSPT  
#        Row 2: STEP INTO   - STEP OVER  - DROP FRM  
#      Each key receives a 64x64 image with the name centered on a black background.  
#  
#   2. BEHAVIOR: When a key is pressed, simulates the corresponding keyboard  
#      shortcut via ydotool:  
#        KEY_1: Ctrl+Shift+B  (Toggle Breakpoint)  
#        KEY_2: F8            (Resume)  
#        KEY_3: Ctrl+Shift+I  (Inspect)  
#        KEY_4: F5            (Step Into)  
#        KEY_5: F6            (Step Over)  
#        KEY_6: F9            (Drop to Frame)  
#  
# External dependencies:  
#   - ydotool (key simulation)  
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
    1: "Break\nPoint",          # Toggle Breakpoint (Ctrl+Shift+B)  
    2: "Resum",           # Resume (F8)  
    3: "Inspc",          # Inspect (Ctrl+Shift+I)  
    4: "Step\nInto",     # Step Into (F5)  
    5: "Step\nOver",     # Step Over (F6)  
    6: "Drop\nFrm",      # Drop to Frame (F9)  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_eclipse_debug_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "eclipse_debug_page_schema" no dispositivo K1Pro.  
    Gera imagens com os nomes dos atalhos de debug do Eclipse e envia  
    para o dispositivo.  
  
    Layout:  
        KEY_1: BRKPT      KEY_2: RSME        KEY_3: INSPT  
        KEY_4: STEP INTO   KEY_5: STEP OVER   KEY_6: DROP FRM  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "eclipse_debug_page_schema" page to the K1Pro device.  
    Generates images with Eclipse debug shortcut names and sends them  
    to the device.  
  
    Layout:  
        KEY_1: BRKPT      KEY_2: RSME        KEY_3: INSPT  
        KEY_4: STEP INTO   KEY_5: STEP OVER   KEY_6: DROP FRM  
  
    Args:  
        device: K1Pro instance already opened and initialized.  
    """  
    render_keys_from_labels(device, KEY_LABELS)  
  
  
######################################################################################  
#  
# PT_BR: MAPEAMENTO DE TECLAS → AÇÕES DE TECLADO  
#  
# KEY_ACTIONS: dicionário {ButtonKey: str} que mapeia cada tecla do K1Pro  
#   para o atalho de teclado no formato simbólico aceito por send_key.  
#  
#   Layout:  
#     KEY_1: ctrl+shift+b   KEY_2: F8            KEY_3: ctrl+shift+i  
#     KEY_4: F5             KEY_5: F6            KEY_6: F9  
#  
# EN_US: KEY → KEYBOARD ACTION MAPPING  
#  
# KEY_ACTIONS: dict {ButtonKey: str} mapping each K1Pro key  
#   to the keyboard shortcut in symbolic format accepted by send_key.  
#  
#   Layout:  
#     KEY_1: ctrl+shift+b   KEY_2: F8            KEY_3: ctrl+shift+i  
#     KEY_4: F5             KEY_5: F6            KEY_6: F9  
#  
######################################################################################  
  
KEY_ACTIONS = {  
    ButtonKey.KEY_1: "ctrl+shift+b",      # Toggle Breakpoint  
    ButtonKey.KEY_2: "F8",                 # Resume  
    ButtonKey.KEY_3: "ctrl+shift+i",       # Inspect  
    ButtonKey.KEY_4: "F5",                 # Step Into  
    ButtonKey.KEY_5: "F6",                 # Step Over  
    ButtonKey.KEY_6: "F9",                 # Drop to Frame  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página eclipse_debug_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), simula o atalho  
    de teclado correspondente do Eclipse usando ydotool (via utils.keys.send_key).  
    Eventos de release (state == 0) são ignorados.  
  
    Ações:  
        ctrl+shift+b:  Toggle Breakpoint  
        F8:            Resume (continuar execução)  
        ctrl+shift+i:  Inspect (inspecionar variável/expressão)  
        F5:            Step Into (entrar na função)  
        F6:            Step Over (passar por cima)  
        F9:            Drop to Frame (voltar ao frame)  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the eclipse_debug_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), simulates the corresponding  
    Eclipse keyboard shortcut using ydotool (via utils.keys.send_key).  
    Release events (state == 0) are ignored.  
  
    Actions:  
        ctrl+shift+b:  Toggle Breakpoint  
        F8:            Resume (continue execution)  
        ctrl+shift+i:  Inspect (inspect variable/expression)  
        F5:            Step Into  
        F6:            Step Over  
        F9:            Drop to Frame  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Extrai a ação; retorna None se release ou tecla sem mapeamento  
    # EN_US: Extracts the action; returns None if release or unmapped key  
    action = get_action_for_event(event, KEY_ACTIONS)  
    if action is None:  
        return  
  
    # PT_BR: Simula o atalho via ydotool  
    # EN_US: Simulates the shortcut via ydotool  
    send_key(action)