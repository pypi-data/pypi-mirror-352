from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

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
    ctx: typer.Context,
    input_meas: Path = OPTIONS["input_meas"],
    base_output_dir: Path = OPTIONS["output_dir"],
    # qc_criteria_path: Path = OPTIONS["qc_criteria"],
    # layer: str = OPTIONS["layer"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    log = logging.getLogger(__name__)
    log.setLevel(verbosity.value)

    test_type = Path(__file__).stem
    if test_type == "GENERIC_NONELEC":
        if ctx.info_name in ["wirebonding-information", "analysis-WIREBONDING"]:
            test_type = "WIREBONDING"
        elif ctx.info_name in [
            "glue-module-flex-attach",
            "analysis-GLUE-MODULE-FLEX-ATTACH",
        ]:
            test_type = "GLUE_MODULE_FLEX_ATTACH"
        elif ctx.info_name in ["parylene", "analysis-PARYLENE"]:
            test_type = "PARYLENE"
        elif ctx.info_name in ["de-masking", "analysis-DE-MASKING"]:
            test_type = "DE_MASKING"
        elif ctx.info_name in ["wp-envelope", "analysis-WP-ENVELOPE"]:
            test_type = "WP_ENVELOPE"
        elif ctx.info_name in ["thermal-cycling", "analysis-THERMAL-CYCLING"]:
            test_type = "THERMAL_CYCLING"
        elif ctx.info_name in ["flatness", "analysis-FLATNESS"]:
            test_type = "FLATNESS"
        elif ctx.info_name in ["cutter-pcb-tab", "analysis-CUTTER-PCB-TAB"]:
            test_type = "CUTTER_PCB_TAB"
        else:
            msg = f"Running an unsupported generic non-electrical test type: {ctx.info_name}"
            raise ValueError(msg)

    msg = f" \tPerforming GENERIC_NONELEC analysis: {test_type}"
    log.info("")
    log.info(" ===============================================")
    log.info(msg)
    log.info(" ===============================================")
    log.info("")

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
            # alternatively, props.get("MODULE_SN")

            #  Simplistic QC criteria
            # temp = results.get("Measurements").get("TEMP")
            # humidity = results.get("Measurements").get("HUMIDITY")

            passes_qc = True

            #  Output a json file
            outputDF = outputDataFrame()
            outputDF.set_test_type(test_type)
            data = qcDataFrame()

            if metadata is not None:
                data._meta_data.update(metadata)
            #  Pass-through properties in input
            for key, value in props.items():
                data.add_property(key, value)

            #  Add analysis version
            data.add_property(
                "ANALYSIS_VERSION",
                __version__,
            )
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

            time_start = qcframe.get_meta_data()["TimeStart"]
            time_end = qcframe.get_meta_data().get("TimeEnd")
            duration = (
                (arrow.get(time_end) - arrow.get(time_start)).total_seconds()
                if time_end
                else -1
            )

            data.add_property(
                "MEASUREMENT_DATE",
                arrow.get(time_start).isoformat(timespec="milliseconds"),
            )
            data.add_property("MEASUREMENT_DURATION", int(duration))

            for key, value in results["Measurements"].items():
                data.add_parameter(key, value)
            outputDF.set_results(data)
            outputDF.set_pass_flag(passes_qc)

            outfile = output_dir.joinpath(f"{module_name}.json")
            log.info(f" Saving output of analysis to: {outfile}")
            out = outputDF.to_dict(True)
            out.update({"serialNumber": module_name})
            save_dict_list(outfile, [out])


if __name__ == "__main__":
    typer.run(main)
