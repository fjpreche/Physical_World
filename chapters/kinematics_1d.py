"""Illustrations for Kinematics in one dimension."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st


def _build_animation_figure(t, v_t, x_t, v_range, x_range):
    """Shared scaffolding: top v(t) plot with a moving marker, bottom track with a moving circle."""
    n_frames = len(t)
    t_max = t[-1]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[t[0]], y=[v_t[0]], mode="markers", marker=dict(size=12, color="crimson"),
                name="current time", xaxis="x", yaxis="y",
            ),
            go.Scatter(
                x=t, y=v_t, mode="lines", line=dict(color="royalblue"),
                name="v(t)", xaxis="x", yaxis="y",
            ),
            go.Scatter(
                x=[x_t[0]], y=[0], mode="markers", marker=dict(size=28, color="crimson"),
                name="particle", xaxis="x2", yaxis="y2",
            ),
        ],
        layout=go.Layout(
            grid=dict(rows=2, columns=1, pattern="independent"),
            height=500,
            showlegend=False,
            xaxis=dict(title="t (s)", range=[0, t_max], domain=[0.0, 1.0], anchor="y"),
            yaxis=dict(title="v (m/s)", range=v_range, domain=[0.55, 1.0]),
            xaxis2=dict(title="position (m)", range=x_range, domain=[0.0, 1.0], anchor="y2"),
            yaxis2=dict(range=[-1, 1], domain=[0.0, 0.35], showticklabels=False),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    y=1.15,
                    x=0.0,
                    xanchor="left",
                    buttons=[
                        dict(label="Play", method="animate",
                             args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                        dict(label="Pause", method="animate",
                             args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                    ],
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(
                            method="animate",
                            args=[[f"frame{i}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                            label=f"{ti:.1f}",
                        )
                        for i, ti in enumerate(t)
                    ],
                    x=0.0, y=0, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"frame{i}",
                data=[
                    go.Scatter(x=[t[i]], y=[v_t[i]]),
                    go.Scatter(x=t, y=v_t),
                    go.Scatter(x=[x_t[i]], y=[0]),
                ],
            )
            for i in range(n_frames)
        ],
    )
    return fig


def render_constant_velocity():
    st.markdown(
        "A particle moves at **constant velocity** $v$ for $T$ seconds. "
        "Adjust the sliders and press play to watch the velocity graph and "
        "the particle's motion along a horizontal track."
    )

    col1, col2 = st.columns(2)
    with col1:
        v = st.slider("Velocity, v (m/s)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)
    with col2:
        T = st.slider("Duration, T (s)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    n_frames = 60
    t = np.linspace(0, T, n_frames)
    x = v * t
    x_max = v * T
    v_t = np.full_like(t, v)

    # Track limits so the circle stays visible regardless of sign of v
    track_min, track_max = (min(0, x_max), max(0, x_max))
    pad = max(1.0, 0.1 * (track_max - track_min if track_max != track_min else 1))

    fig = _build_animation_figure(
        t, v_t, x,
        v_range=[min(0, v) - 1, max(0, v) + 1],
        x_range=[track_min - pad, track_max + pad],
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Total displacement after T = {T:g} s: v·T = {x_max:g} m")


def render_constant_acceleration():
    st.markdown(
        "A particle starts with initial velocity $v_0$ and moves with "
        "constant acceleration $a$ for $T$ seconds. Acceleration may be "
        "positive or negative."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        v0 = st.slider("Initial velocity, v0 (m/s)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5)
    with col2:
        a = st.slider("Acceleration, a (m/s^2)", min_value=-5.0, max_value=5.0, value=1.0, step=0.5)
    with col3:
        T = st.slider("Duration, T (s)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    t = np.linspace(0, T, 80)
    v_t = v0 + a * t
    x_t = v0 * t + 0.5 * a * t ** 2
    x_min, x_max = float(x_t.min()), float(x_t.max())
    pad = max(1.0, 0.1 * (x_max - x_min))
    v_min, v_max = float(v_t.min()), float(v_t.max())
    v_pad = max(1.0, 0.1 * (v_max - v_min))

    fig = _build_animation_figure(
        t, v_t, x_t,
        v_range=[v_min - v_pad, v_max + v_pad],
        x_range=[x_min - pad, x_max + pad],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Final velocity: {v_t[-1]:g} m/s — Displacement: {x_t[-1]:g} m")


def render_accelerate_cruise_decelerate():
    st.markdown(
        "A particle **accelerates** from rest to speed $v$ over $t_r$ seconds, "
        "**cruises** at $v$ for $T$ seconds, then **decelerates** back to rest "
        "over $t_r$ seconds."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        v = st.slider("Cruise speed, v (m/s)", min_value=0.5, max_value=10.0, value=4.0, step=0.5)
    with col2:
        T = st.slider("Cruise duration, T (s)", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
    with col3:
        t_r = st.slider("Accel/decel time, tr (s)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)

    t_total = 2 * t_r + T
    n_frames = 90
    t = np.linspace(0, t_total, n_frames)
    a = v / t_r  # accel/decel magnitude

    v_t = np.piecewise(
        t,
        [t < t_r, (t >= t_r) & (t < t_r + T), t >= t_r + T],
        [
            lambda tt: a * tt,
            lambda tt: v,
            lambda tt: v - a * (tt - (t_r + T)),
        ],
    )

    x_ramp = 0.5 * a * t_r ** 2  # distance covered during accel (= during decel)
    x_t = np.piecewise(
        t,
        [t < t_r, (t >= t_r) & (t < t_r + T), t >= t_r + T],
        [
            lambda tt: 0.5 * a * tt ** 2,
            lambda tt: x_ramp + v * (tt - t_r),
            lambda tt: x_ramp + v * T + v * (tt - (t_r + T)) - 0.5 * a * (tt - (t_r + T)) ** 2,
        ],
    )
    x_max = 2 * x_ramp + v * T

    pad = max(1.0, 0.1 * x_max)

    fig = _build_animation_figure(
        t, v_t, x_t,
        v_range=[-0.5, v + 1],
        x_range=[-pad, x_max + pad],
    )

    st.plotly_chart(fig, use_container_width=True)

    acceleration_fig = go.Figure(
        data=[
            go.Scatter(
                x=[0, t_r, t_r, t_r + T, t_r + T, t_total],
                y=[a, a, 0, 0, -a, -a],
                mode="lines",
                name="a(t)",
                line=dict(color="darkorange", width=3),
            )
        ],
        layout=go.Layout(
            height=300,
            xaxis=dict(title="time, t (s)", range=[0, t_total]),
            yaxis=dict(title="acceleration, a (m/s^2)", range=[-1.25 * a, 1.25 * a]),
            showlegend=False,
        ),
    )
    st.plotly_chart(acceleration_fig, use_container_width=True)
    st.caption(
        f"Total time: {t_total:g} s — Total distance: {x_max:g} m "
        f"(accel/decel each cover {x_ramp:g} m, cruise covers {v * T:g} m)"
    )
