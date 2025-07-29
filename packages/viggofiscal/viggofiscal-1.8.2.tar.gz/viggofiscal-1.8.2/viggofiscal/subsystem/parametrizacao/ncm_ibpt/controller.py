import csv

import flask
from viggocore.common import exception, utils
from viggocore.common.subsystem import controller
from datetime import datetime
from sqlalchemy import exc as sqlexc


class Controller(controller.Controller):

    def convert_string_to_date(self, date: str):
        return datetime.strptime(date, '%d/%m/%Y')

    def get_ex(self, ex: str):
        if ex == '':
            return None
        else:
            return int(ex)

    def limpar_ncmibpt_e_os_ncmibpt_erros_por_sigla(self, sigla_uf):
        response = self.manager.limpar_por_sigla(**{'sigla': sigla_uf})
        return response

    def make_ncm_ibpt_erro_dict(self, linha, sigla_uf, filename, msg_erro):
        erro_dict = {
            "ncm": linha['ncm'],
            "uf": sigla_uf,
            "chave": linha['chave'],
            "versao": linha['versao'],
            "extipi":  linha['extipi'],
            "tipo": linha['tipo'],
            "filename": filename,
            "msg_erro": msg_erro,
            "erro_em": datetime.now()
        }
        return erro_dict

    def make_ncmibpt_dict(self, ncmibpt_file_line, sigla_uf, user_id):
        ncmibpt_dict = {
            'ncm': ncmibpt_file_line['codigo'],
            'uf': sigla_uf,
            'chave': ncmibpt_file_line['chave'],
            'versao': ncmibpt_file_line['versao'],
            'descricao': ncmibpt_file_line['descricao'],
            'aliq_nacional': float(ncmibpt_file_line['nacionalfederal']),
            'aliq_importacao': float(ncmibpt_file_line['importadosfederal']),
            'aliq_estadual': float(ncmibpt_file_line['estadual']),
            'aliq_municipal': float(ncmibpt_file_line['municipal']),
            'inicio_vigencia': self.convert_string_to_date(
                ncmibpt_file_line['vigenciainicio']),
            'fim_vigencia': self.convert_string_to_date(
                ncmibpt_file_line['vigenciafim']),
            'extipi': self.get_ex(ncmibpt_file_line['ex']),
            'tipo': self.get_ex(ncmibpt_file_line['tipo']),
            'created_by': user_id
        }
        return ncmibpt_dict

    def get_user_id(self):
        user_id = None
        if flask.has_request_context():
            token_id = flask.request.headers.get('token')
            if token_id is not None:
                self.token = self.manager.api.tokens().get(id=token_id)
                user_id = self.token.user_id
        return user_id

    def get_linhas_dict(self, ncmibpt_file_lines, sigla_uf, user_id):
        linhas = []
        for ncmibpt_file_line in ncmibpt_file_lines:
            linhas.append(
                self.make_ncmibpt_dict(ncmibpt_file_line, sigla_uf, user_id))
        return linhas

    def get_erro_in_db(self, erro):
        filter_dict = {
            "ncm": erro['ncm'],
            "uf": erro['uf'],
            "chave": erro['chave'],
            "versao": erro['versao'],
            "extipi": erro['extipi']
        }
        erro = self.manager.api.ncm_ibpt_erros().get_erro_existe(
            **filter_dict)
        return erro

    def cadastrar_ncm_ibpt_erro(self, erro, user_id) -> None:
        exists = self.get_erro_in_db(erro)
        if exists is None:
            erro['created_by'] = user_id
            self.manager.api.ncm_ibpt_erros().create(**erro)
        else:
            self.manager.api.ncm_ibpt_erros().update(
                id=exists.id,
                **{'updated_at': datetime.now(), 'updated_by': user_id})

    def cadastrar_por_arquivo(self):
        file = flask.request.files.get('file', None)
        sigla_uf = flask.request.form.get('sigla_uf', None)
        erros = []
        linhas = []
        tipo = file.mimetype.split('/')[-1].upper()

        if tipo == 'CSV':
            filename = file.filename
            file_content = file.read()
            ncmibpt_file_lines = csv.DictReader(
                file_content.decode('unicode_escape').splitlines(),
                delimiter=';')
            if len(ncmibpt_file_lines.fieldnames) == 1:
                msg = ("O delimitador de coluna usado no código foi o ';', " +
                       "mas apenas uma coluna foi gerada então verifique o " +
                       "delimitador de colunas no arquivo.")
                return flask.Response(response=msg,
                                      mimetype="application/text",
                                      status=400)
            user_id = self.get_user_id()

            linhas = self.get_linhas_dict(
                ncmibpt_file_lines, sigla_uf, user_id)

            line_count = 0
            qtd_sucesso = 0
            self.limpar_ncmibpt_e_os_ncmibpt_erros_por_sigla(sigla_uf=sigla_uf)
            for linha in linhas:
                if line_count != 0:
                    if linha['tipo'] == 0:
                        try:
                            self.manager.driver.transaction_manager.count = 0
                            self.manager.create(**linha)
                            qtd_sucesso += 1
                        except exception.ViggoCoreException as exc:
                            erro_dict = self.make_ncm_ibpt_erro_dict(
                                linha,
                                sigla_uf,
                                filename,
                                exc.message)
                            erros.append(erro_dict)
                            self.cadastrar_ncm_ibpt_erro(erro_dict, user_id)
                        except sqlexc.DataError as exc:
                            erro_dict = self.make_ncm_ibpt_erro_dict(
                                linha,
                                sigla_uf,
                                filename,
                                str(exc))
                            erros.append(erro_dict)
                            self.cadastrar_ncm_ibpt_erro(erro_dict, user_id)
                        except AttributeError as exc:
                            erro_dict = self.make_ncm_ibpt_erro_dict(
                                linha,
                                sigla_uf,
                                filename,
                                str(exc))
                            erros.append(erro_dict)
                            self.cadastrar_ncm_ibpt_erro(erro_dict, user_id)
                        except Exception as exc:
                            erro_dict = self.make_ncm_ibpt_erro_dict(
                                linha,
                                sigla_uf,
                                filename,
                                exc.message)
                            erros.append(erro_dict)
                            self.cadastrar_ncm_ibpt_erro(erro_dict, user_id)
                else:
                    line_count += 1
        else:
            msg = 'A aplicação só permite arquivos .csv'
            return flask.Response(response=msg,
                                  status=400)

        response = {
            'filename': filename,
            'sigla_uf': sigla_uf,
            'qtd_sucesso': qtd_sucesso,
            'qtd_erros': len(erros),
            'erros': erros}

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")
