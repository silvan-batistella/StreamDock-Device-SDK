# app.py  
"""Ponto de entrada — testa renderização dos ícones no K1 Pro."""  
  
import logging  
import os  
import time  
  
from auxiliar.k1pro_util import K1ProUtil  
from pagina.navegacao import PaginaNavegacao
  
logging.basicConfig(  
    level=logging.DEBUG,  
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  
    datefmt="%H:%M:%S",  
)  
logger = logging.getLogger("app")  
  
DIR_IMAGENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagens")  
  
  
def main():  
    logger.info("Iniciando aplicação")  
  
    util = K1ProUtil.encontrar_k1pro()
    if not util:  
        return  
  
    util.configurar_teclado(brilho=6, efeito=0, r=255, g=0, b=0)  
    time.sleep(1)  
  
    pagina = PaginaNavegacao(util, DIR_IMAGENS)  
    pagina.exibir()  
    util.registrar_callback(pagina.tratar_evento)  
  
    logger.info("Aguardando eventos... Ctrl+C para encerrar.")  
    try:  
        while True:  
            time.sleep(0.1)  
    except KeyboardInterrupt:  
        logger.info("Encerrando...")  
    finally:  
        util.fechar()  
  
  
if __name__ == "__main__":  
    main()