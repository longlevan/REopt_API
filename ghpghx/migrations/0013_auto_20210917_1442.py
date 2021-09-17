# Generated by Django 3.1.12 on 2021-09-17 14:42

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import ghpghx.models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ghpghx', '0012_auto_20210908_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='borehole_depth_ft',
            field=models.FloatField(blank=True, default=400.0, help_text='Vertical depth of each borehole [ft]', validators=[django.core.validators.MinValueValidator(10.0), django.core.validators.MaxValueValidator(600.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='borehole_diameter_inch',
            field=models.FloatField(blank=True, default=5.0, help_text='Diameter of the borehole/well drilled in the ground [in]', validators=[django.core.validators.MinValueValidator(0.25), django.core.validators.MaxValueValidator(24.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='borehole_spacing_ft',
            field=models.FloatField(blank=True, default=20.0, help_text='Distance from the centerline of each borehole to the centerline of its adjacent boreholes [ft]', validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='cop_map_eft_heating_cooling',
            field=django.contrib.postgres.fields.ArrayField(base_field=picklefield.fields.PickledObjectField(editable=False), default=ghpghx.models.GHPGHXModel._get_cop_map, help_text='Heat pump coefficient of performance (COP) map: list of dictionaries, each with 3 keys: 1) EFT, 2) HeatingCOP, 3) CoolingCOP', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='dst_ghx_timesteps_per_hour',
            field=models.IntegerField(blank=True, default=12, help_text='Time steps per hour to use for the DST GHX model', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='existing_boiler_efficiency',
            field=models.FloatField(blank=True, default=0.8, help_text='Efficiency of the existing boiler/heater serving the heating load', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_fluid_dynamic_viscosity_lbm_per_ft_hr',
            field=models.FloatField(blank=True, default=2.75, help_text='Dynamic viscosity of the fluid in the GHX (nominally water) [lb/(ft-hr)]', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_fluid_flow_rate_gpm_per_ton',
            field=models.FloatField(blank=True, default=2.5, help_text='Volumetric flow rate of the fluid in the GHX per peak ton heating/cooling [GPM/ton]', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_fluid_mass_density_lb_per_ft3',
            field=models.FloatField(blank=True, default=62.4, help_text='Mass density of the fluid in the GHX (nominally water) [lb/ft^3]', validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(200.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_fluid_specific_heat_btu_per_lb_f',
            field=models.FloatField(blank=True, default=1.0, help_text='Specific heat of the fluid in the GHX (nominally water) [Btu/(lb-degF)]', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_fluid_thermal_conductivity_btu_per_hr_ft_f',
            field=models.FloatField(blank=True, default=0.34, help_text='Thermal conductivity of the fluid in the GHX (nominally water) [Btu/(hr-ft-degF)]', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_header_depth_ft',
            field=models.FloatField(blank=True, default=4.0, help_text='Depth under the ground of the GHX header pipe [ft]', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(50.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pipe_outer_diameter_inch',
            field=models.FloatField(blank=True, default=1.66, help_text='Outer diameter of the GHX pipe [in]', validators=[django.core.validators.MinValueValidator(0.25), django.core.validators.MaxValueValidator(24.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pipe_thermal_conductivity_btu_per_hr_ft_f',
            field=models.FloatField(blank=True, default=0.25, help_text='Thermal conductivity of the GHX pipe [Btu/(hr-ft-degF)]', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pipe_wall_thickness_inch',
            field=models.FloatField(blank=True, default=0.16, help_text='Wall thickness of the GHX pipe [in]', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pump_min_speed_fraction',
            field=models.FloatField(blank=True, default=0.1, help_text='The minimum turndown fraction of the pump. 1.0 is a constant speed pump.', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pump_power_exponent',
            field=models.FloatField(blank=True, default=2.2, help_text='The pump power curve exponent', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_pump_power_watt_per_gpm',
            field=models.FloatField(blank=True, default=15.0, help_text='Pumping power required for a given volumetric flow rate of the fluid in the GHX [Watt/GPM]', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ghx_shank_space_inch',
            field=models.FloatField(blank=True, default=2.5, help_text='Distance between the centerline of the upwards and downwards u-tube legs [in]', validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ground_mass_density_lb_per_ft3',
            field=models.FloatField(blank=True, default=162.3, help_text='Mass density of the ground surrounding the borehole field [lb/ft^3]', validators=[django.core.validators.MinValueValidator(10.0), django.core.validators.MaxValueValidator(500.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ground_specific_heat_btu_per_lb_f',
            field=models.FloatField(blank=True, default=0.211, help_text='Specific heat of the ground surrounding the borehole field', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='ground_thermal_conductivity_btu_per_hr_ft_f',
            field=models.FloatField(blank=True, default=1.18, help_text='Thermal conductivity of the ground surrounding the borehole field [Btu/(hr-ft-degF)]', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(15.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='grout_thermal_conductivity_btu_per_hr_ft_f',
            field=models.FloatField(blank=True, default=1.0, help_text='Thermal conductivity of the grout material in a borehole [Btu/(hr-ft-degF)]', validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='init_sizing_factor_ft_per_peak_ton',
            field=models.FloatField(blank=True, default=246.1, help_text='Initial guess of total feet of GHX boreholes (total feet = N bores * Length bore) based on peak ton heating/cooling [ft/ton]', validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5000.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='max_eft_allowable_f',
            field=models.FloatField(blank=True, default=104.0, help_text='Maximum allowable entering fluid temperature (EFT) of the heat pump (used in cooling dominated loads) [degF]', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(150.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='max_sizing_iterations',
            field=models.IntegerField(blank=True, default=15, help_text='Maximum number of sizing iterations before the GHPGHX model times out', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(15)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='min_eft_allowable_f',
            field=models.FloatField(blank=True, default=23.0, help_text='Minimum allowable entering fluid temperature (EFT) of the heat pump (used in heating dominated loads) [degF]', validators=[django.core.validators.MinValueValidator(-50.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='simulation_years',
            field=models.IntegerField(blank=True, default=25, help_text='The time span for which GHX is sized to meet the entering fluid temperature constraints [year]', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='solver_eft_tolerance_f',
            field=models.FloatField(blank=True, default=2.0, help_text='Tolerance for GHX sizing based on the entering fluid temperature limits [degF]', validators=[django.core.validators.MinValueValidator(0.001), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='ghpghxmodel',
            name='tess_ghx_minimum_timesteps_per_hour',
            field=models.IntegerField(blank=True, default=1, help_text='Minimum time steps per hour to use for the TESS GHX model; the model will decide if more is needed each hour', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
    ]
