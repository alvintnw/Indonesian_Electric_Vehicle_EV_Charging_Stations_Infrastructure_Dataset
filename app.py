import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Indonesia EV Charging Infrastructure Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Indonesian Electric Vehicle (EV) Charging Infrastructure Dashboard")
st.markdown(
    "Explore the distribution, operators, and capacity of Electric Vehicle"
    " Charging Stations (SPKLU) across Indonesia."
)


# Fungsi untuk memuat dataset CSV
@st.cache_data
def load_ev_data():
  filename = "indonesia_ev_charging_stations.csv"
  if os.path.exists(filename):
    return pd.read_csv(filename)
  else:
    return pd.DataFrame()


df = load_ev_data()

if df.empty:
  st.warning(
      "Dataset file (`indonesia_ev_charging_stations.csv`) not found. Please"
      " ensure the CSV file is uploaded."
  )
else:
  # Sidebar Filters
  st.sidebar.header("⚙️ Filter Options")

  provinces = sorted(df["province"].unique())
  selected_provinces = st.sidebar.multiselect(
      "Select Provinces:", options=provinces, default=provinces
  )

  charger_types = sorted(df["charger_type"].unique())
  selected_types = st.sidebar.multiselect(
      "Select Charger Type:", options=charger_types, default=charger_types
  )

  # Filter DataFrame
  filtered_df = df[
      (df["province"].isin(selected_provinces))
      & (df["charger_type"].isin(selected_types))
  ]

  # Metrik Ringkasan di Atas
  st.subheader("📊 Overview Summary")
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="Total Stations Selected", value=f"{len(filtered_df)} Stations"
    )
  with col2:
    total_ports = (
        filtered_df["ports_count"].sum() if not filtered_df.empty else 0
    )
    st.metric(label="Total Charging Ports", value=f"{total_ports} Ports")
  with col3:
    operational_count = len(
        filtered_df[filtered_df["status"] == "Operational"]
    )
    st.metric(
        label="Operational Status",
        value=f"{operational_count} Operational",
    )

  st.markdown("---")

  # Visualisasi Peta Persebaran (Scatter Mapbox / Scatter Geo)
  st.subheader("🗺️ Geographic Distribution of EV Stations")
  if not filtered_df.empty:
    fig_map = px.scatter_geo(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="station_name",
        size="ports_count",
        color="charger_type",
        projection="natural earth",
        title="EV Charging Stations Map across Indonesia",
    )
    fig_map.update_geos(
        fitbounds="locations",
        visible=True,
        center={"lat": -2.5489, "lon": 118.0149},
    )  # Pusat Indonesia
    st.plotly_chart(fig_map, use_container_width=True)
  else:
    st.warning("No data available for the selected filters.")

  # Bar Chart: Stasiun per Provinsi
  col_a, col_b = st.columns(2)
  with col_a:
    st.subheader("📍 Stations by Province")
    if not filtered_df.empty:
      prov_counts = (
          filtered_df["province"].value_counts().reset_index_name()
          if hasattr(pd.Series, "reset_index_name")
          else filtered_df["province"].value_counts().reset_index()
      )
      prov_counts.columns = ["Province", "Count"]
      fig_bar = px.bar(
          prov_counts,
          x="Province",
          y="Count",
          color="Province",
          title="Number of Stations per Province",
      )
      st.plotly_chart(fig_bar, use_container_width=True)

  with col_b:
    st.subheader("🔌 Charger Type Breakdown")
    if not filtered_df.empty:
      type_counts = filtered_df["charger_type"].value_counts().reset_index()
      type_counts.columns = ["Charger Type", "Count"]
      fig_pie = px.pie(
          type_counts,
          names="Charger Type",
          values="Count",
          title="Proportion of Charger Types",
          hole=0.4,
      )
      st.plotly_chart(fig_pie, use_container_width=True)

  # Raw Data Expander
  with st.expander("🔍 View Raw EV Stations Dataset"):
    st.dataframe(df, use_container_width=True)
