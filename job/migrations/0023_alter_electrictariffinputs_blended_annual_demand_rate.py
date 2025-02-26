# Generated by Django 4.0.7 on 2023-01-24 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0022_remove_financialoutputs_replacement_costs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electrictariffinputs',
            name='blended_annual_demand_rate',
            field=models.FloatField(blank=True, help_text='Average monthly demand charge [$ per kW per month]. Rate will be applied to monthly peak demand.', null=True),
        ),
    ]
