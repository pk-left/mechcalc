"""Fluid mechanics. SI units."""

from __future__ import annotations

import math

G = 9.80665
WATER = {"rho": 998.0, "mu": 1.002e-3}  # at 20 C
AIR = {"rho": 1.204, "mu": 1.825e-5}  # at 20 C, 1 atm


def reynolds(rho: float, v: float, D: float, mu: float) -> float:
    """Re = rho v D / mu"""
    return rho * v * D / mu


def flow_regime(Re: float) -> str:
    """Pipe flow: laminar below 2300, turbulent above 4000."""
    if Re < 2300:
        return "laminar"
    return "transitional" if Re < 4000 else "turbulent"


def hydrostatic_pressure(depth: float, rho: float = WATER["rho"]) -> float:
    """Gauge pressure at a depth: p = rho g h  (Pa)"""
    return rho * G * depth


def flow_rate(v: float, D: float) -> float:
    """Q = v A for a round pipe  (m^3/s)"""
    return v * math.pi * D**2 / 4


def velocity_from_flow(Q: float, D: float) -> float:
    return Q / (math.pi * D**2 / 4)


def torricelli(head: float) -> float:
    """Speed of a jet from a tank (Bernoulli): v = sqrt(2 g h)"""
    return math.sqrt(2 * G * head)


def friction_factor(Re: float, roughness: float = 0.0, D: float = 1.0) -> float:
    """Darcy friction factor.

    Laminar: f = 64 / Re.  Turbulent: Colebrook equation solved by iteration,
    started from the Swamee-Jain approximation.  roughness and D in the same units.
    """
    if Re <= 0:
        raise ValueError("Reynolds number must be positive.")
    if Re < 2300:
        return 64 / Re
    rel = roughness / D
    f = 0.25 / math.log10(rel / 3.7 + 5.74 / Re**0.9) ** 2  # Swamee-Jain
    for _ in range(50):
        new = (-2 * math.log10(rel / 3.7 + 2.51 / (Re * math.sqrt(f)))) ** -2
        if abs(new - f) < 1e-12:
            break
        f = new
    return f


def pressure_drop(L: float, D: float, v: float, rho: float = WATER["rho"], mu: float = WATER["mu"],
                  roughness: float = 0.0) -> float:
    """Darcy-Weisbach pressure drop in a straight pipe: dp = f (L/D) rho v^2 / 2  (Pa)"""
    f = friction_factor(reynolds(rho, v, D, mu), roughness, D)
    return f * (L / D) * rho * v**2 / 2


def pump_power(Q: float, head: float, efficiency: float = 1.0, rho: float = WATER["rho"]) -> float:
    """Shaft power needed: P = rho g Q H / eta  (W)"""
    if not 0 < efficiency <= 1:
        raise ValueError("Efficiency must be between 0 and 1.")
    return rho * G * Q * head / efficiency


# Absolute roughness of common pipe materials (m), from the Moody chart tables
ROUGHNESS = {
    "PVC / plastic": 1.5e-6,
    "Copper": 1.5e-6,
    "Commercial steel": 4.5e-5,
    "Galvanised iron": 1.5e-4,
    "Cast iron": 2.6e-4,
    "Concrete": 1.0e-3,
}
