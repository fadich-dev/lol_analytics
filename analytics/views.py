from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .models import Account
from .statistic import Updater
from .api_external import RiotAPI


# Create your views here.


def info(request):
    acc = ''
    reg = ''
    params = request.GET
    if 'acc' in params:
        acc = params['acc']
    if 'srv' in params:
        reg = params['srv']

    if not (acc or reg):
        return render(request, 'summoner-not-found.html')

    api = RiotAPI(reg)

    res = api.get_account(acc)

    if not res.status_code == 200:
        return render(request, 'summoner-not-found.html', {
            'name': acc,
            'region': reg
        })

    acc_info = res.json()

    try:
        account = Account.objects.get(name=acc_info['name'], server=reg)
    except ObjectDoesNotExist as e:
        account = Account.objects.create(
            name=acc_info['name'],
            server=reg,
            account_id=acc_info['accountId'],
            summoner_id=acc_info['id'],
            icon_id=acc_info['profileIconId'],
            summoner_level=acc_info['summonerLevel'],
        )

    updater = Updater(account)

    if not updater.is_updated():
        updater.update_data()

    return render(request, 'summoner-info.html', {
        'account': account
    })
