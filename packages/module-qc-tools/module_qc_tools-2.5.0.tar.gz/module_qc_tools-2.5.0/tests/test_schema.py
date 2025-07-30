from __future__ import annotations

import json

import jsonschema
import module_qc_data_tools as mqdt
import pytest


@pytest.fixture(scope="session")
def schema():
    return json.loads((mqdt.utils.datapath / "schema_measurement.json").read_text())


@pytest.mark.parametrize(
    ("measurement"),
    [
        "cutter_pcb_tab.json",
        "cutter_pcb_tab_BAD.json",
    ],
)
def test_measurement(measurement, schema, datadir):
    output = json.loads(datadir.joinpath(measurement).read_text())

    if "_BAD" in measurement:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(output, schema)
    else:
        jsonschema.validate(output, schema)
