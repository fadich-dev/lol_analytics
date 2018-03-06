import requests
from django.conf import settings


class RiotAPI(object):
    __api_key = settings.RIOT_API_KEY
    _region = ''

    def __init__(self, region):
        self._region = region

    def get_account(self, summoner_name):
        url = '{base}/lol/summoner/v3/summoners/by-name/{summoner_name}'\
            .format(base=self._get_base_url(), summoner_name=summoner_name.strip().lower())
        return requests.get(url=url, params=self._get_params())

    def get_champions(self):
        url = '{base}/lol/static-data/v3/champions/'.format(base=self._get_base_url())
        return requests.get(url=url, params=self._get_params())

    def get_match_history(self, account_id, begin_index=0, end_index=20):
        url = '{base}/lol/match/v3/matchlists/by-account/{account_id}'.format(
            base=self._get_base_url(),
            account_id=account_id
        )
        params = {'beginIndex': begin_index, 'endIndex': end_index}
        return requests.get(url=url, params={**self._get_params(), **params})

    def get_leagues(self, summoner_id):
        url = '{base}/lol/league/v3/positions/by-summoner/{summoner_id}'\
            .format(base=self._get_base_url(), summoner_id=summoner_id)
        return requests.get(url=url, params=self._get_params())

    def get_match(self, match_id):
        url = '{base}/lol/match/v3/matches/{match_id}'.format(base=self._get_base_url(), match_id=match_id)
        return requests.get(url=url, params=self._get_params())

    def _get_base_url(self):
        return 'https://{region}.api.riotgames.com'.format(region=self._region.strip().lower())

    def _get_params(self):
        return {'api_key': self.__api_key}
