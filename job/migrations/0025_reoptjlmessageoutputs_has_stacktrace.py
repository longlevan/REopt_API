# Generated by Django 4.0.7 on 2023-03-06 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0024_alter_electrictariffinputs_blended_annual_demand_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='reoptjlmessageoutputs',
            name='has_stacktrace',
            field=models.BooleanField(blank=True, default=False, help_text='True if the error message has a stacktrace, false otherwise'),
        ),
    ]
