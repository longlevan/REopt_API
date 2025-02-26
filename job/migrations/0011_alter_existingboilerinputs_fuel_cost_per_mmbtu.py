# Generated by Django 4.0.4 on 2022-10-30 18:37

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0010_rename_prod_factor_series_pvinputs_production_factor_series_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='existingboilerinputs',
            name='fuel_cost_per_mmbtu',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)]), blank=True, default=list, help_text='The ExistingBoiler default operating cost is zero. Please provide this field to include non-zero BAU heating costs.The `fuel_cost_per_mmbtu` can be a scalar, a list of 12 monthly values, or a time series of values for every time step.If a vector of length 8760, 17520, or 35040 is provided, it is adjusted to match timesteps per hour in the optimization.', size=None),
        ),
    ]
