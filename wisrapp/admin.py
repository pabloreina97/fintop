from datetime import datetime
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .models import Categoria, SyncHistory, Transaction, UserToken


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'grupo')


@admin.register(Transaction)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'categoria', 'timestamp')


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(SyncHistory)
class SyncHistoryAdmin(admin.ModelAdmin):
    list_display = ('new_rows', 'sync_datetime')
