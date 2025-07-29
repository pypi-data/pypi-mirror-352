import logging
from hnt_sap_gui.common.sap_status_bar import sbar_extracted_text
from hnt_sap_gui.common.tx_result import TxResult
from hnt_sap_gui.hnt_sap_exception import HntSapException

logger = logging.getLogger(__name__)
MSG_SAP_CODIGO_DOCUMENTO = "^Documento ([0-9]*) HFNT foi pré-editado$"
MSG_SAP_JA_FOI_CRIADO = "^Verificar se o documento já foi criado com o nº HFNT ([0-9]*) ([0-9]{4})$"
MSG_SAP_COND_PGTO_MODIFICADAS = "Condições de pagamento foram modificadas, verificar"
DATA_DOCUMENTO_DATA_LANÇAMENTO_EM_EXERCICIOS_DIFERENTES ='Data de documento e data de lançamento em exercícios diferentes'
MSG_SAP_BLOQUEADO_LANÇAMENTOS = "^Centro de custo HGHF\/([A-Z0-9]+) em \d{2}\.\d{2}\.\d{4} bloqueado para lançamentos primários$"
MSG_SAP_VENCIMENTO_NO_PASSADO = "^Vencimento líquido a ([0-9]{2}.[0-9]{2}.[0-9]{4}) situa-se no passado$"
class FaturaTransaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, fatura):
        logger.info(f"Enter execute fatura:{fatura}")
        sapGuiLib.run_transaction('/nFV60')
        if sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS", False) != None:
            sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS").Text = "HFNT"
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # ABA DADOS BÁSICOS
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-ACCNT").Text = fatura['dados_basicos']['cod_fornecedor']
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-BLDAT").Text = fatura['dados_basicos']['data_fatura']
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/txtINVFO-XBLNR").Text = fatura['dados_basicos']['referencia']
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/txtINVFO-WRBTR").Text = sapGuiLib.format_float(fatura['dados_basicos']['montante'])
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-BUPLA").Text = fatura['dados_basicos']['bus_pl_sec_cd']
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-SGTXT").Text = fatura['dados_basicos']['texto']
        sapGuiLib.send_vkey(0)
        status = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if DATA_DOCUMENTO_DATA_LANÇAMENTO_EM_EXERCICIOS_DIFERENTES == status:
            sapGuiLib.send_vkey(0)
        if sapGuiLib.session.findById("wnd[1]/usr", False) is not None:
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        if sbar_extracted_text(MSG_SAP_VENCIMENTO_NO_PASSADO, sapGuiLib.session.findById("wnd[0]/sbar").Text) != None:
            sapGuiLib.send_vkey(0)
        if sapGuiLib.session.findById("wnd[1]/usr/txtMESSTXT2", False) is not None:
            if sapGuiLib.session.findById("wnd[1]/usr/txtMESSTXT2").Text == 'Adiantamento ativo circulante':
                sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        status = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar_extracted_text(MSG_SAP_JA_FOI_CRIADO, status) != None:
            raise HntSapException(status)
        for i, iten in enumerate(fatura['dados_basicos']['itens']):
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-HKONT[1,{i}]").Text = iten['cta_razao']
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/txtACGL_ITEM-WRBTR[4,{i}]").Text = sapGuiLib.format_float(iten['montante'])
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-BUPLA[6,{i}]").Text = iten['loc_negocios']
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/txtACGL_ITEM-ZUONR[10,{i}]").Text = iten['atribuicao']
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-SGTXT[12,{i}]").Text = iten['texto']
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-KOSTL[18,{i}]").Text = iten['centro_custo']

        sapGuiLib.send_vkey(0)
        status = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar_extracted_text(MSG_SAP_BLOQUEADO_LANÇAMENTOS, status) != None:
            raise HntSapException(status)

        # ABA DADOS PAGAMENTO
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM").Select()
        sapGuiLib.send_vkey(0)
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/cmbINVFO-ZLSPR").Key = ""
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/ctxtINVFO-ZFBDT").Text = fatura['pagamento']['data_basica']
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/ctxtINVFO-ZTERM").Text = fatura['pagamento']['cond_pgto']
        sapGuiLib.send_vkey(0)
        sapGuiLib.send_vkey(0)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if MSG_SAP_COND_PGTO_MODIFICADAS == sbar:
            sapGuiLib.send_vkey(0)

        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[42]").press()
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        documento = sbar_extracted_text(MSG_SAP_CODIGO_DOCUMENTO, sbar)
        if documento == None:
            raise HntSapException(sbar)
        return TxResult(documento, sbar)

