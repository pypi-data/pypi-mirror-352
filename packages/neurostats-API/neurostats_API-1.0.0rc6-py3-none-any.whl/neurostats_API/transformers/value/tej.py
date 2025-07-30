from .base import BaseValueTransformer

class TEJValueTransformer(BaseValueTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
    
    def process_transform(self):
        pass