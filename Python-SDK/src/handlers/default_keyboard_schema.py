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
#      correspondente via xdotool.  
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
#      key via xdotool.  
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
    1: "INS",  
    2: "HOME",  
    3: "PG\nUP",  
    4: "DEL",  
    5: "END",  
    6: "PG\nDN",  
}  
  
  
# =============================================================================  
# PT_BR: FUNÇÕES AUXILIARES  
# EN_US: HELPER FUNCTIONS  
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
# PT_BR: MAPEAMENTO DE TECLAS → AÇÕES DE TECLADO  
#  
# KEY_ACTIONS: dicionário {ButtonKey: str} que mapeia cada tecla do K1Pro  
#   para o nome da tecla do teclado no formato aceito pelo xdotool.  
#  
#   Layout:  
#     KEY_1: INSERT    KEY_2: HOME    KEY_3: Page_Up  
#     KEY_4: DELETE    KEY_5: END     KEY_6: Page_Down  
#  
# EN_US: KEY → KEYBOARD ACTION MAPPING  
#  
# KEY_ACTIONS: dict {ButtonKey: str} mapping each K1Pro key  
#   to the keyboard key name in xdotool format.  
#  
#   Layout:  
#     KEY_1: INSERT    KEY_2: HOME    KEY_3: Page_Up  
#     KEY_4: DELETE    KEY_5: END     KEY_6: Page_Down  
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
  
  
def _run_cmd(cmd):  
    """  
    PT_BR: Executa comando de forma assíncrona (não-bloqueante).  
    EN_US: Executes command asynchronously (non-blocking).  
    """  
    try:  
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)  
    except Exception as e:  
        print(f"Command error: {e}", flush=True)  
  
  
def handle_key_press(event):  
    """  
    PT_BR:  
    Handler de pressionamento de teclas da página default_keyboard_schema.  
  
    Quando uma tecla do K1Pro é pressionada (state == 1), simula a tecla  
    de teclado correspondente usando xdotool.  
    Eventos de release (state == 0) são ignorados.  
  
    Args:  
        event: InputEvent com event_type == EventType.BUTTON  
  
    EN_US:  
    Key press handler for the default_keyboard_schema page.  
  
    When a K1Pro key is pressed (state == 1), simulates the corresponding  
    keyboard key using xdotool.  
    Release events (state == 0) are ignored.  
  
    Args:  
        event: InputEvent with event_type == EventType.BUTTON  
    """  
    # PT_BR: Só age no pressionamento, ignora release  
    # EN_US: Only acts on press, ignores release  
    if event.state != 1:  
        return  
  
    # PT_BR: Busca a tecla de teclado correspondente  
    # EN_US: Looks up the corresponding keyboard key  
    xdotool_key = KEY_ACTIONS.get(event.key)  
    if xdotool_key is None:  
        print(f"Key {event.key} has no action mapped.", flush=True)  
        return  
  
    # PT_BR: Simula o pressionamento da tecla via xdotool  
    # EN_US: Simulates the key press via xdotool  
    _run_cmd(["xdotool", "key", xdotool_key])