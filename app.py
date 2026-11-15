import streamlit as st
import pandas as pd
from src.data import load_demo_data, validate_columns
from src.analysis import summary_metrics
from src.features import add_temporal_features

st.set_page_config(page_title="Autonomous Driving Risk Intelligence", layout="wide")
st.title("🚗 Autonomous Driving Risk Intelligence")
st.caption("Telemetry exploration prototype — not a certified driver-assistance or autonomous-driving system.")

df = load_demo_data()
st.warning("DEMO MODE: this is synthetic data created for software testing. It is not real vehicle telemetry and is not used to claim predictive performance.")

st.subheader("Telemetry sample")
st.dataframe(df.head(15), use_container_width=True)

df = add_temporal_features(df, sequence_col=None)
metrics = summary_metrics(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{metrics['observations']:,}")
c2.metric("Mean speed", f"{metrics['mean_speed']:.1f} km/h")
c3.metric("Mean obstacle distance", f"{metrics['mean_distance']:.1f} m")
c4.metric("Brake-active rows", f"{metrics['brake_rate']:.1%}")

st.subheader("Speed and obstacle distance")
st.scatter_chart(df, x="obstacle_distance_m", y="speed_kmh", color="scenario")
st.subheader("Speed over time")
st.line_chart(df.set_index("timestamp_s")[["speed_kmh"]])
st.subheader("Distance change")
st.line_chart(df.set_index("timestamp_s")[["distance_change_m"]])

st.info("Next: replace demo data with a properly documented real dataset and independently annotated target before any machine-learning claims.")
