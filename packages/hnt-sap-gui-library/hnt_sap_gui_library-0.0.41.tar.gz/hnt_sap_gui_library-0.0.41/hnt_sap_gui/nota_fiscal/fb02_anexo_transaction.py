import logging
from datetime import datetime
from hnt_sap_gui.common.sap_status_bar import sbar_extracted_text
from hnt_sap_gui.hnt_sap_exception import HntSapException

logger = logging.getLogger(__name__)

MSG_SAP_CODIGO_DOCUMENTO = "^Documento ([0-9]*) só foi pré-editado$"
DOCUMENTO_NAO_EXISTE_NO_EXERCICIO = '^O documento [0-9]+ HFNT não existe no exercício ([0-9]{4})$'
MSG_SAP_ANEXO_EXITO = "O anexo foi criado com êxito"

class Fb02AnexoTransaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, codigo_fv60, filename, dest_path):
        logger.info(f"Enter execute codigo_fv60:{codigo_fv60}, filename:{filename}, dest_path: {dest_path}")        
        sapGuiLib.run_transaction('/nFB02')
        self.query(sapGuiLib, codigo_fv60)

        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        documento = sbar_extracted_text(MSG_SAP_CODIGO_DOCUMENTO, sbar)
        if documento == codigo_fv60:
            sapGuiLib.session.findById("wnd[0]/titl/shellcont/shell").pressContextButton("%GOS_TOOLBOX")
            sapGuiLib.session.findById("wnd[0]/titl/shellcont/shell").selectContextMenuItem("%GOS_PCATTA_CREA")
            sapGuiLib.session.findById("wnd[1]/usr/ctxtDY_PATH").text = dest_path
            sapGuiLib.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = filename
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
            if sbar != MSG_SAP_ANEXO_EXITO:
                raise HntSapException(sbar)

    def query(self, sapGuiLib, codigo_fv60):
        sapGuiLib.session.findById("wnd[0]/usr/txtRF05L-BELNR").Text = codigo_fv60 # '[SAP: Nº documento | Doc contábil da FV60]
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF05L-BUKRS").Text = "HFNT"#  '[SAP: Empresa | Constante]
        exercicio = str(datetime.now().year)
        sapGuiLib.session.findById("wnd[0]/usr/txtRF05L-GJAHR").Text = exercicio#  '[SAP: Exercício | Ano lçto do doc contábil]
        sapGuiLib.send_vkey(0)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        sbar_exercicio = sbar_extracted_text(DOCUMENTO_NAO_EXISTE_NO_EXERCICIO, sbar)
        if sbar_exercicio is not None:
            raise HntSapException(f"Exercício atual {exercicio} é diferente do documento, sbar:{sbar}")