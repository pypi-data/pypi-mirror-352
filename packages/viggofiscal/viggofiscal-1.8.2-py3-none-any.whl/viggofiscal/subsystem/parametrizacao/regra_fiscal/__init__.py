from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.regra_fiscal import resource, manager
from viggocore.common import controller

subsystem = subsystem.Subsystem(resource=resource.RegraFiscal,
                                manager=manager.Manager,
                                controller=controller.CommonController)
