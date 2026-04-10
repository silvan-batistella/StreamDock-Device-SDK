# pagina/base.py  
"""Enum de páginas e classe base abstrata."""  
  
import logging  
from enum import Enum, auto  
from abc import ABC, abstractmethod
import os  
  
from auxiliar.k1pro_util import K1ProUtil
from StreamDock.InputTypes import EventType, InputEvent  
  
logger = logging.getLogger(__name__)  
  
  
class Pagina(Enum):  
    NAVEGACAO = auto()  
  
  
class PaginaBase(ABC):  
    """Contrato que toda página deve implementar."""  
  
    nome: str  
    pagina: Pagina
    subpasta: str
  
    def __init__(self, util: K1ProUtil, diretorio_imagens: str):  
        self.util = util  
        self.diretorio_imagens = os.path.join(diretorio_imagens, self.subpasta)   
  
    @abstractmethod  
    def get_imagens(self) -> dict[int, str]:  
        """Retorna {numero_tecla: caminho_imagem} para as 6 teclas."""  
        ...  
  
    @abstractmethod  
    def ao_pressionar(self, tecla: int):  
        """Ação ao pressionar uma tecla."""  
        ...  
  
    def ao_soltar(self, tecla: int):  
        """Override opcional."""  
        logger.debug("[%s] Tecla %d solta", self.nome, tecla)  
  
    def exibir(self):  
        """Carrega imagens nas teclas e loga."""  
        logger.info(">>> Exibindo página: %s (%s)", self.nome, self.pagina.name)  
        imagens = self.get_imagens()  
        self.util.enviar_imagens(imagens)  
        logger.info(">>> Página %s pronta", self.nome)  
  
    def tratar_evento(self, device, event: InputEvent):  
        """Callback — despacha para ao_pressionar / ao_soltar."""  
        if event.event_type == EventType.BUTTON:  
            if event.state == 1:  
                logger.info("[%s] Tecla %d PRESSIONADA", self.nome, event.key.value)  
                self.ao_pressionar(event.key.value)  
            else:  
                self.ao_soltar(event.key.value)  
        elif event.event_type == EventType.KNOB_ROTATE:  
            logger.info(  
                "[%s] Knob %s girado %s",  
                self.nome, event.knob_id.value, event.direction.value,  
            )  
        elif event.event_type == EventType.KNOB_PRESS:  
            logger.info(  
                "[%s] Knob %s pressionado (state=%d)",  
                self.nome, event.knob_id.value, event.state,  
            )