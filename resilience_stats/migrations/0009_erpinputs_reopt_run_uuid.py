# Generated by Django 4.0.4 on 2022-09-19 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0008_erpmeta_erpinputs_erpoutputs'),
    ]

    operations = [
        migrations.AddField(
            model_name='erpinputs',
            name='reopt_run_uuid',
            field=models.UUIDField(blank=True, help_text='The unique ID of a REopt optimization run from which to load inputs.', null=True),
        ),
    ]
