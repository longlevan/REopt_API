# Generated by Django 4.0.4 on 2022-11-02 00:08

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import job.models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0010_rename_prod_factor_series_pvinputs_production_factor_series_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutageOutputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='OutageOutputs', serialize=False, to='job.apimeta')),
                ('expected_outage_cost', models.FloatField(blank=True, help_text='The expected outage cost over the random outages modeled.', null=True)),
                ('max_outage_cost_per_outage_duration_series', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The maximum outage cost for every outage duration modeled.', size=None)),
                ('unserved_load_series', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, size=None), blank=True, default=list, size=None), blank=True, default=list, help_text='The amount of unserved load in each outage time step for each outage start time and duration. Outage duration changes along the first dimension, outage start time step along the second, and time step in outage along the third.', size=None)),
                ('unserved_load_per_outage_series', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, size=None), blank=True, default=list, help_text='The total unserved load for each outage start time and duration. Outage duration changes along the first dimension and outage start time changes along the second dimention.', size=None)),
                ('microgrid_upgrade_capital_cost', models.FloatField(blank=True, help_text='Total capital cost of including technologies in the microgrid.', null=True)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.AddField(
            model_name='electricutilityinputs',
            name='outage_durations',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1)]), blank=True, default=list, help_text='One-to-one with outage_probabilities. A list of possible time step durations of the grid outage. This input is used for robust optimization across multiple outages. The maximum (over outage_start_time_steps) of the expected value (over outage_durations with probabilities outage_probabilities) of outage cost is included in the objective function minimized by REopt.', size=None),
        ),
        migrations.AddField(
            model_name='electricutilityinputs',
            name='outage_probabilities',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]), blank=True, default=list, help_text='One-to-one with outage_durations. The probability of each duration of the grid outage. Defaults to equal probability for each duration. This input is used for robust optimization across multiple outages. The maximum (over outage_start_time_steps) of the expected value (over outage_durations with probabilities outage_probabilities) of outage cost is included in the objective function minimized by REopt.', size=None),
        ),
        migrations.AddField(
            model_name='electricutilityinputs',
            name='outage_start_time_steps',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1)]), blank=True, default=list, help_text='A list of time steps that the grid outage may start. This input is used for robust optimization across multiple outages. The maximum (over outage_start_time_steps) of the expected value (over outage_durations with probabilities outage_probabilities) of outage cost is included in the objective function minimized by REopt.', size=None),
        ),
        migrations.AddField(
            model_name='siteinputs',
            name='min_resil_time_steps',
            field=models.IntegerField(blank=True, default=0, help_text='The minimum number consecutive timesteps that load must be fully met once an outage begins. Only applies to multiple outage modeling using inputs outage_start_time_steps and outage_durations.', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='financialinputs',
            name='value_of_lost_load_per_kwh',
            field=models.FloatField(blank=True, default=100, help_text='Value placed on unmet site load during grid outages. Units are US dollars per unmet kilowatt-hour. The value of lost load (VoLL) is used to determine outage costs by multiplying VoLL by unserved load for each outage start time and duration. Only applies when modeling outages using the outage_start_time_steps, outage_durations, and outage_probabilities inputs, and do not apply when modeling a single outage using outage_start_time_step and outage_end_time_step.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000.0)]),
        ),
    ]
