from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.uficms_sugestao \
    import resource, manager, controller

subsystem = subsystem.Subsystem(resource=resource.UficmsSugestao,
                                manager=manager.Manager,
                                controller=controller.Controller)
