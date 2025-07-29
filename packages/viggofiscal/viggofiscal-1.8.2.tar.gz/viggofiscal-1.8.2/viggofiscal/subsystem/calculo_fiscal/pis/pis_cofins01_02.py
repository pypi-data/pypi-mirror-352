from viggofiscal.subsystem.calculo_fiscal.utils import round_abnt
from viggofiscal.subsystem.calculo_fiscal.pis.base_pis \
    import BasePis


class PisCofins01_02():

    def __init__(self, valor_produto: float, valor_frete: float,
                 valor_seguro: float, despesas_acessorias: float,
                 valor_desconto: float, aliquota_pis: float,
                 valor_icms: float = 0):
        self.valor_produto = float(valor_produto)
        self.valor_frete = float(valor_frete)
        self.valor_seguro = float(valor_seguro)
        self.despesas_acessorias = float(despesas_acessorias)
        self.valor_desconto = float(valor_desconto)
        self.aliquota_pis = float(aliquota_pis)
        self.valor_icms = float(valor_icms)

    def base_pis_normal(self):
        base_pis = BasePis(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, 0.0)
        return round_abnt(base_pis.calcular_base_pis(), 2)

    # def valor_icms(self):
    #     valor_icms = (self.base_pis_normal() * (self.aliquota_icms / 100))
    #     return round_abnt(valor_icms, 2)

    def base_pis_menos_icms(self):
        # valor_icms = self.valor_icms()
        base_pis = BasePis(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_icms)
        return round_abnt(base_pis.calcular_base_pis(), 2)

    def valor_pis(self):
        valor_pis = (self.base_pis_menos_icms() * (self.aliquota_pis / 100))
        return round_abnt(valor_pis, 2)
