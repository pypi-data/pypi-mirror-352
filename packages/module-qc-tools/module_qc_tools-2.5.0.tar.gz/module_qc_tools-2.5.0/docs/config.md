<style type="text/css">
/* make sure we don't wrap first column of tables on this page */
table tr td:first-of-type {
    text-wrap: nowrap;
}
</style>

# Configuration and external commands

All the configuration/settings are defined in two json files: one for the
hardware and one for the measurements. The hardware config is specific to the
site and needs to be modified, but the default measurement config should not
modified when running standard module QC. Examples are provided in
`$(module-qc-tools --prefix)/configs/`, such as:

- `hw_config_example_merged_vmux_itkpixv2.json`
- `meas_config.json`

!!! note

    There are 4 example hardware configs for the different combinations of V1 or V2 modules and a merged or separate VMUX:

    - `hw_config_example_merged_vmux_itkpixv2.json`
    - `hw_config_example_merged_vmux_v1.json`
    - `hw_config_example_separate_vmux_itkpixv2.json`
    - `hw_config_example_separate_vmux_v1.json`

    The only difference between the `_v1.json` hw_config and the `_itkpixv2.json` lies in the paths for the chip-specific `lpm_digitalscan` and `read_ringosc_exe`. For more info see below.

??? abstract "reference json configuration"

    ```json title="$(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux_itkpixv2.json"
    --8<-- "hw_config_example_merged_vmux_itkpixv2.json"
    ```
    ```json title="$(module-qc-tools --prefix)/configs/meas_config.json"
    --8<-- "meas_config.json"
    ```

The major blocks (e.g. `yarr`, `power_supply`, `multimeter`, `ntc`) correspond
to how the scripts will communicate with the module via YARR and how they will
communicate with the lab equipment. Each of these blocks are explained in the
following sections. The `task` block specifies the settings of each scan
performed by the scripts, and will be explained in
[measurements](measurements.md).

## Hardware Configuration

### yarr

The `yarr` block specifies the path to the `YARR` repository as well as the
corresponding YARR configuration files.

**Configuration settings**

| Name                   | Description                                                                                                                                                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run_dir`              | path (relative or absolute) to the directory where `YARR` commands should be run                                                                                                                                                    |
| `controller`           | path (relative to `run_dir` or absolute) to the controller file                                                                                                                                                                     |
| `scanConsole_exe`      | path (relative to `run_dir` or absolute) to the `scanConsole` executable                                                                                                                                                            |
| `write_register_exe`   | path (relative to `run_dir` or absolute) to the `write_register` executable                                                                                                                                                         |
| `read_register_exe`    | path (relative to `run_dir` or absolute) to the `read_register` executable                                                                                                                                                          |
| `read_adc_exe`         | path (relative to `run_dir` or absolute) to the `read_adc` executable                                                                                                                                                               |
| `switchLPM_exe`        | path (relative to `run_dir` or absolute) to the `switchLPM` executable                                                                                                                                                              |
| `lpm_digitalscan`      | path (relative to `run_dir` or absolute) to the low-power mode digital scan in YARR; for ITkPix v2, make sure that the path points to the correct scan config directory, e.g. `"configs/scans/itkpixv2/lpm_digitalscan.json"`       |
| `read_ringosc_exe`     | path (relative to `run_dir` or absolute) to the `Rd53bReadRingosc` or `Itkpixv2ReadRingosc` executable in YARR; for ITkPix v2, make sure the path points to the executable for the correct chip, e.g. `"./bin/Itkpixv2ReadRingosc"` |
| `eyeDiagram_exe`       | path (relative to `run_dir` or absolute) to the `eyeDiagram` executable in YARR                                                                                                                                                     |
| `dataMergingCheck_exe` | path (relative to `run_dir` or absolute) to the `dataMergingCheck` executable in YARR                                                                                                                                               |
| `success_code`         | exit status that indicates success. The default is 0 besides `configure`, which has exit status 1 for success. The user do not need to set the `success_code` as the default in QC software is synchronized with YARR.              |

### power_supply

The `power_supply` block specifies the path and the commands for handling the
low voltage power supply

**Configuration settings**

| Name                  | Description                                                                                                                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run_dir`             | path (relative or absolute) to the directory where `power_supply` commands should be run                                                                                                                                                    |
| `on_cmd`              | command to turn on the power supply with specified voltage and current. Use the syntax `{v}` and `{i}` to represent the voltage and current that are to be given as input arguments                                                         |
| `off_cmd`             | command to turn off the power supply                                                                                                                                                                                                        |
| `set_cmd`             | command to set voltage and current for power supply. Use the syntax `{v}` and `{i}` to represent the voltage and current that are to be given as input arguments                                                                            |
| `getI_cmd`            | command to inquire the set current of the power supply. This command shall return a std output which represents the value of the current (float in the unit of [A]). For example, when I = 5.2A, `getI_cmd` returns std output = `5.2`.     |
| `getV_cmd`            | command to inquire the set voltage of the power supply. This command shall return a std output which represents the value of the voltage (float in the unit of [V]). For example, when V = 1.8V, `getV_cmd` returns std output = `1.8`.     |
| `measI_cmd`           | command to measure the output current of the power supply. This command shall return a std output which represents the value of the current (float in the unit of [A]). For example, when I = 5.2A, `measI_cmd` returns std output = `5.2`. |
| `measV_cmd`           | command to measure the output voltage of the power supply. This command shall return a std output which represents the value of the voltage (float in the unit of [V]). For example, when V = 1.8V, `measV_cmd` returns std output = `1.8`. |
| `n_try`               | number of re-tries in case the script fails to read from the power supply                                                                                                                                                                   |
| `checkTarget_timeout` | after each `set_cmd` call, `measI_cmd` is called to check if the target is reached, if not after `checkTarget_timeout` (in sec.), an exception is raised                                                                                    |
| `success_code`        | exit status that indicates success. The default is 0.                                                                                                                                                                                       |

