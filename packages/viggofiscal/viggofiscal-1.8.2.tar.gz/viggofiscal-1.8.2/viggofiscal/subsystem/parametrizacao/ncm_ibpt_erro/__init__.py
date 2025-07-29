from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.ncm_ibpt_erro \
    import resource, controller, manager, router

subsystem = subsystem.Subsystem(resource=resource.NcmIbptErro,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router)
