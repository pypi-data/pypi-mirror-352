import logging
import locale
from SapGuiLibrary import SapGuiLibrary
from dotenv import load_dotenv

from hnt_sap_gui.RPA_HNT_Constants import COD_LIBERACAO_BLOQUADO
from hnt_sap_gui.nota_fiscal.fatura_transaction import FaturaTransaction
from hnt_sap_gui.nota_fiscal.fb02_anexo_transaction import Fb02AnexoTransaction
from hnt_sap_gui.nota_fiscal.juros_transaction import JurosTransaction
from hnt_sap_gui.nota_fiscal.miro_transaction import MiroTransaction

from .common.session import sessionable
from .nota_fiscal.nota_pedido_transaction import NotaPedidoTransaction
from .nota_fiscal.liberacao_transaction import LiberacaoTransaction

logger = logging.getLogger(__name__)

class SapGui(SapGuiLibrary):
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, ('pt_BR.UTF-8'))
        load_dotenv()
        pass
    def format_float(self, value):
        return locale.format_string("%.2f", value)

    @sessionable
    def hnt_run_transaction(self, data):
        logger.info(f"enter execute run_hnt_transactions data:{data}")
        results = {
            "nota_pedido": None,
            "liberacao": None,
            "miro": None,
            "juros": None,
            "error": None
        }
        try:
            tx_result_nota_pedido = NotaPedidoTransaction().execute(self, nota_pedido=data['nota_pedido'])
            results['nota_pedido'] = tx_result_nota_pedido
            tx_result_liberacao = LiberacaoTransaction().execute(self, tx_result_nota_pedido.codigo)
            results['liberacao'] = tx_result_liberacao
            if COD_LIBERACAO_BLOQUADO == tx_result_liberacao.codigo:
                logger.info(f"leave execute run_hnt_transactions result:{', '.join([str(results[obj]) for obj in results])}")
                return results
            
            tx_result_miro = MiroTransaction().execute(self, data=data["miro"], numero_pedido=tx_result_nota_pedido.codigo)
            results['miro'] = tx_result_miro
            results['juros'] = self._juros(nota_pedido=data['nota_pedido'], miro=data["miro"], codigo_contabil=tx_result_miro.codigo_contabil)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute run_hnt_transactions result:{', '.join([str(results[obj]) for obj in results])}")
        return results

    @sessionable
    def hnt_run_transaction_miro(self, numero_pedido, data):
        logger.info(f"enter execute hnt_run_transaction_miro data:{data['miro']}")
        results = {
            "liberacao": None,
            "miro": None,
            "juros" : None,
            "error": None
        }
        try:
            tx_result_liberacao = LiberacaoTransaction().execute(self, numero_pedido)
            results["liberacao"] = tx_result_liberacao
            if COD_LIBERACAO_BLOQUADO == tx_result_liberacao.codigo:
                logger.info(f"leave execute hnt_run_transaction_miro result:{', '.join([str(results[obj]) for obj in results])}")
                return results

            tx_result_miro = MiroTransaction().execute(self, data['miro'], numero_pedido)
            results['miro'] = tx_result_miro
            results['juros'] = self._juros(nota_pedido=data['nota_pedido'], miro=data["miro"], codigo_contabil=tx_result_miro.codigo_contabil)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute hnt_run_transaction_miro result:{', '.join([str(results[obj]) for obj in results])}")
        return results

    def _juros(self, nota_pedido, miro, codigo_contabil):
        if nota_pedido['juros'] != 0 and codigo_contabil is not None:
            return JurosTransaction().execute(self, nota_pedido, miro, codigo_contabil)

    @sessionable
    def hnt_run_transaction_FV60(self, data):
        results = {
            "fatura": None,
            "error": None
        }
        try:
            results["fatura"] = FaturaTransaction().execute(self, data)
            if 'anexo' in data:
                for anexo in data['anexo']:
                    Fb02AnexoTransaction().execute(
                        sapGuiLib=self, 
                        codigo_fv60=results["fatura"].codigo,
                        filename=anexo['filename'],
                        dest_path=anexo['path'])
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute hnt_run_transaction_FV60 result:{', '.join([str(results[obj]) for obj in results])}")
        return results

    @sessionable
    def hnt_run_transaction_liberacao(self, cod_nota_pedido):
        results = {
            "liberacao": None,
            "error": None
        }
        try:
            results["liberacao"] = LiberacaoTransaction().execute(self, cod_nota_pedido)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute hnt_run_transaction_FV60 result:{', '.join([str(results[obj]) for obj in results])}")
        return results

    @sessionable
    def hnt_run_transaction_F51(self, nota_pedido, miro, codigo_contabil):
        results = {
            "juros": None,
            "error": None
        }
        try:
            results['juros'] = JurosTransaction().execute(self, nota_pedido, miro, codigo_contabil)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute hnt_run_transaction_F-51 result:{', '.join([str(results[obj]) for obj in results])}")
        return results