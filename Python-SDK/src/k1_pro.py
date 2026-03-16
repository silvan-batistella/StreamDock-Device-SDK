# Python-SDK/src/k1_pro.py  
  
######################################################################################  
#  
# PT_BR:  
# Entry point para K1 PRO no Linux.  
# Inicializa o dispositivo, aplica a página visual padrão (default_keyboard_schema)  
# e registra os handlers de knobs (volume/mic) e teclas (teclado padrão).  
#  
# EN_US:  
# Entry point for K1 PRO on Linux.  
# Initializes the device, applies the default visual page (default_keyboard_schema)  
# and registers knob handlers (volume/mic) and key handlers (standard keyboard).  
#  
######################################################################################  
  
from StreamDock.DeviceManager import DeviceManager  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType, KnobId  
from handlers.knob_handlers import handle_knob_2, handle_knob_3  
from handlers.default_keyboard_schema import (  
    apply_default_keyboard_schema,  
    handle_key_press,  
)  
import threading  
import time  
  
  
KNOB_HANDLERS = {  
    KnobId.KNOB_2: handle_knob_2,  # Microfone  
    KnobId.KNOB_3: handle_knob_3,  # Speaker  
}  
  
  
def key_callback(device, event):  
    """  
    PT_BR:  
    Callback unificado para todos os eventos de input do K1Pro.  
    Despacha eventos de knob para os handlers de knob e  
    eventos de botão para o handler da página ativa.  
  
    EN_US:  
    Unified callback for all K1Pro input events.  
    Dispatches knob events to knob handlers and  
    button events to the active page handler.  
    """  
    try:  
        # PT_BR: Eventos de knob (rotação e pressionamento)  
        # EN_US: Knob events (rotation and press)  
        if event.event_type in (EventType.KNOB_ROTATE, EventType.KNOB_PRESS):  
            handler = KNOB_HANDLERS.get(event.knob_id)  
            if handler:  
                handler(  
                    event_type=event.event_type,  
                    direction=getattr(event, "direction", None),  
                    state=getattr(event, "state", None),  
                )  
  
        # PT_BR: Eventos de botão (teclas 1-6)  
        # EN_US: Button events (keys 1-6)  
        elif event.event_type == EventType.BUTTON:  
            handle_key_press(event)  
  
    except Exception as e:  
        print(f"Callback error: {e}", flush=True)  
  
  
def main():  
    # PT_BR: Aguarda estabilização da conexão USB  
    # EN_US: Waits for USB connection stabilization  
    time.sleep(0.5)  
  
    manager = DeviceManager()  
    devices = manager.enumerate()  
  
    if not devices:  
        print("Nenhum dispositivo encontrado.")  
        print("  lsusb | grep 6603")  
        print("  ls -la /dev/hidraw*")  
        return  
  
    k1pro_devices = []  
  
    for device in devices:  
        if not isinstance(device, K1Pro):  
            continue  
  
        try:  
            device.open()  
            device.init()  
        except Exception as e:  
            print(f"Falha ao abrir K1 Pro: {e}", flush=True)  
            continue  
  
        print(f"K1 PRO conectado: {device.path}")  
  
        # PT_BR: Aplica a página visual padrão com nomes das teclas do teclado  
        # EN_US: Applies the default visual page with keyboard key names  
        apply_default_keyboard_schema(device)  
  
        device.set_key_callback(key_callback)  
        k1pro_devices.append(device)  
  
    if not k1pro_devices:  
        print("Nenhum K1 PRO encontrado.")  
        return  
  
    listen_thread = threading.Thread(target=manager.listen, daemon=True)  
    listen_thread.start()  
  
    print("\nK1 PRO ativo:")  
    print("  Knob 2: mic volume (press = mute)")  
    print("  Knob 3: speaker volume (press = mute)")  
    print("  Teclas: INSERT, HOME, PAGE UP, DELETE, END, PAGE DN")  
    print("  Ctrl+C para sair\n")  
  
    try:  
        while True:  
            time.sleep(0.1)  
    except KeyboardInterrupt:  
        print("\nEncerrando...")  
    finally:  
        for device in reversed(k1pro_devices):  
            try:  
                device.set_key_callback(None)  
                time.sleep(0.1)  
                device.close()  
            except Exception:  
                pass  
        time.sleep(0.2)  
        print("Finalizado.")  
  
  
if __name__ == "__main__":  
    main()