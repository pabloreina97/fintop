from datetime import datetime, timedelta
from decimal import Decimal
import requests
from wisrapp.models import Categoria, SyncHistory, Transaction, UserToken
from wisrapp.serializers import SyncHistorySerializer, TransactionSerializer
from wisrapp.utils import flatten_json
import environ

env = environ.Env()


class TokenManager:
    @staticmethod
    def refresh_token():
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

            return {'old_access_token': old_access_token, 'new_access_token': access_token, 'details': 'Token refrescado correctamente'}, None
        else:
            return None, {'error': 'Error al refrescar el token', 'status': response.status_code}


class SyncManager:
    @staticmethod
    def sincronizar_transacciones():
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
        print(f'Fechas de sincronización: {from_date} a {to_date}')

        # Hacer la petición a la API de TrueLayer para sincronizar las transacciones
        for account_id in accounts:
            api_url = f'https://api.truelayer.com/data/v1/accounts/{account_id}/transactions?from={from_date}&to={to_date}'
            headers = {'Authorization': f'Bearer {access_token}'}

            try:
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    transacciones_json = response.json().get('results')
                    # Aplanar JSON y eliminar campos no deseados
                    for json_obj in transacciones_json:
                        json_obj.pop('transaction_type', None)
                        json_obj.pop('transaction_classification', None)
                    transacciones_json = [flatten_json(
                        json_obj) for json_obj in transacciones_json]
                    # Filtrar transacciones no sincronizadas.
                    past_transactions = set(Transaction.objects.filter(transaction_id__in=[
                        d['transaction_id'] for d in transacciones_json]).values_list('transaction_id', flat=True))
                    new_transactions = [
                        d for d in transacciones_json if d['transaction_id'] not in past_transactions]
                    # Cargar todas las categorías una vez al inicio del método para evitar múltiples consultas a la BD.
                    all_categorias = Categoria.objects.all()

                    print(
                        f'Transacciones nuevas ({len(new_transactions)}): {new_transactions}')
                    for transaccion in new_transactions:
                        serializer = TransactionSerializer(data=transaccion)
                        if serializer.is_valid():
                            print('Serializador valido')
                            # Guardar la instancia de la transacción para crearla en la base de datos
                            transaccion = serializer.save()
                            # Aplicar la función para asignar categoría
                            categoria = SyncManager.asignar_categoria(
                                transaccion, all_categorias)
                            # Asignar la categoría a la transacción y guardar los cambios
                            transaccion.categoria = categoria
                            transaccion.save()
                            # Contador de nuevas filas añadidas
                            new_rows += 1
                        else:
                            print('Serializador no valido', serializer.errors)

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

    @staticmethod
    def asignar_categoria(transaccion, categorias):
        categorias_dict = {
            categoria.nombre: categoria for categoria in categorias}

        descripcion = transaccion.description.upper()
        importe = transaccion.amount
        print(type(importe))
        destinatario = transaccion.merchant_name.upper() if transaccion.merchant_name else (
            transaccion.counter_party_preferred_name.upper() if transaccion.counter_party_preferred_name else None)

        if 'PAGO' in descripcion:  # TODO: Esto no esta funcionando bien
            # Descripción > Importe
            if importe == Decimal(-116.42):
                return categorias_dict.get('Comunidad')
            elif importe == Decimal(-20.00) or importe == Decimal(-50.00):
                return categorias_dict.get('Donativos')
            elif importe == Decimal(-56.28):
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
            'Combustible': ['REPSOL', 'PETROIL'],
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
