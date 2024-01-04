# Generated by Django 5.0.1 on 2024-01-04 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('grupo', models.CharField(max_length=255)),
                ('tipo', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'categoría',
                'verbose_name_plural': 'categorías',
            },
        ),
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('mes', models.PositiveSmallIntegerField()),
                ('anio', models.PositiveSmallIntegerField()),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wisrapp.categoria')),
            ],
            options={
                'verbose_name': 'presupuesto',
                'verbose_name_plural': 'presupuestos',
            },
        ),
        migrations.CreateModel(
            name='TransaccionProgramada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_transaccion', models.CharField(choices=[('I', 'Ingreso'), ('G', 'Gasto')], max_length=1)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('inicio', models.DateTimeField()),
                ('final', models.DateTimeField(blank=True, null=True)),
                ('frecuencia', models.CharField(choices=[('S', 'Semanal'), ('M', 'Mensual')], max_length=1)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wisrapp.categoria')),
            ],
            options={
                'verbose_name': 'transacción programada',
                'verbose_name_plural': 'transacciones programadas',
            },
        ),
        migrations.CreateModel(
            name='Transaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_transaccion', models.CharField(choices=[('I', 'Ingreso'), ('G', 'Gasto')], max_length=1)),
                ('fecha', models.DateTimeField()),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('realizada', models.BooleanField(default=True)),
                ('validada', models.BooleanField(default=True)),
                ('is_programada', models.BooleanField(default=False)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wisrapp.categoria')),
                ('programada', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wisrapp.transaccionprogramada')),
            ],
            options={
                'verbose_name': 'transacción',
                'verbose_name_plural': 'transacciones',
            },
        ),
    ]
