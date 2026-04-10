# =============================================================================  
# test_k1pro_6teclas.py  
# =============================================================================  
# Gera 6 imagens JPEG (64x64) com cores e números distintos e envia  
# para as 6 teclas do K1 PRO usando o fluxo padrão do SDK.  
#  
# Como executar:  
#   cd Python-SDK/src  
#   sudo ../../venv/bin/python test_k1pro_6teclas.py  
# =============================================================================  
  
import time  
import threading  
from PIL import Image, ImageDraw, ImageFont  
  
from StreamDock.DeviceManager import DeviceManager  
from StreamDock.Devices.K1Pro import K1Pro  
from StreamDock.InputTypes import EventType  
  
  
# --- CONSTANTES --------------------------------------------------------------  
  
TOTAL_TECLAS = 6  
TAMANHO = (64, 64)  
  
# Cor de fundo e nome para cada tecla (1 a 6)  
TECLAS = {  
    1: {"cor": (220, 50, 50),   "nome": "Vermelho"},  
    2: {"cor": (50, 180, 50),   "nome": "Verde"},  
    3: {"cor": (50, 80, 220),   "nome": "Azul"},  
    4: {"cor": (230, 200, 30),  "nome": "Amarelo"},  
    5: {"cor": (180, 50, 200),  "nome": "Magenta"},  
    6: {"cor": (30, 200, 200),  "nome": "Ciano"},  
}  
  
  
# --- GERAR IMAGEM ------------------------------------------------------------  
  
def gerar_imagem(numero):  
    """  
    Cria uma imagem 64x64 com:  
      - Fundo colorido (cor da tecla)  
      - Borda branca de 2px  
      - Número centralizado  
    Salva como JPEG e retorna o caminho do arquivo.  
    """  
    cor = TECLAS[numero]["cor"]  
    img = Image.new("RGB", TAMANHO, color=cor)  
    draw = ImageDraw.Draw(img)  
  
    # Borda branca (2px)  
    draw.rectangle(  
        [0, 0, TAMANHO[0] - 1, TAMANHO[1] - 1],  
        outline=(255, 255, 255),  
        width=2,  
    )  
  
    # Texto (número da tecla)  
    try:  
        fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)  
    except OSError:  
        fonte = ImageFont.load_default()  
  
    texto = str(numero)  
    bbox = draw.textbbox((0, 0), texto, font=fonte)  
    larg_texto = bbox[2] - bbox[0]  
    alt_texto = bbox[3] - bbox[1]  
    x = (TAMANHO[0] - larg_texto) // 2  
    y = (TAMANHO[1] - alt_texto) // 2  
  
    # Sombra preta para contraste  
    draw.text((x + 1, y + 1), texto, fill=(0, 0, 0), font=fonte)  
    # Texto branco  
    draw.text((x, y), texto, fill=(255, 255, 255), font=fonte)  
  
    caminho = f"teste_tecla_{numero}.jpg"  
    img.save(caminho)  
    return caminho  
  
  
# --- CALLBACK DE EVENTOS -----------------------------------------------------  
  
def callback(device, event):  
    """Imprime eventos de teclas e knobs no terminal."""  
    if event.event_type == EventType.BUTTON:  
        estado = "PRESSIONADA" if event.state == 1 else "SOLTA"  
        print(f"  [TECLA] {event.key.name} → {estado}")  
    elif event.event_type == EventType.KNOB_ROTATE:  
        direcao = "DIREITA" if event.direction.name == "RIGHT" else "ESQUERDA"  
        print(f"  [KNOB] {event.knob.name} → {direcao}")  
    elif event.event_type == EventType.KNOB_PRESS:  
        estado = "PRESSIONADO" if event.state == 1 else "SOLTO"  
        print(f"  [KNOB] {event.knob.name} → {estado}")  
  
  
# --- MAIN --------------------------------------------------------------------  
  
def main():  
    print("=" * 60)  
    print("  TESTE DE IMAGENS — K1 PRO (64x64)")  
    print("=" * 60)  
  
    manner = DeviceManager()  
    dispositivos = manner.enumerate()  
  
    if not dispositivos:  
        print("Nenhum dispositivo encontrado.")  
        return  
  
    # Escutar plug/unplug em thread separada  
    listen_thread = threading.Thread(target=manner.listen)  
    listen_thread.daemon = True  
    listen_thread.start()  
  
    print(f"\n{len(dispositivos)} dispositivo(s) encontrado(s).\n")  
  
    for device in dispositivos:  
        if not isinstance(device, K1Pro):  
            continue  
  
        # Abrir e inicializar  
        device.open()  
        device.init()  
        print(f"K1 PRO conectado")  
        print(f"  Path:     {device.path}")  
        print(f"  Firmware: {device.firmware_version}")  
        print(f"  Serial:   {device.serial_number}")  
  
        # Setup K1Pro (padrão do main.py oficial)  
        device.set_keyboard_backlight_brightness(6)  
        device.set_keyboard_lighting_speed(3)  
        device.set_keyboard_lighting_effects(0)  # estático  
        device.set_keyboard_rgb_backlight(255, 0, 0)  
        device.keyboard_os_mode_switch(0)  # modo Windows  
  
        time.sleep(1)  
  
        # Gerar e enviar imagens para as 6 teclas  
        print(f"\nEnviando imagens 64x64 para {TOTAL_TECLAS} teclas:\n")  
  
        for num in range(1, TOTAL_TECLAS + 1):  
            caminho = gerar_imagem(num)  
            resultado = device.set_key_image(num, caminho)  
            nome = TECLAS[num]["nome"]  
            status = "OK" if resultado == 0 else f"ERRO ({resultado})"  
            print(f"  Tecla {num}: {nome:8s} → [{status}]")  
  
        # Um único refresh após todas as imagens  
        device.refresh()  
  
        # Registrar callback de eventos  
        device.set_key_callback(callback)  
  
        print(f"\n  ┌─────────┬─────────┬─────────┐")  
        print(f"  │ 1 Verm. │ 2 Verde │ 3 Azul  │")  
        print(f"  ├─────────┼─────────┼─────────┤")  
        print(f"  │ 4 Amar. │ 5 Magen.│ 6 Ciano │")  
        print(f"  └─────────┴─────────┴─────────┘")  
        print(f"\n  Pressione teclas ou gire knobs para testar eventos.")  
  
    print("\nCtrl+C para encerrar.\n")  
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
                print(f"  Dispositivo fechado: {device.path}")  
            except Exception as e:  
                print(f"  [ERRO ao fechar] {e}")  
        time.sleep(0.2)  
        print("Teste encerrado.")  
  
  
if __name__ == "__main__":  
    try:  
        main()  
    except Exception as e:  
        print(f"\n[ERRO FATAL] {e}")  
        import traceback  
        traceback.print_exc()