from viggocore.common import subsystem, controller
from viggofiscal.subsystem.financeiro.centro_resultado \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.CentroResultado,
                                manager=manager.Manager,
                                controller=controller.CommonController)
