import math

import pytest

from mechcalc import convert, fluids, machines, solids, thermo
from mechcalc.cli import main


# ----- units ---------------------------------------------------------------
@pytest.mark.parametrize("v, a, b, expected", [
    (1, "in", "mm", 25.4),
    (1, "ft", "m", 0.3048),
    (1, "lbf", "N", 4.448222),
    (1, "ksi", "MPa", 6.894757),
    (1, "atm", "kPa", 101.325),
    (1, "hp", "kW", 0.745700),
    (1, "kWh", "MJ", 3.6),
    (100, "km/h", "m/s", 27.77778),
    (1000, "rpm", "rad/s", 104.7198),
    (100, "C", "F", 212),
    (-40, "C", "F", -40),
    (0, "C", "K", 273.15),
    (1, "g/cm3", "kg/m3", 1000),
])
def test_convert(v, a, b, expected):
    assert convert(v, a, b) == pytest.approx(expected, rel=1e-5)


def test_round_trip():
    assert convert(convert(123.4, "psi", "kPa"), "kPa", "psi") == pytest.approx(123.4)


def test_bad_units():
    with pytest.raises(ValueError):
        convert(1, "m", "kg")
    with pytest.raises(ValueError):
        convert(1, "furlong", "m")


# ----- solids --------------------------------------------------------------
def test_stress_strain():
    # 10 kN on a 10 mm x 10 mm bar -> 100 MPa
    assert solids.normal_stress(10e3, 1e-4) == pytest.approx(100e6)
    assert solids.youngs_modulus(10e3, 1e-4, 0.5e-3, 1.0) == pytest.approx(200e9)
    assert solids.elongation(10e3, 1.0, 1e-4, 200e9) == pytest.approx(0.5e-3)


def test_section_properties():
    assert solids.I_rectangle(0.1, 0.2) == pytest.approx(0.1 * 0.2**3 / 12)
    assert solids.J_shaft(0.05) == pytest.approx(2 * solids.I_circle(0.05))  # J = 2I for a circle


def test_torsion_round_trip():
    T, tau = 500.0, 40e6
    d = solids.shaft_diameter_for_torque(T, tau)
    assert solids.torsional_shear_stress(T, d) == pytest.approx(tau)


def test_buckling_and_mohr():
    I = solids.I_circle(0.02)
    pinned = solids.euler_buckling_load(200e9, I, 1.0)
    fixed_free = solids.euler_buckling_load(200e9, I, 1.0, K=2.0)
    assert pinned / fixed_free == pytest.approx(4)
    s1, s2, tmax = solids.principal_stresses(80, -40, 25)
    assert (s1, s2, tmax) == pytest.approx((85, -45, 65))
    assert solids.von_mises(100) == pytest.approx(100)
    assert solids.von_mises(0, 0, 10) == pytest.approx(10 * math.sqrt(3))


# ----- thermo --------------------------------------------------------------
def test_thermo():
    assert thermo.ideal_gas_density(101325, 288.15) == pytest.approx(1.225, rel=1e-3)
    assert thermo.carnot_efficiency(600, 300) == pytest.approx(0.5)
    assert thermo.sensible_heat(1, 4186, 10) == pytest.approx(41860)
    with pytest.raises(ValueError):
        thermo.carnot_efficiency(25, 100)  # Celsius by mistake / reversed
    # wall: 0.2 m concrete (k=1.4), 10 m^2, 20 K difference, plus film coefficients
    q = thermo.wall_heat_loss(30, 10, 10, [(0.2, 1.4)], h_in=10, h_out=25)
    R = 0.2 / 14 + 1 / 100 + 1 / 250
    assert q == pytest.approx(20 / R)


# ----- fluids --------------------------------------------------------------
def test_fluids():
    assert fluids.friction_factor(1000) == pytest.approx(0.064)
    # smooth pipe, Re = 1e5: Moody chart gives f ~ 0.018
    assert fluids.friction_factor(1e5, 0, 0.1) == pytest.approx(0.0180, abs=3e-4)
    assert fluids.hydrostatic_pressure(10) == pytest.approx(97_870, rel=1e-3)
    assert fluids.flow_regime(1000) == "laminar" and fluids.flow_regime(1e5) == "turbulent"
    assert fluids.torricelli(5) == pytest.approx(9.903, rel=1e-3)


# ----- machines ------------------------------------------------------------
def test_machines():
    P = machines.power_from_torque(100, 1500)
    assert P == pytest.approx(15_708, rel=1e-4)
    assert machines.torque_from_power(P, 1500) == pytest.approx(100)
    g = machines.gear_train([(20, 60), (15, 45)], rpm_in=1800, torque_in=10)
    assert g["ratio"] == pytest.approx(9) and g["rpm_out"] == pytest.approx(200)
    assert g["torque_out"] == pytest.approx(90)
    assert machines.springs_series(100, 100) == pytest.approx(50)
    assert machines.natural_frequency(4 * math.pi**2, 1) == pytest.approx(1)


def test_cli(capsys):
    main(["convert", "10", "kN", "lbf"])
    assert "2248.09" in capsys.readouterr().out
    main(["shaft", "--torque", "500", "--tau", "40e6"])
    assert "mm" in capsys.readouterr().out
