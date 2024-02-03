from celery import shared_task

from wisrapp.views import SyncTransactionsView


@shared_task
def sync_transactions():
    vista = SyncTransactionsView()
    vista.get()
    print("Transacciones sincronizadas")


@shared_task
def sumar(x, y):
    return x + y
