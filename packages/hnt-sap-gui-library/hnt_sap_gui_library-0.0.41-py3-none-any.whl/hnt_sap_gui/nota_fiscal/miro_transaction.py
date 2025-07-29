import logging
from hnt_sap_gui.common.sap_status_bar import sbar_extracted_text
from hnt_sap_gui.common.tx_result import TxResult
from hnt_sap_gui.hnt_sap_exception import HntSapException

logger = logging.getLogger(__name__)

MSG_SAP_EXIST_DOC = '^Verificar se fatura já foi registrada sob documento contábil ([0-9]{10,15}) ([0-9]+)$'
MSG_SAP_CODIGO_DOCUMENTO = '^O documento do faturamento ([0-9]{10,15}) foi registrado  \( Doc.contábil ([0-9]{10,15}) \)$'
MSG_SAP_CODIGO_DOCUMENTO_CONTABIL = "Doc.contábil ([0-9]+)"
MSG_MIRO_SEM_ESTRAGIA_DE_APROVACAO = "^Doc.faturamento ([0-9]+) lançado; bloqueado para pagamento  \( Doc.contábil ([0-9]+) \)$"
MSG_MIRO_VALID_PERIOD = "Períodos contábeis permitidos:"
MSG_MIRO_VENCIMENTO_NO_PASSADO = "^Vencimento líquido a ([0-9]{2}.[0-9]{2}.[0-9]{4}) situa-se no passado$"
MSG_DIGITO_VERIFICADOR_INCORRETO = "Dígito Verificador Incorreto"
# Ex status bar msgs:
# Verificar se fatura já foi registrada sob documento contábil 5100918001 2024
# O documento de compra 4505629945 ainda não está liberado
# Doc.faturamento 5109872720 lançado; bloqueado para pagamento  ( Doc.contábil 5100526500 )
# Ped.C.Custo/Ordem criado sob o nº 4505629947
# Dígito Verificador Incorreto
class MiroTransaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, data, numero_pedido):
        sapGuiLib.run_transaction("/nMIRO")
        sapGuiLib.send_vkey(0)
        if sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS", False) != None:
            sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS").Text = "HFNT"
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
        sapGuiLib.session.findById("wnd[0]/usr/cmbRM08M-VORGANG").Key = "1"
        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_TOTAL/ssubHEADER_SCREEN:SAPLFDCB:0010/ctxtINVFO-BLDAT").Text = data['dados_basicos']['data_da_fatura'] #Data da fatura
        sapGuiLib.send_vkey(0)
        sapGuiLib.send_vkey(0)
        if sapGuiLib.session.findById("wnd[1]/usr/txtMESSTXT1", False) != None:
            msg1 = sapGuiLib.session.findById("wnd[1]/usr/txtMESSTXT1").Text
            msg2 = sapGuiLib.session.findById("wnd[1]/usr/txtMESSTXT2").Text
            sapGuiLib.send_vkey(0)
            if MSG_MIRO_VALID_PERIOD == msg1:
                raise HntSapException(f"{msg1} : {msg2}")

        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_TOTAL/ssubHEADER_SCREEN:SAPLFDCB:0010/txtINVFO-XBLNR").Text = data['dados_basicos']['referencia'] #Referência (Nº NF | Formato: 9 dígitos + "-" + série com 3 dígitos)
        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_TOTAL/ssubHEADER_SCREEN:SAPLFDCB:0010/txtINVFO-WRBTR").Text = sapGuiLib.format_float(data['dados_basicos']['montante'])  #Montante
        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_TOTAL/ssubHEADER_SCREEN:SAPLFDCB:0010/ctxtINVFO-SGTXT").Text = data['dados_basicos']['texto']  #Texto (Mês de referência + Dt leitura anterior + Dt leitura atual)
        sapGuiLib.send_vkey(0)


        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/subITEMS:SAPLMR1M:6010/tabsITEMTAB/tabpITEMS_PO/ssubTABS:SAPLMR1M:6020/subREFERENZBELEG:SAPLMR1M:6211/ctxtRM08M-EBELN").Text = numero_pedido  #Nº Pedido
        sapGuiLib.send_vkey(0)
        sapGuiLib.send_vkey(0)
        if sapGuiLib.session.findById("wnd[1]/usr", False) is not None:
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        msg = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar_extracted_text(MSG_SAP_EXIST_DOC, msg) != None:
                raise HntSapException(msg)
        if sbar_extracted_text(MSG_MIRO_VENCIMENTO_NO_PASSADO, sapGuiLib.session.findById("wnd[0]/sbar").Text) != None:
            sapGuiLib.send_vkey(0)
        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_PAY").Select()  #Exibe Pagamento
        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_PAY/ssubHEADER_SCREEN:SAPLFDCB:0020/ctxtINVFO-ZFBDT").Text = data['pagamento']['data_basica'] #Data de vencimento
        try:
            sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_PAY/ssubHEADER_SCREEN:SAPLFDCB:0020/ctxtINVFO-ZTERM").Text = data['pagamento']['cond_pgto']
        except Exception as ex:
            cond_pgto = sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_PAY/ssubHEADER_SCREEN:SAPLFDCB:0020/ctxtINVFO-ZTERM", False).Text
            logger.warn(f"Read only Cond.pgto,:{cond_pgto}")
        sapGuiLib.send_vkey(0)
        if sbar_extracted_text(MSG_MIRO_VENCIMENTO_NO_PASSADO, sapGuiLib.session.findById("wnd[0]/sbar").Text) != None:
            sapGuiLib.send_vkey(0)

        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_FI").Select()  #Exibe cabeçalho
        if sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_FI/ssubHEADER_SCREEN:SAPLFDCB:0150/ctxtINVFO-J_1BNFTYPE", False) == None:
            msg = sapGuiLib.session.findById("wnd[0]/sbar").Text
            if sbar_extracted_text(MSG_SAP_EXIST_DOC, msg) != None:
                raise HntSapException(msg)

        sapGuiLib.session.findById("wnd[0]/usr/subHEADER_AND_ITEMS:SAPLMR1M:6005/tabsHEADER/tabpHEADER_FI/ssubHEADER_SCREEN:SAPLFDCB:0150/ctxtINVFO-J_1BNFTYPE").Text = data['detalhe']['ctg_nf']  #Ctg.NF
        sapGuiLib.send_vkey(0)
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[21]").press()

        for i, sintese_item in enumerate(data['sintese']):
            if i > 1:
                sapGuiLib.session.findById(f"wnd[0]/usr/tabsTABSTRIP1/tabpTAB1/ssubHEADER_TAB:SAPLJ1BB2:2100/tblSAPLJ1BB2ITEM_CONTROL").verticalScrollbar.position = i-1
            pos = 0 if i == 0 else 1
            sapGuiLib.session.findById(f"wnd[0]/usr/tabsTABSTRIP1/tabpTAB1/ssubHEADER_TAB:SAPLJ1BB2:2100/tblSAPLJ1BB2ITEM_CONTROL/ctxtJ_1BDYLIN-CFOP[9,{pos}]").Text = sintese_item['CFOP']
        
        if data['dados_nfe']['chave_acesso_sefaz']['tp_emissao'] != None and data['dados_nfe']['nfe_sefaz']['numero_log'] != None:
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8").Select()
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subRANDOM_NUMBER:SAPLJ1BB2:2801/ctxtJ_1BNFE_DOCNUM9_DIVIDED-TPEMIS").Text = data['dados_nfe']['chave_acesso_sefaz']['tp_emissao']  #Tipo emissão (1 dígitos da Chave de Acesso, contando a partir do dígito 35)
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subRANDOM_NUMBER:SAPLJ1BB2:2801/txtJ_1BNFE_DOCNUM9_DIVIDED-DOCNUM8").Text = data['dados_nfe']['chave_acesso_sefaz']['numero_aleatorio']  #Nº aleatório (8 dígitos da Chave de Acesso, contando a partir do dígito 36)
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subRANDOM_NUMBER:SAPLJ1BB2:2801/txtJ_1BNFE_ACTIVE-CDV").Text = data['dados_nfe']['chave_acesso_sefaz']['dig_verif']  #Díg.verif.
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subTIMESTAMP:SAPLJ1BB2:2803/txtJ_1BDYDOC-AUTHCOD").Text = data['dados_nfe']['nfe_sefaz']['numero_log']  #Nº do log (Protocolo de autorização - 15 primeiros dígitos)
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subTIMESTAMP:SAPLJ1BB2:2803/ctxtJ_1BDYDOC-AUTHDATE").Text = data['dados_nfe']['nfe_sefaz']['data_procmto']  #Data procmto.
            sapGuiLib.session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB8/ssubHEADER_TAB:SAPLJ1BB2:2800/subTIMESTAMP:SAPLJ1BB2:2803/ctxtJ_1BDYDOC-AUTHTIME").Text = data['dados_nfe']['nfe_sefaz']['hora_procmto']  #Hora procmto.
            sapGuiLib.send_vkey(0)
            msg = sapGuiLib.session.findById("wnd[0]/sbar").Text
            if MSG_DIGITO_VERIFICADOR_INCORRETO == msg:
                raise HntSapException(msg)

        sapGuiLib.session.findById("wnd[0]/tbar[0]/btn[3]").press()  #Voltar
        sapGuiLib.session.findById("wnd[0]/tbar[0]/btn[11]").press()  #Gravar
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        documento = None
        for patter in [MSG_SAP_CODIGO_DOCUMENTO, MSG_MIRO_SEM_ESTRAGIA_DE_APROVACAO]: 
            documento = sbar_extracted_text(patter, sbar)
            if documento != None:
                documento_contabil = sbar_extracted_text(MSG_SAP_CODIGO_DOCUMENTO_CONTABIL, sbar)
                break
        if documento == None:
            raise HntSapException(f"SAP status bar: '{sbar}'")
        tx_result = TxResult(documento, sbar, documento_contabil)
        logger.info(f"Leave execute código do miro:{tx_result}")
        return tx_result