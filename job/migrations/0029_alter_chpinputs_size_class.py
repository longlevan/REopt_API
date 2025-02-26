# Generated by Django 4.0.7 on 2023-03-16 23:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0028_merge_20230314_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chpinputs',
            name='size_class',
            field=models.IntegerField(blank=True, help_text='CHP size class. Must be an integer value between 0 and 6', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)]),
        ),
    ]
