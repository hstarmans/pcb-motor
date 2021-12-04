# PCB Motors

Packages to generate a PCB motor, Carl Bugeja style, for KiCad using Python

## History

Carl Bugeja shared several projects where eletric motors are made directly using PCBs,
see [Hackaday](https://hackaday.io/CarlBugeja), [Youtube](https://www.youtube.com/c/CarlBugeja)
Drawing these circuits can be a pain. The idea is that this scripts draws them directly and gives an
estimate for the coil resistance, magnetic field strength and heating.
Note, I am mainly interested in PCB motors to spin prisms.

## Install
Install poetry and python
```console
sudo apt install python3 python3-pip
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```
Use poetry to install the dependencies in pyproject.toml
```console
poetry install
```
Change parameters in the script and run it
```console
poetry run python spiral.py
```
The script modifies the base_kicad_pcb and creates a spiral.kicad_pcb.
This can be opened with KiCad and should contain the motor.
This design can be attached to another pcb via Kicad PCB import method.
Note, this feature is only available if KiCad PCB is run in standalone mode.
