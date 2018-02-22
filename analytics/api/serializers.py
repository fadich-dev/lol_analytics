from rest_framework import serializers
from analytics.models import Account


class AccountSerializer(serializers.ModelSerializer):
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
        )
