import os
import streamlit as st
import pandas as pd
import plotly.express as px
from code import DataHandling, PriorityCalculator

st.set_page_config(
    page_title="AI Relief Allocator | Augnesh",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise-Grade CSS Injection
st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0b0f19 70%);
            color: #f8fafc;
        }
        
        /* Metric Card Glassmorphism & Animations */
        div[data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            border-color: #3b82f6 !important;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
        }

        /* Highlight Metric Numbers */
        [data-testid="stMetricValue"] span {
            color: #60a5fa !important;
            font-weight: 900 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.5px;
        }

        /* Title Gradients */
        .main-title {
            background: -webkit-linear-gradient(45deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.2rem;
            font-weight: 800;
            padding-bottom: 0px;
            margin-bottom: -10px;
        }
        
        .sub-title {
            color: #94a3b8;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 30px;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* AI Badge */
        .ai-pulse {
            display: inline-block;
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        header, footer { visibility: hidden; }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: transparent;
            border-radius: 4px;
            color: #94a3b8;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            color: #60a5fa !important;
        }
    </style>
""", unsafe_allow_html=True)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(APP_DIR, "flood_data.csv")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621040.png", width=60)
    st.title("System Controls")
    uploaded = st.file_uploader("Upload Flood CSV Data", type="csv")
    
    if uploaded is not None:
        source = uploaded.getvalue()
        st.caption(f"Status: `{uploaded.name}` Loaded")
    else:
        source = SAMPLE_FILE if os.path.exists(SAMPLE_FILE) else "flood_data.csv"
        st.caption("Status: Default DB Loaded")

    try:
        years = DataHandling(source).available_years()
        selected_year = st.selectbox("Select Assessment Year", years, index=len(years)-1 if years else 0)
    except Exception as e:
        st.error(f"Error loading years: {e}")
        st.stop()

    top_n = st.slider("Display Limit (Top Districts)", min_value=3, max_value=20, value=8)
    
    st.markdown("---")
    st.markdown('<div class="ai-pulse">● AI Engine Online</div>', unsafe_allow_html=True)
    st.caption("**Model:** Random Forest Regressor")
    st.caption("**Trees:** 100 Estimators")
    st.caption("**Target:** Logistics Prediction")

try:
    dh = DataHandling(source, selected_year)
    data = dh.load()
    
    calc = PriorityCalculator(data)
    calc.normalize()
    ranked_df, emergency_index = calc.score()
except Exception as e:
    st.error(f"Failed to process dataset: {e}")
    st.stop()

# Main Header Area
st.markdown('<h1 class="main-title">Disaster Relief Intelligence System</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Developed by Team IQX | Dynamic Resource Triage for <b>{selected_year}</b></div>', unsafe_allow_html=True)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("State Emergency Index", f"{emergency_index:.2f}", delta="Mathematical Triage", delta_color="off")
with col2:
    total_ai_camps = ranked_df["AI_Recommended_Camps"].sum()
    st.metric("Total AI Predicted Camps", int(total_ai_camps), delta="Logistics Required", delta_color="off")
with col3:
    top_district = ranked_df.iloc[0]["District"]
    st.metric("Critical Ground Zero", top_district, delta="Highest Severity", delta_color="off")
with col4:
    top_score = ranked_df.iloc[0]["priority_score"]
    st.metric("Peak Impact Score", f"{top_score:.3f}", delta="Max Threat Level", delta_color="off")

st.write("")
st.write("")

# Modern Tab Layout
tab1, tab2, tab3 = st.tabs(["🎛️ Command Center", "🧠 AI Model Analytics", "🗄️ Raw Database"])

with tab1:
    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.subheader("Severity Distribution")
        chart_df = ranked_df.head(top_n).sort_values("priority_score", ascending=True)
        
        fig = px.bar(
            chart_df,
            x="priority_score",
            y="District",
            orientation="h",
            color="priority_score",
            color_continuous_scale=["#334155", "#6366f1", "#ef4444"],
            text_auto=".3f",
            hover_data={"AI_Recommended_Camps": True, "Human_Lives_Lost": True}
        )
        fig.update_layout(
            height=420,
            margin=dict(l=0, r=20, t=10, b=10),
            coloraxis_showscale=False,
            xaxis_title="Calculated Severity Score",
            yaxis_title=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=13),
            xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)"),
        )
        fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🤖 AI Deployment Roster")
        
        top_table = ranked_df.head(10)[
            ["District", "AI_Recommended_Camps", "priority_score"]
        ].rename(columns={"AI_Recommended_Camps": "AI Camps"})
        
        st.dataframe(
            top_table,
            column_config={
                "priority_score": st.column_config.ProgressColumn(
                    "Triage Score",
                    format="%.3f",
                    min_value=0,
                    max_value=float(ranked_df["priority_score"].max())
                ),
                "AI Camps": st.column_config.NumberColumn(format="%d ⛺")
            },
            use_container_width=True,
            hide_index=True,
            height=370
        )
        
        st.download_button(
            label="Download Secure AI Report (.CSV)",
            data=ranked_df.to_csv(index=False).encode("utf-8"),
            file_name=f"team_iqx_ai_relief_{selected_year}.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab2:
    st.subheader("Random Forest Feature Geometry")
    st.markdown("This 3D spatial plot demonstrates how the AI maps multi-dimensional disaster metrics (Lives Lost vs. Villages Damaged) to output its final resource prediction (Z-Axis).")
    
    # 3D Plotly Chart for Maximum Presentation Impact
    fig_3d = px.scatter_3d(
        ranked_df,
        x='Human_Lives_Lost',
        y='Villages_Damaged',
        z='AI_Recommended_Camps',
        color='priority_score',
        hover_name='District',
        color_continuous_scale="Viridis",
        opacity=0.8,
        labels={
            'Human_Lives_Lost': 'Lives Lost (Feature 1)',
            'Villages_Damaged': 'Villages Hit (Feature 2)',
            'AI_Recommended_Camps': 'Camps Needed (Target)'
        }
    )
    fig_3d.update_layout(
        height=500,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)")
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True)
    
    with st.expander("View AI Architecture Documentation"):
        st.markdown("""
        ### Supervised Machine Learning Pipeline
        Instead of manually estimating logistics, this platform utilizes a Random Forest Regressor to analyze historical disaster metrics and forecast exact operational needs.
        
        *   **Algorithm:** `sklearn.ensemble.RandomForestRegressor`
        *   **Input Features (X):** `Population Affected`, `Villages Damaged`, `Crop Damage`, `Human Deaths`
        *   **Target Variable (y):** `Relief Camps Required`
        *   **Ensemble Methodology:** The AI trains 100 independent decision trees on the state data. Each tree votes on the required resources, and the ensemble averages the output to prevent overfitting and ensure mathematically stable predictions.
        """)

with tab3:
    st.subheader("Integrated System Database")
    st.caption("Full district-level visibility with AI appended logic.")
    st.dataframe(ranked_df, use_container_width=True, hide_index=True)
