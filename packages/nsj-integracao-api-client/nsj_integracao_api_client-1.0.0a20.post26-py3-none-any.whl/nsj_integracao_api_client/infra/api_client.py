import requests

from typing import Iterator

from nsj_gcf_utils.json_util import convert_to_dumps, json_dumps

from nsj_integracao_api_client.service.integrador_cfg import (
    Environment, TAMANHO_PAGINA, _E_SEND_DATA, AUTH_HEADER
)

from nsj_integracao_api_client.infra.debug_utils import DebugUtils as _du

class ApiClient:


    def __init__(self, env: Environment):
        self._env = env


    def _trace_envio(self, filename, content):
        _du.conditional_trace(
            condition=_E_SEND_DATA,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )


    def _url_base(self) -> str:
        if self._env == Environment.LOCAL:
            return "http://localhost:5000/integracao-pessoas-api/66"
        elif self._env == Environment.DEV:
            return "https://api.nasajon.dev/integracao-pessoas-api/66"
        elif self._env == Environment.QA:
            return "https://api.nasajon.qa/integracao-pessoas-api/66"
        elif self._env == Environment.PROD:
            return "https://api4.nasajon.app/integracao-pessoas-api/66"
        else:
            raise ValueError(f"Ambiente desconhecido: {self._env}")


    def _url_diretorio(self) -> str:
        if self._env == Environment.LOCAL:
            return "https://dir.nasajon.dev"
        elif self._env == Environment.DEV:
            return "https://dir.nasajon.dev"
        elif self._env == Environment.QA:
            return "https://dir.nasajon.qa"
        elif self._env == Environment.PROD:
            return "https://diretorio.nasajon.com.br"
        else:
            raise ValueError(f"Ambiente desconhecido: {self._env}")


    def enviar_dados(self, dict_data: list, entidade: str, api_key: str):
        """
        """
        self._trace_envio(f"trace/send_data_{entidade}_{_du.time()}.json", json_dumps(dict_data))

        _rota = entidade.replace('.', '/').lower()

        upsert = True #False if (acao in ["processos"] and self._env == Environment.PROD) else True

        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: api_key})

        if upsert:
            response = s.put(f'{self._url_base()}/{_rota}?upsert=true', json=convert_to_dumps(dict_data))

            if response.status_code == 413:
                for _item in dict_data:
                    response = s.put(f'{self._url_base()}/{_rota}?upsert=true', json=convert_to_dumps(_item))
                    self._tratar_resposta(response, dict_data)
            else:
                self._tratar_resposta(response, dict_data)

        else:
            for _item in dict_data:
                response = s.post(f'{self._url_base()}/{_rota}', json=convert_to_dumps(_item))
                if response.status_code < 200 or response.status_code > 299:
                    if 'application/json' in response.headers.get('Content-Type', '') and \
                    isinstance(response.json(), list) and 'message' in response.json()[0] and \
                    ('_bt_check_unique' in response.json()[0].get('message', '') or response.status_code == 409):
                        raise Exception(f"""Erro ao enviar dados ao servidor:
                        Endpoint: {response.url}
                        Status: {response.status_code} - {response.reason}
                        Mensagem: {response.text}""", convert_to_dumps(dict_data))


    def apagar_dados(self, dict_data: list, entidade: str, api_key: str, tenant: int) -> Iterator[str]:
        """
        """
        _rota = entidade.replace('.', '/').lower()

        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: api_key})
        response = s.delete(f'{self._url_base()}/{_rota}?tenant={tenant}', json=convert_to_dumps(dict_data))

        # Caso algum item não exista no servidor tenta apagar individualmente,
        # ignorando os ausentes
        if response.status_code == 404:
            for _item in dict_data:

                response = s.delete(f'{self._url_base()}/{_rota}?tenant={tenant}', json=convert_to_dumps([_item]))
                if response.status_code == 404:
                    yield f"Registro {entidade} id: {_item} não encontrado para exclusão no tenant {tenant}, ignorando."
                    continue
                else:
                    if (response.status_code < 200 or response.status_code > 299) and response.status_code != 404:
                        if 'application/json' in response.headers.get('Content-Type', ''):
                            _json_response = response.json()
                            if isinstance(_json_response, dict):
                                _message = _json_response['message']if 'message' in _json_response else ''
                            else:
                                _message = _json_response[0]['message'] if 'message' in _json_response[0] else ''

                        else:
                            _message = response.text
                        raise Exception(f"""Erro ao apagar dados ao servidor:
                        Endpoint: {response.url}
                        Status: {response.status_code} - {response.reason}
                        Mensagem: {_message}""")

        if (response.status_code < 200 or response.status_code > 299) and response.status_code != 404:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                if isinstance(_json_response, dict):
                    _message = _json_response['message']if 'message' in _json_response else ''
                else:
                    _message = _json_response[0]['message'] if 'message' in _json_response[0] else ''

            else:
                _message = response.text
            raise Exception(f"""Erro ao apagar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")


    def consultar_integridade_de(self, entidade: str, filtros: dict, filtros_extras: list, ultimo_id , detalhar_diferencas: bool, api_key: str, tenant: int):
        """
        """
        _rota = entidade.replace('.', '/').lower()

        filtros_str = None
        if filtros:
            filtros_str = ("&".join(
                [ f"{_chave}={filtros[_chave]}" for _chave in filtros.keys() ]
            ))

        filtros_extras_str = None
        if filtros_extras:
            filtros_extras_str = f"custom_filter={json_dumps(filtros_extras)}"
        else:
            filtros_extras_str = "custom_filter=[]"

        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: api_key})
        _url = (
            f'{self._url_base()}/{_rota}/verificacao-integridade?tenant={tenant}&source={detalhar_diferencas}'
            f'{"&" + filtros_str if filtros_str else ""}'
            f'&limit={TAMANHO_PAGINA}'
            f'{"&after="+str(ultimo_id) if ultimo_id else ""}'
            f'{"&" + filtros_extras_str if filtros_extras_str else ""}'
        )

        response = s.get(_url)
        response_content = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        if response.status_code < 200 or response.status_code > 299:
            if isinstance(response_content, dict):
                _message = response_content.get('message', '')
            else:
                _message = response_content
            raise Exception(f"""Erro ao consultar a integridade no servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")
        return response_content


    def gerar_token_tenant(self, chave_ativacao: str) -> str:
        """
        """
        s = requests.Session()
        s.headers.update({
            'Content-Type':'application/x-www-form-urlencoded',
            'Accept':'application/json'
        })
        response = s.post(
            f'{self._url_diretorio()}/v2/api/gerar_token_ativacao_sincronia/',
            data={"codigo_ativacao": chave_ativacao})

        if response.status_code == 200:
            _json = response.json()
            if "apiKey" in _json:
                return _json["apiKey"]
            else:
                raise Exception(f'Retorno desconhecido:{_json}')

        if response.status_code < 200 or response.status_code > 299:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                _message = _json_response['message'] if 'message' in _json_response else ''
            else:
                _message = response.text
            raise Exception(f"""Erro ao enviar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")


    def _tratar_resposta(self, response, dict_data):
        if response.status_code < 200 or response.status_code > 299:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                if isinstance(_json_response, dict):
                    _message = _json_response['message'] if 'message' in _json_response else ''
                else:
                    _message = _json_response[0]['message'] if 'message' in _json_response[0] else ''
            else:
                _message = response.text
            raise Exception(f"""Erro ao enviar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""", convert_to_dumps(dict_data))