from viggocore.common import subsystem
from viggofiscal.subsystem.financeiro.portador \
    import resource, manager, controller, router

subsystem = subsystem.Subsystem(resource=resource.Portador,
                                manager=manager.Manager,
                                controller=controller.Controller,
                                router=router.Router)
