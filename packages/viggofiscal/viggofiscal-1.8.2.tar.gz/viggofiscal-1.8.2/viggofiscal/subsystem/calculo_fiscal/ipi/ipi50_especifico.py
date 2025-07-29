from viggofiscal.subsystem.calculo_fiscal.utils import round_abnt


class Ipi50Especifico():

    def __init__(self, base_calculo: float, aliquota_por_unidade: float):
        # A Base de IPI será a Quantidade (qTrib) do produto na operação
        self.base_calculo = float(base_calculo)
        # Valor por Unidade Tributável
        self.aliquota_por_unidade = float(aliquota_por_unidade)

    def valor_ipi(self) -> float:
        valor_ipi = self.aliquota_por_unidade * self.base_calculo
        return round_abnt(valor_ipi, 2)
