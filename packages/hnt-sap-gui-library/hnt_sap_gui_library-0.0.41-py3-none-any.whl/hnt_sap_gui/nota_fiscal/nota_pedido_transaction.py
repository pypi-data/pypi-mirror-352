import logging
from hnt_sap_gui.common.sap_status_bar import sbar_extracted_text
from hnt_sap_gui.common.tx_result import TxResult

logger = logging.getLogger(__name__)
MSG_SAP_CODIGO_NOTA_PEDIDO = "^Ped.C.Custo\\/Ordem criado sob o nº ([0-9]{10,11})$"
class NotaPedidoTransaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, nota_pedido):
        logger.info(f"enter execute nota_pedido:{nota_pedido}")
        sapGuiLib.run_transaction('/nme21n')

        sapGuiLib.send_vkey(0)

        # REORGANIZA ELEMENTOS PARA GARANTIR QUE CABEÇALHO ESTEJA ABERTO
        sapGuiLib.send_vkey(29) # Fechar Cabeçalho
        sapGuiLib.send_vkey(30) # Fechar Síntese de itens
        sapGuiLib.send_vkey(31) # Fechar Detahe de item
        sapGuiLib.send_vkey(26) # Abrir Cabeçalho

        # PREENCHE DADOS INICIAIS (Antes do cabeçalho)
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/cmbMEPO_TOPLINE-BSART").Key = nota_pedido['tipo'] # Define o tipo de pedido como Ped.C.Custo/Ordem
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/ctxtMEPO_TOPLINE-SUPERFIELD").Text = nota_pedido['cod_fornecedor'] # Fornecedor

        # CABEÇALHO | Aba Dados Organizacionais
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9").Select() #Seleciona a aba Dados organizacionais
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-EKORG").Text = nota_pedido['org_compras'] #orgCompras
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-EKGRP").Text = nota_pedido['grp_compradores'] #grpCompradores '(Constante: S01)
        sapGuiLib.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").Text = nota_pedido['empresa'] #empresa '(Constante: HFNT)
        # Application.Wait Now + #12:00:02 AM# '(Avaliar a necessidade de inserir espera)

        # REORGANIZA ELEMENTOS PARA GARANTIR QUE SÍNTESE DE ITENS ESTEJA ABERTO
        sapGuiLib.send_vkey(29) #Fechar cabeçalho
        sapGuiLib.send_vkey(27) #Abrir Síntese de itens
        sapGuiLib.send_vkey(31) #Fechar Detahe de item
        sapGuiLib.send_vkey(26) #Abrir Cabeçalho
        sapGuiLib.send_vkey(29) #Fechar cabeçalho


        # SÍNTESE DE ITENS
        for i, sintese_de_iten in enumerate(nota_pedido['sintese_itens']):
            id_0015 = "wnd[0]/usr/subSUB0:SAPLMEGUI:0015"
            id_0016 = "wnd[0]/usr/subSUB0:SAPLMEGUI:0016"
            id_0019 = "wnd[0]/usr/subSUB0:SAPLMEGUI:0019"
            id_gui = id_0016 if sapGuiLib.session.findById(id_0016, False) != None else id_0019
            if i > 0:
                sapGuiLib.session.findById(f"{id_gui}/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211").verticalScrollbar.position = i-1 
            pos = 0 if i == 0 else 1
            sapGuiLib.session.findById(f"{id_gui}/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-KNTTP[2,{pos}]").Text = sintese_de_iten['categoria_cc'] #categoriaCC '(Constante: K)
            sapGuiLib.session.findById(f"{id_gui}/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-EMATN[4,{pos}]").Text = sintese_de_iten['cod_material']  # material
            sapGuiLib.session.findById(f"{id_gui}/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/txtMEPO1211-MENGE[6,{pos}]").Text = sintese_de_iten['quantidade'] #quantidade
            sapGuiLib.session.findById(f"{id_gui}/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-NAME1[10,{pos}]").Text = sintese_de_iten['item']['centro'] #centro 'Local de negócio
            sapGuiLib.send_vkey(0)

            # DETALHES DE ITEM | Aba Fatura
            id_gui_detalhes_item = id_0015 if sapGuiLib.session.findById(id_0015, False) != None else id_0019
            if sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT7", False) != None:
                sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT7").Select() #Seleciona a aba fatura
            
            id_gui_detalhes_item = id_0015 if sapGuiLib.session.findById(id_0015, False) != None else id_0019
            sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT7/ssubTABSTRIPCONTROL1SUB:SAPLMEGUI:1317/ctxtMEPO1317-MWSKZ").Text = sintese_de_iten['item']['cod_imposto'] #codigoImposto #Inclui o código do imposto
            sapGuiLib.send_vkey(0)

            # DETALHES DE ITEM | Aba C|C
            id_gui_detalhes_item = id_0015 if sapGuiLib.session.findById(id_0015, False) != None else id_0019
            if sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT13", False) != None:
                sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT13").Select() #Seleciona a aba C|C

            id_gui_detalhes_item = id_0015 if sapGuiLib.session.findById(id_0015, False) != None else id_0019
            sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT13/ssubTABSTRIPCONTROL1SUB:SAPLMEVIEWS:1101/subSUB2:SAPLMEACCTVI:0100/subSUB1:SAPLMEACCTVI:1100/subKONTBLOCK:SAPLKACB:1101/ctxtCOBL-KOSTL").Text = sintese_de_iten['item']['centro_custo'] #centroCusto
            sapGuiLib.send_vkey(0)
            sapGuiLib.send_vkey(0)
            sapGuiLib.send_vkey(0)
            id_gui_detalhes_item = id_0015 if sapGuiLib.session.findById(id_0015, False) != None else id_0019
            # DETALHES DE ITEM | Aba Condições
            if sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT8", False) != None:
                sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT8").Select() #Seleciona a aba Condições
            sapGuiLib.session.findById(f"{id_gui_detalhes_item}/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT8/ssubTABSTRIPCONTROL1SUB:SAPLMEGUI:1333/ssubSUB0:SAPLV69A:6201/tblSAPLV69ATCTRL_KONDITIONEN/txtKOMV-KBETR[3,1]").Text = sapGuiLib.format_float(sintese_de_iten['item']['montante']) #valorItem 'Valor bruto
            sapGuiLib.send_vkey(0)

        # PROCESSO PARA ANEXAR O DOCUMENTO NO PEDIDO
        for anexo in nota_pedido['anexo']:
            sapGuiLib.session.findById("wnd[0]/titl/shellcont/shell").pressButton("%GOS_TOOLBOX")
            sapGuiLib.session.findById("wnd[0]/shellcont/shell").pressContextButton("CREATE_ATTA")
            sapGuiLib.session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("PCATTA_CREA")
            sapGuiLib.session.findById("wnd[1]/usr/ctxtDY_PATH").Text = anexo['path'] #Diretório de NFs
            sapGuiLib.session.findById("wnd[1]/usr/ctxtDY_FILENAME").Text = anexo['filename'] #PDF da DANFE
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()

        sapGuiLib.session.findById("wnd[0]/tbar[0]/btn[11]").press() #'Grava o lançamento
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        cod_nota_pedido = sbar_extracted_text(MSG_SAP_CODIGO_NOTA_PEDIDO, sbar)
        tx_result = TxResult(cod_nota_pedido, sbar)
        logger.info(f"Leave execute código da nota_pedido:{str(tx_result)}")

        return tx_result
