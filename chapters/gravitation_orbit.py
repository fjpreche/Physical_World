"""Satellite motion under Earth's gravitational attraction."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st


G = 6.67430e-11
EARTH_MASS = 5.9722e24
EARTH_RADIUS = 6.371e6


def _trajectory(initial_height, initial_speed, duration):
    """Integrate a satellite trajectory with velocity-Verlet time steps."""
    gravitational_parameter = G * EARTH_MASS
    time_step = 2.0
    position = np.array([0.0, EARTH_RADIUS + initial_height])
    velocity = np.array([initial_speed, 0.0])
    time = 0.0
    times = [time]
    positions = [position.copy()]
    impacted = False

    def acceleration(point):
        distance = np.linalg.norm(point)
        return -gravitational_parameter * point / distance ** 3

    current_acceleration = acceleration(position)
    while time < duration:
        step = min(time_step, duration - time)
        next_position = position + velocity * step + 0.5 * current_acceleration * step ** 2
        next_distance = np.linalg.norm(next_position)

        if next_distance <= EARTH_RADIUS:
            current_distance = np.linalg.norm(position)
            fraction = (current_distance - EARTH_RADIUS) / (current_distance - next_distance)
            position = position + fraction * (next_position - position)
            time += fraction * step
            times.append(time)
            positions.append(position.copy())
            impacted = True
            break

        next_acceleration = acceleration(next_position)
        velocity += 0.5 * (current_acceleration + next_acceleration) * step
        position = next_position
        current_acceleration = next_acceleration
        time += step
        times.append(time)
        positions.append(position.copy())

    specific_energy = 0.5 * initial_speed ** 2 - gravitational_parameter / (EARTH_RADIUS + initial_height)
    return np.asarray(times), np.asarray(positions), impacted, specific_energy


def render_earth_satellite_orbit():
    st.markdown(
        "A satellite starts above Earth's north pole with an initial horizontal "
        r"velocity $v_0$. Earth's gravity continuously changes its direction: "
        r"$\vec{a}=-GM\vec{r}/r^3$. Tune the height and speed to compare impact, "
        "bound orbit, and escape. The orbital plane is shown edge-on; air resistance "
        "and Earth's rotation are ignored."
    )

    gravitational_parameter = G * EARTH_MASS
    col1, col2, col3 = st.columns(3)
    with col1:
        height_km = st.slider("Initial height, h (km)", min_value=100, max_value=2000, value=400, step=50)
    with col2:
        speed_km_s = st.slider("Horizontal speed, v0 (km/s)", min_value=0.0, max_value=12.0, value=0.0, step=0.1)
    with col3:
        duration_minutes = st.slider("Simulation duration (min)", min_value=30, max_value=180, value=120, step=15)

    initial_height = height_km * 1000.0
    initial_speed = speed_km_s * 1000.0
    initial_radius = EARTH_RADIUS + initial_height
    circular_speed = np.sqrt(gravitational_parameter / initial_radius)
    escape_speed = np.sqrt(2.0 * gravitational_parameter / initial_radius)
    times, positions, impacted, specific_energy = _trajectory(
        initial_height, initial_speed, duration_minutes * 60.0
    )

    frame_indices = np.unique(np.linspace(0, len(times) - 1, min(180, len(times))).astype(int))
    positions_km = positions / 1000.0
    earth_radius_km = EARTH_RADIUS / 1000.0
    plot_radius = max(np.max(np.linalg.norm(positions_km, axis=1)), earth_radius_km) * 1.12

    if impacted:
        status = f"Impact after {times[-1] / 60:.2f} min"
    elif specific_energy < 0:
        status = "Bound orbit: the satellite remains above Earth's surface"
    else:
        status = "Escape trajectory: the satellite is not gravitationally bound"

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[positions_km[0, 0]], y=[positions_km[0, 1]],
                mode="lines", line=dict(color="#e9a23b", width=2), name="trajectory",
            ),
            go.Scatter(
                x=[positions_km[0, 0]], y=[positions_km[0, 1]],
                mode="markers", marker=dict(size=13, color="#e9a23b", line=dict(color="white", width=2)),
                name="satellite",
            ),
        ],
        layout=go.Layout(
            height=620,
            title=dict(text=status, x=0.5),
            xaxis=dict(title="horizontal distance (km)", range=[-plot_radius, plot_radius], zeroline=False),
            yaxis=dict(
                title="distance from Earth's centre (km)", range=[-plot_radius, plot_radius],
                scaleanchor="x", scaleratio=1, zeroline=False,
            ),
            showlegend=False,
            shapes=[
                dict(
                    type="circle", xref="x", yref="y",
                    x0=-earth_radius_km, y0=-earth_radius_km,
                    x1=earth_radius_km, y1=earth_radius_km,
                    fillcolor="#277da1", line=dict(color="#185b78", width=2), layer="below",
                )
            ],
            annotations=[dict(x=0, y=0, text="Earth", showarrow=False, font=dict(color="white", size=18))],
            updatemenus=[
                dict(
                    type="buttons", showactive=False, x=0.0, y=1.12, xanchor="left",
                    buttons=[
                        dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=35, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                        dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                    ],
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(
                            method="animate",
                            args=[[f"frame{frame_number}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                            label=f"{times[index] / 60:.1f}",
                        )
                        for frame_number, index in enumerate(frame_indices)
                    ],
                    x=0.0, y=-0.08, len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"frame{frame_number}",
                data=[
                    go.Scatter(x=positions_km[:index + 1, 0], y=positions_km[:index + 1, 1]),
                    go.Scatter(x=[positions_km[index, 0]], y=[positions_km[index, 1]]),
                ],
            )
            for frame_number, index in enumerate(frame_indices)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"At h = {height_km:g} km: circular speed = {circular_speed / 1000:.2f} km/s; "
        f"escape speed = {escape_speed / 1000:.2f} km/s. A trajectory that intersects "
        "Earth impacts its surface; a bound trajectory that stays clear is an orbit."
    )


def render_iss_weightlessness():
    st.markdown(
        "The ISS and its astronaut are both in continuous free fall around Earth. "
        "Gravity is still acting on them, but it accelerates them together, so the "
        "astronaut has no supporting floor force and appears weightless. The empty "
        "square represents the ISS; the circle inside it represents the astronaut."
    )

    initial_height = 405_000.0
    initial_radius = EARTH_RADIUS + initial_height
    gravitational_parameter = G * EARTH_MASS
    circular_speed = np.sqrt(gravitational_parameter / initial_radius)

    col1, col2 = st.columns(2)
    with col1:
        speed_km_s = st.slider(
            "Initial horizontal speed, v0 (km/s)",
            min_value=0.0,
            max_value=12.0,
            value=7.7,
            step=0.1,
        )
    with col2:
        duration_minutes = st.slider(
            "Simulation duration (min)",
            min_value=20,
            max_value=150,
            value=100,
            step=10,
        )

    times, positions, impacted, specific_energy = _trajectory(
        initial_height,
        speed_km_s * 1000.0,
        duration_minutes * 60.0,
    )
    frame_indices = np.unique(np.linspace(0, len(times) - 1, min(180, len(times))).astype(int))
    positions_km = positions / 1000.0
    earth_radius_km = EARTH_RADIUS / 1000.0
    plot_radius = max(np.max(np.linalg.norm(positions_km, axis=1)), earth_radius_km) * 1.12

    if impacted:
        status = f"ISS and astronaut impact Earth after {times[-1] / 60:.2f} min"
    elif specific_energy < 0:
        status = "Bound trajectory: ISS and astronaut remain in orbit"
    else:
        status = "Unbound trajectory: ISS and astronaut escape Earth"

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[positions_km[0, 0]],
                y=[positions_km[0, 1]],
                mode="lines",
                line=dict(color="#e9a23b", width=2),
                name="orbit path",
            ),
            go.Scatter(
                x=[positions_km[0, 0]],
                y=[positions_km[0, 1]],
                mode="markers",
                marker=dict(symbol="square-open", size=40, color="#f4f1de", line=dict(width=3)),
                name="ISS",
            ),
            go.Scatter(
                x=[positions_km[0, 0]],
                y=[positions_km[0, 1]],
                mode="markers",
                marker=dict(symbol="circle", size=12, color="#f4a261", line=dict(color="white", width=1)),
                name="astronaut",
            ),
        ],
        layout=go.Layout(
            height=620,
            title=dict(text=status, x=0.5),
            xaxis=dict(title="horizontal distance (km)", range=[-plot_radius, plot_radius], zeroline=False),
            yaxis=dict(
                title="distance from Earth's centre (km)",
                range=[-plot_radius, plot_radius],
                scaleanchor="x",
                scaleratio=1,
                zeroline=False,
            ),
            legend=dict(orientation="h", y=1.08),
            shapes=[
                dict(
                    type="circle",
                    xref="x",
                    yref="y",
                    x0=-earth_radius_km,
                    y0=-earth_radius_km,
                    x1=earth_radius_km,
                    y1=earth_radius_km,
                    fillcolor="#277da1",
                    line=dict(color="#185b78", width=2),
                    layer="below",
                )
            ],
            annotations=[dict(x=0, y=0, text="Earth", showarrow=False, font=dict(color="white", size=18))],
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    x=0.0,
                    y=1.16,
                    xanchor="left",
                    buttons=[
                        dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=35, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                        dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                    ],
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(
                            method="animate",
                            args=[[f"frame{frame_number}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                            label=f"{times[index] / 60:.1f}",
                        )
                        for frame_number, index in enumerate(frame_indices)
                    ],
                    x=0.0,
                    y=-0.08,
                    len=1.0,
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"frame{frame_number}",
                data=[
                    go.Scatter(x=positions_km[:index + 1, 0], y=positions_km[:index + 1, 1]),
                    go.Scatter(x=[positions_km[index, 0]], y=[positions_km[index, 1]]),
                    go.Scatter(x=[positions_km[index, 0]], y=[positions_km[index, 1]]),
                ],
            )
            for frame_number, index in enumerate(frame_indices)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Initial height: 405 km. Circular speed at this altitude: {circular_speed / 1000:.2f} km/s. "
        "The ISS and astronaut markers share the same computed position at every instant; "
        "their sizes are enlarged for visibility."
    )