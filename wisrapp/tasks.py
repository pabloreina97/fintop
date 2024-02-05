from celery import shared_task
from wisrapp.services import SyncManager, TokenManager

from wisrapp.views import AuthRefresh, SyncTransactionsView


@shared_task
def sync_transactions():
    TokenManager.refresh_token()
    SyncManager.sincronizar_transacciones()
    print("Transacciones sincronizadas")


@shared_task
def sumar(x, y):
    return x + y
