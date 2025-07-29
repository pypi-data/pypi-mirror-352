from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.codigo_seguranca_contribuinte \
    import resource, manager, controller

subsystem = subsystem.Subsystem(resource=resource.CodigoSegurancaContribuinte,
                                manager=manager.Manager,
                                controller=controller.Controller)
