import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engines.demand_forecaster import forecast_trend, get_trend_direction
from config.settings import APP_NAME
from utils.data_paths import LEGACY_FASHION_CSV, LEGACY_TRAVEL_CSV


st.set_page_config(
    page_title=f"{APP_NAME} Dashboard",
    page_icon="T",
    layout="wide",
)


@st.cache_data
def load_frame(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index.name = "date"
    return df


def build_summary(df, label):
    if df.empty:
        return {"label": label, "items": 0, "latest": "Not available"}
    latest = df.index.max().strftime("%d %b %Y")
    return {"label": label, "items": len(df.columns), "latest": latest}


def trend_table(df):
    if df.empty:
        return pd.DataFrame(columns=["name", "avg_score"])
    recent = df.tail(4).mean().sort_values(ascending=False)
    return recent.reset_index().rename(columns={"index": "name", 0: "avg_score"})


fashion_df = load_frame(LEGACY_FASHION_CSV)
travel_df = load_frame(LEGACY_TRAVEL_CSV)

st.title(f"{APP_NAME} Big Data Analysis Dashboard")
st.caption("Google Trends ingestion, Spark-ready analytics, and Streamlit reporting in one repository.")

fashion_summary = build_summary(fashion_df, "Fashion keywords")
travel_summary = build_summary(travel_df, "Travel destinations")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Fashion series", fashion_summary["items"])
c2.metric("Travel series", travel_summary["items"])
c3.metric("Fashion updated", fashion_summary["latest"])
c4.metric("Travel updated", travel_summary["latest"])

page = st.sidebar.radio("View", ["Overview", "Fashion Trends", "Travel Trends", "Forecast"])

if page == "Overview":
    left, right = st.columns(2)

    with left:
        st.subheader("Top fashion signals")
        st.dataframe(trend_table(fashion_df).head(10), use_container_width=True, hide_index=True)

    with right:
        st.subheader("Top travel signals")
        st.dataframe(trend_table(travel_df).head(10), use_container_width=True, hide_index=True)

elif page == "Fashion Trends":
    st.subheader("Fashion trend explorer")
    if fashion_df.empty:
        st.warning("Fashion CSV data is not available.")
    else:
        selection = st.multiselect(
            "Choose fashion keywords",
            fashion_df.columns.tolist(),
            default=fashion_df.columns.tolist()[: min(3, len(fashion_df.columns))],
        )
        if selection:
            chart_df = fashion_df[selection].reset_index().melt(id_vars="date", var_name="keyword", value_name="score")
            fig = px.line(chart_df, x="date", y="score", color="keyword", title="Fashion interest over time")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(trend_table(fashion_df[selection]), use_container_width=True, hide_index=True)

elif page == "Travel Trends":
    st.subheader("Travel trend explorer")
    if travel_df.empty:
        st.warning("Travel CSV data is not available.")
    else:
        selection = st.multiselect(
            "Choose destinations",
            travel_df.columns.tolist(),
            default=travel_df.columns.tolist()[: min(4, len(travel_df.columns))],
        )
        if selection:
            chart_df = travel_df[selection].reset_index().melt(id_vars="date", var_name="destination", value_name="score")
            fig = px.area(chart_df, x="date", y="score", color="destination", title="Travel interest over time")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(trend_table(travel_df[selection]), use_container_width=True, hide_index=True)

elif page == "Forecast":
    st.subheader("Forecast viewer")
    dataset = st.selectbox("Dataset", ["Fashion", "Travel"])
    source_df = fashion_df if dataset == "Fashion" else travel_df

    if source_df.empty:
        st.warning(f"{dataset} data is not available.")
    else:
        series_name = st.selectbox("Series", source_df.columns.tolist())
        history = source_df[series_name]
        forecast_df = forecast_trend(history, periods=8, freq="W")
        info = get_trend_direction(forecast_df)

        m1, m2, m3 = st.columns(3)
        m1.metric("Direction", info["direction"].capitalize())
        m2.metric("Projected change", f"{info['change_pct']:+.1f}%")
        m3.metric("Peak date", info["peak_date"])

        history_df = history.reset_index()
        history_df.columns = ["date", "actual"]
        future_df = forecast_df[["ds", "yhat"]].rename(columns={"ds": "date", "yhat": "forecast"})
        fig = px.line(history_df, x="date", y="actual", title=f"{series_name} forecast")
        fig.add_scatter(x=future_df["date"], y=future_df["forecast"], mode="lines", name="forecast")
        st.plotly_chart(fig, use_container_width=True)
