from rest_framework import viewsets
from rest_framework.views import APIView

from .models import Categoria, SyncHistory, Transaction, UserToken
from .serializers import CategoriaSerializer, SyncHistorySerializer, TransactionSerializer
from django.db.models import Sum
from rest_framework.response import Response

from django.shortcuts import redirect
import requests
import environ
from datetime import datetime, timedelta

env = environ.Env()


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


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
        user_token = UserToken.objects.first()
        old_access_token = user_token.access_token
        refresh_token = user_token.refresh_token

        response = requests.post(
            'https://auth.truelayer.com/connect/token',
            data={
                'grant_type': 'refresh_token',
                'client_id': env('TRUELAYER_CLIENT_ID'),
                'client_secret': env('TRUELAYER_CLIENT_SECRET'),
                'refresh_token': refresh_token
            }
        )
        if response.status_code == 200:

            access_token = response.json().get('access_token')

            user_token.access_token = access_token
            user_token.save()

            return Response({'old_access_token': old_access_token,
                             'new_access_token': access_token,
                             'details': 'Token refrescado correctamente'})
        else:
            return Response({'error': 'Error al refrescar el token',
                             'status': response.status_code})


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


class GetTransaccionesView(APIView):
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


class SincronizarTransaccionesView(APIView):

    def get(self, request, *args, **kwargs):
        new_rows, error = self.sincronizar_transacciones()
        if error:
            return Response({'error': error}, status=500)
        return Response({'status': f'Transacciones sincronizadas correctamente. Se han añadido {new_rows} nuevas transacciones'})

    def sincronizar_transacciones(self):
        new_rows = 0

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

        # Hacer la petición a la API de TrueLayer para sincronizar las transacciones
        for account_id in accounts:
            api_url = f'https://api.truelayer.com/data/v1/accounts/{account_id}/transactions?from={from_date}&to={to_date}'
            headers = {'Authorization': f'Bearer {access_token}'}

            try:
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    transacciones_json = response.json().get('results')
                    for transaccion in transacciones_json:
                        added = self.procesar_transaccion(transaccion)
                        if added:
                            new_rows += 1
                else:
                    return new_rows, f"Error: {response.status_code}. Ha ocurrido un error al importar las transacciones de TrueLayer. Revisa el código de error."
            except Exception as e:
                return new_rows, str(e)

        # Guardar historial de sincronización
        sync_serializer = SyncHistorySerializer(
            data={'new_rows': new_rows})
        if sync_serializer.is_valid():
            sync_serializer.save()
            return new_rows, None
        else:
            return new_rows, "Error en la validación del serializer para el historial de sincronización."

    def procesar_transaccion(self, transaccion):
        serializer = TransactionSerializer(data=transaccion)
        if serializer.is_valid():
            # Verificar si la transacción ya existe
            transaction_id = serializer.validated_data.get('transaction_id')
            # TODO: Esto se puede hacer más eficiente:
            if not Transaction.objects.filter(transaction_id=transaction_id).exists():
                transaccion = serializer.save()
                categoria = self.asignar_categoria(transaccion)
                transaccion.categoria = categoria
                transaccion.save()
                return True
            return False
        else:
            # Manejar datos inválidos
            print(
                f'Error en función "procesar_transaccion": {serializer.errors}')
            return False

    def asignar_categoria(self, transaccion):
        # Cargar todas las categorías una vez al inicio del método para evitar múltiples consultas a la BD.
        all_categorias = Categoria.objects.all()
        categorias_dict = {
            categoria.nombre: categoria for categoria in all_categorias}

        descripcion = transaccion.description.upper()
        importe = transaccion.amount
        print(type(importe))
        destinatario = transaccion.merchant_name.upper() if transaccion.merchant_name else (
            transaccion.counter_party_preferred_name.upper() if transaccion.counter_party_preferred_name else None)

        if 'PAGO' in descripcion:
            # Descripción > Importe
            if importe == -116.42:
                return categorias_dict.get('Comunidad')
            elif importe == -20 | -50:
                return categorias_dict.get('Donativos')
            elif importe == -56.28:
                return categorias_dict.get('Seguro coche')

        # Destinatario
        if destinatario:
            if 'CARITAS' in destinatario:
                return categorias_dict.get('Donativos')
            elif 'NORTEHISPANA' in destinatario:
                return categorias_dict.get('Seguros')

        # Descripción
        categorias = {
            'Salud': ['FARMA', 'CROSSFIT'],
            'Limpieza': ['NOMINAS', '30831225R'],
            'Hogar': ['ZARA HOME', 'LEROY'],
            'Ropa': ['ZARA', 'ALVARO MORENO', 'SILBON', 'OYSHO', 'MANGO', 'VINTED'],
            'Supermercado': ['MERCADONA', 'DEZA', 'ALCASH'],
            'Combustible': ['REPSOL'],
            'Regalos': ['PUENTECILLO'],
            'Electricidad': ['NATURGY'],
            'Gas': ['NATURGY'],
            'Hipoteca': ['32208842335'],
            'Préstamo coche': ['32127059741'],
            'Internet': ['PTV'],
            'Agua': ['EMACSA'],
            'Pilar': ['ANDALUZ PED'],
            'Servicios digitales': ['APPLE', 'GPT', 'ACONTRA'],
            'Seguros': ['SEVIAM', 'MYBOX'],
            'Personal': ['ALIEXPRESS', 'PINEDA', 'PAPIRO', 'COPISTERIA'],
            'Mantenimiento coche': ['MOVILIDAD']
        }

        for categoria, palabras_clave in categorias.items():
            if any(palabra in descripcion for palabra in palabras_clave):
                return categorias_dict.get(categoria)

        if importe > 0:
            if importe > 800:
                return categorias_dict.get('Salario')
            else:
                return categorias_dict.get('Otros ingresos')

        return None
