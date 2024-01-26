from django.db import models


class Categoria(models.Model):
    OPCIONES_TIPO_TRANSACCION = (
        ('I', 'Ingreso'),
        ('G', 'Gasto')
    )
    nombre = models.CharField(max_length=255)
    grupo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=1, choices=OPCIONES_TIPO_TRANSACCION)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=100)
    merchant_name = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=100)
    transaction_category = models.CharField(max_length=100)
    timestamp = models.DateTimeField(max_length=100)
    # Campos meta
    counter_party_preferred_name = models.CharField(
        max_length=100, null=True, blank=True)
    provider_category = models.CharField(max_length=100)
    provider_reference = models.CharField(max_length=100)
    # Campos añadidos
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    computable = models.BooleanField(default=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'transacción'
        verbose_name_plural = 'transacciones'
        ordering = ['-timestamp']


class Presupuesto(models.Model):
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.categoria} {self.mes}/{self.anio} ({self.cantidad})'

    class Meta:
        verbose_name = 'presupuesto'
        verbose_name_plural = 'presupuestos'


class UserToken(models.Model):
    user_id = models.PositiveSmallIntegerField(default=1)
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class SyncHistory(models.Model):
    sync_datetime = models.DateTimeField(auto_now_add=True)
    new_rows = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'sincronización'
        verbose_name_plural = 'sincronizaciones'
        ordering = ['-sync_datetime']


"""
En el patrón Model-View-Controller (MVC) que Django sigue, generalmente es mejor
poner la lógica que tiene que ver con la manipulación y gestión de los datos en el
modelo. Esto hace que el código sea más reutilizable, ya que puedes llamar a esos
métodos del modelo desde diferentes vistas.

Por otro lado, la lógica que implica recibir una solicitud HTTP, interactuar con
el modelo y devolver una respuesta HTTP, debe ir en la vista.

En este caso, el código para generar transacciones a partir de una transacción
programada está directamente relacionado con los datos y no implica la interacción
con las solicitudes HTTP. Por lo tanto, es más apropiado colocarlo en el método
save del modelo TransaccionProgramada.
"""
