# Generated by Django 3.2.2 on 2021-12-16 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAPIs', '0004_auto_20211216_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]