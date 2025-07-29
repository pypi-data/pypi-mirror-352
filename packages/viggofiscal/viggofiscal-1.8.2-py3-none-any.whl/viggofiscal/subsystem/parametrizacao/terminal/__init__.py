from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.terminal \
    import resource, manager, controller, router

subsystem = subsystem.Subsystem(resource=resource.Terminal,
                                manager=manager.Manager,
                                controller=controller.Controller,
                                router=router.Router)
