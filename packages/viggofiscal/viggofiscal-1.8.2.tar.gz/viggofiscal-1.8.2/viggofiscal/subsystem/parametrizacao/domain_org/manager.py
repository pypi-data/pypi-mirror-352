from viggocore.common.subsystem import operation, manager
from viggocore.common import exception


class Create(operation.Create):

    def post(self):

        natureza_list = ['Compra', 'Venda', 'Transferência', 'Devolução',
                         'Importação', 'Consignação', 'Outra',
                         'Remessa para fins de demonstração',
                         'Remessa para fins de industrialização']

        domain_org_id = self.entity.id
        if domain_org_id is not None:
            for item in natureza_list:
                natureza = {
                    'domain_org_id': domain_org_id,
                    'titulo': item,
                    'descricao': item
                }
                self.manager.api.natureza_operacaos().create(**natureza)


class UpdateSettings(operation.Update):

    def pre(self, session, id: str, **kwargs) -> bool:
        self.settings = kwargs
        if self.settings is None or not self.settings:
            raise exception.BadRequest("Erro! There is not a setting")
        return super().pre(session=session, id=id)

    def do(self, session, **kwargs):
        result = {}
        for key, value in self.settings.items():
            new_value = self.entity.update_setting(key, value)
            result[key] = new_value
        super().do(session)

        return result


class RemoveSettings(operation.Update):

    def pre(self, session, id: str, **kwargs) -> bool:
        self.keys = kwargs.get('keys', [])
        if not self.keys:
            raise exception.BadRequest('Erro! keys are empty')
        super().pre(session, id=id)

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        result = {}
        for key in self.keys:
            value = self.entity.remove_setting(key)
            result[key] = value
        super().do(session=session)

        return result


class GetDomainOrgSettingsByKeys(operation.Get):

    def pre(self, session, id, **kwargs):
        self.keys = kwargs.get('keys', [])
        if not self.keys:
            raise exception.BadRequest('Erro! keys are empty')
        return super().pre(session, id=id)

    def do(self, session, **kwargs):
        entity = super().do(session=session)
        settings = {}
        for key in self.keys:
            value = entity.settings.get(key, None)
            if value is not None:
                settings[key] = value
        return settings


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update_settings = UpdateSettings(self)
        self.remove_settings = RemoveSettings(self)
        self.get_domain_org_settings_by_keys = GetDomainOrgSettingsByKeys(self)
