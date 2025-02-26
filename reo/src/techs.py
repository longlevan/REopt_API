# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
from reo.src.data_manager import big_number
from reo.src.pvwatts import PVWatts
from reo.src.wind import WindSAMSDK
from reo.src.incentives import Incentives, IncentivesNoProdBased
from reo.utilities import TONHOUR_TO_KWHT, generate_year_profile_hourly, MMBTU_TO_KWH
import os
import json
import copy
import CoolProp.CoolProp as CP


class Tech(object):
    """
    base class for REopt energy generation technology
    """

    def __init__(self, min_kw=0, max_kw=big_number, installed_cost_us_dollars_per_kw=big_number,
                 om_cost_us_dollars_per_kw=0.0, *args, **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.om_cost_us_dollars_per_kw = om_cost_us_dollars_per_kw
        self.nmil_regime = None
        self.reopt_class = ""
        self.derate = 1.0
        self.is_chp = False
        self.is_hot = False
        self.is_cool = False
        self.derate = 1
        self.acres_per_kw = None  # for land constraints
        self.kw_per_square_foot = None  # for roof constraints
        self.can_net_meter = kwargs.get("can_net_meter", False)
        self.can_wholesale = kwargs.get("can_wholesale", False)
        self.can_export_beyond_site_load = kwargs.get("can_export_beyond_site_load", False)
        self.can_curtail = kwargs.get("can_curtail", False)
        self.kwargs = kwargs

    @property
    def prod_factor(self):
        """
        Production Factor.  Combination of resource, efficiency, and availability.
        :return: prod_factor
        """
        return None


class Util(Tech):

    def __init__(self, dfm, outage_start_time_step=None, outage_end_time_step=None):
        super(Util, self).__init__(max_kw=12000000)

        self.outage_start_time_step = outage_start_time_step
        self.outage_end_time_step = outage_end_time_step
        self.derate = 0.0
        self.n_timesteps = dfm.n_timesteps

        dfm.add_util(self)

    @property
    def prod_factor(self):

        grid_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        if self.outage_start_time_step is not None and self.outage_end_time_step is not None:  # "turn off" grid resource
            # minus 1 in next line accounts for Python's zero-indexing
            grid_prod_factor[self.outage_start_time_step - 1:self.outage_end_time_step] = \
                [0] * (self.outage_end_time_step - self.outage_start_time_step + 1)

        return grid_prod_factor


class PV(Tech):
    array_type_to_tilt_angle = {
        0: 0,  # ground-mount fixed array type's tilt should be equal to the latitude
        1: 10,
        2: 0,
        3: 0,
        4: 0
    }

    def __init__(self, dfm, degradation_pct, time_steps_per_hour=1, acres_per_kw=6e-3, kw_per_square_foot=0.01,
                 existing_kw=0.0, tilt=0.537, azimuth=180, pv_number=1, location='both', prod_factor_series_kw=None,
                 **kwargs):
        super(PV, self).__init__(**kwargs)

        self.degradation_pct = degradation_pct
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'PV' + str(pv_number)
        self.acres_per_kw = acres_per_kw
        self.kw_per_square_foot = kw_per_square_foot
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.tilt = tilt
        self.azimuth = azimuth
        self.pvwatts_prod_factor = None
        self.existing_kw = existing_kw
        self.prod_factor_series_kw = prod_factor_series_kw
        self.tech_name = 'pv' + str(pv_number)
        self.location = location
        self.station = None
        self.pvwatts = None
        self.sr_required_pct = kwargs.get("sr_required_pct")

        # If site is in southern hemisphere and user has not changed from default azimuth of 180, update to 0 for all array types
        if kwargs.get('latitude') < 0:
            if self.azimuth == 180: # Assume user does not want array facing away from equator
                self.azimuth = 0
        # if user hasn't entered the tilt (default value is 0.537), tilt value gets assigned based on array_type
        if self.tilt == 0.537:
            if kwargs.get('array_type') == 0:  # 0 are Ground Mount Fixed (Open Rack) arrays, we assume an optimal tilt
                """
                start assuming the site is in the northern hemisphere, set the tilt to the latitude and leave the
                default azimuth of 180 (unless otherwise specified)
                """
                self.tilt = abs(kwargs.get('latitude')) # if site is in southern hemisphere will set tilt to positive latitude value
            else:  # All other tilts come from lookup table included in the array_type_to_tilt_angle dictionary above
                self.tilt = PV.array_type_to_tilt_angle[kwargs.get('array_type')]

        if self.prod_factor_series_kw is not None:  # then don't call PVWatts
            self.station = (kwargs.get("latitude", 0), kwargs.get("longitude", 0), 0)
        else:
            self.pvwatts = PVWatts(time_steps_per_hour=self.time_steps_per_hour, azimuth=self.azimuth, tilt=self.tilt, **self.kwargs)

        dfm.add_pv(self)

    @property
    def prod_factor(self):
        if self.prod_factor_series_kw is None:
            if self.pvwatts_prod_factor is None:
                self.pvwatts_prod_factor = self.pvwatts.pv_prod_factor
            return self.pvwatts_prod_factor
        else:
            return self.prod_factor_series_kw

    @property
    def station_location(self):
        if self.pvwatts is not None:
            station = (self.pvwatts.response['station_info']['lat'],
                       self.pvwatts.response['station_info']['lon'],
                       round(self.pvwatts.response['station_info']['distance']/1000,1))
        else:
            station = self.station
        return station


class Wind(Tech):
    size_class_to_hub_height = {
        'residential': 20,  # 3/17/22 got 30m from Wind team, but Wind Toolkit has increments of 20m
        'commercial': 40,
        'medium': 60,  # Owen Roberts provided 50m for medium size_class, but Wind Toolkit has increments of 20m
        'large': 80,
    }
    size_class_to_installed_cost = { # indexed on api_version number
        1: {
            'residential': 11950,
            'commercial': 7390,
            'medium': 4440,
            'large': 3450,
        },
        2: {
            'residential': 5675,
            'commercial': 4300,
            'medium': 2766,
            'large': 2239,
        }
    }

    size_class_to_itc_incentives = { # indexed on api_version number
        1: {
            'residential': 0.3,
            'commercial': 0.3,
            'medium': 0.12,
            'large': 0.12,
        },
        2: {
            'residential': 0.3,
            'commercial': 0.3,
            'medium': 0.3,
            'large': 0.3,
        }
    }

    def __init__(self, dfm, inputs_path, acres_per_kw=.03, time_steps_per_hour=1, api_version=1,
                prod_factor_series_kw=None, **kwargs):
        super(Wind, self).__init__(**kwargs)

        self.path_inputs = inputs_path
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'WIND'
        self.acres_per_kw = acres_per_kw
        self.hub_height_meters = Wind.size_class_to_hub_height[kwargs['size_class']]
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.installed_cost_us_dollars_per_kw = kwargs.get('installed_cost_us_dollars_per_kw')
        self.prod_factor_series_kw = prod_factor_series_kw
        self.sr_required_pct = kwargs.get("sr_required_pct")

        # if user hasn't entered the federal itc, itc value gets assigned based on size_class
        if self.incentives.federal.itc == 0.123:
            self.incentives.federal.itc = Wind.size_class_to_itc_incentives[api_version][kwargs.get('size_class')]

        # if user hasn't entered the installed cost per kw, it gets assigned based on size_class
        if kwargs.get('installed_cost_us_dollars_per_kw') == 3013:
            self.installed_cost_us_dollars_per_kw = \
                Wind.size_class_to_installed_cost[api_version][kwargs.get('size_class')]

        self.sam_prod_factor = None
        dfm.add_wind(self)

    @property
    def prod_factor(self):
        """
        Pass resource_meters_per_sec to SAM SDK to get production factor
        :return: wind turbine production factor for 1kW system for 1 year with length = 8760 * time_steps_per_hour
        """
        if self.prod_factor_series_kw is None:
            if self.sam_prod_factor is None:
                sam = WindSAMSDK(path_inputs=self.path_inputs, hub_height_meters=self.hub_height_meters,
                                 time_steps_per_hour=self.time_steps_per_hour, **self.kwargs)
                self.sam_prod_factor = sam.wind_prod_factor()
            return self.sam_prod_factor
        else:
            return self.prod_factor_series_kw


class Generator(Tech):

    def __init__(self, dfm, min_kw, max_kw, existing_kw, fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr,
                 fuel_avail_gal, min_turn_down_pct, outage_start_time_step=None, outage_end_time_step=None, time_steps_per_hour=1,
                 fuel_avail_before_outage_pct=1, generator_fuel_percent_RE=None, emissions_factor_lb_CO2_per_gal=None, emissions_factor_lb_NOx_per_gal=None,
                 emissions_factor_lb_SO2_per_gal=None, emissions_factor_lb_PM25_per_gal=None, **kwargs):

        super(Generator, self).__init__(min_kw=min_kw, max_kw=max_kw, **kwargs)
        """
        super class init for generator is not unique anymore as we are now allowing users to define min/max sizes;
        and include diesel generator's size as optimization decision variable.

        Note that default burn rate, slope, and min/max sizes are handled in ValidateNestedInput.
        """
        self.fuel_slope = fuel_slope_gal_per_kwh
        self.fuel_intercept = fuel_intercept_gal_per_hr
        self.fuel_avail = fuel_avail_gal
        self.min_turn_down_pct = min_turn_down_pct
        self.reopt_class = 'GENERATOR'
        self.outage_start_time_step = outage_start_time_step
        self.outage_end_time_step = outage_end_time_step
        self.time_steps_per_hour = time_steps_per_hour
        self.generator_only_runs_during_grid_outage = kwargs['generator_only_runs_during_grid_outage']
        self.fuel_avail_before_outage_pct = fuel_avail_before_outage_pct
        self.generator_sells_energy_back_to_grid = kwargs['generator_sells_energy_back_to_grid']
        self.diesel_fuel_cost_us_dollars_per_gallon = kwargs['diesel_fuel_cost_us_dollars_per_gallon']
        self.om_cost_us_dollars_per_kwh = kwargs['om_cost_us_dollars_per_kwh']
        self.derate = 0.0
        self.incentives = Incentives(**kwargs)
        if max_kw < min_kw:
            min_kw = max_kw
        self.min_kw = min_kw
        self.max_kw = max_kw
        self.existing_kw = existing_kw
        self.generator_fuel_percent_RE = generator_fuel_percent_RE
        self.useful_life_years = kwargs['useful_life_years']
        self.emissions_factor_lb_CO2_per_gal = emissions_factor_lb_CO2_per_gal
        self.emissions_factor_lb_NOx_per_gal = emissions_factor_lb_NOx_per_gal
        self.emissions_factor_lb_SO2_per_gal = emissions_factor_lb_SO2_per_gal
        self.emissions_factor_lb_PM25_per_gal = emissions_factor_lb_PM25_per_gal

        dfm.add_generator(self)

    @property
    def prod_factor(self):
        gen_prod_factor = [0.0 for _ in range(8760 * self.time_steps_per_hour)]

        if self.generator_only_runs_during_grid_outage:
            if self.outage_start_time_step is not None and self.outage_end_time_step is not None:
                # minus 1 in next line accounts for Python's zero-indexing
                gen_prod_factor[self.outage_start_time_step - 1:self.outage_end_time_step] \
                    = [1] * (self.outage_end_time_step - self.outage_start_time_step + 1)
        else:
            gen_prod_factor = [1] * len(gen_prod_factor)

        return gen_prod_factor

    @staticmethod
    def default_fuel_burn_rate(size_kw):
        """
        Based off of size_kw, we have default (fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr) pairs
        :return: (fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr)
        """
        if size_kw <= 40:
            m = 0.068
            b = 0.0125
        elif size_kw <= 80:
            m = 0.066
            b = 0.0142
        elif size_kw <= 150:
            m = 0.0644
            b = 0.0095
        elif size_kw <= 250:
            m = 0.0648
            b = 0.0067
        elif size_kw <= 750:
            m = 0.0656
            b = 0.0048
        elif size_kw <= 1500:
            m = 0.0657
            b = 0.0043
        else:
            m = 0.0657
            b = 0.004
        return m, b


class CHP(Tech):
    """
    Default cost and performance parameters based on prime_mover, size_class, and Boiler.existing_boiler_production_type_steam_or_hw are stored here
    validators.py and view.py uses these Class attributes to load in and communicate these defaults into the API and UI, respectively

    """
    # Default data, created from input_files.CHP.chp_input_defaults_processing, copied from chp_default_data.json
    prime_mover_defaults_all = json.load(open(os.path.join("input_files","CHP","chp_default_data.json")))

    # Lower and upper bounds for size classes - Class 0 is the total average across entire range of data
    class_bounds = {"recip_engine": [(30, 9300), (30, 100), (100, 630), (630, 1140), (1140, 3300), (3300, 9300)],
                    "micro_turbine": [(30, 1290), (30, 60), (60, 190), (190, 950), (950, 1290)],
                    "combustion_turbine": [(950, 20000), (950, 1800), (1800, 3300), (3300, 5400), (5400, 7500),
                                           (7500, 14000), (14000, 20000)],
                    "fuel_cell": [(440, 9300), (440, 1400), (1400, 9300)]}

    # The default CHP size class, currently set to size_class 0 which is the average values across the entire range of data (i.e. all size classes)
    default_chp_size_class = {"recip_engine": 0,
                              "micro_turbine": 0,
                              "combustion_turbine": 0,
                              "fuel_cell": 0}

    def __init__(self, dfm, run_uuid, existing_boiler_production_type_steam_or_hw, oa_temp_degF, site_elevation_ft,
                 emissions_factor_lb_CO2_per_mmbtu=None, emissions_factor_lb_NOx_per_mmbtu=None,
                 emissions_factor_lb_SO2_per_mmbtu=None, emissions_factor_lb_PM25_per_mmbtu=None,
                 outage_start_time_step=None, outage_end_time_step=None, time_steps_per_hour=1, year=None, **kwargs):
        super(CHP, self).__init__(**kwargs)

        self.prime_mover = kwargs.get('prime_mover')
        self.size_class = kwargs.get('size_class')
        self.existing_boiler_production_type_steam_or_hw = existing_boiler_production_type_steam_or_hw
        self.reopt_class = 'CHP'
        self.is_chp = True
        self.time_steps_per_hour = time_steps_per_hour
        self.derate = 1  # Need to rectify this legacy derate, maybe remove this and replace if no needed (NM/IL?)
        self.incentives = Incentives(**kwargs)

        # All of these attributes are assigned based on defaults in validators.py or they should all be in the inputs
        self.min_kw = kwargs['min_kw']
        self.max_kw = kwargs['max_kw']
        self.installed_cost_us_dollars_per_kw = kwargs['installed_cost_us_dollars_per_kw']
        self.tech_size_for_cost_curve = kwargs.get('tech_size_for_cost_curve')
        self.om_cost_us_dollars_per_kw = kwargs['om_cost_us_dollars_per_kw']
        self.om_cost_us_dollars_per_kwh = kwargs['om_cost_us_dollars_per_kwh']
        self.om_cost_us_dollars_per_hr_per_kw_rated = kwargs['om_cost_us_dollars_per_hr_per_kw_rated']
        self.elec_effic_full_load = kwargs['elec_effic_full_load']
        self.elec_effic_half_load = kwargs['elec_effic_half_load']
        self.thermal_effic_full_load = kwargs['thermal_effic_full_load']
        self.thermal_effic_half_load = kwargs['thermal_effic_half_load']
        self.min_turn_down_pct = kwargs['min_turn_down_pct']
        self.min_allowable_kw = kwargs['min_allowable_kw']
        self.use_default_derate = kwargs['use_default_derate']
        self.max_derate_factor = kwargs['max_derate_factor']
        self.derate_start_temp_degF = kwargs['derate_start_temp_degF']
        self.derate_slope_pct_per_degF = kwargs['derate_slope_pct_per_degF']
        self.chp_unavailability_periods = kwargs['chp_unavailability_periods']
        self.cooling_thermal_factor = kwargs['cooling_thermal_factor']
        self.outage_start_time_step = outage_start_time_step
        self.outage_end_time_step = outage_end_time_step
        self.year = year
        self.can_supply_steam_turbine = kwargs.get('can_supply_steam_turbine')
        self.supplementary_firing_max_steam_ratio = kwargs.get('supplementary_firing_max_steam_ratio')
        self.supplementary_firing_efficiency = kwargs.get('supplementary_firing_efficiency')
        self.supplementary_firing_capital_cost_per_kw = kwargs.get('supplementary_firing_capital_cost_per_kw')
        self.emissions_factor_lb_CO2_per_mmbtu = emissions_factor_lb_CO2_per_mmbtu
        self.emissions_factor_lb_NOx_per_mmbtu = emissions_factor_lb_NOx_per_mmbtu
        self.emissions_factor_lb_SO2_per_mmbtu = emissions_factor_lb_SO2_per_mmbtu
        self.emissions_factor_lb_PM25_per_mmbtu = emissions_factor_lb_PM25_per_mmbtu

        self.fuel_burn_slope, self.fuel_burn_intercept, self.thermal_prod_slope, self.thermal_prod_intercept = \
            self.convert_performance_params(self.elec_effic_full_load, self.elec_effic_half_load,
                                            self.thermal_effic_full_load,
                                            self.thermal_effic_half_load)
        if self.use_default_derate:
            # TODO: Use either site altitude OR derate_max, depending on which, if any, are input. VALIDATORS.PY to handle this!
            # TODO: implement derate factor array based on input temperature profile, with derate_max from above TODO
            self.chp_power_derate = [1.0 for _ in range(8760 * self.time_steps_per_hour)]

        dfm.add_chp(self)

    @property
    def prod_factor(self):
        self.chp_unavailability_hourly_list, self.start_day_of_month_list, self.errors_list = generate_year_profile_hourly(self.year, self.chp_unavailability_periods)

        chp_elec_prod_factor = [1.0 - self.chp_unavailability_hourly_list[i] for i in range(8760) for _ in range(self.time_steps_per_hour)]
        # Note, we are handling boiler efficiency explicitly so not embedding that into chp thermal prod factor
        chp_thermal_prod_factor = [1.0 - self.chp_unavailability_hourly_list[i] for i in range(8760) for _ in range(self.time_steps_per_hour)]

        # Ignore unavailability in timestep if it intersects with an outage interval
        if self.outage_start_time_step and self.outage_end_time_step:
            chp_elec_prod_factor[self.outage_start_time_step - 1:self.outage_end_time_step] = \
                [1.0] * (self.outage_end_time_step - self.outage_start_time_step + 1)
            chp_thermal_prod_factor[self.outage_start_time_step - 1:self.outage_end_time_step] = \
                [1.0] * (self.outage_end_time_step - self.outage_start_time_step + 1)

        return chp_elec_prod_factor, chp_thermal_prod_factor

    @staticmethod
    def convert_performance_params(elec_effic_full_load, elec_effic_half_load, thermal_effic_full_load,
                                   thermal_effic_half_load):
        """
        Convert the performance parameter inputs to coefficients used readily in Xpress
        :return: fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept
        """
        # Fuel burn slope and intercept
        fuel_burn_full_load = 1 / elec_effic_full_load * 1.0  # [kWt/kWe]
        fuel_burn_half_load = 1 / elec_effic_half_load * 0.5  # [kWt/kWe]
        fuel_burn_slope = (fuel_burn_full_load - fuel_burn_half_load) / (1.0 - 0.5)  # [kWt/kWe]
        fuel_burn_intercept = fuel_burn_full_load - fuel_burn_slope * 1.0  # [kWt/kWe_rated]
        # Thermal production slope and intercept
        thermal_prod_full_load = 1.0 * 1 / elec_effic_full_load * thermal_effic_full_load  # [kWt/kWe]
        thermal_prod_half_load = 0.5 * 1 / elec_effic_half_load * thermal_effic_half_load   # [kWt/kWe]
        thermal_prod_slope = (thermal_prod_full_load - thermal_prod_half_load) / (1.0 - 0.5)  # [kWt/kWe]
        thermal_prod_intercept = thermal_prod_full_load - thermal_prod_slope * 1.0  # [kWt/kWe_rated]

        return fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept

    @staticmethod
    def get_chp_defaults(prime_mover, hw_or_steam=None, size_class=None):
        """
        Parse the default CHP cost and performance parameters based on:
        1. prime_mover (required)
        2. hw_or_steam (optional)
        3. size_class (optional)
        :return: dictionary of default cost and performance parameters
        """

        # Thermal efficiency has an extra dimension for hot_water (0) or steam (1) index
        hw_or_steam_index_dict = {"hot_water": 0, "steam": 1}
        if hw_or_steam is None:  # Use default hw_or_steam based on prime_mover
            hw_or_steam = Boiler.boiler_type_by_chp_prime_mover_defaults[prime_mover]
        hw_or_steam_index = hw_or_steam_index_dict[hw_or_steam]

        # Default to average parameter values across all size classes (size_class = 0) if None is input
        if size_class is None:
            size_class = CHP.default_chp_size_class[prime_mover]

        # Get default CHP parameters based on prime_mover, hw_or_steam, and size_class
        prime_mover_defaults_all = copy.deepcopy(CHP.prime_mover_defaults_all)
        prime_mover_defaults = {}
        for param in prime_mover_defaults_all[prime_mover].keys():
            if param in ["thermal_effic_full_load", "thermal_effic_half_load"]:
                prime_mover_defaults[param] = prime_mover_defaults_all[prime_mover][param][hw_or_steam_index][size_class]
            else:
                prime_mover_defaults[param] = prime_mover_defaults_all[prime_mover][param][size_class]

        return prime_mover_defaults


class Boiler(Tech):

    boiler_efficiency_defaults = {"hot_water": 0.80,
                                  "steam": 0.75}

    boiler_type_by_chp_prime_mover_defaults = {"recip_engine": "hot_water",
                                               "micro_turbine": "hot_water",
                                               "combustion_turbine": "steam",
                                               "fuel_cell": "hot_water"}

    def __init__(self, dfm, boiler_fuel_series_bau, emissions_factor_lb_CO2_per_mmbtu=None, emissions_factor_lb_NOx_per_mmbtu=None,
                 emissions_factor_lb_SO2_per_mmbtu=None, emissions_factor_lb_PM25_per_mmbtu=None, **kwargs):
        super(Boiler, self).__init__(**kwargs)

        self.is_hot = True
        self.reopt_class = 'BOILER'  # Not sure why UTIL tech is not assigned to the UTIL class
        self.max_thermal_factor_on_peak_load = kwargs.get('max_thermal_factor_on_peak_load')
        self.existing_boiler_production_type_steam_or_hw = kwargs.get('existing_boiler_production_type_steam_or_hw')
        self.boiler_efficiency = kwargs.get('boiler_efficiency')
        self.can_supply_steam_turbine = kwargs.get('can_supply_steam_turbine')
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps
        self.emissions_factor_lb_CO2_per_mmbtu = emissions_factor_lb_CO2_per_mmbtu
        self.emissions_factor_lb_NOx_per_mmbtu = emissions_factor_lb_NOx_per_mmbtu
        self.emissions_factor_lb_SO2_per_mmbtu = emissions_factor_lb_SO2_per_mmbtu
        self.emissions_factor_lb_PM25_per_mmbtu = emissions_factor_lb_PM25_per_mmbtu

        # Assign boiler max size equal to the peak load multiplied by the thermal_factor
        self.max_kw = max(boiler_fuel_series_bau) * self.boiler_efficiency * self.max_thermal_factor_on_peak_load * MMBTU_TO_KWH

        dfm.add_boiler(self)

    @property
    def prod_factor(self):

        # Note boiler efficiency is explicitly accounted for instead of being embedded in the prod_factor
        boiler_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return boiler_prod_factor


class ElectricChiller(Tech):

    def __init__(self, dfm, lpct, **kwargs):
        super(ElectricChiller, self).__init__(**kwargs)
        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ELECCHL'
        self.max_thermal_factor_on_peak_load = kwargs['max_thermal_factor_on_peak_load']
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps
        self.chiller_cop = lpct.chiller_cop

        # Assign max_kw based on cooling thermal load (kw is cooling thermal production capacity)
        self.max_cooling_load_tons = max(lpct.load_list) / TONHOUR_TO_KWHT
        self.max_chiller_thermal_capacity_tons = self.max_cooling_load_tons * self.max_thermal_factor_on_peak_load
        self.max_kw = self.max_chiller_thermal_capacity_tons * TONHOUR_TO_KWHT

        dfm.add_electric_chiller(self)

    @property
    def prod_factor(self):

        # Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps
        # Note chiller_cop is explicitly accounted for instead of being embedded in the prod_factor
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor


class AbsorptionChiller(Tech):

    absorption_chiller_cop_defaults = {"hot_water": 0.74,
                                       "steam": 1.42}

    # Data format for cost is (ton, $/ton, $/ton/yr); less than 1st or greater than last size uses constant, otherwise lin-interp
    absorption_chiller_cost_defaults = {"hot_water": [(10, 7000.0, 300.0), (50, 3066.0, 80.0), (200, 2027.0, 36.0), (300, 1587.0, 32.0),
                                                      (400, 1527.0, 31.0), (500, 1426.0, 30.0), (600, 1365.0, 28.0), (700, 1313.0, 26.0),
                                                      (800, 1312.0, 23.0), (900, 1277.0, 20.0), (1000, 1248.0, 18.0)],
                                        "steam": [(50, 3723.0, 80.0), (200, 2461.0, 36.0), (300, 1960.0, 32.0),
                                                      (400, 1855.0, 31.0), (500, 1709.0, 30.0), (600, 1623.0, 28.0), (700, 1547.0, 26.0),
                                                      (800, 1520.0, 23.0), (900, 1470.0, 20.0), (1000, 1427.0, 18.0)]}

    def __init__(self, dfm, max_cooling_load_tons, hw_or_steam, chp_prime_mover, chiller_cop, **kwargs):
        super(AbsorptionChiller, self).__init__(**kwargs)

        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ABSORPCHL'
        self.chiller_cop = chiller_cop
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        # Convert a size-based inputs from ton to kwt
        self.min_kw = kwargs.get('min_ton') * TONHOUR_TO_KWHT
        self.max_kw = kwargs.get('max_ton') * TONHOUR_TO_KWHT
        self.installed_cost_us_dollars_per_ton = kwargs.get('installed_cost_us_dollars_per_ton')
        self.om_cost_us_dollars_per_ton = kwargs.get('om_cost_us_dollars_per_ton')
        self.max_cooling_load_tons = max_cooling_load_tons
        self.hw_or_steam = hw_or_steam
        self.chp_prime_mover = chp_prime_mover
        self.chiller_elec_cop = kwargs.get('chiller_elec_cop')

        # Calc default CapEx and OpEx costs, and use if the user did not enter a value
        installed_cost_per_ton_calc, om_cost_per_ton_per_yr_calc = self.get_absorp_chiller_costs(
            self.max_cooling_load_tons, self.hw_or_steam, self.chp_prime_mover)

        if self.installed_cost_us_dollars_per_ton is None and self.om_cost_us_dollars_per_ton is None:
            self.installed_cost_us_dollars_per_ton = installed_cost_per_ton_calc
            self.om_cost_us_dollars_per_ton = om_cost_per_ton_per_yr_calc
        elif self.installed_cost_us_dollars_per_ton is None:
            self.installed_cost_us_dollars_per_ton = installed_cost_per_ton_calc
        elif self.om_cost_us_dollars_per_ton is None:
            self.om_cost_us_dollars_per_ton = om_cost_per_ton_per_yr_calc

        self.installed_cost_us_dollars_per_kw = self.installed_cost_us_dollars_per_ton / TONHOUR_TO_KWHT
        self.om_cost_us_dollars_per_kw = self.om_cost_us_dollars_per_ton / TONHOUR_TO_KWHT

        kwargs['macrs_itc_reduction'] = 0.0
        self.incentives = IncentivesNoProdBased(**kwargs)

        dfm.add_absorption_chiller(self)

    @property
    def prod_factor(self):
        """
        Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps (but don't currently)
        :return: prod_factor
        """
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor

    @staticmethod
    def get_absorp_chiller_costs(max_cooling_load_tons, hw_or_steam, chp_prime_mover):
        """
        Pass max_cooling_load_tons, hw_or_steam, and/or CHP.prime_mover to get absorption chiller installed and O&M costs.
        :return: absorp_chiller_capex, absorp_chiller_opex
        """
        if hw_or_steam is not None:
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults[hw_or_steam]
        elif chp_prime_mover is not None:
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults[Boiler.boiler_type_by_chp_prime_mover_defaults[chp_prime_mover]]
        else:
            # If hw_or_steam and CHP prime_mover are not provided, use hot_water defaults
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults["hot_water"]

        if max_cooling_load_tons <= defaults_sizes[0][0]:
            absorp_chiller_capex = defaults_sizes[0][1]
            absorp_chiller_opex = defaults_sizes[0][2]
        elif max_cooling_load_tons >= defaults_sizes[-1][0]:
            absorp_chiller_capex = defaults_sizes[-1][1]
            absorp_chiller_opex = defaults_sizes[-1][2]
        else:
            for size in range(1, len(defaults_sizes)):
                if max_cooling_load_tons > defaults_sizes[size - 1][0] and \
                        max_cooling_load_tons <= defaults_sizes[size][0]:
                    slope_capex = (defaults_sizes[size][1] - defaults_sizes[size - 1][1]) / \
                                  (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                    slope_opex = (defaults_sizes[size][2] - defaults_sizes[size - 1][2]) / \
                                 (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                    absorp_chiller_capex = defaults_sizes[size - 1][1] + slope_capex * \
                                           (max_cooling_load_tons - defaults_sizes[size - 1][0])
                    absorp_chiller_opex = defaults_sizes[size - 1][2] + slope_opex * \
                                          (max_cooling_load_tons - defaults_sizes[size - 1][0])

        return absorp_chiller_capex, absorp_chiller_opex

    @staticmethod
    def get_absorp_chiller_cop(hot_water_or_steam=None, chp_prime_mover=None):
        """
        Pass hot_water_or_steam or chp_prime_mover to get absorption chiller COP. If none is passed, assume hot_water
        :return: chiller_cop
        """
        if hot_water_or_steam is not None:
            absorp_chiller_cop = AbsorptionChiller.absorption_chiller_cop_defaults[hot_water_or_steam]
        elif chp_prime_mover is not None:
            absorp_chiller_cop = AbsorptionChiller.absorption_chiller_cop_defaults[Boiler.boiler_type_by_chp_prime_mover_defaults[chp_prime_mover]]
        else:  # If hot_water_or_steam and CHP prime_mover are not provided, use hot_water defaults
            absorp_chiller_cop = AbsorptionChiller.absorption_chiller_cop_defaults["hot_water"]

        return absorp_chiller_cop


class NewBoiler(Tech):

    boiler_efficiency_defaults = {"hot_water": 0.90,
                                  "steam_lp": 0.80,
                                  "steam_hp": 0.75}

    def __init__(self, dfm, **kwargs):
        super(NewBoiler, self).__init__(**kwargs)

        self.is_hot = True
        self.reopt_class = 'NEWBOILER'
        self.min_mmbtu_per_hr = kwargs.get('min_mmbtu_per_hr')
        self.max_mmbtu_per_hr = kwargs.get('max_mmbtu_per_hr')
        self.boiler_efficiency = kwargs.get('boiler_efficiency')
        self.can_supply_steam_turbine = kwargs.get('can_supply_steam_turbine')
        self.installed_cost_us_dollars_per_mmbtu_per_hr = kwargs.get('installed_cost_us_dollars_per_mmbtu_per_hr')
        self.om_cost_us_dollars_per_mmbtu_per_hr = kwargs.get('om_cost_us_dollars_per_mmbtu_per_hr')
        self.om_cost_us_dollars_per_mmbtu = kwargs.get('om_cost_us_dollars_per_mmbtu')
        self.emissions_factor_lb_CO2_per_mmbtu = kwargs.get('emissions_factor_lb_CO2_per_mmbtu')
        self.emissions_factor_lb_NOx_per_mmbtu = kwargs.get('emissions_factor_lb_NOx_per_mmbtu')
        self.emissions_factor_lb_SO2_per_mmbtu = kwargs.get('emissions_factor_lb_SO2_per_mmbtu')
        self.emissions_factor_lb_PM25_per_mmbtu = kwargs.get('emissions_factor_lb_PM25_per_mmbtu')

        # Convert cost basis of mmbtu/mmbtu_per_hr to kwh/kw
        self.installed_cost_us_dollars_per_kw = self.installed_cost_us_dollars_per_mmbtu_per_hr / MMBTU_TO_KWH
        self.om_cost_us_dollars_per_kw = self.om_cost_us_dollars_per_mmbtu_per_hr / MMBTU_TO_KWH
        self.om_cost_us_dollars_per_kwh = self.om_cost_us_dollars_per_mmbtu / MMBTU_TO_KWH

        self.derate = 0  # TODO remove this from data_manager and *.jl model
        self.n_timesteps = dfm.n_timesteps

        kwargs['macrs_itc_reduction'] = None
        self.incentives = IncentivesNoProdBased(**kwargs)

        dfm.add_newboiler(self)

    @property
    def prod_factor(self):
        """
        NewBoiler ProdFactor is where we can account for unavailability
           and/or ambient temperature affects
        :return: prod_factor
        """
        newboiler_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return newboiler_prod_factor

class SteamTurbine(Tech):

    # Default data, created from input_files.CHP.steam_turbine_Default_data.json
    # Data points for steam turbine are 500 kW, 3000 kW, and 15000 kW; class bounds span above and below the data point sizes
    class_bounds = [(0.0, 25000.0), (0, 1000.0), (1000.0, 5000.0), (5000.0, 250000.0)]
    steam_turbine_defaults_all = json.load(open(os.path.join("input_files","CHP","steam_turbine_default_data.json")))

    def __init__(self, dfm, **kwargs):
        super(SteamTurbine, self).__init__(**kwargs)

        self.reopt_class = 'STEAMTURBINE'
        self.electric_produced_to_thermal_consumed_ratio = kwargs.get('electric_produced_to_thermal_consumed_ratio')
        self.thermal_produced_to_thermal_consumed_ratio = kwargs.get('thermal_produced_to_thermal_consumed_ratio')
        self.is_condensing = kwargs.get('is_condensing')
        self.inlet_steam_pressure_psig = kwargs.get('inlet_steam_pressure_psig')
        self.inlet_steam_temperature_degF = kwargs.get('inlet_steam_temperature_degF')
        self.inlet_steam_superheat_degF = kwargs.get('inlet_steam_superheat_degF')
        self.outlet_steam_pressure_psig = kwargs.get('outlet_steam_pressure_psig')
        self.outlet_steam_min_vapor_fraction = kwargs.get('outlet_steam_min_vapor_fraction')
        self.isentropic_efficiency = kwargs.get('isentropic_efficiency')
        self.gearbox_generator_efficiency = kwargs.get('gearbox_generator_efficiency')
        self.net_to_gross_electric_ratio = kwargs.get('net_to_gross_electric_ratio')
        self.om_cost_us_dollars_per_kwh = kwargs.get('om_cost_us_dollars_per_kwh')

        self.derate = 0  # TODO remove this from data_manager and *.jl model
        self.n_timesteps = dfm.n_timesteps

        self.st_elec_out_to_therm_in_ratio, self.st_therm_out_to_therm_in_ratio = self.st_elec_and_therm_prod_ratios()

        kwargs['macrs_itc_reduction'] = 0.0
        self.incentives = IncentivesNoProdBased(**kwargs)

        dfm.add_steamturbine(self)

    @property
    def prod_factor(self):
        """
        SteamTurbine ProdFactor is where we can account for unavailability
           and/or ambient temperature affects for condensing ST
        :return: prod_factor
        """
        st_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return st_prod_factor

    def st_elec_and_therm_prod_ratios(self):
        """
        Calculate steam turbine (ST) electric output to thermal input ratio based on inlet and outlet steam conditions and ST performance.
           Units of [kWe_net / kWt_in]
        :return: st_elec_out_to_therm_in_ratio, st_therm_out_to_therm_in_ratio
        """

        # Convert input steam conditions to SI (absolute pressures, not gauge)
        # ST Inlet
        self.p_in_pa = (self.inlet_steam_pressure_psig / 14.5038 + 1.01325) * 1.0E5
        if self.inlet_steam_temperature_degF is None:
            self.t_in_sat_k = CP.PropsSI("T","P",self.p_in_pa,"Q",1.0,"Water")
            self.t_superheat_in_k = (self.inlet_steam_superheat_degF - 32.0) * 5.0 / 9.0 + 273.15
            self.t_in_k = self.t_in_sat_k + self.t_superheat_in_k
        else:
            self.t_in_k = (self.inlet_steam_temperature_degF - 32.0) * 5.0 / 9.0 + 273.15
        self.h_in_j_per_kg = CP.PropsSI("H","P",self.p_in_pa,"T",self.t_in_k,"Water")
        self.s_in_j_per_kgK = CP.PropsSI("S","P",self.p_in_pa,"T",self.t_in_k,"Water")

        # ST Outlet
        self.p_out_pa = (self.outlet_steam_pressure_psig / 14.5038 + 1.01325) * 1.0E5
        self.h_out_ideal_j_per_kg = CP.PropsSI("H","P",self.p_out_pa,"S",self.s_in_j_per_kgK,"Water")
        self.h_out_j_per_kg = self.h_in_j_per_kg - self.isentropic_efficiency * (self.h_in_j_per_kg - self.h_out_ideal_j_per_kg)
        self.x_out = CP.PropsSI("Q","P",self.p_out_pa,"H",self.h_out_j_per_kg,"Water")

        # ST Power
        self.st_shaft_power_kwh_per_kg = (self.h_in_j_per_kg - self.h_out_j_per_kg) / 1000.0 / 3600.0
        self.st_net_elec_power_kwh_per_kg = self.st_shaft_power_kwh_per_kg * self.gearbox_generator_efficiency * self.net_to_gross_electric_ratio

        # Condenser heat rejection or heat recovery if ST is back-pressure
        if self.is_condensing:
            self.heat_recovered_kwh_per_kg = 0.0
        else:
            self.h_out_sat_liq_j_per_kg = CP.PropsSI("H","P",self.p_out_pa,"Q",0.0,"Water")
            self.heat_recovered_kwh_per_kg = (self.h_out_j_per_kg - self.h_out_sat_liq_j_per_kg) / 1000.0 / 3600.0

        # Boiler Thermal Power - assume enthalpy at saturated liquid condition (ignore delta H of pump)
        self.h_boiler_in_j_per_kg = CP.PropsSI("H","P",self.p_out_pa,"Q",0.0,"Water")
        self.boiler_therm_power_kwh_per_kg = (self.h_in_j_per_kg - self.h_boiler_in_j_per_kg) / 1000.0 / 3600.0

        # Calculate output ratios
        if self.electric_produced_to_thermal_consumed_ratio is None:
            st_elec_out_to_therm_in_ratio = self.st_net_elec_power_kwh_per_kg / self.boiler_therm_power_kwh_per_kg
        else:
            st_elec_out_to_therm_in_ratio = self.electric_produced_to_thermal_consumed_ratio

        if self.thermal_produced_to_thermal_consumed_ratio is None:
            st_therm_out_to_therm_in_ratio = self.heat_recovered_kwh_per_kg / self.boiler_therm_power_kwh_per_kg
        else:
            st_therm_out_to_therm_in_ratio = self.thermal_produced_to_thermal_consumed_ratio

        return st_elec_out_to_therm_in_ratio, st_therm_out_to_therm_in_ratio

    @staticmethod
    def get_steam_turbine_defaults(size_class=None):
        """
        Parse the default steam turbine cost and performance parameters
        :return: dictionary of default cost and performance parameters
        """

        # Default to average parameter values across all size classes (size_class = 0) if None is input
        if size_class is None:
            size_class = 0

        # Get default steam turbine parameters based on size_class
        steam_turbine_defaults_all = copy.deepcopy(SteamTurbine.steam_turbine_defaults_all)
        steam_turbine_defaults = {}
        for param in steam_turbine_defaults_all.keys():
            steam_turbine_defaults[param] = steam_turbine_defaults_all[param][size_class]

        return steam_turbine_defaults
