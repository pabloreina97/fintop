from celery import shared_task

from wisrapp.views import AuthRefresh, SyncTransactionsView


@shared_task
def sync_transactions():
    AuthRefresh.get()
    SyncTransactionsView().get()
    print("Transacciones sincronizadas")


@shared_task
def sumar(x, y):
    return x + y
