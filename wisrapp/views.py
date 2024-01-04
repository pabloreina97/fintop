from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.views import APIView

from .services import crear_transacciones_futuras, eliminar_transacciones_futuras
from .models import Categoria, Transaccion, TransaccionProgramada
from .serializers import CategoriaSerializer, TransaccionProgramadaSerializer, TransaccionSerializer
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.decorators import action


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer

    @action(detail=True, methods=['delete'])
    def delete_this(self, request, pk=None):
        transaccion = self.get_object()
        transaccion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'])
    def delete_future(self, request, pk=None):
        transaccion = self.get_object()
        if transaccion.is_programada:
            # Encuentra todas las transacciones futuras asociadas a esta transaccion programada
            transacciones_futuras = Transaccion.objects.filter(
                programada=transaccion.programada,
                fecha__gte=transaccion.fecha
            )
            # Borra todas las transacciones futuras
            transacciones_futuras.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Esta transacción no tiene transacciones futuras asociadas"}, status=status.HTTP_400_BAD_REQUEST)


class TransaccionProgramadaViewSet(viewsets.ModelViewSet):
    queryset = TransaccionProgramada.objects.all()
    serializer_class = TransaccionProgramadaSerializer


class TotalesView(APIView):
    def get(self, request):
        fecha_inicial = request.GET.get('fecha_inicial')
        fecha_final = request.GET.get('fecha_final')
        categoria_id = request.GET.get('categoria_id')

        # Filtrar transacciones según los parámetros de fecha y categoría
        transacciones = Transaccion.objects.all()
        if fecha_inicial:
            fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
            transacciones = transacciones.filter(fecha__gte=fecha_inicial)
        if fecha_final:
            fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d').date()
            transacciones = transacciones.filter(fecha__lte=fecha_final)
        if categoria_id:
            transacciones = transacciones.filter(categoria_id=categoria_id)

        # Calcular gastos totales e ingresos totales
        gastos_totales = transacciones.filter(tipo_transaccion='G').aggregate(
            total=Sum('cantidad'))['total'] or 0
        ingresos_totales = transacciones.filter(
            tipo_transaccion='I').aggregate(total=Sum('cantidad'))['total'] or 0

        # Devolver los resultados en una respuesta JSON
        data = {
            'gastos_totales': gastos_totales,
            'ingresos_totales': ingresos_totales
        }
        return Response(data)
