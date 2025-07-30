# tfbi_theory

**tfbi_theory** solves the linear theory of the Thermal Farley-Buneman Instability (TFBI).


## Examples

(1) Solve TFBI theory given physical parameters (`ds0`).

```python
import tfbi_theory as tt
ds0 = xr.Dataset(...)  # provide a Dataset with all required physical values...
kp = tt.kPickerLowres(ds0)
dsk = kp.get_ds()   # copy of ds0, but with ds['k'] = k from kPicker.
drel = tt.TfbiDisprelC.from_ds(dsk)
dsR = drel.solve()  # copy of dsk, but with ds['omega'] = solution to TFBI theory!
```


(2) Solve TFBI theory at values from a PlasmaCalculator object from [PlasmaCalcs](https://pypi.org/project/PlasmaCalcs/)

```python
import tfbi_theory as tt
import PlasmaCalcs as pc
cc = ... # any PlasmaCalculator object from PlasmaCalcs.
ds0 = cc.tfbi_ds()  # calls the PlasmaCalculator to load all required values
kp = tt.kPickerLowres(ds0)
dsk = kp.get_ds()   # copy of ds0, but with ds['k'] = k from kPicker.
drel = tt.TfbiDisprelC.from_ds(dsk)
dsR = drel.solve()  # copy of dsk, but with ds['omega'] = solution to TFBI theory!
```


(3) Solve TFBI theory at values from a PlasmaCalculator object from [PlasmaCalcs](https://pypi.org/project/PlasmaCalcs/) (simplified)
```python
import PlasmaCalcs as pc
cc = ... # any PlasmaCalculator object from PlasmaCalcs.
solver = cc.tfbi_solver()  # see help(solver) for more details.
solver.solve()
```

## Installation

You can install the latest release via pip:
```bash
pip install tfbi_theory
```

Or you can install directly from git:
```bash
cd directory_where_you_want_this_code_to_be_installed
git clone https://gitlab.com/Sevans7/tfbi_theory
cd tfbi_theory  # into the directory where the pyproject.toml can be found.
pip install -e .   # you can drop the "-e" if you will never edit tfbi_theory.
```


## License
Licensed under the MIT License; see also: LICENSE

## Project status
Completed, more or less. Not really under active development.

## Contributing
If you are interested in contributing, please feel free to reach out.
I might be happy to discuss or work with you, depending on your goals and ideas.
However, I am not actively looking for contributions at this time;
the relevant project has been completed and I am not planning to further improve the code at this point.

If I am unavailable or you prefer to just get started, please feel free to instead just create your own fork of the code!
