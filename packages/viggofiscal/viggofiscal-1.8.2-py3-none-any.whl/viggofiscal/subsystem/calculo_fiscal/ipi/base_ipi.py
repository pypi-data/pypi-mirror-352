from viggofiscal.subsystem.calculo_fiscal.utils import round_abnt


class BaseIpi():

    def __init__(self, valor_produto: float, valor_frete: float,
                 valor_seguro: float, despesas_acessorias: float):
        self.valor_produto = float(valor_produto)
        self.valor_frete = float(valor_frete)
        self.valor_seguro = float(valor_seguro)
        self.despesas_acessorias = float(despesas_acessorias)

    def calcular_base_ipi(self) -> float:
        base_ipi = (self.valor_produto + self.valor_frete + self.valor_seguro +
                    self.despesas_acessorias)
        return round_abnt(base_ipi, 2)
