from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

SCORES = Path(r"C:\Users\reinh\Downloads\Projects\Output CSVs\customer_scores_final.csv")
SEGMENTS = ["Champions", "Recent", "At Risk", "Lost"]

@st.cache_data
def load_data():
    df = pd.read_csv(SCORES)
    df["log10_CLV"] = np.log10(df["CLV_12m_cutoff"].clip(lower=1))
    return df

df = load_data()

st.title("Customer Retention Dashboard")
st.caption(
    "Customers who bought before 10 Sep 2011. Churn means no purchase in the following 90 days. "
    "CLV is predicted 12-month revenue as of that date. Expected revenue at risk = churn probability × CLV."
)

segments = st.sidebar.multiselect("Segments", SEGMENTS, default=SEGMENTS)
min_risk = st.sidebar.slider("Minimum churn probability", 0.0, 1.0, 0.5, 0.05)
view = df[df["segment_name"].isin(segments) & (df["churn_probability"] >= min_risk)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(view):,}")
c2.metric("Average churn probability", f"{view['churn_probability'].mean():.0%}")
c3.metric("Likely to churn (≥50%)", f"{(view['churn_probability'] >= 0.5).sum():,}")
c4.metric("Expected revenue at risk", f"£{view['value_at_risk'].sum():,.0f}")

st.subheader("Segment summary")
summary = view.groupby("segment_name").agg(
    Customers=("churn_probability", "size"),
    Avg_churn=("churn_probability", "mean"),
    Total_CLV=("CLV_12m_cutoff", "sum"),
    Revenue_at_risk=("value_at_risk", "sum"),
)
st.dataframe(
    summary.style.format({
        "Customers": "{:,}",
        "Avg_churn": "{:.0%}",
        "Total_CLV": "£{:,.0f}",
        "Revenue_at_risk": "£{:,.0f}",
    })
)
st.bar_chart(summary["Avg_churn"])

st.subheader("Churn risk vs customer value")
st.scatter_chart(view, x="churn_probability", y="log10_CLV", color="segment_name", size=8)
st.caption("Vertical axis is log10 of 12-month CLV: 4 = £10k, 5 = £100k.")

st.subheader("Contact first: top 50 by expected revenue at risk")
priority = view.sort_values("value_at_risk", ascending=False)
show = priority[
    ["Customer ID", "segment_name", "churn_probability", "CLV_12m_cutoff", "value_at_risk", "large_order_capped"]
].head(50)
st.dataframe(
    show.style.format({
        "churn_probability": "{:.0%}",
        "CLV_12m_cutoff": "£{:,.0f}",
        "value_at_risk": "£{:,.0f}",
    })
)
st.caption("large_order_capped = 1 means the customer has an invoice above £50k. Check that order before contacting.")
st.download_button(
    "Download full priority list (CSV)",
    priority.to_csv(index=False),
    "priority_list.csv",
    "text/csv",
)