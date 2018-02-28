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


class AccountSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'


class MatchPlayerSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    champion = ChampionsSerializer(read_only=True)

    class Meta:
        model = MatchPlayer
        fields = (
            'role',
            'lane',
            'champion',
            'account',
        )


class MatchesSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    players = MatchPlayerSerializer(many=True, read_only=True, source='matchplayer_set')

    class Meta:
        model = Match
        ordering = ('-timestamp',)
        fields = (
            'platform_id',
            'game_id',
            'queue',
            'season',
            'timestamp',
            'region',
            'players',
        )


class LeaguesSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class SummonerInfoSerializer(serializers.ModelSerializer):
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
            'leagues',
            'matches',
        )
