from viggocore.common import subsystem, controller
from viggofiscal.subsystem.parametrizacao.cfop \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.Cfop,
                                manager=manager.Manager,
                                controller=controller.CommonController)
