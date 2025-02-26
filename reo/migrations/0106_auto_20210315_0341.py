# Generated by Django 2.2.13 on 2021-03-15 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0105_auto_20210304_0400'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamturbinemodel',
            name='electric_produced_to_thermal_consumed_ratio',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='steamturbinemodel',
            name='thermal_produced_to_thermal_consumed_ratio',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
