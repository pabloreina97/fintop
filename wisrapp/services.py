from datetime import datetime
from wisrapp.models import Transaccion


def crear_transacciones_futuras(transaccion_programada):
    fecha_actual = transaccion_programada.inicio
    final = transaccion_programada.final

    if final is None:
        # Si no hay fecha de finalización, creamos transacciones para el año en curso
        final = datetime(datetime.now().year, 12, 31)

    while fecha_actual <= final:
        Transaccion.objects.create(
            fecha=fecha_actual,
            cantidad=transaccion_programada.cantidad,
            categoria=transaccion_programada.categoria,
            realizada=False,
        )
        fecha_actual += transaccion_programada.frecuencia


def eliminar_transacciones_futuras(transaccion_programada):
    Transaccion.objects.filter(
        transaccion_programada=transaccion_programada, realizada=False).delete()
