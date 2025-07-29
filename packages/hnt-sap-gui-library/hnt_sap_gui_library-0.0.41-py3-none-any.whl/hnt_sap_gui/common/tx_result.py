from datetime import datetime
from typing import Optional


class TxResult:
    def __init__(self, codigo, sbar=None, codigo_contabil: Optional[str] = None) -> None:
        self.codigo = codigo
        self.sbar = sbar
        self.codigo_contabil = codigo_contabil
        self.created_at = datetime.now().strftime("%Y%m%d%H%M%S")

    def __str__(self):
        return f"TxResult instance with codigo: '{self.codigo}', sbar: '{self.sbar}', codigo_contabil: '{self.codigo_contabil}', created_at:'{self.created_at}'"