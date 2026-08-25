import os
import streamlit as st
import pandas as pd
import plotly.express as px
from code import DataHandling, PriorityCalculator

st.set_page_config(
    page_title="Flood Relief Allocation",
    page_icon="🚨",
    layout="wide"
)

st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(
                rgba(15, 23, 42, 0.88), 
                rgba(15, 23, 42, 0.94)
            ), 
            url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }

        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp label, .stApp div {
            color: #f8fafc !important;
        }

        section[data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(16px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        div[data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        [data-testid="stMetricValue"] span {
            color: #38bdf8 !important;
            font-weight: 800 !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }

        div[data-testid="stDataFrame"], .stSelectbox div[data-baseweb="select"] {
            background: rgba(30, 41, 59, 0.7) !important;
            backdrop-filter: blur(12px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(APP_DIR, "flood_data.csv")

with st.sidebar:
    st.title("Data Controls")
    uploaded = st.file_uploader("Upload Flood CSV", type="csv")
    
    if uploaded is not None:
        source = uploaded.getvalue()
        st.caption(f"Loaded: `{uploaded.name}`")
    else:
        source = SAMPLE_FILE if os.path.exists(SAMPLE_FILE) else "flood_data.csv"
        st.caption("Using default dataset")

    try:
        years = DataHandling(source).available_years()
        selected_year = st.selectbox("Assessment Year", years, index=len(years)-1 if years else 0)
    except Exception as e:
        st.error(f"Error loading years: {e}")
        st.stop()

    top_n = st.slider("Chart Items", min_value=3, max_value=20, value=8)

try:
    dh = DataHandling(source, selected_year)
    data = dh.load()
    
    calc = PriorityCalculator(data)
    calc.normalize()
    ranked_df, emergency_index = calc.score()
except Exception as e:
    st.error(f"Failed to process dataset: {e}")
    st.stop()

st.title("Disaster Relief Allocation System")
st.caption(f"District-level flood impact assessment and resource prioritization for **{selected_year}**.")

st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric("State Emergency Index", f"{emergency_index:.2f}")

with col2:
    with st.container(border=True):
        st.metric("Districts Assessed", len(ranked_df))

with col3:
    top_district = ranked_df.iloc[0]["District"]
    with st.container(border=True):
        st.metric("Highest Priority", top_district)

with col4:
    top_score = ranked_df.iloc[0]["priority_score"]
    with st.container(border=True):
        st.metric("Peak Severity Score", f"{top_score:.3f}")

st.write("")

left_col, right_col = st.columns([1.1, 0.9], gap="large")

with left_col:
    st.subheader("Priority Distribution")
    chart_df = ranked_df.head(top_n).sort_values("priority_score", ascending=True)
    
    fig = px.bar(
        chart_df,
        x="priority_score",
        y="District",
        orientation="h",
        color="priority_score",
        color_continuous_scale=["#64748b", "#f59e0b", "#dc2626"],
        text_auto=".3f"
    )
    fig.update_layout(
        height=380,
        margin=dict(l=0, r=20, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_title="Severity Score",
        yaxis_title=None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.15)"),
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Top Action List")
    
    top_table = ranked_df.head(5)[
        ["District", "Human_Lives_Lost", "Population_Affected", "priority_score"]
    ].rename(columns={
        "Human_Lives_Lost": "Lives Lost",
        "Population_Affected": "Affected Pop."
    })
    
    st.dataframe(
        top_table,
        column_config={
            "priority_score": st.column_config.ProgressColumn(
                "Priority Score",
                format="%.3f",
                min_value=0,
                max_value=float(ranked_df["priority_score"].max())
            ),
            "Affected Pop.": st.column_config.NumberColumn(format="%d"),
            "Lives Lost": st.column_config.NumberColumn(format="%d"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.download_button(
        label="Download Allocation Report (.CSV)",
        data=ranked_df.to_csv(index=False).encode("utf-8"),
        file_name=f"relief_priority_{selected_year}.csv",
        mime="text/csv",
        use_container_width=True
    )

with st.expander("Inspect Raw District Dataset"):
    st.dataframe(ranked_df, use_container_width=True, hide_index=True)
