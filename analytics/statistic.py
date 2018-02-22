from .models import Account, Champion, Match, League, SummonerLeague
from django.core.exceptions import ObjectDoesNotExist
from .api_external import RiotAPI
from django.utils import timezone

# TODO: rework this (_update_leagues, for example)... :)


class Updater:

    def __init__(self, account):
        """
        Collecting summoner data

        :param account: Account entity
        :type account: Account
        """
        self._account = account
        self._api = RiotAPI(self._account.server)

    def update_data(self):
        self._account.updated_at = timezone.now()
        self._account.save()
        self._update_matches()
        self._update_leagues()

    def is_updated(self):
        if not self._account.updated_at:
            return False

        return timezone.now().timestamp() - self._account.updated_at.timestamp() < 600

    def get_last_update(self):
        return self._account.updated_at.timestamp()

    def get_next_update(self):
        diff = timezone.now().timestamp() - self._account.updated_at.timestamp()
        return (0, 600 - diff)[diff < 600]

    def _update_matches(self):
        res = self._api.get_match_history(self._account.account_id)
        if res.status_code == 200:
            for match in res.json()['matches']:
                if self._account.match_set \
                        .filter(platform_id=match['platformId'], game_id=match['gameId'], queue=match['queue']).count():
                    continue

                champ = Champion.objects.get(champion_id=match['champion'])
                mtch = Match.objects.create(
                    platform_id=match['platformId'],
                    game_id=match['gameId'],
                    queue=match['queue'],
                    season=match['season'],
                    timestamp=int(match['timestamp'] / 1000),
                    role=match['role'],
                    lane=match['lane'],
                    account=self._account
                )
                mtch.champions.add(champ)

    def _update_leagues(self):
        res = self._api.get_leagues(self._account.summoner_id)
        if res.status_code == 200:
            leagues = res.json()
            for lg in leagues:
                try:
                    league = League.objects.get(league_id=lg['leagueId'], tier=lg['tier'], rank=lg['rank'])
                except ObjectDoesNotExist as e:
                    league = League.objects.create(
                        league_id=lg['leagueId'],
                        name=lg['leagueName'],
                        tier=lg['tier'],
                        queue_type=lg['queueType'],
                        rank=lg['rank']
                    )

                try:
                    summoner_league = self._account.summonerleague_set.get(league=league, account=self._account)
                    summoner_league.league_points = lg['leaguePoints']
                    summoner_league.wins = lg['wins']
                    summoner_league.losses = lg['losses']
                    summoner_league.is_veteran = lg['veteran']
                    summoner_league.is_inactive = lg['inactive']
                    summoner_league.is_fresh_blood = lg['freshBlood']
                    summoner_league.is_hot_streak = lg['hotStreak']
                    summoner_league.save()
                    continue
                except ObjectDoesNotExist as e:
                    SummonerLeague.objects.create(
                        league_points=lg['leaguePoints'],
                        wins=lg['wins'],
                        losses=lg['losses'],
                        is_veteran=lg['veteran'],
                        is_inactive=lg['inactive'],
                        is_fresh_blood=lg['freshBlood'],
                        is_hot_streak=lg['hotStreak'],
                        account=self._account,
                        league=league
                    )

            lgs = [lg['leagueId'] for lg in leagues]
            summoner_leagues = self._account.summonerleague_set.all()
            for summoner_league in summoner_leagues:
                if summoner_league.league.league_id not in lgs:
                    summoner_league.delete()
