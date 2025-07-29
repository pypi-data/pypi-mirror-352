import json
from enum import Enum

import sqlalchemy
from typing import Any
from sqlalchemy import ForeignKeyConstraint, orm
from viggocore.common.subsystem import entity
from viggocore.common import exception
from viggocore.database import db


class Crt(Enum):
    SIMPLES_NACIONAL = 1
    SN_EXC_REC_BRUTA = 2
    REGIME_NORMAL = 3
    MEI = 4


class RegPisCofins(Enum):
    CUMULATIVO = 1
    NAO_CUMULATIVO = 2


class DomainOrg(entity.Entity, db.Model):

    attributes = ['crt', 'cpf_cnpj', 'insc_est', 'razao_social',
                  'nome_fantasia', 'insc_mun', 'cnae', 'cpf_cnpj_contador',
                  'reg_pis_cofins', 'aliq_pis', 'aliq_cofins', 'cred_sn',
                  'email', 'fone', 'settings']
    attributes += entity.Entity.attributes

    domain = orm.relationship(
        'Domain', backref=orm.backref('domain_org_domain'))

    crt = db.Column(sqlalchemy.Enum(Crt), nullable=False)
    cpf_cnpj = db.Column(db.String(14), nullable=False, unique=True)
    insc_est = db.Column(db.String(14), nullable=False)
    razao_social = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    insc_mun = db.Column(db.String(15), nullable=True)
    cnae = db.Column(db.String(15), nullable=True)
    cpf_cnpj_contador = db.Column(db.String(14), nullable=True)
    reg_pis_cofins = db.Column(sqlalchemy.Enum(RegPisCofins), nullable=True)
    aliq_pis = db.Column(db.Numeric(7, 2), nullable=False,
                         default=0, server_default="0.0")
    aliq_cofins = db.Column(db.Numeric(7, 2), nullable=False,
                            default=0, server_default="0.0")
    cred_sn = db.Column(db.Numeric(7, 2), nullable=False,
                        default=0, server_default="0.0")
    email = db.Column(db.String(60), nullable=False)
    fone = db.Column(db.String(60), nullable=True)
    _settings = db.Column('settings', db.Text, nullable=False, default='{}',
                          server_default='{}')

    __table_args__ = (ForeignKeyConstraint(['id'], ['domain.id']),)

    def __init__(self, id, crt, cpf_cnpj, insc_est, razao_social,
                 nome_fantasia, email, insc_mun=None, cnae=None,
                 cpf_cnpj_contador=None, reg_pis_cofins=None, aliq_pis=0.0,
                 aliq_cofins=0.0, cred_sn=0.0, fone=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.crt = crt
        self.cpf_cnpj = cpf_cnpj
        self.insc_est = insc_est
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.insc_mun = insc_mun
        self.cnae = cnae
        self.cpf_cnpj_contador = cpf_cnpj_contador
        self.reg_pis_cofins = reg_pis_cofins
        self.aliq_pis = float(aliq_pis)
        self.aliq_cofins = float(aliq_cofins)
        self.cred_sn = float(cred_sn)
        self.email = email
        self.fone = fone

    def _has_setting(self, key: str) -> bool:
        return self.settings.get(key) is not None

    def remove_setting(self, key: str):
        if not self._has_setting(key):
            raise exception.BadRequest(f"Erro! Setting {key} not exists")

        settings = self.settings
        value = settings.pop(key)
        self._save_settings(settings)

        return value

    def update_setting(self, key: str, value: Any):
        settings = self.settings
        settings[key] = value
        self._save_settings(settings)
        return value

    @property
    def settings(self):
        try:
            settings_str = '{}' if self._settings is None else self._settings
            return json.loads(settings_str)
        except Exception:
            return {}

    def _save_settings(self, settings: dict):
        self._settings = json.dumps(settings, default=str)

    def get_api_fiscal_in_settings(self):
        return self.settings.get('api_fiscal', None)

    @classmethod
    def individual(cls):
        return 'domain_org'
