# k1pro_linux.py  
# Entry point para K1 PRO no Linux — apenas controle de knobs (volume/mic).  
  
from StreamDock.DeviceManager import DeviceManager  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType, KnobId  
from handlers.knob_handlers import handle_knob_2, handle_knob_3  
import threading  
import time  
  
  
KNOB_HANDLERS = {  
    KnobId.KNOB_2: handle_knob_2,  # Microfone  
    KnobId.KNOB_3: handle_knob_3,  # Speaker  
}  
  
  
def key_callback(device, event):  
    try:  
        if event.event_type in (EventType.KNOB_ROTATE, EventType.KNOB_PRESS):  
            handler = KNOB_HANDLERS.get(event.knob_id)  
            if handler:  
                handler(  
                    event_type=event.event_type,  
                    direction=getattr(event, "direction", None),  
                    state=getattr(event, "state", None),  
                )  
    except Exception as e:  
        print(f"Callback error: {e}", flush=True)  
  
  
def main():  
    time.sleep(0.5)  # Estabilização USB  
  
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