# Generated by Django 3.1.8 on 2021-06-21 14:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ghpghx', '0010_auto_20210525_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='borehole_diameter_inch',
            field=models.FloatField(blank=True, default=5.0, help_text='Diameter of the borehole/well drilled in the ground [in]', null=True, validators=[django.core.validators.MinValueValidator(0.25), django.core.validators.MaxValueValidator(24.0)]),
        ),
    ]
