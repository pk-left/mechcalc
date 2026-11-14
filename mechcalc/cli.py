"""Command-line interface.

    mechcalc convert 10 kN lbf
    mechcalc units
    mechcalc shaft --torque 500 --tau 40e6
    mechcalc power --torque 50 --rpm 1450
    mechcalc pipe --length 100 --diameter 0.05 --velocity 1.5 --material "Commercial steel"
"""

from __future__ import annotations

import argparse

from . import fluids, machines, solids
from .units import convert, list_units


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="mechcalc", description="Mechanical engineering calculator")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("convert", help="convert a value between units")
    c.add_argument("value", type=float)
    c.add_argument("from_unit")
    c.add_argument("to_unit")

    sub.add_parser("units", help="list every supported unit")

    s = sub.add_parser("shaft", help="minimum solid shaft diameter for a torque")
    s.add_argument("--torque", type=float, required=True, help="N.m")
    s.add_argument("--tau", type=float, required=True, help="allowable shear stress, Pa")

    w = sub.add_parser("power", help="power from torque and speed")
    w.add_argument("--torque", type=float, required=True, help="N.m")
    w.add_argument("--rpm", type=float, required=True)

    f = sub.add_parser("pipe", help="pressure drop in a pipe (water at 20 C)")
    f.add_argument("--length", type=float, required=True, help="m")
    f.add_argument("--diameter", type=float, required=True, help="m")
    f.add_argument("--velocity", type=float, required=True, help="m/s")
    f.add_argument("--material", default="Commercial steel", choices=list(fluids.ROUGHNESS))

    a = p.parse_args(argv)
    try:
        if a.cmd == "convert":
            print(f"{a.value:g} {a.from_unit} = {convert(a.value, a.from_unit, a.to_unit):.6g} {a.to_unit}")
        elif a.cmd == "units":
            for q, units in list_units().items():
                print(f"{q:>14}: {', '.join(units)}")
        elif a.cmd == "shaft":
            d = solids.shaft_diameter_for_torque(a.torque, a.tau)
            print(f"Minimum diameter: {d * 1000:.2f} mm")
        elif a.cmd == "power":
            P = machines.power_from_torque(a.torque, a.rpm)
            print(f"Power: {P / 1000:.3f} kW ({convert(P, 'W', 'hp'):.2f} hp)")
        elif a.cmd == "pipe":
            w_ = fluids.WATER
            Re = fluids.reynolds(w_["rho"], a.velocity, a.diameter, w_["mu"])
            dp = fluids.pressure_drop(a.length, a.diameter, a.velocity, roughness=fluids.ROUGHNESS[a.material])
            print(f"Re = {Re:,.0f} ({fluids.flow_regime(Re)})")
            print(f"Pressure drop = {dp / 1000:.2f} kPa  (head loss {dp / (w_['rho'] * fluids.G):.2f} m)")
    except ValueError as e:
        p.error(str(e))


if __name__ == "__main__":
    main()
