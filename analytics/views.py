from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .models import Account
from .statistic import Updater
from .api import RiotAPI
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.forms.models import model_to_dict


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


@api_view(['GET'])
def api_info(request, region, account):
    api = RiotAPI(region)
    res = api.get_account(account)

    if not res.status_code == 200:
        return render(request, 'summoner-not-found.html', {
            'name': account,
            'region': region
        })

    acc_info = res.json()

    try:
        _account = Account.objects.get(name=acc_info['name'], server=region)
    except ObjectDoesNotExist as e:
        _account = Account.objects.create(
            name=acc_info['name'],
            server=region,
            account_id=acc_info['accountId'],
            summoner_id=acc_info['id'],
            icon_id=acc_info['profileIconId'],
            summoner_level=acc_info['summonerLevel'],
        )

    updater = Updater(_account)

    if not updater.is_updated():
        updater.update_data()

    account = model_to_dict(_account)
    account['matches'] = [model_to_dict(match) for match in _account.match_set.all()]

    return Response({
        'account': account
    })
