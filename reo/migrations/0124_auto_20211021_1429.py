# Generated by Django 3.1.12 on 2021-10-21 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0123_auto_20211021_0337'),
    ]

    operations = [
        migrations.AddField(
            model_name='fueltariffmodel',
            name='boiler_fuel_percent_RE',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fueltariffmodel',
            name='chp_fuel_percent_RE',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
