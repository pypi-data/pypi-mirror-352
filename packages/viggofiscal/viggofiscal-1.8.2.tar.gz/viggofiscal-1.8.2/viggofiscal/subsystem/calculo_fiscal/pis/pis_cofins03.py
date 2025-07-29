from viggofiscal.subsystem.calculo_fiscal.utils import round_abnt


class PisCofins03():

    def __init__(self, base_calculo: float,
                 aliq_por_unidade_pis: float):
        # A Base de PIS será a Quantidade (qTrib) do produto na operação
        self.base_calculo = float(base_calculo)
        # Valor por Unidade Tributável
        self.aliq_por_unidade_pis = float(aliq_por_unidade_pis)

    def valor_pis(self):
        valor_pis = (self.aliq_por_unidade_pis * self.base_calculo)
        return round_abnt(valor_pis, 2)
