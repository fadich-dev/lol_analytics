from analytics.api.serializers import SummonerInfoSerializer
from analytics.models import Account, Region
from analytics.api_external import RiotAPI
from analytics.statistic import Updater, Analyzer

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response


class AccountRetrieveView(APIView):
    _filters = [
        'lane',
        'role',
        'champion_id',
    ]

    def get(self, request, server=None, name=None, format=None):
        server = server.upper()
        api = RiotAPI(server)
        res = api.get_account(name)
        update = 'update' in request.GET
        matches_limit = int(request.GET.get('matches-limit', 20))
        matches_offset = int(request.GET.get('matches-offset', 0))
        try:
            limit = int(request.GET.get('limit', 20))
        except ValueError as e:
            limit = 20

        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError as e:
            offset = 0

        filters = self._get_match_filters(request)

        if not res.status_code == 200:
            return Response(status=res.status_code)

        acc_info = res.json()

        region = Region.objects.get_or_create(name=server)[0]
        account = Account.objects.filter(name=acc_info['name'], region=region).first()

        if not account:
            account = Account.objects.create(
                name=acc_info['name'],
                region=region,
                account_id=acc_info['accountId'],
                summoner_id=acc_info['id'],
                icon_id=acc_info['profileIconId'],
                summoner_level=acc_info['summonerLevel'],
            )
            # update = True
        else:
            account.icon_id = acc_info['profileIconId']
            account.summoner_level = acc_info['summonerLevel']
            account.save()

        updater = Updater(account)
        if update:
            if not updater.is_updated():
                updater.update_data(matches_limit=matches_limit, matches_offset=matches_offset)
            else:
                return Response({
                    'message':
                        'Account is already updated. '
                        'Next update is possible in %d seconds' % updater.get_next_update()
                }, status=400)

        lookup = {'region': region, 'name': acc_info['name']}

        vessel = get_object_or_404(Account, **lookup)
        response = SummonerInfoSerializer(vessel, context={'request': request}).data
        matches = response.get('matches')

        # Custom filtering... TODO: guess... :)
        def filter_matches(match):
            for match_player in match.get('players'):
                print(match_player)
                if match_player.get('account').get('name') == acc_info['name']:
                    for prop, val in filters.items():
                        if not match_player.get(prop) == val:
                            return False
                    return True

            return False

        response['matches'] = list(filter(filter_matches, matches))[offset:limit]

        analyzer = Analyzer(account=account, **filters)
        analyzer.set_limit(limit)
        analyzer.set_offset(offset)
        response['analytics'] = analyzer.get_full_analytics()

        return Response(response)

    def _get_match_filters(self, request):
        f = dict()

        for param in self._filters:
            if param in request.GET:
                f[param] = request.GET.get(param)

        return f
