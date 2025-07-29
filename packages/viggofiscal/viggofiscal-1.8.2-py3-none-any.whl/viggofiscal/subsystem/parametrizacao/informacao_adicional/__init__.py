from viggocore.common import subsystem, controller
from viggofiscal.subsystem.parametrizacao.informacao_adicional \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.InformacaoAdicional,
                                manager=manager.Manager,
                                controller=controller.CommonController)
