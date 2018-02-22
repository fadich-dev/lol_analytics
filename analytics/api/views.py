from analytics.api.serializers import AccountSerializer
from analytics.models import Account, Region
from analytics.api_external import RiotAPI
from analytics.statistic import Updater

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response


class AccountRetrieveView(APIView):
    def get(self, request, server=None, name=None, format=None):
        server = server.upper()
        api = RiotAPI(server)
        res = api.get_account(name)
        update = 'update' in request.GET

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
            update = True

        updater = Updater(account)
        if update:
            # if not updater.is_updated():
            updater.update_data()
            # else:
            #     return Response({
            #         'message':
            #             'The account is already updated. '
            #             'Next update is possible in %d seconds' % updater.get_next_update()
            #     }, status=400)

        lookup = {'region': region, 'name': acc_info['name']}

        vessel = get_object_or_404(Account, **lookup)
        serializer = AccountSerializer(vessel, context={'request': request})

        return Response(serializer.data)
