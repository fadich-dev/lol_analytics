import requests
from django.conf import settings


class RiotAPI(object):
    __api_key = settings.RIOT_APY_KEY
    _region = ''

    def __init__(self, region):
        self._region = region

    def get_account(self, summoner_name):
        url = self._get_base_url() + '/lol/summoner/v3/summoners/by-name/%s' % summoner_name.strip().lower()
        return requests.get(url=url, params=self._get_params())

    def get_champions(self):
        url = self._get_base_url() + '/lol/static-data/v3/champions/'
        return requests.get(url=url, params=self._get_params())

    def get_match_history(self, account_id):
        url = self._get_base_url() + '/lol/match/v3/matchlists/by-account/%d' % account_id
        return requests.get(url=url, params=self._get_params())

    def _get_base_url(self):
        return 'https://%s.api.riotgames.com' % (self._region.strip().lower(),)

    def _get_params(self):
        return {'api_key': self.__api_key}
