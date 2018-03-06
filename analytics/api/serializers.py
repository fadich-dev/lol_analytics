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
            'role',
            'lane',
            'win',
            'kills',
            'deaths',
            'assists',
            'largest_multi_kill',
            'largest_killing_spree',
            'killing_sprees',
            'double_kills',
            'triple_kills',
            'quadra_kills',
            'penta_kills',
            'first_blood_kill',
            'first_blood_assist',
            'turret_kills',
            'first_tower_kill',
            'first_tower_assist',
            'inhibitor_kills',
            'first_inhibitor_kill',
            'first_inhibitor_assist',
            'unreal_kills',
            'total_minions_killed',
            'neutral_minions_killed',
            'neutral_minions_killed_enemy_jungle',
            'total_damage_dealt',
            'total_damage_dealt_to_champions',
            'physical_damage_dealt',
            'physical_damage_dealt_to_champions',
            'largest_critical_strike',
            'magic_damage_dealt',
            'magic_damage_dealt_to_champions',
            'true_damage_dealt',
            'true_damage_dealt_to_champions',
            'damage_dealt_to_turrets',
            'damage_dealt_to_objectives',
            'total_damage_taken',
            'physical_damage_taken',
            'magical_damage_taken',
            'true_damage_taken',
            'damage_self_mitigated',
            'total_heal',
            'total_units_healed',
            'vision_score',
            'wards_placed',
            'wards_killed',
            'vision_wards_bought_in_game',
            'sight_wards_bought_in_game',
            'total_time_crowd_control_dealt',
            'longest_time_spent_living',
            'gold_spent',
            'gold_earned',
            'champ_level',
            'time_ccing_others',
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
