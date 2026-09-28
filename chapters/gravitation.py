"""Illustrations for gravitation."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


G = 6.67430e-11
BODIES = {
    "Earth": {"mass": 5.9722e24, "radius": 6.371e6},
    "Moon": {"mass": 7.342e22, "radius": 1.7374e6},
    "Mars": {"mass": 6.4171e23, "radius": 3.3895e6},
    "Venus": {"mass": 4.8675e24, "radius": 6.0518e6},
    "Mercury": {"mass": 3.3011e23, "radius": 2.4397e6},
    "Jupiter": {"mass": 1.89813e27, "radius": 6.9911e7},
    "Saturn": {"mass": 5.6834e26, "radius": 5.8232e7},
    "Uranus": {"mass": 8.6810e25, "radius": 2.5362e7},
    "Neptune": {"mass": 1.02413e26, "radius": 2.4622e7},
}


def _fall_trajectory(body, initial_height):
    """Integrate radial free fall using Newton's inverse-square law."""
    body_mass = body["mass"]
    body_radius = body["radius"]
    surface_gravity = G * body_mass / body_radius ** 2
    time_step = 0.01
    max_steps = int(np.ceil(2 * np.sqrt(2 * initial_height / surface_gravity) / time_step)) + 100

    time = 0.0
    height = initial_height
    velocity = 0.0
    times = [time]
    heights = [height]

    for _ in range(max_steps):
        acceleration = -G * body_mass / (body_radius + height) ** 2
        next_height = height + velocity * time_step + 0.5 * acceleration * time_step ** 2

        if next_height <= 0:
            impact_fraction = height / (height - next_height)
            times.append(time + impact_fraction * time_step)
            heights.append(0.0)
            break

        next_acceleration = -G * body_mass / (body_radius + next_height) ** 2
        velocity += 0.5 * (acceleration + next_acceleration) * time_step
        time += time_step
        height = next_height
        times.append(time)
        heights.append(height)

    return np.asarray(times), np.asarray(heights), surface_gravity


def render_compare_free_fall():
    st.markdown(
        "Compare a mass $m$ falling from rest at height $h$ above two spherical bodies. "
        r"Newton's law gives $F_g=GMm/r^2$ and $a=GM/r^2$, where $r=R+h$. "
        "The falling mass changes the force, but not its acceleration. For gas giants, "
        "the reference radius is the conventional 1-bar level, not a solid surface."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        test_mass = st.slider("Falling mass, m (kg)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
    with col2:
        initial_height = st.slider("Initial height, h (m)", min_value=10.0, max_value=500.0, value=100.0, step=10.0)
    with col3:
        body1_name = st.selectbox("First body (M1)", list(BODIES), index=0)
    with col4:
        body2_name = st.selectbox("Second body (M2)", list(BODIES), index=1)

    body1 = BODIES[body1_name]
    body2 = BODIES[body2_name]
    time1, height1, gravity1 = _fall_trajectory(body1, initial_height)
    time2, height2, gravity2 = _fall_trajectory(body2, initial_height)

    total_time = max(time1[-1], time2[-1])
    frame_times = np.linspace(0.0, total_time, 100)
    frame_heights1 = np.interp(frame_times, time1, height1, right=0.0)
    frame_heights2 = np.interp(frame_times, time2, height2, right=0.0)

    subplot_titles = (
        f"{body1_name}: M = {body1['mass']:.3g} kg, R = {body1['radius'] / 1000:.0f} km",
        f"{body2_name}: M = {body2['mass']:.3g} kg, R = {body2['radius'] / 1000:.0f} km",
    )
    fig = make_subplots(rows=1, cols=2, subplot_titles=subplot_titles)
    for column, height, color in (
        (1, frame_heights1, "#2a9d8f"),
        (2, frame_heights2, "#e9a23b"),
    ):
        fig.add_trace(
            go.Scatter(x=[0, 0], y=[0, initial_height], mode="lines", line=dict(color="#999999", dash="dot"), showlegend=False),
            row=1, col=column,
        )
        fig.add_trace(
            go.Scatter(x=[-0.8, 0.8], y=[0, 0], mode="lines", line=dict(color="#555555", width=14), showlegend=False),
            row=1, col=column,
        )
        fig.add_trace(
            go.Scatter(
                x=[0], y=[initial_height], mode="markers+text", text=[f"m = {test_mass:g} kg"],
                textposition="top center", marker=dict(size=18, color=color, line=dict(color="white", width=2)),
                showlegend=False,
            ),
            row=1, col=column,
        )

    fig.frames = [
        go.Frame(
            name=f"frame{index}",
            data=[go.Scatter(x=[0], y=[frame_heights1[index]]), go.Scatter(x=[0], y=[frame_heights2[index]])],
            traces=[2, 5],
        )
        for index in range(len(frame_times))
    ]
    fig.update_layout(
        height=470,
        showlegend=False,
        margin=dict(t=90, b=70),
        updatemenus=[
            dict(
                type="buttons", showactive=False, x=0.0, y=1.18, xanchor="left",
                buttons=[
                    dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                    dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[[f"frame{index}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                        label=f"{time_value:.1f}",
                    )
                    for index, time_value in enumerate(frame_times)
                ],
                x=0.0, y=-0.08, len=1.0,
            )
        ],
    )
    for column in (1, 2):
        fig.update_xaxes(range=[-1, 1], visible=False, row=1, col=column)
        fig.update_yaxes(range=[-15, initial_height + 20], title_text="height above reference level (m)", row=1, col=column)

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Gravity at the reference radius: {body1_name} {gravity1:.3f} m/s^2, "
        f"{body2_name} {gravity2:.3f} m/s^2. "
        f"Fall time from {initial_height:g} m: {body1_name} {time1[-1]:.2f} s, "
        f"{body2_name} {time2[-1]:.2f} s. Initial gravitational force on m: "
        f"{body1_name} {test_mass * gravity1:.2f} N, {body2_name} {test_mass * gravity2:.2f} N."
    )