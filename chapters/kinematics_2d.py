"""Illustrations for Kinematics in two dimensions."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def render_constant_velocity_2d():
    st.markdown(
        "A particle starts at the origin and moves with **constant velocity** "
        r"$(v_x, v_y)$ for $T$ seconds."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        vx = st.slider("vx (m/s)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    with col2:
        vy = st.slider("vy (m/s)", min_value=0.0, max_value=10.0, value=5.0, step=0.5)
    with col3:
        T = st.slider("Duration, T (s)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    n_frames = 60
    t = np.linspace(0, T, n_frames)
    x = vx * t
    y = vy * t
    max_coord = max(vx * T, vy * T, 1.0)
    pad = 0.05 * max_coord

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[0, vx * T], y=[0, vy * T], mode="lines",
                line=dict(color="lightgray", dash="dash"), name="path",
            ),
            go.Scatter(
                x=[x[0]], y=[y[0]], mode="markers", marker=dict(size=20, color="crimson"),
                name="particle",
            ),
        ],
        layout=go.Layout(
            width=550, height=550,
            xaxis=dict(title="x (m)", range=[-pad, max_coord + pad]),
            yaxis=dict(title="y (m)", range=[-pad, max_coord + pad], scaleanchor="x", scaleratio=1),
            showlegend=False,
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    y=1.1,
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
                    x=0.0, y=-0.05, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(name=f"frame{i}", data=[go.Scatter(), go.Scatter(x=[x[i]], y=[y[i]])])
            for i in range(n_frames)
        ],
    )

    st.plotly_chart(fig, use_container_width=False)
    st.caption(f"Final position: ({vx * T:g}, {vy * T:g}) m")


def render_constant_acceleration_2d():
    st.markdown(
        "A particle starts at the origin with initial velocity "
        r"$(v_{x0}, v_{y0})$ and moves with constant acceleration $(a_x, a_y)$ "
        "for $T$ seconds."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        vx0 = st.slider("Initial vx, vx0 (m/s)", min_value=-10.0, max_value=10.0, value=6.0, step=0.5)
        vy0 = st.slider("Initial vy, vy0 (m/s)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)
    with col2:
        ax = st.slider("Acceleration ax (m/s^2)", min_value=-5.0, max_value=5.0, value=-1.0, step=0.5)
        ay = st.slider("Acceleration ay (m/s^2)", min_value=-5.0, max_value=5.0, value=0.5, step=0.5)
    with col3:
        T = st.slider("Duration, T (s)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    n_frames = 80
    t = np.linspace(0, T, n_frames)
    x = vx0 * t + 0.5 * ax * t ** 2
    y = vy0 * t + 0.5 * ay * t ** 2
    vx = vx0 + ax * t
    vy = vy0 + ay * t

    x_min, x_max = float(x.min()), float(x.max())
    y_min, y_max = float(y.min()), float(y.max())
    coord_min = min(x_min, y_min)
    coord_max = max(x_max, y_max)
    pad = max(1.0, 0.05 * (coord_max - coord_min))

    vx_min, vx_max = min(vx0, vx[-1]), max(vx0, vx[-1])
    vy_min, vy_max = min(vy0, vy[-1]), max(vy0, vy[-1])
    vx_pad = max(0.5, 0.05 * (vx_max - vx_min))
    vy_pad = max(0.5, 0.05 * (vy_max - vy_min))

    trajectory_fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Trajectory", "Velocity space"),
        horizontal_spacing=0.12,
    )
    trajectory_fig.add_trace(
        go.Scatter(x=x, y=y, mode="lines", line=dict(color="lightgray", dash="dash"), name="trajectory"),
        row=1, col=1,
    )
    trajectory_fig.add_trace(
        go.Scatter(x=[x[0]], y=[y[0]], mode="markers", marker=dict(size=20, color="crimson"), name="particle"),
        row=1, col=1,
    )
    trajectory_fig.add_trace(
        go.Scatter(x=[vx[0]], y=[vy[0]], mode="lines", line=dict(color="seagreen", width=3), name="velocity path"),
        row=1, col=2,
    )
    trajectory_fig.add_trace(
        go.Scatter(x=[vx[0]], y=[vy[0]], mode="markers", marker=dict(size=12, color="darkorange"), name="current velocity"),
        row=1, col=2,
    )
    trajectory_fig.update_layout(
        width=1100,
        height=600,
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=1.1,
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
                x=0.0, y=-0.05, len=1.0,
            )
        ],
        xaxis=dict(title="x (m)", range=[coord_min - pad, coord_max + pad]),
        yaxis=dict(title="y (m)", range=[coord_min - pad, coord_max + pad], scaleanchor="x", scaleratio=1),
        xaxis2=dict(title="vx (m/s)", range=[vx_min - vx_pad, vx_max + vx_pad]),
        yaxis2=dict(title="vy (m/s)", range=[vy_min - vy_pad, vy_max + vy_pad], scaleanchor="x2", scaleratio=1),
    )
    trajectory_fig.frames = [
        go.Frame(
            name=f"frame{i}",
            data=[
                go.Scatter(x=[x[i]], y=[y[i]]),
                go.Scatter(x=vx[:i + 1], y=vy[:i + 1]),
                go.Scatter(x=[vx[i]], y=[vy[i]]),
            ],
            traces=[1, 2, 3],
        )
        for i in range(n_frames)
    ]
    st.plotly_chart(trajectory_fig, use_container_width=True)

    velocity_time_fig = go.Figure(
        data=[
            go.Scatter(x=t, y=vx, mode="lines", name="vx(t)"),
            go.Scatter(x=t, y=vy, mode="lines", name="vy(t)"),
        ],
        layout=go.Layout(
            height=350,
            xaxis=dict(title="time, t (s)"),
            yaxis=dict(title="velocity (m/s)"),
            legend=dict(orientation="h", y=1.1),
        ),
    )
    st.plotly_chart(velocity_time_fig, use_container_width=True)

    st.caption(f"Final position: ({x[-1]:g}, {y[-1]:g}) m — Final velocity: ({vx[-1]:g}, {vy[-1]:g}) m/s")
