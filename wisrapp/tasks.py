from celery import shared_task

from wisrapp.views import SincronizarTransaccionesView


@shared_task
def sync_transactions():
    vista = SincronizarTransaccionesView()
    vista.sincronizar_transacciones()
    print("Transacciones sincronizadas")


@shared_task
def sumar(x, y):
    return x + y
