"""Thermodynamics and heat transfer. SI units; temperatures in kelvin unless noted."""

from __future__ import annotations

R_UNIVERSAL = 8.314462618  # J/mol.K
SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant, W/m^2.K^4
R_AIR = 287.05  # specific gas constant of air, J/kg.K


def ideal_gas_pressure(m: float, T: float, V: float, R: float = R_AIR) -> float:
    """P = m R T / V  (Pa), with R the specific gas constant (default: air)."""
    _kelvin(T)
    return m * R * T / V


def ideal_gas_density(P: float, T: float, R: float = R_AIR) -> float:
    """rho = P / (R T)  (kg/m^3)"""
    _kelvin(T)
    return P / (R * T)


def sensible_heat(m: float, cp: float, delta_T: float) -> float:
    """Q = m cp dT  (J)"""
    return m * cp * delta_T


def carnot_efficiency(T_hot: float, T_cold: float) -> float:
    """Maximum possible efficiency of a heat engine: 1 - Tc/Th"""
    _kelvin(T_hot, T_cold)
    if T_cold >= T_hot:
        raise ValueError("T_hot must be greater than T_cold.")
    return 1 - T_cold / T_hot


def carnot_cop_refrigerator(T_hot: float, T_cold: float) -> float:
    """COP_R = Tc / (Th - Tc)"""
    _kelvin(T_hot, T_cold)
    return T_cold / (T_hot - T_cold)


def conduction(k: float, A: float, T1: float, T2: float, L: float) -> float:
    """Fourier's law through a plane wall: q = k A (T1 - T2) / L  (W)"""
    return k * A * (T1 - T2) / L


def convection(h: float, A: float, T_surface: float, T_fluid: float) -> float:
    """Newton's law of cooling: q = h A (Ts - Tinf)  (W)"""
    return h * A * (T_surface - T_fluid)


def radiation(emissivity: float, A: float, T_surface: float, T_surroundings: float) -> float:
    """Net radiation to large surroundings: q = eps sigma A (Ts^4 - Tsur^4)  (W)"""
    _kelvin(T_surface, T_surroundings)
    if not 0 <= emissivity <= 1:
        raise ValueError("Emissivity must be between 0 and 1.")
    return emissivity * SIGMA * A * (T_surface**4 - T_surroundings**4)


def wall_heat_loss(T_inside: float, T_outside: float, A: float, layers: list[tuple[float, float]],
                   h_in: float | None = None, h_out: float | None = None) -> float:
    """Heat flow through a composite wall using thermal resistances in series.

    layers = [(thickness_m, k), ...].  Returns q in W.
    """
    R = sum(L / (k * A) for L, k in layers)
    if h_in:
        R += 1 / (h_in * A)
    if h_out:
        R += 1 / (h_out * A)
    return (T_inside - T_outside) / R


def _kelvin(*temps: float) -> None:
    for T in temps:
        if T <= 0:
            raise ValueError("Temperatures must be in kelvin (> 0). Use units.convert(T, 'C', 'K').")
