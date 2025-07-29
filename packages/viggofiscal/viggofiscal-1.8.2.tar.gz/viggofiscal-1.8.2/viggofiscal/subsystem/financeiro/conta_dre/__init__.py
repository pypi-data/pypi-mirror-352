from viggocore.common import subsystem, controller
from viggofiscal.subsystem.financeiro.conta_dre \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.ContaDre,
                                manager=manager.Manager,
                                controller=controller.CommonController)
