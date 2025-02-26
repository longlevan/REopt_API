# Generated by Django 4.0.7 on 2023-03-09 19:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0026_alter_chpinputs_federal_itc_fraction_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialoutputs',
            old_name='breakeven_cost_of_emissions_reduction_per_tonnes_CO2',
            new_name='breakeven_cost_of_emissions_reduction_per_tonne_CO2',
        ),
        migrations.AddField(
            model_name='financialoutputs',
            name='lifecycle_om_costs_after_tax_bau',
            field=models.FloatField(blank=True, help_text='BAU Component of lifecycle costs (LCC). This value is the present value of all O&M costs, after tax in the BAU case.', null=True),
        ),
        migrations.AddField(
            model_name='financialoutputs',
            name='year_one_om_costs_before_tax_bau',
            field=models.FloatField(blank=True, help_text='Year one operations and maintenance cost before tax in the BAU case.', null=True),
        ),
        migrations.AlterField(
            model_name='electricloadinputs',
            name='year',
            field=models.IntegerField(blank=True, default=2022, help_text="Year of Custom Load Profile. If a custom load profile is uploaded via the loads_kw parameter, it is important that this year correlates with the load profile so that weekdays/weekends are determined correctly for the utility rate tariff. If a DOE Reference Building profile (aka 'simulated' profile) is used, the year is set to 2017 since the DOE profiles start on a Sunday.", null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)]),
        ),
    ]
