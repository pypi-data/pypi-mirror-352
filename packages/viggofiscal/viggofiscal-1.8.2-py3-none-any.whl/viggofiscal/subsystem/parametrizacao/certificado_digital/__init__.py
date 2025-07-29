from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.certificado_digital \
    import resource, manager, controller


subsystem = subsystem.Subsystem(resource=resource.CertificadoDigital,
                                manager=manager.Manager,
                                controller=controller.Controller)
