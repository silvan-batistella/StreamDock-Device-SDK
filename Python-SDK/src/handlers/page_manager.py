# Python-SDK/src/handlers/page_manager.py  
  
######################################################################################  
#  
# PT_BR: Gerenciador de páginas para o K1 PRO.  
# Mantém um array de páginas e o índice da página ativa.  
# O Knob 1 navega entre as páginas (rotação).  
#  
# EN_US: Page manager for the K1 PRO.  
# Maintains an array of pages and the active page index.  
# Knob 1 navigates between pages (rotation).  
#  
######################################################################################  
  
import os  
import random 
import threading  
from PIL import Image, ImageDraw, ImageFont 
from StreamDock.ImageHelpers.PILHelper import create_key_image
from StreamDock.InputTypes import EventType, Direction, ButtonKey  
  
_pages = []  
_device = None  
_current_index = 0  
_lock = threading.Lock()  
_showing_selector = False
  
  
def register_page(name, short_label, apply_fn, handle_key_fn):  
    """  
    PT_BR: Registra uma página. Ordem de registro = ordem no array.  
    EN_US: Registers a page. Registration order = array order.  
    """  
    _pages.append({  
        "name": name,  
        "apply": apply_fn,
         "label": short_label,  
        "handle_key": handle_key_fn,  
    })  
  
  
def init_pages(device):  
    """  
    PT_BR: Inicializa com o device e renderiza a página 0.  
    EN_US: Initializes with the device and renders page 0.  
    """  
    global _device, _current_index, _showing_selector  
    _device = device  
    _current_index = 0  
    _showing_selector = False  
    if _pages:  
        _pages[0]["apply"](device)  
  
  
def get_current_page():  
    """  
    PT_BR: Retorna a página ativa (dict com 'name', 'apply', 'handle_key').  
    EN_US: Returns the active page (dict with 'name', 'apply', 'handle_key').  
    """  
    if _showing_selector or not _pages:
        return None  
    return _pages[_current_index]  
  
  
def _switch_to(index):  
    """  
    PT_BR: Muda para a página no índice dado (wrap-around com %).  
    EN_US: Switches to the page at the given index (wrap-around with %).  
    """  
    global _current_index, _showing_selector    
    if not _pages or _device is None:
        return  
    _showing_selector = False
    _current_index = index % len(_pages)  
    page = _pages[_current_index]  
    print(f"[PageManager] Page {_current_index}: {page['name']}", flush=True)  
    page["apply"](_device)


# ─── Seletor de páginas ───────────────────────────────────────────────  
  
def _generate_selector_image(label):  
    """  
    PT_BR: Gera imagem 64x64 para um botão do seletor (fundo azul escuro).  
    EN_US: Generates 64x64 image for a selector button (dark blue background).  
    """  
    img = create_key_image(_device, background="#1a1a4e")  
    draw = ImageDraw.Draw(img)  
    try:  
        font = ImageFont.truetype(  
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13  
        )  
    except (IOError, OSError):  
        font = ImageFont.load_default()  
  
    bbox = draw.textbbox((0, 0), label, font=font)  
    text_w = bbox[2] - bbox[0]  
    text_h = bbox[3] - bbox[1]  
    x = (img.width - text_w) // 2  
    y = (img.height - text_h) // 2  
    draw.text((x, y), label, fill="#00ccff", font=font, align="center")  
  
    temp_path = f"selector_{random.randint(9999, 999999)}.jpg"  
    img.save(temp_path, "JPEG")  
    return temp_path  
  
  
def _generate_blank_image():  
    """  
    PT_BR: Gera imagem 64x64 preta (tecla vazia no seletor).  
    EN_US: Generates 64x64 black image (empty key on selector).  
    """  
    img = create_key_image(_device, background="black")  
    temp_path = f"blank_{random.randint(9999, 999999)}.jpg"  
    img.save(temp_path, "JPEG")  
    return temp_path  
  
  
def _show_selector():  
    """  
    PT_BR: Renderiza o seletor de páginas nas 6 teclas.  
    EN_US: Renders the page selector on the 6 keys.  
    """  
    global _showing_selector  
    _showing_selector = True  
  
    for key_index in range(1, 7):  
        page_idx = key_index - 1  
  
        if page_idx < len(_pages):  
            temp_path = _generate_selector_image(_pages[page_idx]["label"])  
        else:  
            temp_path = _generate_blank_image()  
  
        try:  
            _device.set_key_image(key_index, temp_path)  
            _device.refresh()  
        finally:  
            if os.path.exists(temp_path):  
                os.remove(temp_path)  
  
    print("[PageManager] Selector shown", flush=True)  
  
  
def _hide_selector():  
    """  
    PT_BR: Sai do seletor e re-renderiza a página ativa.  
    EN_US: Exits the selector and re-renders the active page.  
    """  
    global _showing_selector  
    _showing_selector = False  
    page = _pages[_current_index]  
    print(f"[PageManager] Selector hidden -> page {_current_index}: {page['name']}", flush=True)  
    page["apply"](_device)  
  
  
def handle_selector_key_press(event):  
    """  
    PT_BR: Trata pressionamento de tecla quando o seletor está visível.  
    EN_US: Handles key press when the selector is visible.  
    """  
    if event.state != 1:  
        return  
  
    key_to_index = {  
        ButtonKey.KEY_1: 0,  
        ButtonKey.KEY_2: 1,  
        ButtonKey.KEY_3: 2,  
        ButtonKey.KEY_4: 3,  
        ButtonKey.KEY_5: 4,  
        ButtonKey.KEY_6: 5,  
    }  
  
    page_idx = key_to_index.get(event.key)  
    if page_idx is not None and page_idx < len(_pages):  
        _switch_to(page_idx)
  
  
def handle_knob_1_page_nav(event_type, direction=None, state=None):  
    """  
    PT_BR: Handler do Knob 1:  
      - ROTAÇÃO: navega páginas (ignorado se seletor visível).  
      - PRESSIONAR: toggle do seletor de páginas.  
    EN_US: Knob 1 handler:  
      - ROTATE: navigates pages (ignored if selector visible).  
      - PRESS: toggles the page selector.  
    """  
    if event_type == EventType.KNOB_ROTATE:  
        with _lock:  
            if _showing_selector:  
                return  
            if direction == Direction.RIGHT:  
                _switch_to(_current_index + 1)  
            elif direction == Direction.LEFT:  
                _switch_to(_current_index - 1)  
  
    elif event_type == EventType.KNOB_PRESS:  
        if state == 1:  
            with _lock:  
                if _showing_selector:  
                    _hide_selector()  
                else:  
                    _show_selector()