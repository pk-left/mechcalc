"""Streamlit web app for mechcalc.  Run with:  streamlit run app.py"""

import math

import streamlit as st

from mechcalc import convert, fluids, machines, solids, thermo
from mechcalc.units import UNITS, list_units

st.set_page_config(page_title="MechCalc", page_icon="⚙️", layout="centered")
st.title("⚙️ MechCalc")
st.caption("Unit converter and quick formulas for mechanical engineering students.")

tabs = st.tabs(["Units", "Stress & strain", "Shafts", "Columns", "Heat transfer", "Pipe flow", "Gears"])

with tabs[0]:
    q = st.selectbox("Quantity", list(list_units()))
    units = list_units()[q]
    c1, c2, c3 = st.columns([2, 1.5, 1.5])
    v = c1.number_input("Value", value=1.0, format="%g")
    a = c2.selectbox("From", units, index=0)
    b = c3.selectbox("To", units, index=min(1, len(units) - 1))
    st.success(f"**{v:g} {a} = {convert(v, a, b):.6g} {b}**")

with tabs[1]:
    st.subheader("Axial loading")
    F = st.number_input("Force F (kN)", value=10.0) * 1e3
    A = st.number_input("Cross-sectional area A (mm²)", value=100.0, min_value=0.001) * 1e-6
    L = st.number_input("Original length L (mm)", value=1000.0, min_value=0.001) * 1e-3
    E = st.number_input("Young's modulus E (GPa)", value=200.0, min_value=0.001) * 1e9
    Sy = st.number_input("Yield strength (MPa)", value=250.0) * 1e6
    s = solids.normal_stress(F, A)
    c = st.columns(3)
    c[0].metric("Stress σ", f"{s / 1e6:.2f} MPa")
    c[1].metric("Elongation δ", f"{solids.elongation(F, L, A, E) * 1e3:.4f} mm")
    c[2].metric("Factor of safety", f"{solids.factor_of_safety(Sy, s):.2f}")
    st.subheader("Plane stress (Mohr's circle)")
    c = st.columns(3)
    sx = c[0].number_input("σx (MPa)", value=80.0)
    sy = c[1].number_input("σy (MPa)", value=-40.0)
    txy = c[2].number_input("τxy (MPa)", value=25.0)
    s1, s2, tm = solids.principal_stresses(sx, sy, txy)
    c = st.columns(4)
    c[0].metric("σ₁", f"{s1:.1f} MPa")
    c[1].metric("σ₂", f"{s2:.1f} MPa")
    c[2].metric("τ max", f"{tm:.1f} MPa")
    c[3].metric("Von Mises", f"{solids.von_mises(sx, sy, txy):.1f} MPa")

with tabs[2]:
    P = st.number_input("Power (kW)", value=5.0) * 1e3
    rpm = st.number_input("Speed (rpm)", value=1450.0, min_value=1.0)
    tau = st.number_input("Allowable shear stress (MPa)", value=40.0, min_value=0.1) * 1e6
    T = machines.torque_from_power(P, rpm)
    d = solids.shaft_diameter_for_torque(T, tau)
    c = st.columns(2)
    c[0].metric("Torque", f"{T:.2f} N·m")
    c[1].metric("Minimum solid shaft diameter", f"{d * 1e3:.2f} mm")

with tabs[3]:
    shape = st.radio("Section", ["Solid round", "Rectangle"], horizontal=True)
    if shape == "Solid round":
        I = solids.I_circle(st.number_input("Diameter (mm)", value=30.0, min_value=0.1) * 1e-3)
    else:
        b_ = st.number_input("b (mm)", value=40.0, min_value=0.1) * 1e-3
        h_ = st.number_input("h (mm)", value=20.0, min_value=0.1) * 1e-3
        I = min(solids.I_rectangle(b_, h_), solids.I_rectangle(h_, b_))  # buckles about the weak axis
    Lc = st.number_input("Column length (m)", value=2.0, min_value=0.01)
    Ec = st.number_input("E (GPa) ", value=200.0, min_value=0.1) * 1e9
    ends = {"Pinned–pinned (K = 1)": 1.0, "Fixed–free (K = 2)": 2.0, "Fixed–pinned (K = 0.7)": 0.7,
            "Fixed–fixed (K = 0.5)": 0.5}
    K = ends[st.selectbox("End conditions", list(ends))]
    st.metric("Critical buckling load", f"{solids.euler_buckling_load(Ec, I, Lc, K) / 1e3:.2f} kN")

