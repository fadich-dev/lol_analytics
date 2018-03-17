from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .models import Account, Region
from .statistic import Updater, Analyzer
from .api_external import RiotAPI


# Create your views here.


def info(request):
    name = request.GET.get('account')
    server = request.GET.get('region')
    update = 'update' in request.GET

    if not (name and server):
        return render(request, 'summoner-not-found.html')

    api = RiotAPI(server)
    res = api.get_account(name)

    if not res.status_code == 200:
        return render(request, 'summoner-not-found.html')

    acc_info = res.json()

    region = Region.objects.get_or_create(name=server.upper())[0]

    try:
        account = Account.objects.get(name=acc_info['name'], region=region)
        account.icon_id = acc_info['profileIconId']
        account.summoner_level = acc_info['summonerLevel']
        account.save()
    except ObjectDoesNotExist as e:
        account = Account.objects.create(
            name=acc_info['name'],
            region=region,
            account_id=acc_info['accountId'],
            summoner_id=acc_info['id'],
            icon_id=acc_info['profileIconId'],
            summoner_level=acc_info['summonerLevel'],
        )

    updater = Updater(account)
    analyzer = Analyzer(account)

    if not updater.is_updated() and update:
        updater.update_data()

    return render(request, 'summoner-info.html', {
        'account': account,
        'base_analytics': analyzer.get_base_info()
    })