### high_voltage

Similar to the `power_supply` block, the `high_voltage` block specifies the path
and the commands for handling the high voltage power supply needed for leakage
current vs. bias voltage (IV) measurements.

**Configuration settings**

| Name                  | Description                                                                                                                                                                                                                                                                                                                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ramp_cmd`            | (optional) command to ramp the high voltage to the target value without measuring. If no command is available or provided, module-qc-tools will use its internal ramp function.                                                                                                                                                                                                                                  |
| `getI_cmd`            | command to measure the leakage current of the high voltage. This command shall return a std output which represents the value of the current (float in the unit of [A]). For example, when I = 1uA, `getI_cmd` returns std output = `0.000001`.                                                                                                                                                                  |
| `polarity`            | indicator if normal polarity (default 1) or reverse polarity (-1) is used. Can also take a command that returns a value, e.g. `"polarity": "echo 1"`. For power supplies that accept and output both positive and negative values of the bias voltage, the polarity is `1`. For power supplies that only accept and output a single polarity, this setting is `-1` and the wiring should be adapted accordingly. |
| `checkTarget_timeout` | after each `set_cmd` call, `measV_cmd` is called to check if the target is reached, if not after `checkTarget_timeout` (in sec.), an exception is raised                                                                                                                                                                                                                                                         |

### multimeter

The `multimeter` block specifies the path and the commands for handling the
multimeter

**Configuration settings**

| Name           | Description                                                                                                                                                                                                                                                                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run_dir`      | path (relative or absolute) to the directory where `multimeter` commands should be run                                                                                                                                                                                                                                                          |
| `dcv_cmd`      | list of commands to measure voltage from the multimeter. Each command corresponds to a single multimeter channel (only the used channels need to be listed). Each command returns a std output which represents the value of measured voltage (float in the unit of [V]). For example, when V = 0.352V, `dcv_cmd` returns std output = `0.352`. |
| `n_try`        | number of re-tries in case the script fails to read from the multimeter                                                                                                                                                                                                                                                                         |
| `success_code` | exit status that indicates success. The default is 0.                                                                                                                                                                                                                                                                                           |

### ntc

The `ntc` block specifies the path and the commands for handling the NTC

**Configuration settings**

| Name           | Description                                                                                                                                                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run_dir`      | path (relative or absolute) to the directory where `ntc` commands should be run                                                                                                                                                     |
| `cmd`          | command to measure temperature from the module NTC. The command returns a std output which represents the value of measured temperature (float in the unit of [C]). For example: when T = 36.2C, `cmd` returns std output = `36.2`. |
| `n_try`        | number of re-tries in case the script fails to read from the ntc                                                                                                                                                                    |
| `success_code` | exit status that indicates success. The default is 0.                                                                                                                                                                               |

### Humidity Reading

The `hrc` block specifies the path and the commands for handling the humidity
reading

**Configuration settings**

| Name             | Description                                                                                                                                                                                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `run_dir`        | path (relative or absolute) to the directory where the script for humidity reading `ReadHR` should be run                                                                                                                                                                      |
| `cmd`            | command to read the humidity (relative humidity, RH) from InfluxDB. The command returns a std output which represents the value of measured humidity (float rrepresenting the percentage realitive humidity). For example: when RH = 2.15%, `cmd` returns std output = `2.15`. |
| `share_vmux`     | whether Vmux channels are shorted on the data adapter card or not                                                                                                                                                                                                              |
| `v_mux_channels` | multimeter channel to measure the Vmux for each chip (correspond to each element in the dcv_cmd in the multimeter block)                                                                                                                                                       |
| `n_try`          | number of re-tries in case the script fails to read from the ntc                                                                                                                                                                                                               |
| `success_code`   | exit status that indicates success. The default is 0.                                                                                                                                                                                                                          |

The script to read the humidity data from InfluxDB can have a format similar to
the following:

    ```python title="ReadHR.py"
    from influxdb import InfluxDBClient
    import re
    import sys

    client = InfluxDBClient(
        host="your.host.number",
        port=8086,
        username="your_username",
        password="your_password",
        ssl=False,
    )
    client.switch_database("DB1")

    query = 'select mean("HR_variable_name_mqtt") from "autogen"."mqtt_consumer" where "your_topic_tag" = \'/your_mqtt_topic_name\' and time > now() -1m ORDER BY time DESC LIMIT 1'

    result = client.query(query)

    if not result.error:
        if str(result) != "ResultSet({})":
            mystring = str(result.raw)
            if len(mystring) > 0:
                chunks = re.split(",", mystring)
                hum = re.split("]", chunks[len(chunks) - 1])
                print(hum[0])
                sys.exit(0)

    sys.exit(1)
    ```

## Measurement Configuration

### tasks

The `tasks` block starts with the `GENERAL` section that specifies the
layer-dependent power settings:

**Configuration settings**

| Name       | Description                                                                                                                |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| `v_max`    | the voltage to be set to the power supply (i.e. the max voltage since the power supply should operate in constant current) |
| `i_config` | the current at which the module should be configured                                                                       |

The main part of the `tasks` block is to specify all
[measurements](measurements.md).
