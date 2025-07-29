from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.portaria import resource, manager

subsystem = subsystem.Subsystem(resource=resource.Portaria,
                                manager=manager.Manager)
