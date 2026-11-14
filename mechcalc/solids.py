"""Mechanics of materials. All inputs and outputs in SI units (N, m, Pa) unless noted."""

from __future__ import annotations

import math


def normal_stress(force: float, area: float) -> float:
    """sigma = F / A  (Pa)"""
    _positive(area=area)
    return force / area


def strain(delta_L: float, L: float) -> float:
    """epsilon = dL / L  (dimensionless)"""
    _positive(L=L)
    return delta_L / L


def youngs_modulus(force: float, area: float, delta_L: float, L: float) -> float:
    """E = stress / strain = (F/A) / (dL/L)  (Pa)"""
    return normal_stress(force, area) / strain(delta_L, L)


def elongation(force: float, L: float, area: float, E: float) -> float:
    """dL = F L / (A E)  (m)"""
    _positive(area=area, E=E)
    return force * L / (area * E)


def thermal_stress(E: float, alpha: float, delta_T: float) -> float:
    """Stress in a bar that is fully restrained while it heats up: sigma = -E alpha dT (compressive when heated)."""
    return -E * alpha * delta_T


# ----- section properties --------------------------------------------------
def area_circle(d: float) -> float:
    return math.pi * d**2 / 4


def I_rectangle(b: float, h: float) -> float:
    """Second moment of area about the centroidal axis parallel to b: I = b h^3 / 12  (m^4)"""
    return b * h**3 / 12


def I_circle(d: float) -> float:
    """I = pi d^4 / 64  (m^4)"""
    return math.pi * d**4 / 64


def J_shaft(d: float, d_inner: float = 0.0) -> float:
    """Polar second moment of area for a solid or hollow round shaft: J = pi (D^4 - d^4) / 32  (m^4)"""
    if d_inner >= d:
        raise ValueError("Inner diameter must be smaller than the outer diameter.")
    return math.pi * (d**4 - d_inner**4) / 32


# ----- bending and torsion ------------------------------------------------
def bending_stress(M: float, y: float, I: float) -> float:
    """Flexure formula sigma = M y / I  (Pa)"""
    _positive(I=I)
    return M * y / I


def torsional_shear_stress(T: float, d: float, d_inner: float = 0.0) -> float:
    """Maximum shear stress at the outer surface of a round shaft: tau = T r / J  (Pa)"""
    return T * (d / 2) / J_shaft(d, d_inner)


def angle_of_twist(T: float, L: float, G: float, d: float, d_inner: float = 0.0) -> float:
    """theta = T L / (G J)  (radians)"""
    _positive(G=G)
    return T * L / (G * J_shaft(d, d_inner))


def shaft_diameter_for_torque(T: float, tau_allow: float) -> float:
    """Smallest solid shaft diameter so that tau_max <= tau_allow: d = (16 T / (pi tau))^(1/3)  (m)"""
    _positive(tau_allow=tau_allow)
    return (16 * T / (math.pi * tau_allow)) ** (1 / 3)


def euler_buckling_load(E: float, I: float, L: float, K: float = 1.0) -> float:
    """Critical load for a slender column: P_cr = pi^2 E I / (K L)^2  (N)

    K = effective length factor: 1.0 pinned-pinned, 2.0 fixed-free, 0.5 fixed-fixed, 0.7 fixed-pinned.
    """
    _positive(E=E, I=I, L=L, K=K)
    return math.pi**2 * E * I / (K * L) ** 2


def factor_of_safety(strength: float, stress: float) -> float:
    """FoS = failure strength / working stress"""
    if stress == 0:
        return math.inf
    return strength / abs(stress)


def von_mises(sx: float, sy: float = 0.0, txy: float = 0.0) -> float:
    """Von Mises equivalent stress for plane stress: sqrt(sx^2 - sx sy + sy^2 + 3 txy^2)"""
    return math.sqrt(sx**2 - sx * sy + sy**2 + 3 * txy**2)


def principal_stresses(sx: float, sy: float, txy: float) -> tuple[float, float, float]:
    """Returns (sigma_1, sigma_2, tau_max) for plane stress (Mohr's circle)."""
    centre = (sx + sy) / 2
    R = math.hypot((sx - sy) / 2, txy)
    return centre + R, centre - R, R


def _positive(**kw: float) -> None:
    for name, v in kw.items():
        if v <= 0:
            raise ValueError(f"{name} must be positive (got {v}).")
