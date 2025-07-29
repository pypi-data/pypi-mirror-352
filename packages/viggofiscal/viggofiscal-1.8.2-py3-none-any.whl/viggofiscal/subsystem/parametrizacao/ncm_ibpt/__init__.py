from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.ncm_ibpt \
    import resource, controller, router, manager

subsystem = subsystem.Subsystem(resource=resource.NcmIbpt,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router)