with tabs[4]:
    st.write("Heat loss through a wall (layers in series, plus air films)")
    n = st.number_input("Number of layers", 1, 5, 2)
    layers = []
    for i in range(int(n)):
        c = st.columns(2)
        t_ = c[0].number_input(f"Layer {i + 1} thickness (mm)", value=200.0 if i == 0 else 20.0, key=f"t{i}") / 1e3
        k_ = c[1].number_input(f"Layer {i + 1} k (W/m·K)", value=1.4 if i == 0 else 0.04, key=f"k{i}")
        layers.append((t_, k_))
    c = st.columns(4)
    Ti = c[0].number_input("Inside (°C)", value=24.0)
    To = c[1].number_input("Outside (°C)", value=38.0)
    Aw = c[2].number_input("Area (m²)", value=12.0, min_value=0.01)
    hin = c[3].number_input("h inside", value=8.0)
    q = thermo.wall_heat_loss(Ti, To, Aw, layers, h_in=hin, h_out=25)
    if q >= 0:
        st.metric("Heat lost from the room", f"{q:.1f} W")
    else:
        st.metric("Heat gained by the room", f"{-q:.1f} W", help="This is the load your air conditioner has to remove.")

with tabs[5]:
    D = st.number_input("Pipe diameter (mm)", value=50.0, min_value=0.1) * 1e-3
    vel = st.number_input("Velocity (m/s)", value=1.5, min_value=0.0)
    Lp = st.number_input("Pipe length (m)", value=100.0)
    mat = st.selectbox("Pipe material", list(fluids.ROUGHNESS), index=2)
    w = fluids.WATER
    Re = fluids.reynolds(w["rho"], vel, D, w["mu"])
    c = st.columns(3)
    c[0].metric("Reynolds number", f"{Re:,.0f}", fluids.flow_regime(Re), delta_color="off")
    if Re > 0:
        dp = fluids.pressure_drop(Lp, D, vel, roughness=fluids.ROUGHNESS[mat])
        c[1].metric("Friction factor f", f"{fluids.friction_factor(Re, fluids.ROUGHNESS[mat], D):.4f}")
        c[2].metric("Pressure drop", f"{dp / 1e3:.2f} kPa")
        st.caption(f"Flow rate {fluids.flow_rate(vel, D) * 1000:.2f} L/s · head loss {dp / (w['rho'] * fluids.G):.2f} m")

with tabs[6]:
    stages = st.number_input("Number of stages", 1, 4, 2)
    teeth = []
    for i in range(int(stages)):
        c = st.columns(2)
        teeth.append((c[0].number_input(f"Stage {i + 1} driver teeth", 1, 500, 20, key=f"a{i}"),
                      c[1].number_input(f"Stage {i + 1} driven teeth", 1, 500, 60, key=f"b{i}")))
    c = st.columns(3)
    rin = c[0].number_input("Input speed (rpm)", value=1450.0)
    tin = c[1].number_input("Input torque (N·m)", value=10.0)
    eff = c[2].number_input("Efficiency per stage", 0.5, 1.0, 0.98)
    g = machines.gear_train(teeth, rin, tin, eff)
    c = st.columns(3)
    c[0].metric("Overall ratio", f"{g['ratio']:.3g} : 1")
    c[1].metric("Output speed", f"{g['rpm_out']:.1f} rpm")
    c[2].metric("Output torque", f"{g['torque_out']:.1f} N·m")
