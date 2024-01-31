# Generated by Django 5.0.1 on 2024-01-26 16:15

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
                ('tipo', models.CharField(choices=[('I', 'Ingreso'), ('G', 'Gasto')], max_length=1)),
            ],
            options={
                'verbose_name': 'categoría',
                'verbose_name_plural': 'categorías',
            },
        ),
        migrations.CreateModel(
            name='SyncHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_datetime', models.DateTimeField(auto_now_add=True)),
                ('new_rows', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'sincronización',
                'verbose_name_plural': 'sincronizaciones',
                'ordering': ['-sync_datetime'],
            },
        ),
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveSmallIntegerField(default=1)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-updated_at'],
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
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('description', models.CharField(max_length=100)),
                ('merchant_name', models.CharField(blank=True, max_length=100, null=True)),
                ('currency', models.CharField(max_length=100)),
                ('transaction_type', models.CharField(max_length=100)),
                ('transaction_category', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(max_length=100)),
                ('counter_party_preferred_name', models.CharField(blank=True, max_length=100, null=True)),
                ('provider_category', models.CharField(max_length=100)),
                ('provider_reference', models.CharField(max_length=100)),
                ('computable', models.BooleanField(default=True)),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wisrapp.categoria')),
            ],
            options={
                'verbose_name': 'transacción',
                'verbose_name_plural': 'transacciones',
                'ordering': ['-timestamp'],
            },
        ),
    ]
