from viggocore.common import subsystem, controller
from viggofiscal.subsystem.financeiro.natureza_financeira \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.NaturezaFinanceira,
                                manager=manager.Manager,
                                controller=controller.CommonController)
