# Generated by Django 4.0.7 on 2023-03-08 23:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0025_merge_20230202_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chpinputs',
            name='federal_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Percentage of capital costs that are credited towards federal taxes', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='chpinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='coldthermalstorageinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='coldthermalstorageinputs',
            name='macrs_option_years',
            field=models.IntegerField(blank=True, choices=[(0, 'Zero'), (5, 'Five'), (7, 'Seven')], default=7, help_text='Duration over which accelerated depreciation will occur. Set to zero to disable'),
        ),
        migrations.AlterField(
            model_name='coldthermalstorageinputs',
            name='total_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Total investment tax credit in percent applied toward capital costs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='electricstorageinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='electricstorageinputs',
            name='total_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Total investment tax credit in percent applied toward capital costs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='hotthermalstorageinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='hotthermalstorageinputs',
            name='macrs_option_years',
            field=models.IntegerField(blank=True, choices=[(0, 'Zero'), (5, 'Five'), (7, 'Seven')], default=7, help_text='Duration over which accelerated depreciation will occur. Set to zero to disable'),
        ),
        migrations.AlterField(
            model_name='hotthermalstorageinputs',
            name='total_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Total investment tax credit in percent applied toward capital costs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='pvinputs',
            name='federal_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Percentage of capital costs that are credited towards federal taxes', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='pvinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='windinputs',
            name='federal_itc_fraction',
            field=models.FloatField(blank=True, default=0.3, help_text='Percentage of capital costs that are credited towards federal taxes', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='windinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
