from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .models import Account, Match, Champion
from .api import RiotAPI


# Create your views here.


def info(request):
    acc = ''
    reg = ''
    params = request.GET
    if 'acc' in params:
        acc = params['acc']
    if 'srv' in params:
        reg = params['srv']

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

    matches = Match.objects.filter(account=account)
    if len(matches) == 0:
        res = api.get_match_history(account.account_id)
        if res.status_code == 200:
            for match in res.json()['matches']:
                champ = Champion.objects.get(champion_id=match['champion'])
                mtch = Match.objects.create(
                    platform_id=match['platformId'],
                    game_id=match['gameId'],
                    queue=match['queue'],
                    season=match['season'],
                    timestamp=int(match['timestamp'] / 1000),
                    role=match['role'],
                    lane=match['lane'],
                    account=account
                )
                mtch.champion.add(champ)

    return render(request, 'summoner-info.html', {
        'account': account,
        'region': reg,
        'matches': Match.objects.filter(account=account)
    })
