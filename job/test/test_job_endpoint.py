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
from cProfile import run
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import os
import logging
import requests
logging.disable(logging.CRITICAL)


class TestJobEndpoint(ResourceTestCaseMixin, TestCase):

    def test_pv_battery_and_emissions_defaults_from_julia(self):
        """
        Same test post as"Solar and Storage w/BAU" in the Julia package. Used in development of v3.
        Also tests that inputs with defaults determined in the REopt julia package get updated in the database.
        """
        post_file = os.path.join('job', 'test', 'posts', 'pv_batt_emissions.json')
        post = json.load(open(post_file, 'r'))

        resp = self.api_client.post('/dev/job/', format='json', data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        self.assertAlmostEqual(results["Financial"]["lcc"], 1.240037e7, places=-3)
        self.assertAlmostEqual(results["Financial"]["lcc_bau"], 12766397, places=-3)
        self.assertAlmostEqual(results["PV"]["size_kw"], 216.667, places=1)
        self.assertAlmostEqual(results["ElectricStorage"]["size_kw"], 55.9, places=1)
        self.assertAlmostEqual(results["ElectricStorage"]["size_kwh"], 78.9, places=1)
        self.assertIsNotNone(results["Site"]["total_renewable_energy_fraction"])
        self.assertIsNotNone(results["Site"]["year_one_emissions_tonnes_CO2"])
        self.assertIsNotNone(results["Site"]["lifecycle_emissions_tonnes_NOx"])

        #test that emissions inputs got updated in the database with the defaults determined in REopt julia package
        updated_inputs = r["inputs"]
        self.assertIsNotNone(updated_inputs["ElectricUtility"]["emissions_factor_series_lb_CO2_per_kwh"])
        self.assertIsNotNone(updated_inputs["Financial"]["NOx_grid_cost_per_tonne"])
        self.assertIsNotNone(updated_inputs["Financial"]["SO2_onsite_fuelburn_cost_per_tonne"])
        self.assertIsNotNone(updated_inputs["Financial"]["PM25_cost_escalation_rate_fraction"])

    def test_off_grid_defaults(self):
        """
        Purpose of this test is to validate off-grid functionality and defaults in the API.
        """
        post_file = os.path.join('job', 'test', 'posts', 'off_grid_defaults.json')
        post = json.load(open(post_file, 'r'))

        resp = self.api_client.post('/dev/job/', format='json', data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        # Validate that we got off-grid response fields
        self.assertAlmostEqual(results["Financial"]["offgrid_microgrid_lcoe_dollars_per_kwh"], 0.337, places=-3)
        self.assertAlmostEqual(results["ElectricTariff"]["year_one_bill_before_tax"], 0.0)
        self.assertAlmostEqual(results["ElectricLoad"]["offgrid_load_met_fraction"], 0.99999, places=-2)
        self.assertAlmostEqual(sum(results["ElectricLoad"]["offgrid_load_met_series_kw"]), 8760.0, places=-1)
        self.assertAlmostEqual(results["Financial"]["lifecycle_offgrid_other_annual_costs_after_tax"], 0.0, places=-2)
    
    def test_process_reopt_error(self):
        """
        Purpose of this test is to ensure REopt status 400 is returned using the job endpoint
        """

        post_file = os.path.join('job', 'test', 'posts', 'handle_reopt_error.json')
        post = json.load(open(post_file, 'r'))

        resp = self.api_client.post('/dev/job/', format='json', data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]
        assert(resp.status_code==400)

    def test_superset_input_fields(self):
        """
        Purpose of this test is to test the API's ability to accept all relevant 
        input fields and send to REopt, ensuring name input consistency with REopt.jl.
        """
        post_file = os.path.join('job', 'test', 'posts', 'all_inputs_test.json')
        post = json.load(open(post_file, 'r'))

        resp = self.api_client.post('/dev/job/', format='json', data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        self.assertAlmostEqual(results["Financial"]["npv"], 165.21, places=-2)
        assert(resp.status_code==200)