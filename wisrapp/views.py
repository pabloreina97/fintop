from hmac import new
from wisrapp.services import SyncManager, TokenManager

from wisrapp.utils import flatten_json
from .models import Categoria, SyncHistory, Transaction, UserToken
from .serializers import CategoriaSerializer, SyncHistorySerializer, TransactionSerializer

from django.db import transaction
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.shortcuts import redirect

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import environ
import requests

env = environ.Env()


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=['post'])
    def dividir(self, request, pk=None):
        transaccion_original = self.get_object()
        divisiones = request.data.get('divisiones')

        cantidad_total_divisiones = Decimal(
            sum(division['amount'] for division in divisiones))

        cantidad_total_divisiones = cantidad_total_divisiones.quantize(
            Decimal('.01'), rounding=ROUND_HALF_UP)

        cantidad_restante = transaccion_original.amount - cantidad_total_divisiones

        print(f'Cantidad original: {transaccion_original.amount}')
        print(f'Cantidad total división: {cantidad_total_divisiones}')
        print(f'Cantidad restante: {cantidad_restante}')

        if abs(cantidad_total_divisiones) > abs(transaccion_original.amount):
            return Response({'error': 'La suma de las divisiones excede la cantidad original.'}, status=status.HTTP_400_BAD_REQUEST)

        nuevas_transacciones = []
        transaccion_data = model_to_dict(transaccion_original, exclude=[
                                         'id', 'amount', 'categoria'])

        with transaction.atomic():
            # Crear nuevas transacciones para las divisiones
            for division in divisiones:
                amount = division['amount']
                categoria_id = division['categoria']

                # Preparar los datos para la nueva transacción
                transaccion_data = {
                    **model_to_dict(transaccion_original, exclude=['id', 'categoria', 'amount']),
                    'amount': amount,
                    'categoria': categoria_id
                }
                print(transaccion_data)

                serializer = TransactionSerializer(data=transaccion_data)
                if serializer.is_valid(raise_exception=True):
                    nueva_transaccion = serializer.save()
                    nuevas_transacciones.append(nueva_transaccion)

            # Crear una transacción para la cantidad restante
            if abs(cantidad_restante) > 0:
                transaccion_data.update({
                    'amount': cantidad_restante,
                    'categoria': transaccion_original.categoria.id if transaccion_original.categoria else None
                })
                serializer_restante = TransactionSerializer(
                    data=transaccion_data)
                if serializer_restante.is_valid(raise_exception=True):
                    nuevas_transacciones.append(serializer_restante.save())

            transaccion_original.delete()

        serializer = TransactionSerializer(nuevas_transacciones, many=True)
        return Response(serializer.data)


class AuthTruelayer(APIView):
    # URL de autenticación de TrueLayer
    def get(self, request, *args, **kwargs):
        auth_url = env('AUTH_URL')
        print(auth_url)

        # Redirige automáticamente al enlace de autenticación de TrueLayer
        return redirect(auth_url)


class RedirectTruelayer(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')

        print(code)
        if code:
            # Aquí debes intercambiar el código por un access_token
            # usando una petición HTTP a la API de TrueLayer
            response = requests.post(
                'https://auth.truelayer.com/connect/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': env('TRUELAYER_CLIENT_ID'),
                    'client_secret': env('TRUELAYER_CLIENT_SECRET'),
                    'redirect_uri': env('REDIRECT_URI'),
                    'code': code,
                }
            )
            if response.status_code == 200:

                access_token = response.json().get('access_token')
                refresh_token = response.json().get('refresh_token')

                UserToken.objects.update_or_create(user_id=1,
                                                   defaults={'access_token': access_token,
                                                             'refresh_token': refresh_token}
                                                   )
                return Response({'access_token': access_token,
                                 'details': 'Token generado correctamente'})
            else:
                return Response({'error': 'Error al intercambiar el código por el token',
                                 'status': response.status_code})

            # Aquí puedes redirigir al usuario o mostrar una página con la información
            # Por ejemplo, podrías redirigir al usuario a una página de inicio

        else:
            return Response("No se proporcionó un código", status=400)


class AuthRefresh(APIView):
    def get(self, request, *args, **kwargs):
        result, error = TokenManager.refresh_token()
        if error:
            return Response(error, status=error['status'])
        return Response(result)


class GetAccountsView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener el token de acceso más reciente de la base de datos
        user_token = UserToken.objects.first()
        access_token = user_token.access_token

        # Hacer la petición a la API de TrueLayer
        api_url = f'https://api.truelayer.com/data/v1/accounts/'
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                json_data = response.json().get('results')
                return Response(json_data)
            else:
                return Response({'error': 'Error al obtener las cuentas'}, status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GetTransactionsView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener el token de acceso más reciente de la base de datos
        user_token = UserToken.objects.first()
        access_token = user_token.access_token
        accounts = ['4ec4578ab0b06c3c431f0580e39969d5',
                    'c6b6408a31b67b058d8f4c7af0398f40']

        # Fechas de sincronizacion
        last_sync = SyncHistory.objects.first(
        ).sync_datetime if SyncHistory.objects.first() else None
        from_date = ((last_sync + timedelta(days=-3))
                     if last_sync else datetime(year=2024, month=1, day=1)).strftime(r'%Y-%m-%d')
        to_date = datetime.today().strftime(r'%Y-%m-%d')
        print(f'from {from_date} to {to_date}')

        # Inicializar lista para almacenar todas las transacciones
        all_transactions = []

        # Hacer la petición a la API de TrueLayer
        for account_id in accounts:
            api_url = f'https://api.truelayer.com/data/v1/accounts/{account_id}/transactions?from={from_date}&to={to_date}'
            headers = {'Authorization': f'Bearer {access_token}'}

            try:
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    transacciones_json = response.json().get('results')
                    all_transactions.extend(transacciones_json)
                else:
                    return Response({'error': 'Error al obtener transacciones de alguna de las cuentas'}, status=response.status_code)
            except Exception as e:
                return Response({'error': str(e)}, status=500)

        return Response(all_transactions)


class SyncTransactionsView(APIView):

    def get(self, request, *args, **kwargs):
        new_rows, error = SyncManager.sincronizar_transacciones()
        if error:
            return Response({'error': error}, status=500)
        return Response({'status': f'Transacciones sincronizadas correctamente. Se han añadido {new_rows} nuevas transacciones'})
