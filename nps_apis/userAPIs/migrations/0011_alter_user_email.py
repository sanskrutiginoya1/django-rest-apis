# Generated by Django 3.2.2 on 2021-12-31 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAPIs', '0010_bussiness_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
