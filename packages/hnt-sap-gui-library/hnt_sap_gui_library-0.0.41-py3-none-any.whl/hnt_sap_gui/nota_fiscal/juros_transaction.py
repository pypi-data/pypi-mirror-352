import datetime
import logging
from hnt_sap_gui.common.sap_status_bar import sbar_extracted_text
from hnt_sap_gui.common.tx_result import TxResult

logger = logging.getLogger(__name__)

class JurosTransaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, nota_pedido, miro, codigo_contabil):
        logger.info(f"Enter execute juros, pedido:{nota_pedido}")

        referencia     = miro['dados_basicos']['referencia']
        cod_fornecedor = nota_pedido['cod_fornecedor']
        juros          = nota_pedido['juros']
        loc_negocios   = nota_pedido['centro_destinatario']
        centro_custo   = nota_pedido['centro_custo_destinatario']

        #Acessa transação
        sapGuiLib.run_transaction("/nF-51")
        sapGuiLib.session.findById("wnd[0]").sendVKey(0)

        #Dados do cabeçalho
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBKPF-BLDAT").Text = datetime.date.today().strftime("%d%m%Y")        
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBKPF-BLART").Text = "RE"  #Tp.doc.
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBKPF-BUKRS").Text = "HFNT"  #Empresa
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBKPF-WAERS").Text = "BRL"  #Moeda/taxa câm.
        sapGuiLib.session.findById("wnd[0]/usr/txtBKPF-XBLNR").Text  = referencia #Referência  (Número NF)
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[6]").press()  #Selecionar PA (Botão)

        #Selec.partidas em aberto
        sapGuiLib.session.findById("wnd[0]/usr/sub:SAPMF05A:0710/radRF05A-XPOS1[2,0]").Select()  #Nº documento (3ª opção do radio button)
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF05A-AGKON").Text = cod_fornecedor  #Conta  (Fornecedor. O mesmo do pedido)
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[16]").press()  #Processar PA (Botão)

        #Entrar condições de seleção
        sapGuiLib.session.findById("wnd[0]/usr/sub:SAPMF05A:0731/txtRF05A-SEL01[0,0]").Text = codigo_contabil  #Nº documento contábil. Campo 1, coluna "de")
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[16]").press()  #Processar PA (Botão)

        #Processar partidas em aberto
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[7]").press()  #Dar baixa à difer.
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF05A-NEWBS").Text = "40"  #ChvLnçt
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF05A-NEWKO").Text = "431100"  #Conta
        sapGuiLib.session.findById("wnd[0]").sendVKey(0)

        #Inserir Item cta.do Razão
        sapGuiLib.session.findById("wnd[0]/usr/txtBSEG-WRBTR").Text  = sapGuiLib.format_float(juros)  #Montante
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBSEG-BUPLA").Text = loc_negocios  #Loc.negócios  (O mesmo do pedido)
        sapGuiLib.session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1007/ctxtCOBL-KOSTL").Text = centro_custo  #Centro custo  (O mesmo do pedido)
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[16]").press()

        #Part.residual
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpREST").Select()
        sapGuiLib.session.findById("wnd[0]").sendVKey(2)

        #Gravar
        sapGuiLib.session.findById("wnd[0]/tbar[0]/btn[11]").press()
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        cod_juros = sbar_extracted_text("Documento ([0-9]+)", sbar)
        tx_result = TxResult(cod_juros, sbar)
        logger.info(f"Leave execute juros:{str(tx_result)}")

        return tx_result