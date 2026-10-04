"""Illustrations for Projectile motion."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def render_projectile():
    st.markdown(
        "A projectile launches from height $h$ with initial velocity "
        r"$(v_{x0}, v_{y0})$ under gravity $g$. The trajectory stops when it "
        "reaches the ground, $y = 0$."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        vx0 = st.slider("vx0 (m/s)", min_value=-10.0, max_value=20.0, value=10.0, step=0.5)
    with col2:
        vy0 = st.slider("vy0 (m/s)", min_value=-10.0, max_value=20.0, value=8.0, step=0.5)
    with col3:
        h = st.slider("Launch height, h (m)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
    with col4:
        g = st.slider("Gravity, g (m/s^2)", min_value=1.0, max_value=20.0, value=9.81, step=0.01)

    # Positive root of 0.5*g*t^2 - vy0*t - h = 0 gives the landing time (t > 0)
    t_end = (vy0 + np.sqrt(vy0 ** 2 + 2 * g * h)) / g

    n_frames = 80
    t = np.linspace(0, t_end, n_frames)
    x = vx0 * t
    y = h + vy0 * t - 0.5 * g * t ** 2
    y[-1] = 0.0  # clean up any tiny numerical residual at landing
    vx_t = np.full_like(t, vx0)
    vy_t = vy0 - g * t

    x_min, x_max = min(0, x.min()), max(0, x.max())
    y_min, y_max = 0.0, max(h, y.max())
    x_pad = 0.05 * max(x_max - x_min, 1.0)
    y_pad = 0.05 * max(y_max - y_min, 1.0)
    vx_pad = max(0.5, 0.05 * abs(vx_t[-1] - vx_t[0]))
    vy_pad = max(0.5, 0.05 * abs(vy_t[-1] - vy_t[0]))

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Trajectory", "Velocity space"),
        horizontal_spacing=0.12,
    )
    fig.add_trace(
        go.Scatter(x=x, y=y, mode="lines", line=dict(color="lightgray", dash="dash"), name="path"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[x[0]], y=[y[0]], mode="markers", marker=dict(size=20, color="crimson"), name="projectile"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[vx_t[0]], y=[vy_t[0]], mode="lines", line=dict(color="seagreen", width=3), name="velocity path"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=[vx_t[0]], y=[vy_t[0]], mode="markers", marker=dict(size=12, color="darkorange"), name="current velocity"),
        row=1, col=2,
    )
    fig.update_layout(
        width=1100,
        height=600,
        showlegend=False,
        xaxis=dict(title="x (m)", range=[x_min - x_pad, x_max + x_pad]),
        yaxis=dict(title="y (m)", range=[y_min - y_pad, y_max + y_pad], scaleanchor="x", scaleratio=1),
        xaxis2=dict(title="vx (m/s)", range=[vx_t[0] - vx_pad, vx_t[-1] + vx_pad]),
        yaxis2=dict(title="vy (m/s)", range=[min(vy_t[0], vy_t[-1]) - vy_pad, max(vy_t[0], vy_t[-1]) + vy_pad]),
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
                        label=f"{ti:.2f}",
                    )
                    for i, ti in enumerate(t)
                ],
                x=0.0, y=-0.05, len=1.0,
            )
        ],
    )
    fig.frames = [
        go.Frame(
            name=f"frame{i}",
            data=[
                go.Scatter(x=[x[i]], y=[y[i]]),
                go.Scatter(x=vx_t[:i + 1], y=vy_t[:i + 1]),
                go.Scatter(x=[vx_t[i]], y=[vy_t[i]]),
            ],
            traces=[1, 2, 3],
        )
        for i in range(n_frames)
    ]

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Time of flight: {t_end:g} s — Range: {x[-1]:g} m")

    vel_fig = go.Figure(
        data=[
            go.Scatter(x=t, y=vx_t, mode="lines", name="vx(t)", line=dict(color="seagreen")),
            go.Scatter(x=t, y=vy_t, mode="lines", name="vy(t)", line=dict(color="darkorange")),
        ],
        layout=go.Layout(
            xaxis=dict(title="t (s)"),
            yaxis=dict(title="velocity (m/s)"),
            height=350,
            legend=dict(orientation="h", y=1.1),
        ),
    )
    st.plotly_chart(vel_fig, use_container_width=True)


def _landing_time(vy0, h, g):
    return (vy0 + np.sqrt(vy0 ** 2 + 2 * g * h)) / g


def _trajectory(vx0, vy0, h, g, t):
    """Position at times t, held at ground level once the object has landed."""
    t_end = _landing_time(vy0, h, g)
    t_clip = np.minimum(t, t_end)
    x = vx0 * t_clip
    y = np.maximum(h + vy0 * t_clip - 0.5 * g * t_clip ** 2, 0.0)
    return x, y, t_end


def render_compare_two_projectiles():
    st.markdown(
        "Compare two projectiles launched with different initial velocities "
        "and/or different gravity, to see how their trajectories differ."
    )

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Object A")
        vx0_a = st.slider("vx0 A (m/s)", min_value=-10.0, max_value=20.0, value=10.0, step=0.5)
        vy0_a = st.slider("vy0 A (m/s)", min_value=-10.0, max_value=20.0, value=12.0, step=0.5)
        h_a = st.slider("Launch height A, h (m)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
        g_a = st.slider("Gravity A, g (m/s^2)", min_value=1.0, max_value=20.0, value=9.81, step=0.01)
    with colB:
        st.subheader("Object B")
        vx0_b = st.slider("vx0 B (m/s)", min_value=-10.0, max_value=20.0, value=10.0, step=0.5)
        vy0_b = st.slider("vy0 B (m/s)", min_value=-10.0, max_value=20.0, value=12.0, step=0.5)
        h_b = st.slider("Launch height B, h (m)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
        g_b = st.slider("Gravity B, g (m/s^2)", min_value=1.0, max_value=20.0, value=3.71, step=0.01)

    t_end_a = _landing_time(vy0_a, h_a, g_a)
    t_end_b = _landing_time(vy0_b, h_b, g_b)
    t_total = max(t_end_a, t_end_b)

    n_frames = 100
    t = np.linspace(0, t_total, n_frames)
    x_a, y_a, _ = _trajectory(vx0_a, vy0_a, h_a, g_a, t)
    x_b, y_b, _ = _trajectory(vx0_b, vy0_b, h_b, g_b, t)

    x_min = min(0, x_a.min(), x_b.min())
    x_max = max(x_a.max(), x_b.max())
    y_min = 0.0
    y_max = max(h_a, h_b, y_a.max(), y_b.max())
    x_pad = 0.05 * max(x_max - x_min, 1.0)
    y_pad = 0.05 * max(y_max - y_min, 1.0)

    fig = go.Figure(
        data=[
            go.Scatter(x=x_a, y=y_a, mode="lines", line=dict(color="royalblue", dash="dash"), name="path A"),
            go.Scatter(x=x_b, y=y_b, mode="lines", line=dict(color="darkorange", dash="dash"), name="path B"),
            go.Scatter(x=[x_a[0]], y=[y_a[0]], mode="markers", marker=dict(size=18, color="royalblue"), name="A"),
            go.Scatter(x=[x_b[0]], y=[y_b[0]], mode="markers", marker=dict(size=18, color="darkorange"), name="B"),
        ],
        layout=go.Layout(
            width=700, height=550,
            xaxis=dict(title="x (m)", range=[x_min - x_pad, x_max + x_pad]),
            yaxis=dict(title="y (m)", range=[y_min - y_pad, y_max + y_pad], scaleanchor="x", scaleratio=1),
            legend=dict(orientation="h", y=1.05),
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
                            label=f"{ti:.2f}",
                        )
                        for i, ti in enumerate(t)
                    ],
                    x=0.0, y=-0.05, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"frame{i}",
                data=[go.Scatter(), go.Scatter(), go.Scatter(x=[x_a[i]], y=[y_a[i]]), go.Scatter(x=[x_b[i]], y=[y_b[i]])],
            )
            for i in range(n_frames)
        ],
    )

    st.plotly_chart(fig, use_container_width=False)
    st.caption(f"Time of flight — A: {t_end_a:g} s, B: {t_end_b:g} s. Range — A: {x_a[-1]:g} m, B: {x_b[-1]:g} m")
