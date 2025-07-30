from ..base import BaseTransformer

class BaseChipTransformer(BaseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)