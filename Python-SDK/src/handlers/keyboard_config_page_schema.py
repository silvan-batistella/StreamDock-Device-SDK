#####################################################################################  
#  
# PT_BR:  
# Página "keyboard_config_page_schema" para o K1 PRO.  
#  
# Responsabilidades:  
#   1. VISUAL: Exibe os controles de configuração do teclado nas 6 teclas:  
#        Linha 1: COR RGB    - EFEITO     - VELOC  
#        Linha 2: BL BRILHO  - SCR BRILHO - RESET  
#      Cada tecla mostra o valor atual da configuração.  
#  
#   2. COMPORTAMENTO: Ao pressionar uma tecla, cicla pelo próximo valor  
#      da configuração correspondente e aplica imediatamente no dispositivo:  
#        KEY_1: Cicla cores RGB predefinidas  
#        KEY_2: Cicla efeitos de iluminação (0-9)  
#        KEY_3: Cicla velocidade da animação (0-7)  
#        KEY_4: Cicla brilho do backlight do teclado (0-6)  
#        KEY_5: Cicla brilho da tela (0/25/50/75/100)  
#        KEY_6: Reseta todas as configurações para o padrão  
#  
# EN_US:  
# "keyboard_config_page_schema" page for the K1 PRO.  
#  
# Responsibilities:  
#   1. VISUAL: Displays keyboard configuration controls on the 6 keys:  
#        Row 1: RGB COLOR  - EFFECT     - SPEED  
#        Row 2: BL BRIGHT  - SCR BRIGHT - RESET  
#      Each key shows the current configuration value.  
#  
#   2. BEHAVIOR: When a key is pressed, cycles to the next value  
#      of the corresponding setting and applies it immediately:  
#        KEY_1: Cycles through preset RGB colors  
#        KEY_2: Cycles lighting effects (0-9)  
#        KEY_3: Cycles animation speed (0-7)  
#        KEY_4: Cycles keyboard backlight brightness (0-6)  
#        KEY_5: Cycles screen brightness (0/25/50/75/100)  
#        KEY_6: Resets all settings to defaults  
#  
######################################################################################  
  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import ButtonKey  
from utils.image import render_keys_from_labels  
  
  
######################################################################################  
#  
# PT_BR: ESTADO DA PÁGINA  
#  
# Armazena o estado atual de cada configuração e a referência ao device.  
# O device é capturado quando apply_keyboard_config_page_schema() é chamado.  
#  
# EN_US: PAGE STATE  
#  
# Stores the current state of each setting and the device reference.  
# The device is captured when apply_keyboard_config_page_schema() is called.  
#  
######################################################################################  
  
_device = None  
  
# PT_BR: Cores predefinidas: (nome_curto, R, G, B)  
# EN_US: Preset colors: (short_name, R, G, B)  
COLOR_PRESETS = [  
    ("Red",    255,   0,   0),  
    ("Green",    0, 255,   0),  
    ("Blue",     0,   0, 255),  
    ("White",  255, 255, 255),  
    ("Purple", 128,   0, 255),  
    ("Cyan",     0, 255, 255),  
    ("Yellow", 255, 255,   0),  
    ("Orange", 255, 128,   0),  
    ("Off",      0,   0,   0),  
]  
  
# PT_BR: Nomes dos efeitos de iluminação (0-9)  
# EN_US: Lighting effect names (0-9)  
EFFECT_NAMES = [  
    "Static",     # 0  
    "Breath",     # 1  
    "Wave",       # 2  
    "Rainbow",    # 3  
    "Cycle",      # 4  
    "Ripple",     # 5  
    "Pulse",      # 6  
    "Spiral",     # 7  
    "Rain",       # 8  
    "Firework",   # 9  
]  
  
# PT_BR: Níveis de brilho da tela  
# EN_US: Screen brightness levels  
SCREEN_BRIGHTNESS_LEVELS = [0, 25, 50, 75, 100]  
  
# PT_BR: Índices atuais (estado mutável)  
# EN_US: Current indices (mutable state)  
_color_index = 0  
_effect_index = 0  
_speed_value = 4  
_bl_brightness = 6  
_scr_brightness_index = 2  # 50%  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO AUXILIAR — ATUALIZAÇÃO DE TECLA INDIVIDUAL  
# EN_US: HELPER FUNCTION — SINGLE KEY UPDATE  
# =============================================================================  
  
