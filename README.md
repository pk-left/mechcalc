# ⚙️ MechCalc

A small Python package, command-line tool and web app with the **unit conversions and formulas mechanical engineering students use every week**: stress and strain, torsion, buckling, heat transfer, pipe flow and gears.

I started it in my second year of Mechanical Engineering after typing the same formulas into a calculator over and over. It doesn't need any external libraries (the web app is optional), and the test suite checks every formula against textbook values.

## Install

```bash
git clone https://github.com/pk-left/mechcalc.git
cd mechcalc
pip install -e .            # installs the `mechcalc` command
pip install -e ".[app]"     # optional: also installs the web app's dependency
```

## Command line

```console
$ mechcalc convert 10 kN lbf
10 kN = 2248.09 lbf

$ mechcalc convert 100 C F
100 C = 212 F

$ mechcalc power --torque 50 --rpm 1450
Power: 7.592 kW (10.18 hp)

$ mechcalc shaft --torque 500 --tau 40e6
Minimum diameter: 39.93 mm

$ mechcalc pipe --length 100 --diameter 0.05 --velocity 1.5 --material "Commercial steel"
Re = 74,701 (turbulent)
Pressure drop = 50.61 kPa  (head loss 5.17 m)

$ mechcalc units            # list everything it can convert
```

## Web app

```bash
streamlit run app.py
```

The app has tabs for the unit converter, stress and strain (including Mohr's circle and von Mises), shaft sizing, Euler buckling, wall heat gain, pipe pressure drop and gear trains.

## Python library

```python
from mechcalc import convert, solids, thermo, fluids, machines

convert(1, "ksi", "MPa")                          # 6.894757
solids.shaft_diameter_for_torque(500, 40e6)       # 0.03993 m
solids.principal_stresses(80, -40, 25)            # (85.0, -45.0, 65.0)
solids.euler_buckling_load(200e9, solids.I_circle(0.02), L=1.0, K=2.0)

thermo.carnot_efficiency(T_hot=600, T_cold=300)   # 0.5
thermo.wall_heat_loss(24, 38, A=12, layers=[(0.2, 1.4)], h_in=8, h_out=25)

fluids.friction_factor(Re=1e5, roughness=4.5e-5, D=0.05)   # Colebrook equation
machines.gear_train([(20, 60), (15, 45)], rpm_in=1800, torque_in=10)
```

## What's inside

| Module | Contents |
|---|---|
| `units` | length, area, volume, mass, force, pressure/stress, energy, power, torque, speed, rpm, density, temperature (C, F, K, R) |
| `solids` | stress, strain, Young's modulus, thermal stress, I and J of common sections, flexure formula, torsion, angle of twist, shaft sizing, Euler buckling, factor of safety, principal stresses, von Mises |
| `thermo` | ideal gas, sensible heat, Carnot efficiency and COP, conduction, convection, radiation, composite walls |
| `fluids` | Reynolds number, flow regime, hydrostatic pressure, Torricelli, Colebrook friction factor, Darcy–Weisbach pressure drop, pump power, pipe roughness table |
| `machines` | power and torque, gear trains, belt speed and tension ratio, springs, natural frequency, bolt tightening torque |

All functions use **SI units** (N, m, Pa, W, K). Use `convert()` at the edges when you need other units.

## Tests

```bash
pip install pytest
pytest
```

The tests cover 23 cases, including known conversions (1 in = 25.4 mm, −40 °C = −40 °F), the Moody chart value for a smooth pipe, J = 2I for a circle, the Mohr's circle textbook example, and round trips such as sizing a shaft and checking that the stress equals the allowable value.

## Ideas for next versions

- [ ] Unit-aware inputs (e.g. `"10 kN"` strings)
- [ ] Standard I-beam and channel section tables
- [ ] Weld and bolt group calculations
- [ ] Publish to PyPI

## License

MIT © Dodou Njie (PK)
