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
  
_knob_pressed = False  
_knob_rotated_while_pressed = False  
  
PAGE_TIMEOUT_DEFAULT = 15  
PAGE_TIMEOUT_LONG    = 5 * 60  
_NO_TIMEOUT_PAGES    = {"Keyboard"}  
_LONG_TIMEOUT_PAGES  = {"Eclipse Debug"}  
_timeout_timer       = None  
  
  
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
    _cancel_timeout()  
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
    _schedule_timeout(page["name"])  
  
  
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
    PT_BR: Renderiza o seletor de páginas nas 6 teclas (exclui KB Config, última página).  
    EN_US: Renders the page selector on the 6 keys (excludes KB Config, last page).  
    """  
    global _showing_selector  
    _showing_selector = True  
    navigable_count = len(_pages) - 1  # exclui KB Config (sempre o último)  
  
    for key_index in range(1, 7):  
        page_idx = key_index - 1  
  
        if page_idx < navigable_count:  
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
    _schedule_timeout(page["name"])  
  
  
# ─── Timeout de retorno à página default ─────────────────────────────  
  
def _get_page_timeout(page_name):  
    if page_name in _NO_TIMEOUT_PAGES:  
        return None  
    if page_name in _LONG_TIMEOUT_PAGES:  
        return PAGE_TIMEOUT_LONG  
    return PAGE_TIMEOUT_DEFAULT  
  
  
def _cancel_timeout():  
    global _timeout_timer  
    if _timeout_timer is not None:  
        _timeout_timer.cancel()  
        _timeout_timer = None  
  
  
def _do_timeout_return():  
    with _lock:  
        if _current_index != 0:  
            print("[PageManager] Timeout: retornando para página default", flush=True)  
            _switch_to(0)  
  
  
def _schedule_timeout(page_name):  
    _cancel_timeout()  
    global _timeout_timer  
    timeout = _get_page_timeout(page_name)  
    if timeout is not None:  
        _timeout_timer = threading.Timer(timeout, _do_timeout_return)  
        _timeout_timer.daemon = True  
        _timeout_timer.start()  
  
  
def reset_page_timeout():  
    """Reseta o timer de inatividade da página atual (chamar ao pressionar teclas)."""  
    if _pages and 0 <= _current_index < len(_pages):  
        _schedule_timeout(_pages[_current_index]["name"])  
  
  
# ─── Handlers de input ────────────────────────────────────────────────  
  
def handle_selector_key_press(event):  
    """  
    PT_BR: Trata pressionamento de tecla quando o seletor está visível.  
    EN_US: Handles key press when the selector is visible.  
    """  
    if event.state != 1:  
        return  
  
    navigable_count = len(_pages) - 1  # exclui KB Config (sempre o último)  
  
    key_to_index = {  
        ButtonKey.KEY_1: 0,  
        ButtonKey.KEY_2: 1,  
        ButtonKey.KEY_3: 2,  
        ButtonKey.KEY_4: 3,  
        ButtonKey.KEY_5: 4,  
        ButtonKey.KEY_6: 5,  
    }  
  
    page_idx = key_to_index.get(event.key)  
    if page_idx is not None and page_idx < navigable_count:  
        _switch_to(page_idx)  
  
  
def handle_knob_1_page_nav(event_type, direction=None, state=None):  
    """  
    PT_BR: Handler do Knob 1:  
      - ROTAÇÃO (sem pressionar): navega páginas 0..N-2 (KB Config excluída).  
      - ROTAÇÃO (com knob pressionado): esquerda=KB Config, direita=Seletor.  
      - PRESSIONAR + SOLTAR (sem rotação): toggle do seletor de páginas.  
    EN_US: Knob 1 handler:  
      - ROTATE (not pressed): navigates pages 0..N-2 (KB Config excluded).  
      - ROTATE (knob held): left=KB Config, right=Selector.  
      - PRESS + RELEASE (no rotation): toggles the page selector.  
    """  
    global _knob_pressed, _knob_rotated_while_pressed  
  
    if event_type == EventType.KNOB_ROTATE:  
        with _lock:  
            if _knob_pressed:  
                _knob_rotated_while_pressed = True  
                if direction == Direction.LEFT:  
                    _switch_to(len(_pages) - 1)  
                elif direction == Direction.RIGHT:  
                    _show_selector()  
            else:  
                navigable_count = len(_pages) - 1  # exclui KB Config (último)  
                base = _current_index if _current_index < navigable_count else 0  
                if direction == Direction.RIGHT:  
                    _switch_to((base + 1) % navigable_count)  
                elif direction == Direction.LEFT:  
                    _switch_to((base - 1) % navigable_count)  
  
    elif event_type == EventType.KNOB_PRESS:  
        if state == 1:  
            _knob_pressed = True  
            _knob_rotated_while_pressed = False  
        elif state == 0:  
            _knob_pressed = False  
            if not _knob_rotated_while_pressed:  
                with _lock:  
                    if _showing_selector:  
                        _hide_selector()  
                    else:  
                        _show_selector()