from datetime import datetime
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .models import Categoria, SyncHistory, Transaction, UserToken


def no_computable(modeladmin, request, queryset):
    queryset.update(computable=False)
    no_computable.short_description = "Marcar seleccionados como no computable"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'grupo')


@admin.register(Transaction)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'categoria',
                    'timestamp', 'computable')
    actions = [no_computable]
    list_filter = ['computable', 'categoria']


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(SyncHistory)
class SyncHistoryAdmin(admin.ModelAdmin):
    list_display = ('new_rows', 'sync_datetime')
