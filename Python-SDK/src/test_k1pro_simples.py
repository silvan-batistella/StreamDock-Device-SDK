# test_k1pro_simples.py  
# Teste mínimo seguindo o padrão exato do C++ SDK  
import time  
import threading  
from PIL import Image, ImageDraw, ImageFont  
  
from StreamDock.DeviceManager import DeviceManager  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType  
  
CORES = {  
    1: (220, 50, 50),     # Vermelho  
    2: (50, 180, 50),     # Verde  
    3: (50, 80, 220),     # Azul  
    4: (230, 200, 30),    # Amarelo  
    5: (180, 50, 200),    # Magenta  
    6: (30, 200, 200),    # Ciano  
}  
  
  
def gerar_imagem(numero, tamanho=(64, 64)):  
    """Gera imagem simples com cor e número."""  
    img = Image.new("RGB", tamanho, CORES[numero])  
    draw = ImageDraw.Draw(img)  
  
    try:  
        fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho[0] // 2)  
    except OSError:  
        fonte = ImageFont.load_default()  
  
    texto = str(numero)  
    bbox = draw.textbbox((0, 0), texto, font=fonte)  
    x = (tamanho[0] - (bbox[2] - bbox[0])) // 2  
    y = (tamanho[1] - (bbox[3] - bbox[1])) // 2  
    draw.text((x, y), texto, fill=(255, 255, 255), font=fonte)  
  
    # Borda branca de 2px  
    draw.rectangle([0, 0, tamanho[0]-1, tamanho[1]-1], outline=(255, 255, 255), width=2)  
  
    caminho = f"teste_tecla_{numero}.jpg"  
    # SEM parâmetros extras — igual ao SDK original: image.save(path)  
    img.save(caminho)  
    return caminho  
  
  
def callback(device, event):  
    print(f"  Evento: {event}")  
  
  
def main():  
    manner = DeviceManager()  
    dispositivos = manner.enumerate()  
  
    if not dispositivos:  
        print("Nenhum dispositivo encontrado.")  
        return  
  
    listen_thread = threading.Thread(target=manner.listen)  
    listen_thread.daemon = True  
    listen_thread.start()  
  
    print(f"{len(dispositivos)} dispositivo(s) encontrado(s).\n")  
  
    for device in dispositivos:  
        if not isinstance(device, K1Pro):  
            continue  
  
        device.open()  
        device.init()  
        print(f"K1 PRO: {device.path} | Serial: {device.serial_number}")  
  
        # Setup K1Pro (igual ao main.py oficial)  
        device.set_keyboard_backlight_brightness(6)  
        device.set_keyboard_lighting_speed(3)  
        device.set_keyboard_lighting_effects(0)  
        device.set_keyboard_rgb_backlight(255, 0, 0)  
        device.keyboard_os_mode_switch(0)  
  
        # Pausa após init (igual ao C++ SDK: sleep 1000ms)  
        time.sleep(1)  
  
        # Enviar imagens para as 6 teclas  
        # Usando device.set_key_image() — NÃO bypass  
        for i in range(1, 7):  
            caminho = gerar_imagem(i, (64, 64))  
            resultado = device.set_key_image(i, caminho)  
            print(f"  Tecla {i}: resultado = {resultado}")  
  
        # UM refresh após todas as imagens (padrão C++ SDK)  
        device.refresh()  
  
        device.set_key_callback(callback)  
        print("\nImagens enviadas. Verifique o dispositivo.")  
  
    print("Ctrl+C para encerrar.\n")  
    try:  
        while True:  
            time.sleep(0.1)  
    except KeyboardInterrupt:  
        print("\nEncerrando...")  
    finally:  
        for device in reversed(dispositivos):  
            try:  
                device.set_key_callback(None)  
                time.sleep(0.1)  
                device.close()  
            except Exception:  
                pass  
        time.sleep(0.2)  
        print("Encerrado.")  
  
  
if __name__ == "__main__":  
    try:  
        main()  
    except Exception as e:  
        print(f"[ERRO] {e}")  
        import traceback  
        traceback.print_exc()