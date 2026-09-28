"""Illustrations for Kinematics in two dimensions."""
import numpy as np
import plotly.graph_objects as go
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
