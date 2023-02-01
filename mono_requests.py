import requests


class MonoResponse:
    def __init__(self, status_code: int, balance: float = None, error: str = None):
        self._balance = balance
        self._error = error
        self._status_code = status_code

    @property
    def balance(self):
        return self._balance

    @property
    def error(self):
        return self._error

    @property
    def status_code(self):
        return self._status_code


class MonoRequest:
    def __init__(
            self,
            token: str,
            card_type: str = 'black',
            url: str = 'https://api.monobank.ua/personal/client-info'
    ) -> None:
        self._headers = {'X-Token': token}
        self._card_type = card_type
        self._url = url

    def get_balance_from_mono(self) -> MonoResponse:
        response = requests.get(self._url, headers=self._headers)
        if response.status_code == 200:
            balance = self._get_balance_from_data(response.json())
            return MonoResponse(
                balance=balance,
                status_code=response.status_code
            )
        error = self._get_error_message(response.json())
        return MonoResponse(
            error=error,
            status_code=response.status_code
        )

    @staticmethod
    def _get_error_message(data: dict):
        return data.get('errorDescription')

    def is_status_cod_200(self):
        return True if requests.get(self._url, headers=self._headers).status_code == 200 else False

    def _get_balance_from_data(self, data: dict) -> (float, None):
        accounts = data.get('accounts')
        card = list(filter(lambda x: x.get('type') == self._card_type, accounts))
        if len(card):
            return card[0].get('balance') / 100
        return None
