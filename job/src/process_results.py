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
from job.models import FinancialOutputs, APIMeta, PVOutputs, ElectricStorageOutputs, ElectricTariffOutputs,\
    ElectricUtilityOutputs, GeneratorOutputs, ElectricLoadOutputs, WindOutputs


def process_results(results: dict, run_uuid: str) -> None:
    """
    Saves the results returned from the Julia API in the backend database.
    Called in job/run_jump_model (a celery task)
    """

    meta = APIMeta.objects.get(run_uuid=run_uuid)
    meta.status = results.get("status")
    meta.save(update_fields=["status"])
    FinancialOutputs.create(meta=meta, **results["Financial"]).save()
    ElectricTariffOutputs.create(meta=meta, **results["ElectricTariff"]).save()
    ElectricUtilityOutputs.create(meta=meta, **results["ElectricUtility"]).save()
    ElectricLoadOutputs.create(meta=meta, **results["ElectricLoad"]).save()
    if "PV" in results.keys():
        if isinstance(results["PV"], dict):
            PVOutputs.create(meta=meta, **results["PV"]).save()
        elif isinstance(results["PV"], list):
            for pvdict in results["PV"]:
                PVOutputs.create(meta=meta, **pvdict).save()
    if "ElectricStorage" in results.keys():
        ElectricStorageOutputs.create(meta=meta, **results["ElectricStorage"]).save()
    if "Generator" in results.keys():
        GeneratorOutputs.create(meta=meta, **results["Generator"]).save()
    if "Wind" in results.keys():
        WindOutputs.create(meta=meta, **results["Wind"]).save()
    if "Outages" in results.keys():
        outage_keys_to_skip = [
                    # "storage_upgraded", "Generator_upgraded", "PV_upgraded",
                    "discharge_from_storage_series", 
                    "PVmg_kw", "mg_PV_upgrade_cost", 
                    "mgPV_to_storage_series", "mgPV_curtailed_series", 
                    "mgPV_to_load_series", "Generatormg_kw",
                    "mg_Generator_upgrade_cost", 
                    "mgGenerator_to_storage_series", "mgGenerator_curtailed_series",
                    "mgGenerator_to_load_series", "mg_Generator_fuel_used"
                    ]
        pop_result_keys(results["Outages"], keys_to_skip)
        OutageOutputs.create(meta=meta, **results["Outages"]).save()
    # TODO process rest of results

def pop_result_keys(r:dict, keys_to_skip:list):

    for k in r.keys():
        if (type(r[k])) == dict:
            for s in keys_to_skip:
                r[k].pop(s, None)
        else:
            pass
