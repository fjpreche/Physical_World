"""Entry point for the PX1016 interactive physics illustrations app."""
import streamlit as st

from chapters import kinematics_1d, kinematics_2d, newtons_laws, projectile_motion

st.set_page_config(page_title="The Physical World: Interactive Illustrations", layout="wide")

# Map chapter name -> {illustration name: render function}
CHAPTERS = {
    "1. Kinematics in one dimension": {
        "Constant velocity motion": kinematics_1d.render_constant_velocity,
        "Accelerate, cruise, decelerate": kinematics_1d.render_accelerate_cruise_decelerate,
    },
    "2. Kinematics in two dimensions": {
        "Constant velocity motion": kinematics_2d.render_constant_velocity_2d,
    },
    "3. Projectile motion": {
        "Launch from height h": projectile_motion.render_projectile,
        "Compare two trajectories": projectile_motion.render_compare_two_projectiles,
    },
    "4. Newton's laws of motion": {
        "Two ice skaters push apart": newtons_laws.render_ice_skaters_push,
    },
}

st.title("The Physical World: Interactive Illustrations")

chapter = st.sidebar.selectbox("Chapter", list(CHAPTERS.keys()))
illustration = st.sidebar.selectbox("Illustration", list(CHAPTERS[chapter].keys()))

st.header(f"{chapter} — {illustration}")

CHAPTERS[chapter][illustration]()
