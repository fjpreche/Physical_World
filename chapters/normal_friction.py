"""Illustrations for normal force and friction."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st


GRAVITY = 9.81
BOX_MASS = 1.0
MATERIALS = {
    "Glass on glass (dry)": (0.94, 0.40),
    "Ice on ice (clean, 0 C)": (0.10, 0.02),
    "Rubber on dry concrete": (1.00, 0.80),
    "Rubber on wet concrete": (0.70, 0.50),
    "Steel on ice": (0.10, 0.05),
    "Steel on steel (dry hard steel)": (0.78, 0.42),
    "Teflon on Teflon": (0.04, 0.04),
    "Wood on wood": (0.35, 0.30),
}


def _free_body_figure(force, friction, normal, weight, sliding):
    force_scale = max(force, friction, 0.1)
    friction_length = 1.2 * friction / force_scale
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[0], y=[0], mode="markers+text", text=["1 kg box"], textposition="middle center",
                marker=dict(symbol="square", size=58, color="#f4f1de", line=dict(color="#264653", width=2)),
                textfont=dict(color="#264653", size=12),
            )
        ]
    )
    arrow_style = dict(showarrow=True, arrowhead=3, arrowsize=1.4, arrowwidth=3, axref="x", ayref="y")
    force_length = 1.2 * force / force_scale
    fig.update_layout(
        height=360,
        margin=dict(t=45, b=25, l=25, r=25),
        title="Free-body diagram (arrow lengths are schematic)",
        xaxis=dict(range=[-2.3, 2.3], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-2.3, 2.3], visible=False),
        showlegend=False,
        annotations=[
            dict(x=1.65, y=0, ax=1.65 - force_length, ay=0, text=f"F = {force:.2f} N", arrowcolor="#2a9d8f", font=dict(color="#176b61"), **arrow_style),
            dict(x=-1.65, y=0, ax=-1.65 + friction_length, ay=0, text=f"f = {friction:.2f} N", arrowcolor="#e76f51", font=dict(color="#b64c35"), **arrow_style),
            dict(x=0, y=1.65, ax=0, ay=0.45, text=f"N = {normal:.2f} N", arrowcolor="#457b9d", font=dict(color="#315c76"), **arrow_style),
            dict(x=0, y=-1.65, ax=0, ay=-0.45, text=f"mg = {weight:.2f} N", arrowcolor="#6c757d", font=dict(color="#555b61"), **arrow_style),
            dict(x=0, y=-2.15, text="Sliding" if sliding else "At rest", showarrow=False, font=dict(size=13)),
        ],
    )
    return fig


def _motion_figure(acceleration, sliding):
    duration = 3.0
    times = np.linspace(0.0, duration, 60)
    positions = 0.5 * acceleration * times ** 2 if sliding else np.zeros_like(times)
    maximum_position = float(positions[-1])
    padding = max(1.0, 0.1 * maximum_position)
    fig = go.Figure(
        data=[
            go.Scatter(x=[-padding, maximum_position + padding], y=[0, 0], mode="lines", line=dict(color="#555555", width=5), name="table"),
            go.Scatter(
                x=[positions[0]], y=[0.25], mode="markers+text", text=["box"], textposition="middle center",
                marker=dict(symbol="square", size=42, color="#f4f1de", line=dict(color="#264653", width=2)),
                textfont=dict(color="#264653", size=12), name="box",
            ),
        ],
        layout=go.Layout(
            height=360,
            title="Box motion",
            xaxis=dict(title="position along table (m)", range=[-padding, maximum_position + padding]),
            yaxis=dict(range=[-0.4, 0.9], visible=False),
            showlegend=False,
            updatemenus=[
                dict(
                    type="buttons", showactive=False, x=0.0, y=1.15, xanchor="left",
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
                            label=f"{time:.1f}",
                        )
                        for index, time in enumerate(times)
                    ],
                    x=0.0, y=-0.08, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(name=f"frame{index}", data=[go.Scatter(), go.Scatter(x=[position], y=[0.25])])
            for index, position in enumerate(positions)
        ],
    )
    return fig, positions[-1], acceleration * duration if sliding else 0.0


def render_box_with_friction():
    st.markdown(
        r"A 1 kg box rests on a horizontal table. The table exerts the normal force "
        r"$N=mg$. Static friction adjusts to balance the push up to "
        r"$f_{s,\max}=\mu_sN$. Once $F>f_{s,\max}$, the box slides and the net "
        r"horizontal force is $F_{\rm net}=F-\mu_kN$."
    )

    coefficient_source = st.selectbox("Friction coefficients", ["Use material table", "Set coefficients manually"])
    if coefficient_source == "Use material table":
        material = st.selectbox("Material pair", list(MATERIALS), index=1)
        mu_static, mu_kinetic = MATERIALS[material]
        st.caption(f"{material}: mu_s = {mu_static:g}, mu_k = {mu_kinetic:g}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            mu_static = st.number_input("Static coefficient, mu_s", min_value=0.0, max_value=1.5, value=0.10, step=0.01)
        with col2:
            mu_kinetic = st.number_input("Kinetic coefficient, mu_k", min_value=0.0, max_value=1.5, value=0.02, step=0.01)
        if mu_kinetic > mu_static:
            st.warning("For this simple sliding model, choose mu_k no greater than mu_s.")

    force = st.slider("Applied force to the right, F (N)", min_value=0.0, max_value=20.0, value=0.5, step=0.1)
    normal = BOX_MASS * GRAVITY
    weight = BOX_MASS * GRAVITY
    maximum_static_friction = mu_static * normal
    sliding = force > maximum_static_friction

    if sliding:
        friction = mu_kinetic * normal
        net_force = force - friction
        acceleration = net_force / BOX_MASS
        state = "The push exceeds maximum static friction: the box slides to the right."
    else:
        friction = force
        net_force = 0.0
        acceleration = 0.0
        state = "Static friction balances the push: the box remains at rest."

    if mu_kinetic > mu_static:
        st.warning("The selected coefficients make the post-breakaway net force non-positive; choose mu_k <= mu_s for the illustrated rightward slide.")

    st.info(state)
    metrics = st.columns(5)
    metrics[0].metric("Normal force", f"{normal:.2f} N")
    metrics[1].metric("Max static friction", f"{maximum_static_friction:.2f} N")
    metrics[2].metric("Friction now", f"{friction:.2f} N")
    metrics[3].metric("Net horizontal force", f"{net_force:.2f} N")
    metrics[4].metric("Acceleration", f"{acceleration:.2f} m/s^2")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            _free_body_figure(force, friction, normal, weight, sliding),
            use_container_width=True,
        )
    with right:
        motion_fig, final_position, final_velocity = _motion_figure(acceleration, sliding)
        st.plotly_chart(motion_fig, use_container_width=True)

    st.caption(
        f"For m = {BOX_MASS:g} kg, N = mg = {normal:.2f} N and f_s,max = mu_s N = "
        f"{maximum_static_friction:.2f} N. Over the 3 s animation: displacement = "
        f"{final_position:.2f} m, final speed = {final_velocity:.2f} m/s."
    )