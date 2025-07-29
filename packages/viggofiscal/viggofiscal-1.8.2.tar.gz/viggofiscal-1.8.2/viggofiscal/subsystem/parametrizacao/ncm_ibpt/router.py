from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Cadastrar Ncmibpt via arquivo',
                'method': 'POST',
                'url': self.collection_url + '/cadastrar_por_arquivo',
                'callback': 'cadastrar_por_arquivo'
            }
        ]
