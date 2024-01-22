from rest_framework import serializers
from .models import Categoria, SyncHistory, Transaction, UserToken


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'nombre', 'grupo', 'tipo')


class MetaTransactionSerializer(serializers.Serializer):
    counter_party_preferred_name = serializers.CharField(
        required=False)
    provider_category = serializers.CharField()
    provider_reference = serializers.CharField()


class TransactionSerializer(serializers.ModelSerializer):
    meta = MetaTransactionSerializer(
        source='*')

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'amount',
            'description',
            'merchant_name',
            'currency',
            'transaction_type',
            'transaction_category',
            'timestamp',
            'meta',
            'categoria',
            'computable'
        ]


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__'


class SyncHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncHistory
        fields = '__all__'
