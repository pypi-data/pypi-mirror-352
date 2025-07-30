# module-qc-tools history

---

All notable changes to module-qc-tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [2.5.0](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.5.0) - 2025-06-02 ## {: #mqt-v2.5.0 }

**_Changed:_**

- drop deprecated `importlib` dependency (!253)
- drop python 3.8 and update python version info (!250)
- Updated the durations of all QC tests in
  [measurements](measurements.md#time-estimates)(!248)
- reduce the AR duration by 40% compared to previous (back to the same as before
  !208) (!247)
- Update current (sigma) units in IV progress display (!229)
- Dropped `emulator-XYZ` executables in favor of `mqt emulator` (!232)
- Increased minimum supported python version to 3.8 (dropping 3.7) (!237)
- IV emulator with more realistic values than previous fit (!238)
- updated current for V2+V2BOM chips according to YTF recommendations (!242) !!!
  important

        Requires module-qc-data-tools v1.1.4rc6

**_Added:_**

- Check for module type when recording HV; add option if no HV is intended;
  error if HV not measurable for non-digital modules (!235)
- Record bias voltage, leakage current and module temperature during measurement
  (!214); requires `module-qc-data-tools`
  [v1.1.3](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-data-tools/-/tags/v1.1.3)
- Humidity measurement (!226)

  !!! important

        Requires adding a `hrc` block in the hardware config file:

        ```json
        "hrc": {

            "run_dir": "../Instruments",
            "cmd": "./ReadHR.py",
            "n_try": 0,
            "success_code": 0
        }
        ```

**_Fixed:_**

- Add protection against humidity measurements if the `hrc` block is not
  included in the config (!230)
- added support for `tags` in `yarr.run_scan`
- add `yarr` scan utilities for generic yarr scans as well as for MHT, TUN, PFA
  (!225)
- Added protection in long-term stability dcs test to check the L1/L2 power
  before running (!212)
- Refactored CLI to improve python-only interactions using [typing.Annotated][]
  (!232)

## [2.4.1](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.4.1) - 2025-03-25 ## {: #mqt-v2.4.1 }

**_Fixed:_**

- eye diagram parsing (!228)

## [2.4.0](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.4.0) - 2025-03-11 ## {: #mqt-v2.4.0 }

**_Changed:_**

- reduce number of steps in VCAL calibration (!215)
- increase voltage compliance during SLDO scan (!219)
- improve compatibility of mqt with Felix (!186)

**_Added:_**

- add BOM information to output of SLDO, LP and ADC calibration (!220)
- add ability to enable/disable LPM on targeted TX channels (!207)
- add data merging substest to data transmission test (!218)

  !!! important

      Requires update of the `yarr` section in the hardware config file:

      ```
      "dataMergingCheck_exe": "./bin/dataMergingCheck",
      ```

- add Iref trim information to output of the AR test (!221)
- add protection when ramping HV down (!211)
- CLI to retrieve input current based on chip version (!210)

**_Fixed:_**

- fix write register issue when running with separate vmux (!208)
- fixed number of points in SLDO (!213)

## [2.3.0](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.3.0) - 2024-07-12 ## {: #mqt-v2.3.0 }

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [2.2.8](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.2.8) - 2024-12-17 ## {: #mqt-v2.2.8 }

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [2.2.7](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.2.7) - 2024-10-03 ## {: #mqt-v2.2.7 }

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [2.2.6](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.2.6) - 2024-07-12 ## {: #mqt-v2.2.6 }

**_Changed:_**

- logging now uses `rich` and the formatting is a little different, and should
  be improved once `module-qc-data-tools` is updated (!166)
- refactored all measurements to be more pythonic and getting ready for v3
  (!153, !165, !173, !174)

**_Added:_**

- allow non-zero ADC ground counts (!152)
- `use_calib_adc` is added to all measurements (!156, !157)
- retry configure and read/write registers when communication is lost with
  module (!139)
- `LONG-TERM-STABILITY-DCS` measurement (!175, !176, !177, !178)

**_Fixed:_**

- hard-coded chip type (!105)
- emulator handles disabled chips (!162)
- `pandas` is removed, speeding up this package (!168)
- `hardware_control_base` is refactored to speed up emulator (!169)
- `pkg_resources` is deprecated (!172)

## [2.2.5](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.2.5) - 2024-07-12 ## {: #mqt-v2.2.5 }

Note: this version is skipped due to a packaging issue.

## [2.2.4](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/tags/v2.2.4) - 2024-04-30 ## {: #mqt-v2.2.4 }

First release for this documentation. (!171)

**_Changed:_**

- lower max current for L1 quads (!147)
- improved error handling when measurement uploads to localDB fails (!144)

**_Added:_**

- spec number argument to LP mode switch (!143)

**_Fixed:_**

- support for disabled chips (!145)
- data transmission test ensures correct power supply settings for
  voltage/current (!148)
- `switchLPM` works for more than 1 spec card (!149)
- clear registers when eyeDiagram is launched with the reconfiguration option
  (!150)
- values for emulator are integers (!151)
