from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from statistics import stdev

import arrow
import typer
from module_qc_data_tools import (
    load_json,
    outputDataFrame,
    qcDataFrame,
    save_dict_list,
)

from module_qc_analysis_tools import __version__
from module_qc_analysis_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTIONS,
    LogLevel,
)
from module_qc_analysis_tools.utils.misc import (
    get_inputs,
)

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    input_meas: Path = OPTIONS["input_meas"],
    base_output_dir: Path = OPTIONS["output_dir"],
    # qc_criteria_path: Path = OPTIONS["qc_criteria"],
    # layer: str = OPTIONS["layer"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    """
    Classifies pulls and performs the pulltest statistics.

    It produces an output file with several key parameters (pull strength min, % of wires with lift-off associated with pull strength < 7g...).

    ---

    General idea of how this analysis works:

    - For each pull, define location 'à priori', then extract 'break mode' and 'pull strength'
    - If an error occurred during the pulltest session, 'break mode' is used to show this error. Only, wires without errors are used to compute 'mean' pull strength (Option1 according to https://indico.cern.ch/event/1529894/contributions/6440914/attachments/3037883/5365239/ATLAS-ITk_MQAT_Pulltest_Analysis_MR277_JGIRAUD_2025-03-25.pdf)
    - Location is defined by the position in the list: position 1 to 10 <=> GA1, position 11 to 15 <=> GA2, position 16 to 25 <=> GA3
    - With this information, statistics are made.
    - Analysis in done comparing criterion defined for "PULL_STRENGTH", "PULL_STRENGTH_MIN" and "LIFT_OFFS_LESS_THAN_7G" according to Module Yield Taskforce report (https://indico.cern.ch/event/1533105/contributions/6451232/attachments/3043014/5376048/ModuleYield_GeneralReco_Updated.pdf)

    """
    log = logging.getLogger(__name__)
    log.setLevel(verbosity.value)

    log.info("")
    log.info(" ===============================================")
    log.info(" \tPerforming WIREBOND_PULL_TEST analysis")
    log.info(" ===============================================")
    log.info("")

    test_type = Path(__file__).stem

    time_start = round(datetime.timestamp(datetime.now()))
    output_dir = base_output_dir.joinpath(test_type).joinpath(f"{time_start}")
    output_dir.mkdir(parents=True, exist_ok=False)

    allinputs = get_inputs(input_meas)
    # qc_config = get_qc_config(qc_criteria_path, test_type)

    # alloutput = []
    # timestamps = []
    for filename in sorted(allinputs):
        log.info("")
        log.info(f" Loading {filename}")
        # meas_timestamp = get_time_stamp(filename)

        inputDFs = load_json(filename)
        log.info(
            f" There are results from {len(inputDFs)} module(s) stored in this file"
        )

        with Path(filename).open(encoding="utf-8") as f:
            jsonData = json.load(f)

        for j, inputDF in zip(jsonData, inputDFs):
            d = inputDF.to_dict()
            qcframe = inputDF.get_results()

            results = j[0].get("results")
            props = results.get("property")
            metadata = results.get("Metadata") or results.get("metadata")

            module_name = d.get("serialNumber")

            #  Simplistic QC criteria
            meas_array = metadata.get("pull_data")
            WIRE_PULLS = len(meas_array)
            strength = []
            wire_break_code = None
            counter_of_wires_without_error = 0
            counter_of_wires_with_error = 0
            counter_of_weak_wire = 0
            counter_of_liftoff_below_7g = 0
            counter_of_FE = 0
            counter_of_PCB = 0
            counter_of_peel_on_FE = 0
            counter_of_peel_on_PCB = 0
            counter_of_bond_peel = 0
            counter_of_midspan = 0

            data = []

            y_code_map = {
                "Midspan break": 0,
                "Heel break on hybrid": 1,
                "Heel break on chip": 2,
                "Bond peel on hybrid": 3,
                "Bond peel on chip": 4,
                "Pull failure": 5,
                "Operator error": 5,
                "other error": 5,
            }

            for i in range(WIRE_PULLS):
                each_wire_strength = meas_array[i].get("strength")
                type_of_break = meas_array[i].get("break_mode")

                if meas_array[i].get("location"):
                    location = int(meas_array[i].get("location"))
                else:
                    if i < 10:
                        location = 1
                    elif i < 15:
                        location = 2
                    elif i < 25:
                        location = 3
                    else:
                        location = 4

                wire_break_code = y_code_map.get(type_of_break)

                data.append([[each_wire_strength], [wire_break_code], [location]])

                if wire_break_code in [5, None]:  # Wires with errors or undefined
                    counter_of_wires_with_error += 1
                else:
                    counter_of_wires_without_error += 1
                    if each_wire_strength < 5.0:
                        counter_of_weak_wire += 1
                    if type_of_break == "Heel break on chip":
                        counter_of_FE += 1
                    elif type_of_break == "Heel break on hybrid":
                        counter_of_PCB += 1
                    elif type_of_break == "Bond peel on chip":
                        counter_of_peel_on_FE += 1
                        if each_wire_strength < 7.0:
                            counter_of_liftoff_below_7g += 1
                    elif type_of_break == "Bond peel on hybrid":
                        counter_of_peel_on_PCB += 1
                        if each_wire_strength < 7.0:
                            counter_of_liftoff_below_7g += 1
                    elif type_of_break == "Midspan break":
                        counter_of_midspan += 1
                    strength.append(each_wire_strength)

            results["WIRE_PULLS"] = WIRE_PULLS
            results["WIRE_PULLS_WITHOUT_ERROR"] = counter_of_wires_without_error
            results["PULL_STRENGTH"] = sum(strength) / counter_of_wires_without_error
            results["PULL_STRENGTH_ERROR"] = stdev(strength)
            results["WIRE_BREAKS_5G"] = counter_of_weak_wire
            results["PULL_STRENGTH_MIN"] = min(strength)
            results["PULL_STRENGTH_MAX"] = max(strength)
            results["HEEL_BREAKS_ON_FE_CHIP"] = counter_of_FE / WIRE_PULLS * 100
            results["HEEL_BREAKS_ON_PCB"] = counter_of_PCB / WIRE_PULLS * 100
            results["BOND_PEEL_ON_FE_CHIP"] = counter_of_peel_on_FE / WIRE_PULLS * 100
            results["BOND_PEEL_ON_PCB"] = counter_of_peel_on_PCB / WIRE_PULLS * 100
            results["MIDSPAN"] = counter_of_midspan / WIRE_PULLS * 100
            results["WITH_ERROR"] = counter_of_wires_with_error / WIRE_PULLS * 100

            results["BOND_PEEL"] = counter_of_bond_peel / WIRE_PULLS * 100
            results["LIFT_OFFS_LESS_THAN_7G"] = (
                counter_of_liftoff_below_7g / WIRE_PULLS * 100
            )

            results["DATA_UNAVAILABLE"] = WIRE_PULLS == 0
            results["PULL_STRENGTH_DATA"] = data

            #  QC criterion (according to Module_Yield_Taskforce report): Pass/Fail analysis
            passes_qc = True
            if (
                results["PULL_STRENGTH"] < 7
                or results["PULL_STRENGTH_MIN"] < 4
                or not results["LIFT_OFFS_LESS_THAN_7G"] < 10
            ):
                passes_qc = False

            #  Output a json file
            outputDF = outputDataFrame()
            outputDF.set_test_type(test_type)
            data = qcDataFrame()
            data._meta_data.update(metadata)

            #  Pass-through properties in input
            for key, value in props.items():
                data.add_property(key, value)

            #  Add analysis version
            data.add_property(
                "ANALYSIS_VERSION",
                __version__,
            )
            time_start = qcframe.get_meta_data().get("TimeStart")
            time_end = qcframe.get_meta_data().get("TimeEnd")
            duration = (
                (arrow.get(time_end) - arrow.get(time_start)).total_seconds()
                if time_start and time_end
                else -1
            )

            data.add_property(
                "MEASUREMENT_DATE",
                arrow.get(time_start).isoformat(timespec="milliseconds"),
            )
            data.add_property("MEASUREMENT_DURATION", int(duration))

            #  Pass-through measurement parameters
            for key, value in results.items():
                if key in [
                    "property",
                    "metadata",
                    "Metadata",
                    "Measurements",
                    "comment",
                ]:
                    continue

                data.add_parameter(key, value)

            outputDF.set_results(data)
            outputDF.set_pass_flag(passes_qc)

            outfile = output_dir.joinpath(f"{module_name}.json")
            log.info(f" Saving output of analysis to: {outfile}")
            out = outputDF.to_dict(True)
            out.update({"serialNumber": module_name})
            save_dict_list(outfile, [out])


#            plt_outfile = output_dir.joinpath(f"{module_name}_plot.png")
#           fig.savefig(plt_outfile, dpi=150)


if __name__ == "__main__":
    typer.run(main)
