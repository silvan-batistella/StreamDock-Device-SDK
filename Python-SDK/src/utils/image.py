import os  
import random  
from PIL import ImageDraw, ImageFont  
from StreamDock.ImageHelpers.PILHelper import create_key_image  
from StreamDock.Devices.K1Pro import K1Pro  
  
  
def generate_label_image(  
    device: K1Pro,  
    label: str,  
    bg_color: str = "black",  
    font_size: int = 11,  
) -> str:  
    """  
    PT_BR: Gera imagem 64x64 com texto centralizado e salva como JPEG temporário.  
    EN_US: Generates a 64x64 image with centered text and saves as temporary JPEG.  
    """  
    img = create_key_image(device, background=bg_color)  
    draw = ImageDraw.Draw(img)  
  
    try:  
        font = ImageFont.truetype(  
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size  
        )  
    except (IOError, OSError):  
        font = ImageFont.load_default()  
  
    bbox = draw.textbbox((0, 0), label, font=font)  
    text_w = bbox[2] - bbox[0]  
    text_h = bbox[3] - bbox[1]  
    x = (img.width - text_w) // 2  
    y = (img.height - text_h) // 2  
  
    draw.text((x, y), label, fill="white", font=font, align="center")  
  
    temp_path = f"key_label_{random.randint(9999, 999999)}.jpg"  
    img.save(temp_path, "JPEG")  
    return temp_path  
  
  
def render_keys_from_labels(device: K1Pro, labels: dict, **image_kwargs):  
    """  
    PT_BR: Renderiza um dict {key_index: label} no dispositivo.  
           Gera imagem, envia, limpa temp file.  
    EN_US: Renders a dict {key_index: label} on the device.  
           Generates image, sends it, cleans up temp file.  
    """  
    for key_index, label in labels.items():  
        temp_path = generate_label_image(device, label, **image_kwargs)  
        try:  
            device.set_key_image(key_index, temp_path)  
            device.refresh()  
        finally:  
            if os.path.exists(temp_path):  
                os.remove(temp_path)