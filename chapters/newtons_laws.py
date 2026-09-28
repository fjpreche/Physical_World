"""Illustrations for Newton's laws of motion."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_ice_skaters_push():
    st.markdown(
        "Two ice skaters start at rest and push apart. With no friction, the forces "
        "are equal and opposite, so Newton's second law gives "
        r"$a_{red}=-F_{red}/m_{red}$ and $a_{blue}=F_{blue}/m_{blue}$, "
        "with all motion along the horizontal direction."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        m_red = st.slider("Red mass, m_red (kg)", min_value=20.0, max_value=120.0, value=70.0, step=5.0)
    with col2:
        m_blue = st.slider("Blue mass, m_blue (kg)", min_value=20.0, max_value=120.0, value=100.0, step=5.0)
    with col3:
        force = st.slider("Push force, F (N)", min_value=10.0, max_value=200.0, value=25.0, step=5.0)
    with col4:
        duration = st.slider("Duration, T (s)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)

    n_frames = 90
    t = np.linspace(0.0, duration, n_frames)
    a_red = -force / m_red
    a_blue = force / m_blue
    v_red = a_red * t
    v_blue = a_blue * t
    x_red = -0.5 * force / m_red * t ** 2
    x_blue = 0.5 * force / m_blue * t ** 2

    x_min = min(x_red.min(), x_blue.min())
    x_max = max(x_red.max(), x_blue.max())
    x_pad = max(1.0, 0.12 * (x_max - x_min))
    acceleration_limit = max(abs(a_red), abs(a_blue), 0.1) * 1.25

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[x_red[0]], y=[0], mode="markers+text", text=["red"], textposition="top center",
                marker=dict(size=24, color="crimson"), name="red skater",
            ),
            go.Scatter(
                x=[x_blue[0]], y=[0], mode="markers+text", text=["blue"], textposition="top center",
                marker=dict(size=24, color="royalblue"), name="blue skater",
            ),
            go.Scatter(
                x=[x_red[0], x_red[0] - force * 0.01], y=[0, 0], mode="lines+text",
                text=[None, "F_red"], textposition="bottom center", line=dict(color="crimson", width=4),
                name="force on red",
            ),
            go.Scatter(
                x=[x_blue[0], x_blue[0] + force * 0.01], y=[0, 0], mode="lines+text",
                text=[None, "F_blue"], textposition="bottom center", line=dict(color="royalblue", width=4),
                name="force on blue",
            ),
        ],
        layout=go.Layout(
            height=400,
            xaxis=dict(title="horizontal position, x (m)", range=[x_min - x_pad, x_max + x_pad]),
            yaxis=dict(range=[-1, 1], showticklabels=False, zeroline=True),
            showlegend=False,
            updatemenus=[
                dict(
                    type="buttons", showactive=False, y=1.15, x=0.0, xanchor="left",
                    buttons=[
                        dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                        dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                    ],
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(method="animate", args=[[f"frame{i}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))], label=f"{time:g}")
                        for i, time in enumerate(t)
                    ],
                    x=0.0, y=-0.08, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"frame{i}",
                data=[
                    go.Scatter(x=[x_red[i]], y=[0]),
                    go.Scatter(x=[x_blue[i]], y=[0]),
                    go.Scatter(x=[x_red[i], x_red[i] - force * 0.01], y=[0, 0]),
                    go.Scatter(x=[x_blue[i], x_blue[i] + force * 0.01], y=[0, 0]),
                ],
            )
            for i in range(n_frames)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    velocity_limit = max(abs(v_red[-1]), abs(v_blue[-1]), 0.1) * 1.25
    velocity_fig = go.Figure(
        data=[
            go.Scatter(x=t, y=v_red, mode="lines", name="v_red", line=dict(color="crimson")),
            go.Scatter(x=t, y=v_blue, mode="lines", name="v_blue", line=dict(color="royalblue")),
        ],
        layout=go.Layout(
            height=300,
            xaxis=dict(title="time, t (s)"),
            yaxis=dict(title="velocity, v (m/s)", range=[-velocity_limit, velocity_limit]),
            legend=dict(orientation="h", y=1.1),
        ),
    )
    st.plotly_chart(velocity_fig, use_container_width=True)

    acceleration_fig = go.Figure(
        data=[
            go.Scatter(x=t, y=np.full_like(t, a_red), mode="lines", name="a_red", line=dict(color="crimson")),
            go.Scatter(x=t, y=np.full_like(t, a_blue), mode="lines", name="a_blue", line=dict(color="royalblue")),
        ],
        layout=go.Layout(
            height=300,
            xaxis=dict(title="time, t (s)"),
            yaxis=dict(title="acceleration, a (m/s^2)", range=[-acceleration_limit, acceleration_limit]),
            legend=dict(orientation="h", y=1.1),
        ),
    )
    st.plotly_chart(acceleration_fig, use_container_width=True)
    st.caption(
        f"F_red = F_blue = {force:g} N - a_red = {a_red:g} m/s^2 - "
        f"a_blue = {a_blue:g} m/s^2"
    )