# Generated by Django 3.2.2 on 2021-12-30 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAPIs', '0009_auto_20211230_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='bussiness_domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_name', models.CharField(max_length=255)),
            ],
        ),
    ]
