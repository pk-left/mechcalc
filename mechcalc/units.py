"""Unit conversion for common mechanical-engineering quantities.

Every unit is stored as a factor that converts it TO the SI base unit of its quantity.
Temperature is handled separately because its scales have offsets.

    >>> convert(1, "in", "mm")
    25.4
    >>> convert(100, "psi", "kPa")
    689.4757...
"""

from __future__ import annotations

G0 = 9.80665  # standard gravity, m/s^2
LBF = 4.4482216152605  # N

UNITS: dict[str, dict[str, float]] = {
    "length": {"m": 1, "km": 1e3, "cm": 1e-2, "mm": 1e-3, "um": 1e-6, "in": 0.0254, "ft": 0.3048,
               "yd": 0.9144, "mi": 1609.344},
    "area": {"m2": 1, "cm2": 1e-4, "mm2": 1e-6, "in2": 0.0254**2, "ft2": 0.3048**2, "ha": 1e4},
    "volume": {"m3": 1, "L": 1e-3, "mL": 1e-6, "cm3": 1e-6, "in3": 0.0254**3, "ft3": 0.3048**3,
               "gal": 3.785411784e-3},
    "mass": {"kg": 1, "g": 1e-3, "t": 1e3, "lb": 0.45359237, "oz": 0.028349523125},
    "force": {"N": 1, "kN": 1e3, "MN": 1e6, "kgf": G0, "lbf": LBF, "kip": 1e3 * LBF},
    "pressure": {"Pa": 1, "kPa": 1e3, "MPa": 1e6, "GPa": 1e9, "bar": 1e5, "atm": 101325,
                 "psi": LBF / 0.0254**2, "ksi": 1e3 * LBF / 0.0254**2, "mmHg": 133.322387415,
                 "N/mm2": 1e6},
    "energy": {"J": 1, "kJ": 1e3, "MJ": 1e6, "Wh": 3600, "kWh": 3.6e6, "cal": 4.184, "kcal": 4184,
               "BTU": 1055.05585262, "ft.lbf": 0.3048 * LBF},
    "power": {"W": 1, "kW": 1e3, "MW": 1e6, "hp": 745.69987158227, "PS": 735.49875,
              "BTU/h": 1055.05585262 / 3600},
    "torque": {"N.m": 1, "kN.m": 1e3, "N.mm": 1e-3, "lbf.ft": LBF * 0.3048, "lbf.in": LBF * 0.0254},
    "speed": {"m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "ft/s": 0.3048, "knot": 1852 / 3600},
    "angular speed": {"rad/s": 1, "rpm": 2 * 3.141592653589793 / 60, "deg/s": 3.141592653589793 / 180},
    "density": {"kg/m3": 1, "g/cm3": 1e3, "lb/ft3": 0.45359237 / 0.3048**3},
}

TEMPERATURE = ("C", "F", "K", "R")


def quantity_of(unit: str) -> str:
    if unit in TEMPERATURE:
        return "temperature"
    for q, table in UNITS.items():
        if unit in table:
            return q
    raise ValueError(f"Unknown unit '{unit}'. Run `mechcalc units` to see the list.")


def convert(value: float, from_unit: str, to_unit: str) -> float:
    q1, q2 = quantity_of(from_unit), quantity_of(to_unit)
    if q1 != q2:
        raise ValueError(f"Cannot convert {q1} ({from_unit}) to {q2} ({to_unit}).")
    if q1 == "temperature":
        return _from_kelvin(_to_kelvin(value, from_unit), to_unit)
    table = UNITS[q1]
    return value * table[from_unit] / table[to_unit]


def _to_kelvin(v: float, u: str) -> float:
    return {"K": v, "C": v + 273.15, "F": (v - 32) * 5 / 9 + 273.15, "R": v * 5 / 9}[u]


def _from_kelvin(k: float, u: str) -> float:
    return {"K": k, "C": k - 273.15, "F": (k - 273.15) * 9 / 5 + 32, "R": k * 9 / 5}[u]


def list_units() -> dict[str, list[str]]:
    out = {q: list(t) for q, t in UNITS.items()}
    out["temperature"] = list(TEMPERATURE)
    return out
