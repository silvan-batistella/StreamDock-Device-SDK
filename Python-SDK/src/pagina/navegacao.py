# pagina/navegacao.py  
"""Página de navegação: INSERT, DELETE, HOME, END, PG UP, PG DOWN."""  
  
import logging  
  
from pagina.base import PaginaBase, Pagina  
from auxiliar.k1pro_util import K1ProUtil  
  
logger = logging.getLogger(__name__)  
  
  
# pagina/navegacao.py  
  
class PaginaNavegacao(PaginaBase):  
  
    nome = "Navegação"  
    pagina = Pagina.NAVEGACAO  
    subpasta = "navegacao"       # <-- novo  
  
    MAPA_TECLAS = {  
        1: "INSERT",  
        2: "HOME",  
        3: "PG UP",  
        4: "DELETE",  
        5: "END",  
        6: "PG DOWN",  
    }  
  
    def __init__(self, util: K1ProUtil, diretorio_imagens: str):  
        super().__init__(util, diretorio_imagens)  
  
    def get_imagens(self) -> dict[int, str]:  
        return self.util.resolver_imagens(self.MAPA_TECLAS, self.diretorio_imagens)  
  
    def ao_pressionar(self, tecla: int):  
        if tecla not in self.MAPA_TECLAS:  
            logger.warning("Tecla %d não mapeada nesta página", tecla)  
            return  
        rotulo = self.MAPA_TECLAS[tecla]  
        logger.info("Tecla pressionada: %s (tecla %d)", rotulo, tecla)