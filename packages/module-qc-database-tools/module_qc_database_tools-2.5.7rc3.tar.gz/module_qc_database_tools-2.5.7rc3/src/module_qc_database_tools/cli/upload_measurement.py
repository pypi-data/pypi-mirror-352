from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
import typer
from jsonschema import Draft202012Validator
from jsonschema.exceptions import relevance
from module_qc_data_tools.utils import datapath as mqdt_data

from module_qc_database_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTIONS,
    LogLevel,
    Protocol,
)

log = logging.getLogger(__name__)
app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    measurement_path: Path = OPTIONS["measurement_path"],
    host: str = OPTIONS["host"],
    port: int = OPTIONS["port"],
    protocol: Protocol = OPTIONS["protocol"],
    verify_ssl: bool = OPTIONS["verify_ssl"],
    dry_run: bool = OPTIONS["dry_run"],
    output_path: Path = OPTIONS["output_path"],
    _verbosity: LogLevel = OPTIONS["verbosity"],
    tags: list[str] = OPTIONS["tags"],
):
    """
    Walk through the specified directory (recursively) and attempt to submit all json files to LocalDB as the QC measurement

    Given a path to a directory with the output files, the script will recursively
    search the directory and upload all files with the `.json` extension. Supply the
    option `--dry-run` to see which files the script finds without uploading to
    localDB.

    Args:
        path (str or pathlib.Path): root directory to walk through
        host (str): localDB server host
        port (int): localDB server port
        out  (str): analysis output result json file path to save in the local host

    Returns:
        None: The files are uploaded to localDB.
    """

    log.addHandler(
        logging.FileHandler(Path(output_path).parent.joinpath("output_upload.log"))
    )

    log.info("Searching candidate RAW json files...")

    # Allow user to submit single file or directory
    if measurement_path.is_dir():
        flist = list(measurement_path.glob("*.json"))
    elif measurement_path.is_file():
        if measurement_path.suffix == ".json":
            flist = [measurement_path]
        else:
            log.error(
                "The file you are trying to upload (%s) is not a json file! Please upload the measurement json output file, or a path to the directory containing the measurement output json files.",
                measurement_path,
            )
            return
    else:
        log.error(
            "Input measurement path (%s) is not recognized as a json file or path to directory containing json file - please check!",
            measurement_path,
        )
        return

    schema = json.loads(
        (mqdt_data / "schema_measurement.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)

    pack = []
    for path in flist:
        log.info("  - %s", path)
        with path.open(encoding="utf-8") as fpointer:
            meas_data = json.load(fpointer)

            # Perform some basic checks on data before uploading
            if len(meas_data) == 0:
                log.warning("%s is empty - please check!", path)
                continue

            errors = list(validator.iter_errors(meas_data))
            if errors:
                log.error(
                    "The provided measurement (%s) does not adhere to the common schema.",
                    path,
                )
            for error in sorted(errors, key=relevance):
                log.error(error.message)
            if errors:
                continue

            pack.extend(meas_data)

    if not pack:
        log.error("No valid results were found for uploading. Aborting.")
        raise typer.Exit(1)

    validator.validate(pack)

    log.info("Extracted %d tests from %d input files.", len(pack), len(flist))
    log.info("==> Submitting RAW results pack...")

    if not dry_run:
        try:
            url = f"{protocol.value}://{host}:{port}/localdb/qc_uploader_post"
            if tags:
                tags_str = ",".join(tags)
                url += f"?tags={tags_str}"

            response = requests.post(
                url,
                json=pack,
                timeout=120,
                verify=verify_ssl,
            )
            response.raise_for_status()

            data = response.json()

            log.info(data)

        except Exception as err:
            log.error(response.content)
            log.exception("failure in uploading!")
            raise typer.Exit(1) from err

        log.info(
            "\nDone! LocalDB has accepted the following %d TestRun results", len(data)
        )
        for testRun in data:
            if testRun is None:
                log.info("A test run is already uploaded and will be skipped.")
                continue

            log.info(
                "Component: %s, Stage: %s, TestType: %s, QC-passed: %s",
                testRun["component"],
                testRun["stage"],
                testRun["testType"],
                testRun["passed"],
            )

        try:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                log.info("Saved the output TestRun to %s", output_path)

        except OSError:
            log.warning("Failed to saved the output TestRun to %s", output_path)

            kwargs = {"delete": False, "encoding": "utf-8"}
            if sys.version_info >= (3, 12):
                kwargs["delete_on_close"] = False
            with NamedTemporaryFile(**kwargs) as f:
                json.dump(data, f, indent=4)
                log.info("Saved the output TestRun to %s", f.name)


if __name__ == "__main__":
    typer.run(main)
