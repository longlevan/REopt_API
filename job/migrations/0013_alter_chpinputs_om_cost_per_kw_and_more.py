# Generated by Django 4.0.6 on 2022-11-10 22:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0012_alter_chpinputs_size_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chpinputs',
            name='om_cost_per_kw',
            field=models.FloatField(blank=True, default=0.0, help_text='Annual CHP fixed operations and maintenance costs in $/kW', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000.0)]),
        ),
        migrations.AlterField(
            model_name='chpinputs',
            name='prime_mover',
            field=models.TextField(blank=True, choices=[('recip_engine', 'Recip Engine'), ('micro_turbine', 'Micro Turbine'), ('combustion_turbine', 'Combustion Turbine'), ('fuel_cell', 'Fuel Cell')], help_text='CHP prime mover, one of recip_engine, micro_turbine, combustion_turbine, fuel_cell', null=True),
        ),
        migrations.AlterField(
            model_name='chpinputs',
            name='size_class',
            field=models.IntegerField(blank=True, help_text='CHP size class. Must be a strictly positive integer value', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
    ]
