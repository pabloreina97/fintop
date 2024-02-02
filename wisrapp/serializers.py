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
    categoria = serializers.CategoriaSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'

    def create(self, validated_data):
        print(f'Validated data: {validated_data}')
        # Extraer y eliminar los datos meta anidados
        meta_data = validated_data.pop('meta', {})
        transaction = Transaction.objects.create(**validated_data)

        # Asignar los campos meta del modelo Transaction
        for field, value in meta_data.items():
            if hasattr(transaction, field):
                setattr(transaction, field, value)
        transaction.save()
        return transaction

    def update(self, instance, validated_data):
        meta_data = validated_data.pop('meta', {})

        # Actualizar campos normales
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        # Actualizar campos meta
        for field, value in meta_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        instance.save()
        return instance


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__'


class SyncHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncHistory
        fields = '__all__'
