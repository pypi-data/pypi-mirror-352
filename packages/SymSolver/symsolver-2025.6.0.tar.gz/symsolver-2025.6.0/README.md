# SymSolver

Symbolic Solver for system of equations, system of linear differential equations, first order plane wave perturbation dispersion relation.

## Getting Started - Using the Code

Once you have followed the installation steps below, getting started is as simple as:
```python
import SymSolver as ss
x, y = ss.symbols(['x', 'y'])
z = x + y
str(z)
>>> 'x + y'
# And, you should check if your coding environment is compatible with in-line rendering by trying:
z   # or z.view()
>>> #rendered math text for x + y, if your environment can handle it.
```

## Getting Started - Examples
- The [AcousticWaves.ipynb](AcousticWaves.ipynb) is a great way to get started and see what SymSolver can do.
- In the future, more examples may be added.

## Getting Started - Installation

You can install the latest release via pip:
```bash
pip install symsolver
```

Or you can install directly from git
```bash
cd desired_directory
git clone https://gitlab.com/Sevans7/symsolver choose_a_name_for_local_repo
cd choose_a_name_for_local_repo
pip install -e .
```

Notes:
- `desired_directory` can be anywhere on your machine.
- You can choose whatever name you want for the local repo. I recommend `SymSolver`.
- The `-e` tells to install in development mode, so if you make changes they can be applied without re-installing.