def _update_key(key_index: int, label: str):  
    """  
    PT_BR: Atualiza uma única tecla com novo label (sem re-renderizar toda a página).  
    EN_US: Updates a single key with a new label (without re-rendering the whole page).  
    """  
    if _device is None:  
        return  
    render_keys_from_labels(_device, {key_index: label}, font_size=10)  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES DE LABEL — GERAM O TEXTO ATUAL DE CADA TECLA  
# EN_US: LABEL FUNCTIONS — GENERATE CURRENT TEXT FOR EACH KEY  
# =============================================================================  
  
def _label_color():  
    name = COLOR_PRESETS[_color_index][0]  
    return f"Cor\n{name}"  
  
  
def _label_effect():  
    name = EFFECT_NAMES[_effect_index]  
    return f"Efeit\n{name}"  
  
  
def _label_speed():  
    return f"Veloc\n{_speed_value}"  
  
  
def _label_bl_brightness():  
    return f"BL\n{_bl_brightness}"  
  
  
def _label_scr_brightness():  
    pct = SCREEN_BRIGHTNESS_LEVELS[_scr_brightness_index]  
    return f"Tela\n{pct}%"  
  
  
def _label_reset():  
    return "Reset"  
  
  
# =============================================================================  
# PT_BR: FUNÇÃO PRINCIPAL DA PÁGINA  
# EN_US: PAGE MAIN FUNCTION  
# =============================================================================  
  
def apply_keyboard_config_page_schema(device: K1Pro):  
    """  
    PT_BR:  
    Aplica a página "keyboard_config_page_schema" no dispositivo K1Pro.  
    Gera imagens com os valores atuais das configurações e envia para o dispositivo.  
  
    Layout:  
        KEY_1: COR RGB    KEY_2: EFEITO      KEY_3: VELOCIDADE  
        KEY_4: BL BRILHO  KEY_5: SCR BRILHO  KEY_6: RESET  
  
    Args:  
        device: instância do K1Pro já aberta e inicializada.  
  
    EN_US:  
    Applies the "keyboard_config_page_schema" page to the K1Pro device.  
    Generates images with current setting values and sends them to the device.  
  
    Layout:  
        KEY_1: RGB COLOR  KEY_2: EFFECT      KEY_3: SPEED  
        KEY_4: BL BRIGHT  KEY_5: SCR BRIGHT  KEY_6: RESET  
  
    Args:  
        device: K1Pro instance already opened and initialized.  
    """  
    global _device  
    _device = device  
  
    labels = {  
        1: _label_color(),  
        2: _label_effect(),  
        3: _label_speed(),  
        4: _label_bl_brightness(),  
        5: _label_scr_brightness(),  
        6: _label_reset(),  
    }  
  
    render_keys_from_labels(device, labels, font_size=10)  
  
  
######################################################################################  
#  
# PT_BR: HANDLERS DE TECLA — CADA TECLA CICLA UMA CONFIGURAÇÃO  
# EN_US: KEY HANDLERS — EACH KEY CYCLES A SETTING  
#  
######################################################################################  
  
def _handle_color():  
    """  
    PT_BR: Cicla para a próxima cor predefinida e aplica no teclado.  
    EN_US: Cycles to the next preset color and applies it to the keyboard.  
    """  
    global _color_index  
    _color_index = (_color_index + 1) % len(COLOR_PRESETS)  
    name, r, g, b = COLOR_PRESETS[_color_index]  
    _device.set_keyboard_rgb_backlight(r, g, b)  
    _update_key(1, _label_color())  
    print(f"[KBConfig] Color: {name} ({r},{g},{b})", flush=True)  
  
  
def _handle_effect():  
    """  
    PT_BR: Cicla para o próximo efeito de iluminação (0-9).  
    EN_US: Cycles to the next lighting effect (0-9).  
    """  
    global _effect_index  
    _effect_index = (_effect_index + 1) % len(EFFECT_NAMES)  
    _device.set_keyboard_lighting_effects(_effect_index)  
    _update_key(2, _label_effect())  
    print(f"[KBConfig] Effect: {_effect_index} ({EFFECT_NAMES[_effect_index]})", flush=True)  
  
  
def _handle_speed():  
    """  
    PT_BR: Cicla a velocidade da animação (0-7).  
    EN_US: Cycles the animation speed (0-7).  
    """  
    global _speed_value  
    _speed_value = (_speed_value + 1) % 8  
    _device.set_keyboard_lighting_speed(_speed_value)  
    _update_key(3, _label_speed())  
    print(f"[KBConfig] Speed: {_speed_value}", flush=True)  
  
  
