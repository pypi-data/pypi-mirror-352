import os
import viggocore
import viggolocal

from flask_cors import CORS

from viggocore.system import System

from viggofiscal.subsystem.parametrizacao \
    import (portaria, uficms, forma_pagamento_sefaz, domain_org, cfop,
            cstcofins, csticms, cstipi, cstpis, origem, unidade_medida,
            ncm_ibpt, terminal,
            regra_fiscal, tipo_operacao, natureza_operacao, serial_fiscal,
            certificado_digital, ncm_ibpt_erro, codigo_seguranca_contribuinte,
            uficms_sugestao, informacao_adicional)
from viggofiscal.resources import SYSADMIN_EXCLUSIVE_POLICIES, \
    SYSADMIN_RESOURCES, USER_RESOURCES
from viggofiscal.subsystem.financeiro \
    import (portador, natureza_financeira, centro_resultado)


system = System('viggofiscal',
                [portaria.subsystem, uficms.subsystem,
                 forma_pagamento_sefaz.subsystem, domain_org.subsystem,
                 cfop.subsystem, cstcofins.subsystem, csticms.subsystem,
                 cstipi.subsystem, cstpis.subsystem, origem.subsystem,
                 unidade_medida.subsystem, ncm_ibpt.subsystem,
                 regra_fiscal.subsystem, tipo_operacao.subsystem,
                 natureza_operacao.subsystem, serial_fiscal.subsystem,
                 certificado_digital.subsystem, ncm_ibpt_erro.subsystem,
                 codigo_seguranca_contribuinte.subsystem,
                 terminal.subsystem, uficms_sugestao.subsystem,
                 portador.subsystem, natureza_financeira.subsystem,
                 centro_resultado.subsystem,
                 informacao_adicional.subsystem],
                USER_RESOURCES,
                SYSADMIN_RESOURCES,
                SYSADMIN_EXCLUSIVE_POLICIES)


class SystemFlask(viggocore.SystemFlask):

    def __init__(self):
        super().__init__(system, viggolocal.system)

    def configure(self):
        origins_urls = os.environ.get('ORIGINS_URLS', '*')
        CORS(self, resources={r'/*': {'origins': origins_urls}})

        self.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        viggofiscal_database_uri = os.getenv('VIGGOFISCAL_DATABASE_URI', None)
        if viggofiscal_database_uri is None:
            raise Exception(
                'VIGGOFISCAL_DATABASE_URI not defined in enviroment.')
        else:
            # URL os enviroment example for MySQL
            # export VIGGOFISCAL_DATABASE_URI=
            # mysql+pymysql://root:mysql@localhost:3306/viggofiscal
            self.config['SQLALCHEMY_DATABASE_URI'] = viggofiscal_database_uri
