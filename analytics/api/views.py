from analytics.api.serializers import AccountSerializer
from analytics.models import Account
from analytics.api_external import RiotAPI

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response
from django.http.response import Http404


class AccountRetrieveView(APIView):
    def get(self, request, server=None, name=None, format=None):
        server = server.upper()
        api = RiotAPI(server)
        res = api.get_account(name)

        if not res.status_code == 200:
            return Response(status=404)

        acc_info = res.json()

        lookup = {'server': server, 'name': acc_info['name']}
        try:
            return Response(self._get_account(request, lookup))
        except Http404 as e:
            Account.objects.create(
                name=acc_info['name'],
                server=server,
                account_id=acc_info['accountId'],
                summoner_id=acc_info['id'],
                icon_id=acc_info['profileIconId'],
                summoner_level=acc_info['summonerLevel'],
            )

        return Response(self._get_account(request, lookup))

    def _get_account(self, request, lookup):
        vessel = get_object_or_404(Account, **lookup)
        serializer = AccountSerializer(vessel, context={'request': request})
        return serializer.data
