from rest_framework import serializers
from .models import Categoria, Transaccion, TransaccionProgramada


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'nombre', 'grupo', 'tipo')


class TransaccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaccion
        fields = ('id', 'tipo_transaccion', 'categoria', 'categoria_nombre', 'fecha',
                  'descripcion', 'cantidad', 'created_at', 'realizada', 'validada',
                  'is_programada', 'programada')

    categoria_nombre = serializers.SerializerMethodField()

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre


class TransaccionProgramadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionProgramada
        fields = ['id', 'cantidad', 'categoria',
                  'inicio', 'final', 'frecuencia']
