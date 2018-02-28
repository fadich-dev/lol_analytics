from rest_framework import serializers
from analytics.models import Account, Match, Champion, League, Region, MatchPlayer


class ChampionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Champion
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class MatchPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPlayer
        fields = '__all__'


class MatchesSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    players = MatchPlayerSerializer(read_only=True, source='matchplayer_set')

    class Meta:
        model = Match
        fields = '__all__'


class LeaguesSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    matches = MatchesSerializer(many=True, read_only=True, source='get_matches')
    leagues = LeaguesSerializer(many=True, read_only=True, source='get_leagues')

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'region',
            'account_id',
            'summoner_id',
            'icon_id',
            'summoner_level',
            'updated_at',
            'matches',
            'leagues',
        )
