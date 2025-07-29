from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.domain_org \
    import resource, manager, controller, router

subsystem = subsystem.Subsystem(resource=resource.DomainOrg,
                                manager=manager.Manager,
                                controller=controller.Controller,
                                router=router.Router)
