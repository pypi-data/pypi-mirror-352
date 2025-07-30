<style type="text/css">
/* make sure we don't wrap first column of tables on this page */
table tr td:first-of-type {
    text-wrap: nowrap;
}
</style>

# Measurements

## Overview

An overview of the steps in the module QC procedure is documented in the
[Electrical specification and QC procedures for ITkPixV1.1 modules](https://gitlab.cern.ch/atlas-itk/pixel/module/itkpix-electrical-qc/)
document and in
[this spreadsheet](https://docs.google.com/spreadsheets/d/1qGzrCl4iD9362RwKlstZASbhphV_qTXPeBC-VSttfgE/edit#gid=989740987).
Each measurement is performed with one script. All scripts assume that the
modules to be tested are already powered on.

### Time Estimates

The following were measured using an old Keithley multimeter with
[v2.4.2](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.4.2)
running `run-full-qc`. The analysis includes uploading to localDB and
downloading the results.

| Measurement                | Duration (hh:mm:ss) |
| -------------------------- | ------------------- |
| update k-shunt             | 00:00:01            |
| eye diagram                | 00:00:05            |
| core column scan           | 00:00:27            |
| **ADC calib**              | **00:02:32**        |
| analysis                   | 00:00:09            |
| update chip config         | 00:00:04            |
| **Analog Readback**        | **00:30:47**        |
| analysis                   | 00:00:14            |
| update chip config         | 00:00:04            |
| **SLDO VI**                | **00:19:30**        |
| analysis                   | 00:00:12            |
| update chip config         | 00:00:02            |
| **Vcal calib**             | **00:05:47**        |
| analysis                   | 00:00:10            |
| update chip config         | 00:00:04            |
| **Injection Cap.**         | **00:02:29**        |
| analysis                   | 00:00:09            |
| update chip config         | 00:00:04            |
| **LP Mode**                | **00:06:51**        |
| analysis                   | 00:00:09            |
| update chip config         | 00:00:01            |
| **DATA_TRANSMISSION**      | **00:00:35**        |
| analysis                   | 00:00:09            |
| update chip config         | 00:00:02            |
| **Minimum Health Test**    | **00:06:40**        |
| clear chip config          | 00:00:00            |
| **Tuning**                 | **00:13:09**        |
| **Pixel Failure Analysis** | **00:09:02**        |
| -------------------------- | ------------------- |
| _total_                    | _01:39:29_          |

### Local Filesystem

The output of the measurements follows the structure below:

```
Measurements/
├── ADC_CALIBRATION
│   └── 2024-06-18_221312
│       ├── 20UPGXM1234567.json
│       └── output.log
├── <test_type>
│   ├── <timestamp:YYYY-MM-DD_HHMMSS>
│   │   ├── <identifier:chipName or ModuleSN>.json
│   │   └── output.log
│   └── ...
└── ...
    ├── ...
    │   └── ...
    └── ...
        └── ...
```

The test-type of each measurement is the corresponding test-mode used in the
Production Data Base. The naming of each measurement script is chosen to be the
same as the test-type. The timestamp is chosen to be the start time of the
measurement.

### Schema

The schema for the output json files is checked based on the schema files
specified in the folder `schema`. To run the common schema check for all test
outputs, do:

```
check-jsonschema [path to output json files] --schemafile $(mqdt --prefix)/schema_measurement.json

```

To run the further schema check for a specific test output, do:

```
check-jsonschema [path to output json files] --schemafile $(module-qc-tools
--prefix)/schema/[qc_task].json
```

??? example "Example (with the emulator output files)"

    ```
    check-jsonschema emulator/outputs/SLDO_reference/<timestamp>/chip1.json
    --schemafile $(mqdt --prefix)/schema_measurement.json check-jsonschema
    emulator/outputs/SLDO_reference/<timestamp>/chip1.json --schemafile $(module-qc-tools
    --prefix)/schema/SLDO.json
    ```

### Uploading measurements to localDB

Please use `mqdbt` to upload measurements to localDB.

## Sensor IV Measure

- [`mqt measurement iv-measure`](reference/cli.md#mqt-measurement-iv-measure)
- [`module-qc-tools measurement iv-measure`](reference/cli.md#mqt-measurement-iv-measure)
- [`measurement-IV-MEASURE`](reference/cli.md#mqt-measurement-iv-measure)

This script will test the sensor leakage current vs. reverse bias voltage
(`task = IV_MEASURE`) as specified in the input configuration json file (i.e.
'$(module-qc-tools --prefix)/configs/meas_config.json').

**Configuration settings**

| Name            | Description                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `v_min`         | the starting voltage of this measurement                                                                              |
| `v_max`         | the end voltage of this measurement                                                                                   |
| `i_max`         | the current compliance throughout the measurement                                                                     |
| `n_points`      | how many points should be measured depending on the required voltage steps (i.e. 1V for 3D and 5V for planar modules) |
| `settling_time` | delay in seconds between setting a bias voltage and reading the current                                               |

??? example

    ```
    measurement-IV-MEASURE -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_LP.json
    ```

??? example "emulator"

    ```
    measurement-IV-MEASURE -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs
    ```

## Eye Diagram

The eye diagram scan is a YARR executable. It updates the controller
configuration with the optimal sampling delay setting to ensure good data
transmission, and is dependent on the setup, incl. cables and modules. Thus it
should be run before any electrical QC test and repeated whenever the setup is
changed.

For more information please refer to the
[YARR docs](https://yarr.web.cern.ch/yarr/rd53b/#data-transmission)

??? example

    ```
    cd ~/Yarr
    ./bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

## ADC Calibration

- [`mqt measurement adc-calibration`](reference/cli.md#mqt-measurement-adc-calibration)
- [`module-qc-tools measurement adc-calibration`](reference/cli.md#mqt-measurement-adc-calibration)
- [`measurement-ADC-CALIBRATION`](reference/cli.md#mqt-measurement-adc-calibration)

This script will run the ADC calibration (`task = ADC_CALIBRATION`) as specified
in the input configuration json file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json').

**Configuration settings**

| Name           | Description                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `MonitorV`     | list of Vmux channels to be measured                                                                                             |
| `InjVcalRange` | the range of the calibration injection circuit(1: a large range and 0: a small range i.e. half the large range but a finer step) |
| `Range`        | the DACs scan range ["start", "stop", "step"]                                                                                    |

??? example

    ```
    measurement-ADC-CALIBRATION -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-ADC-CALIBRATION -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```

## Analog readback

- [`mqt measurement analog-readback`](reference/cli.md#mqt-measurement-analog-readback)
- [`module-qc-tools measurement analog-readback`](reference/cli.md#mqt-measurement-analog-readback)
- [`measurement-ANALOG-READBACK`](reference/cli.md#mqt-measurement-analog-readback)

This script will measure all internal voltages available through VMUX and IMUX,
measure the chip temperature, and measure VDDA/VDDD/ROSC vs Trim. channels. The
scan settings are defined in the `task = ANALOG_READBACK` block of the input
configuration file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json'). The NTC needs to be set in order to run
this script, so that the temperature can be read.

**Configuration settings**

| Name                    | Description                                                    |
| ----------------------- | -------------------------------------------------------------- |
| `v_mux`                 | list of Vmux channels to be measured                           |
| `i_mux`                 | list of Imux channels to be measured                           |
| `v_mux_ntc`             | list of Vmux channels to be measured for ntc temperature       |
| `i_mux_ntc`             | list of Imux channels to be measured for ntc temperature       |
| `v_mux_tempsens`        | list of Vmux channels to be measured for 3 temperature sensors |
| `MonSensSldoDigSelBias` | Bias 0 and 1 for MOS sensor near digital SLDO                  |
| `MonSensSldoAnaSelBias` | Bias 0 and 1 for MOS sensor near analog SLDO                   |
| `MonSensAcbSelBias`     | Bias 0 and 1 for MOS sensor near center                        |
| `MonSensSldoDigDem`     | Dem 0-15 for MOS sensor near digital SLDO                      |
| `MonSensSldoAnaDem`     | Dem 0-15 for MOS sensor near analog SLDO                       |
| `MonSensAcbDem`         | Dem 0-15 for MOS sensor near center                            |
| `SldoTrimA`             | Sldo analog Trim 0-15                                          |
| `SldoTrimD`             | Sldo digital Trim 0-15                                         |

??? example

    ```
    measurement-ANALOG-READBACK -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-ANALOG-READBACK -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs
    ```

## SLDO VI

- [`mqt measurement sldo`](reference/cli.md#mqt-measurement-sldo)
- [`module-qc-tools measurement sldo`](reference/cli.md#mqt-measurement-sldo)
- [`measurement-SLDO`](reference/cli.md#mqt-measurement-sldo)

This script will run the VI scans (`task = SLDO`) as specified in the input
configuration json file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json').

**Configuration settings**

| Name       | Description                                                                             |
| ---------- | --------------------------------------------------------------------------------------- |
| `i_min`    | the minimum current of the VI scan                                                      |
| `i_max`    | the maximum current of the VI scan                                                      |
| `n_points` | how many points should be measured (equally spread between the max of the min currents) |
| `extra_i`  | extra current points to be measured                                                     |
| `v_mux`    | list of Vmux channels to be measured                                                    |
| `i_mux`    | list of Imux channels to be measured                                                    |

??? example

    ```
    measurement-SLDO -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-SLDO -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs
    ```

## VCal Calibration

- [`mqt measurement vcal-calibration`](reference/cli.md#mqt-measurement-vcal-calibration)
- [`module-qc-tools measurement vcal-calibration`](reference/cli.md#mqt-measurement-vcal-calibration)
- [`measurement-VCAL-CALIBRATION`](reference/cli.md#mqt-measurement-vcal-calibration)

This script will run the VCal calibration (`task = VCAL_CALIBRATION`) as
specified in the input configuration json file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json').

**Configuration settings**

| Name           | Description                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `InjVcalRange` | the range of the calibration injection circuit(1: a large range and 0: a small range i.e. half the large range but a finer step) |
| `MonitorV`     | two DACs VMUX assignments Vcal_med(8) and Vcal_high(7)                                                                           |
| `MonitorV_GND` | the GNDA VMUX assignment 30                                                                                                      |
| `Large_Range`  | the large DACs scan range ["start", "stop", "step"]                                                                              |
| `Small_Range`  | the small DACs scan range ["start", "stop", "step"]                                                                              |

??? example

    ```
    measurement-VCAL-CALIBRATION -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-VCAL-CALIBRATION -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```

## Injection Capacitance

- [`mqt measurement injection-capacitance`](reference/cli.md#mqt-measurement-injection-capacitance)
- [`module-qc-tools measurement injection-capacitance`](reference/cli.md#mqt-measurement-injection-capacitance)
- [`measurement-INJECTION-CAPACITANCE`](reference/cli.md#mqt-measurement-injection-capacitance)

This script will run the injection capacitance measurement
(`task = INJECTION_CAPACITANCE`) as specified in the input configuration json
file (i.e. '$(module-qc-tools --prefix)/configs/meas_config.json').

**Configuration settings**

| Name     | Description                          |
| -------- | ------------------------------------ |
| `n_meas` | number of measurements to perform    |
| `v_mux`  | list of Vmux channels to be measured |
| `i_mux`  | list of Imux channels to be measured |

??? example

    ```
    measurement-INJECTION-CAPACITANCE -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-INJECTION-CAPACITANCE -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```

## Low Power Mode

- [`mqt measurement lp-mode`](reference/cli.md#mqt-measurement-lp-mode)
- [`module-qc-tools measurement lp-mode`](reference/cli.md#mqt-measurement-lp-mode)
- [`measurement-LP-MODE`](reference/cli.md#mqt-measurement-lp-mode)

This script will run the low power mode test (`task = LP_MODE`) as specified in
the input configuration json file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json').

**Configuration settings**

| Name       | Description                                                                        |
| ---------- | ---------------------------------------------------------------------------------- |
| `v_max`    | the voltage to be set to the power supply specific to this measurement             |
| `i_config` | the current at which the module should be configured specific for this measurement |
| `v_mux`    | list of Vmux channels to be measured                                               |
| `i_mux`    | list of Imux channels to be measured                                               |

??? example

    ```
    measurement-LP-MODE -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_LP.json
    ```

??? example "emulator"

    ```
    measurement-LP-MODE -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```

## Overvoltage Protection

- [`mqt measurement overvoltage-protection`](reference/cli.md#mqt-measurement-overvoltage-protection)
- [`module-qc-tools measurement overvoltage-protection`](reference/cli.md#mqt-measurement-overvoltage-protection)
- [`measurement-OVERVOLTAGE-PROTECTION`](reference/cli.md#mqt-measurement-overvoltage-protection)

This script will test the Overvoltage Protection (OVP)
(`task = OVERVOLTAGE_PROTECTION`) as specified in the input configuration json
file (i.e. '$(module-qc-tools --prefix)/configs/meas_config.json').

**Configuration settings**

| Name       | Description                                                                        |
| ---------- | ---------------------------------------------------------------------------------- |
| `v_max`    | the voltage to be set to the power supply specific to this measurement             |
| `i_config` | the current at which the module should be configured specific for this measurement |
| `v_mux`    | list of Vmux channels to be measured                                               |
| `i_mux`    | list of Imux channels to be measured                                               |

??? example

    ```
    measurement-OVERVOLTAGE-PROTECTION -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_LP.json
    ```

??? example "emulator"

    ```
    measurement-OVERVOLTAGE-PROTECTION -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs
    ```

## Undershunt Protection

- [`mqt measurement undershunt-protection`](reference/cli.md#mqt-measurement-undershunt-protection)
- [`module-qc-tools measurement undershunt-protection`](reference/cli.md#mqt-measurement-undershunt-protection)
- [`measurement-UNDERSHUNT-PROTECTION`](reference/cli.md#mqt-measurement-undershunt-protection)

This script will test the Undershunt Protection (USP)
(`task = UNDERSHUNT_PROTECTION`) as specified in the input configuration json
file (i.e. '$(module-qc-tools --prefix)/configs/meas_config.json').

**Configuration settings**

| Name       | Description                                                                        |
| ---------- | ---------------------------------------------------------------------------------- |
| `v_max`    | the voltage to be set to the power supply specific to this measurement             |
| `i_config` | the current at which the module should be configured specific for this measurement |
| `v_mux`    | list of Vmux channels to be measured                                               |
| `i_mux`    | list of Imux channels to be measured                                               |

??? example

    ```
    measurement-UNDERSHUNT-PROTECTION -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_LP.json
    ```

??? example "emulator"

    ```
    measurement-UNDERSHUNT-PROTECTION -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs
    ```

## Data Transmission

- [`mqt measurement data-transmission`](reference/cli.md#mqt-measurement-data-transmission)
- [`module-qc-tools measurement data-transmission`](reference/cli.md#mqt-measurement-data-transmission)
- [`measurement-DATA-TRANSMISSION`](reference/cli.md#mqt-measurement-data-transmission)

This script will run the data transmission (`task = DATA_TRANSMISSION`) as
specified in the input configuration json file (i.e. '$(module-qc-tools
--prefix)/configs/meas_config.json').

**Configuration settings**

| Name          | Description                             |
| ------------- | --------------------------------------- |
| `MonitorV`    | list of VMUX channels to be set         |
| `DataMerging` | list of data merging modes to be tested |

??? example

    ```
    measurement-DATA-TRANSMISSION -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-DATA-TRANSMISSION -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```

## Long-term stability DCS

- [`mqt measurement long-term-stability-dcs`](reference/cli.md#mqt-measurement-long-term-stability-dcs)
- [`module-qc-tools measurement long-term-stability-dcs`](reference/cli.md#mqt-measurement-long-term-stability-dcs)
- [`measurement-LONG-TERM-STABILITY-DCS`](reference/cli.md#mqt-measurement-long-term-stability-dcs)

This adds the ability to run the long-term stability dcs measurement
(`task = LONG_TERM_STABILITY_DCS`) as specified in the input configuration json
file (i.e. '$(module-qc-tools --prefix)/configs/meas_config.json').

**Configuration settings**

| Name       | Description                                      |
| ---------- | ------------------------------------------------ |
| `duration` | total duration for the collection of data points |
| `period`   | time between data points                         |

??? example

    ```
    measurement-LONG-TERM-STABILITY-DCS -c $(module-qc-tools --prefix)/configs/hw_config_example_merged_vmux.json -m ~/module_data/20UPGR91301046/20UPGR91301046_L2_warm.json
    ```

??? example "emulator"

    ```
    measurement-LONG-TERM-STABILITY-DCS -c $(module-qc-tools --prefix)/configs/hw_config_emulator_merged_vmux.json -o emulator/outputs/
    ```
