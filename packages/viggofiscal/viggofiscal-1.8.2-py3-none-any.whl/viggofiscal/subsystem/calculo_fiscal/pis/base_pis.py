

class BasePis():

    def __init__(self, valor_produto: float, valor_frete: float,
                 valor_seguro: float, despesas_acessorias: float,
                 valor_desconto: float, valor_icms: float):
        self.valor_produto = float(valor_produto)
        self.valor_frete = float(valor_frete)
        self.valor_seguro = float(valor_seguro)
        self.despesas_acessorias = float(despesas_acessorias)
        self.valor_desconto = float(valor_desconto)
        self.valor_icms = float(valor_icms)

    def calcular_base_pis(self):
        base_pis = (
            self.valor_produto + self.valor_frete + self.valor_seguro +
            self.despesas_acessorias - self.valor_desconto)
        base_pis -= self.valor_icms
        return base_pis
