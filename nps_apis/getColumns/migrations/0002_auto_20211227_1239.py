# Generated by Django 3.2.2 on 2021-12-27 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('getColumns', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='t_datasource_config',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='t_datasource_config',
            table='t_datasource_config',
        ),
    ]