def _handle_bl_brightness():  
    """  
    PT_BR: Cicla o brilho do backlight do teclado (0-6).  
    EN_US: Cycles the keyboard backlight brightness (0-6).  
    """  
    global _bl_brightness  
    _bl_brightness = (_bl_brightness + 1) % 7  
    _device.set_keyboard_backlight_brightness(_bl_brightness)  
    _update_key(4, _label_bl_brightness())  
    print(f"[KBConfig] Backlight brightness: {_bl_brightness}", flush=True)  
  
  
def _handle_scr_brightness():  
    """  
    PT_BR: Cicla o brilho da tela (0/25/50/75/100).  
    EN_US: Cycles the screen brightness (0/25/50/75/100).  
    """  
    global _scr_brightness_index  
    _scr_brightness_index = (_scr_brightness_index + 1) % len(SCREEN_BRIGHTNESS_LEVELS)  
    pct = SCREEN_BRIGHTNESS_LEVELS[_scr_brightness_index]  
    _device.set_brightness(pct)  
    _update_key(5, _label_scr_brightness())  
    print(f"[KBConfig] Screen brightness: {pct}%", flush=True)  
  
  
def _handle_reset():  
    """  
    PT_BR: Reseta todas as configurações para os valores padrão.  
    EN_US: Resets all settings to default values.  
    """  
    global _color_index, _effect_index, _speed_value, _bl_brightness, _scr_brightness_index  
  
    # PT_BR: Valores padrão (mesmos do teste C++ do K1Pro)  
    # EN_US: Default values (same as K1Pro C++ test)  
    _color_index = 0           # Red  
    _effect_index = 1          # Breath  
    _speed_value = 4           # Mid speed  
    _bl_brightness = 6         # Max backlight  
    _scr_brightness_index = 2  # 50% screen  
  
    name, r, g, b = COLOR_PRESETS[_color_index]  
    _device.set_keyboard_rgb_backlight(r, g, b)  
    _device.set_keyboard_lighting_effects(_effect_index)  
    _device.set_keyboard_lighting_speed(_speed_value)  
    _device.set_keyboard_backlight_brightness(_bl_brightness)  
    _device.set_brightness(SCREEN_BRIGHTNESS_LEVELS[_scr_brightness_index])  
  
    # PT_BR: Re-renderiza todas as teclas com os valores resetados  
    # EN_US: Re-renders all keys with the reset values  
    apply_keyboard_config_page_schema(_device)  
    print("[KBConfig] All settings reset to defaults", flush=True)  
  
  
# PT_BR: Mapeamento de teclas para handlers  
# EN_US: Key to handler mapping  
_KEY_HANDLERS = {  
    ButtonKey.KEY_1: _handle_color,  
    ButtonKey.KEY_2: _handle_effect,  
    ButtonKey.KEY_3: _handle_speed,  
    ButtonKey.KEY_4: _handle_bl_brightness,  
    ButtonKey.KEY_5: _handle_scr_brightness,  
    ButtonKey.KEY_6: _handle_reset,  
}  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página keyboard_config_page_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), cicla a configuração  
    correspondente e atualiza o label da tecla com o novo valor.  
    Eventos de release (state == 0) são ignorados.  
  
    Configurações:  
        KEY_1: Cor RGB (cicla presets)  
        KEY_2: Efeito de iluminação (cicla 0-9)  
        KEY_3: Velocidade da animação (cicla 0-7)  
        KEY_4: Brilho do backlight (cicla 0-6)  
        KEY_5: Brilho da tela (cicla 0/25/50/75/100)  
        KEY_6: Reset para padrão  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the keyboard_config_page_schema page.  
  
    When a K1Pro key is pressed (state == 1), cycles the corresponding  
    setting and updates the key label with the new value.  
    Release events (state == 0) are ignored.  
  
    Settings:  
        KEY_1: RGB Color (cycles presets)  
        KEY_2: Lighting effect (cycles 0-9)  
        KEY_3: Animation speed (cycles 0-7)  
        KEY_4: Backlight brightness (cycles 0-6)  
        KEY_5: Screen brightness (cycles 0/25/50/75/100)  
        KEY_6: Reset to defaults  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    if event.state != 1:  
        return  
  
    handler = _KEY_HANDLERS.get(event.key)  
    if handler is None:  
        print(f"Key {event.key} has no config action mapped.", flush=True)  
        return  
  
    handler()