"""Machine elements and power transmission. SI units."""

from __future__ import annotations

import math


def power_from_torque(torque: float, rpm: float) -> float:
    """P = T * omega  (W), with omega = 2 pi N / 60"""
    return torque * 2 * math.pi * rpm / 60


def torque_from_power(power: float, rpm: float) -> float:
    """T = P / omega  (N.m)"""
    if rpm == 0:
        raise ValueError("rpm cannot be zero.")
    return power / (2 * math.pi * rpm / 60)


def gear_train(teeth: list[tuple[int, int]], rpm_in: float, torque_in: float = 0.0,
               efficiency_per_stage: float = 1.0) -> dict:
    """Simple or compound gear train.

    teeth = [(driver, driven), ...] for each stage.  Returns the overall ratio,
    output speed and output torque (losses applied per stage).
    """
    ratio = 1.0
    for driver, driven in teeth:
        if driver <= 0 or driven <= 0:
            raise ValueError("Tooth counts must be positive.")
        ratio *= driven / driver
    eff = efficiency_per_stage ** len(teeth)
    return {"ratio": ratio, "rpm_out": rpm_in / ratio, "torque_out": torque_in * ratio * eff,
            "efficiency": eff}


def belt_speed(d_pulley: float, rpm: float) -> float:
    """Linear belt speed v = pi d N / 60  (m/s)"""
    return math.pi * d_pulley * rpm / 60


def belt_tension_ratio(mu: float, wrap_angle_deg: float) -> float:
    """Capstan / belt friction equation: T1/T2 = e^(mu theta)"""
    return math.exp(mu * math.radians(wrap_angle_deg))


def spring_force(k: float, x: float) -> float:
    """Hooke's law F = k x"""
    return k * x


def springs_series(*k: float) -> float:
    """1/k = sum(1/k_i)"""
    return 1 / sum(1 / ki for ki in k)


def springs_parallel(*k: float) -> float:
    return sum(k)


def helical_spring_rate(G: float, d_wire: float, D_coil: float, n_active: float) -> float:
    """k = G d^4 / (8 D^3 n)  (N/m)"""
    return G * d_wire**4 / (8 * D_coil**3 * n_active)


def natural_frequency(k: float, m: float) -> float:
    """Undamped natural frequency of a mass-spring system, f = (1/2pi) sqrt(k/m)  (Hz)"""
    return math.sqrt(k / m) / (2 * math.pi)


def bolt_preload_torque(F_preload: float, d: float, K: float = 0.2) -> float:
    """Tightening torque T = K F d  (K ~ 0.2 for dry steel, ~0.15 lubricated)"""
    return K * F_preload * d
