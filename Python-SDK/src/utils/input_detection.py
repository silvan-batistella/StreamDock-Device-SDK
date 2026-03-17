import ctypes  
import ctypes.util  
  
  
def is_shift_pressed() -> bool:  
    """  
    PT_BR: Verifica se Shift está pressionado via XQueryKeymap (X11).  
    EN_US: Checks if Shift is pressed via XQueryKeymap (X11).  
    """  
    try:  
        x11_path = ctypes.util.find_library("X11")  
        if not x11_path:  
            return False  
  
        x11 = ctypes.cdll.LoadLibrary(x11_path)  
        x11.XOpenDisplay.restype = ctypes.c_void_p  
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]  
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]  
        x11.XQueryKeymap.argtypes = [ctypes.c_void_p, ctypes.c_char * 32]  
  
        display = x11.XOpenDisplay(None)  
        if not display:  
            return False  
  
        try:  
            keymap = (ctypes.c_char * 32)()  
            x11.XQueryKeymap(display, keymap)  
  
            def _is_key_pressed(keycode):  
                byte_index = keycode // 8  
                bit_index = keycode % 8  
                return bool(keymap[byte_index][0] & (1 << bit_index))  
  
            return _is_key_pressed(50) or _is_key_pressed(62)  
        finally:  
            x11.XCloseDisplay(display)  
    except Exception:  
        return False