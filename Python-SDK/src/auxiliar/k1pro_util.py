# auxiliar/k1pro_util.py  
"""Métodos utilitários para o K1 Pro — independentes de página."""  
  
import logging  
import os  
import time  
  
from PIL import Image, ImageDraw, ImageFont  
  
from StreamDock.DeviceManager import DeviceManager  
from StreamDock.Devices.K1Pro import K1Pro  
  
logger = logging.getLogger(__name__)  
  
  
class K1ProUtil:  
    """Encapsula operações comuns do K1 Pro."""  
  
    TOTAL_TECLAS = 6  
  
    def __init__(self, device: K1Pro):  
        self.device = device  
  
    # =========================================================================  
    # Conexão e setup  
    # =========================================================================  
  
    @staticmethod  
    def encontrar_k1pro() -> "K1ProUtil | None":  
        """Enumera dispositivos e retorna o primeiro K1 Pro encontrado."""  
        manager = DeviceManager()  
        dispositivos = manager.enumerate()  
        for dev in dispositivos:  
            if isinstance(dev, K1Pro):  
                dev.open()  
                dev.init()  
                logger.info(  
                    "K1 Pro conectado — path=%s, fw=%s, serial=%s",  
                    dev.path,  
                    dev.firmware_version,  
                    dev.serial_number,  
                )  
                return K1ProUtil(dev)  
        logger.error("Nenhum K1 Pro encontrado")  
        return None  
  
    def configurar_teclado(  
        self,  
        brilho: int = 6,  
        efeito: int = 0,  
        r: int = 255,  
        g: int = 0,  
        b: int = 0,  
        os_mode: int = 0,  
    ):  
        """  
        Configura backlight, efeito, cor RGB e modo OS.  
  
        Args:  
            brilho: Brilho do backlight (0-6)  
            efeito: Efeito de iluminação (0-9, 0=estático)  
            r: Componente vermelho (0-255)  
            g: Componente verde (0-255)  
            b: Componente azul (0-255)  
            os_mode: Modo do sistema operacional  
        """  
        logger.info(  
            "Configurando teclado: brilho=%d, efeito=%d, cor=(%d,%d,%d), os_mode=%d",  
            brilho, efeito, r, g, b, os_mode,  
        )  
        self.device.set_keyboard_backlight_brightness(brilho)  
        self.device.set_keyboard_lighting_effects(efeito)  
        self.device.set_keyboard_rgb_backlight(r, g, b)  
        self.device.keyboard_os_mode_switch(os_mode)  
        self.device.refresh()  
  
    # =========================================================================  
    # Imagens  
    # =========================================================================  
  
    def enviar_imagem(self, tecla: int, caminho: str) -> bool:  
        """  
        Envia imagem para uma tecla (1-6).  
  
        Args:  
            tecla: Número da tecla (1-6)  
            caminho: Caminho do arquivo de imagem  
  
        Returns:  
            True se enviou com sucesso, False caso contrário  
        """  
        if not os.path.exists(caminho):  
            logger.error("Imagem não encontrada: %s", caminho)  
            return False  
        resultado = self.device.set_key_image(tecla, caminho)  
        self.device.refresh()  
        ok = resultado == 0  
        if ok:  
            logger.debug("Tecla %d: imagem enviada (%s)", tecla, caminho)  
        else:  
            logger.error(  
                "Tecla %d: falha ao enviar imagem (code=%s)", tecla, resultado  
            )  
        return ok  
  
    def enviar_imagens(self, mapa: dict[int, str], intervalo: float = 0.15):  
        """  
        Envia imagens para múltiplas teclas.  
  
        Args:  
            mapa: {numero_tecla: caminho_imagem}  
            intervalo: Pausa entre envios (segundos)  
        """  
        for tecla, caminho in mapa.items():  
            self.enviar_imagem(tecla, caminho)  
            time.sleep(intervalo)  
  
    def resolver_imagens(  
        self,  
        mapa_rotulos: dict[int, str],  
        diretorio: str,  
    ) -> dict[int, str]:  
        """  
        Resolve caminhos de imagem para cada tecla.  
        - Constrói o caminho a partir do rótulo  
        - Valida se o arquivo existe  
        - Gera automaticamente se não existir  
        - Retorna apenas os caminhos válidos  
  
        Args:  
            mapa_rotulos: {tecla: rotulo} ex: {1: "INSERT", 2: "DELETE"}  
            diretorio: Pasta onde as imagens estão/serão geradas  
  
        Returns:  
            {tecla: caminho} apenas para imagens que existem  
        """  
        if not os.path.isdir(diretorio):  
            logger.warning(  
                "Diretório de imagens não existe: %s — será criado na geração",  
                diretorio,  
            )  
  
        imagens = {}  
        for tecla, rotulo in mapa_rotulos.items():  
            arquivo = f"{rotulo.lower().replace(' ', '_')}.png"  
            caminho = os.path.join(diretorio, arquivo)  
  
            if not os.path.exists(caminho):  
                logger.warning(  
                    "Imagem não encontrada: %s — gerando automaticamente",  
                    caminho,  
                )  
                self.gerar_imagem_texto(rotulo, caminho)  
  
            if os.path.exists(caminho):  
                imagens[tecla] = caminho  
                logger.debug("Tecla %d: imagem OK (%s)", tecla, caminho)  
            else:  
                logger.error(  
                    "Imagem AUSENTE para tecla %d: %s — tecla ficará sem imagem",  
                    tecla, caminho,  
                )  
  
        return imagens  
  
    @staticmethod  
    def gerar_imagem_texto(  
        texto: str,  
        caminho_saida: str,  
        tamanho: tuple[int, int] = (64, 64),  
        cor_fundo: str = "black",  
        cor_texto: str = "white",  
        tamanho_fonte: int = 12,  
    ) -> bool:  
        """  
        Gera uma imagem 64x64 com texto centralizado e salva como JPEG.  
  
        Args:  
            texto: Texto a renderizar  
            caminho_saida: Caminho do arquivo de saída  
            tamanho: Dimensões da imagem (largura, altura)  
            cor_fundo: Cor de fundo  
            cor_texto: Cor do texto  
            tamanho_fonte: Tamanho da fonte em pixels  
  
        Returns:  
            True se gerou com sucesso, False caso contrário  
        """  
        try:  
            diretorio = os.path.dirname(caminho_saida)  
            if diretorio:  
                os.makedirs(diretorio, exist_ok=True)  
  
            img = Image.new("RGB", tamanho, cor_fundo)  
            draw = ImageDraw.Draw(img)  
            try:  
                font = ImageFont.truetype(  
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  
                    tamanho_fonte,  
                )  
            except OSError:  
                font = ImageFont.load_default()  
            bbox = draw.textbbox((0, 0), texto, font=font)  
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]  
            x = (tamanho[0] - tw) // 2  
            y = (tamanho[1] - th) // 2  
            draw.text((x, y), texto, fill=cor_texto, font=font)  
            img.save(caminho_saida, "JPEG", quality=95)  
            logger.info("Imagem gerada: %s (%s)", caminho_saida, texto)  
            return True  
        except Exception as e:  
            logger.error(  
                "Erro ao gerar imagem '%s' em %s: %s", texto, caminho_saida, e  
            )  
            return False  
  
    # =========================================================================  
    # Callback  
    # =========================================================================  
  
    def registrar_callback(self, callback):  
        """Registra callback de eventos no dispositivo."""  
        self.device.set_key_callback(callback)  
        logger.info("Callback de eventos registrado")  
  
    def remover_callback(self):  
        """Remove callback de eventos."""  
        self.device.set_key_callback(None)  
        logger.debug("Callback removido")  
  
    # =========================================================================  
    # Lifecycle  
    # =========================================================================  
  
    def fechar(self):  
        """Fecha o dispositivo de forma segura."""  
        try:  
            self.remover_callback()  
            time.sleep(0.1)  
            self.device.close()  
            logger.info("Dispositivo fechado: %s", self.device.path)  
        except Exception as e:  
            logger.error("Erro ao fechar dispositivo: %s", e)