from rest_framework import serializers
from analytics.models import Account, Match, Champion, League


class ChampionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Champion
        fields = '__all__'


class MatchesSerializer(serializers.ModelSerializer):
    champions = ChampionsSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


class LeaguesSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    matches = MatchesSerializer(many=True, read_only=True, source='match_set')
    leagues = LeaguesSerializer(many=True, read_only=True, source='get_leagues')

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'server',
            'account_id',
            'summoner_id',
            'icon_id',
            'summoner_level',
            'updated_at',
            'matches',
            'leagues',
        )
