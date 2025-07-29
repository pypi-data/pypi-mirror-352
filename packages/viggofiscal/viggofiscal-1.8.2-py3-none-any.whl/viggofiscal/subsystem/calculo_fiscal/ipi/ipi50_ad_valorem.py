from viggofiscal.subsystem.calculo_fiscal.utils import round_abnt
from viggofiscal.subsystem.calculo_fiscal.ipi.base_ipi import BaseIpi


class Ipi50AdValorem():

    def __init__(self, valor_produto: float, valor_frete: float,
                 valor_seguro: float, despesas_acessorias: float,
                 aliquota_ipi: float):
        self.valor_produto = float(valor_produto)
        self.valor_frete = float(valor_frete)
        self.valor_seguro = float(valor_seguro)
        self.aliquota_ipi = float(aliquota_ipi)
        self.base_calculo = BaseIpi(
            valor_produto, valor_frete, valor_seguro, despesas_acessorias)

    def calcular_base_ipi(self):
        return self.base_calculo.calcular_base_ipi()

    def valor_ipi(self):
        valor_ipi = self.calcular_base_ipi() * (self.aliquota_ipi / 100)
        return round_abnt(valor_ipi, 2)
