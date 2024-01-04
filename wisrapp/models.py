from django.db import models
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    grupo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'


class Transaccion(models.Model):
    OPCIONES_TIPO_TRANSACCION = (
        ('I', 'Ingreso'),
        ('G', 'Gasto')
    )

    tipo_transaccion = models.CharField(
        max_length=1, choices=OPCIONES_TIPO_TRANSACCION)
    fecha = models.DateTimeField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    realizada = models.BooleanField(default=True)
    validada = models.BooleanField(default=True)
    is_programada = models.BooleanField(default=False)
    programada = models.ForeignKey(
        'TransaccionProgramada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.descripcion} ({self.tipo_transaccion})'

    class Meta:
        verbose_name = 'transacción'
        verbose_name_plural = 'transacciones'


class TransaccionProgramada(models.Model):

    OPCIONES_FRECUENCIA = (
        ('S', 'Semanal'),
        ('M', 'Mensual'),
    )

    OPCIONES_TIPO_TRANSACCION = (
        ('I', 'Ingreso'),
        ('G', 'Gasto')
    )

    tipo_transaccion = models.CharField(
        max_length=1, choices=OPCIONES_TIPO_TRANSACCION)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    inicio = models.DateTimeField()
    final = models.DateTimeField(blank=True, null=True)
    frecuencia = models.CharField(
        max_length=1, choices=OPCIONES_FRECUENCIA)

    def __str__(self):
        return f'{self.cantidad}, {self.frecuencia} ({self.categoria})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        fecha_actual = self.inicio
        if self.final is None:
            # Si no hay fecha de finalización, creamos transacciones para el año en curso
            self.final = timezone.make_aware(datetime.combine(
                datetime(datetime.now().year, 12, 31), datetime.min.time()))

        while fecha_actual <= self.final:
            Transaccion.objects.create(
                tipo_transaccion=self.tipo_transaccion,
                fecha=fecha_actual,
                categoria=self.categoria,
                descripcion=f'{self.descripcion} (generada automáticamente)',
                cantidad=self.cantidad,
                realizada=False,
                validada=True,
                is_programada=True,
                programada=self
            )

            if self.frecuencia == 'S':
                fecha_actual += timedelta(days=7)
            elif self.frecuencia == 'M':
                fecha_actual += relativedelta(months=1)

    # def delete(self, *args, **kwargs):
    #     # obtener todas las transacciones relacionadas no realizadas
    #     transacciones_no_realizadas = Transaccion.objects.filter(
    #         programada_id=self.id, realizada=False)

    #     # borrar todas las transacciones no realizadas
    #     transacciones_no_realizadas.delete()

    #     # llamar al delete original para borrar la transacción programada
    #     super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'transacción programada'
        verbose_name_plural = 'transacciones programadas'


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
