import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

# Title and Layout
st.set_page_config(page_title="Webinar Performance Forecaster", layout="wide")
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎯 Webinar Performance Forecaster")
st.markdown("Use this tool to forecast webinar campaign outcomes and profitability based on ad spend, conversion rates, and product details.")

# Sidebar Input Section
st.sidebar.title("🔧 Configure Your Campaign")
mode = st.sidebar.radio("Input Method", ["Manual Input", "Upload CSV Data"])

# Initialize variables
data = {}

# --- Benchmarks ---
benchmarks = {
    "landing_cr": 25,
    "attendance_rate": 40,
    "lead_rate": 25,
    "sales_rate": 15,
    "roas": 3.0,
    "cpl": 30,
    "profit_margin": 25
}

industry_benchmarks = {
    "SaaS": {"landing_cr": 25, "attendance_rate": 50, "lead_rate": 30, "sales_rate": 15, "cpc": 3.5},
    "Education": {"landing_cr": 20, "attendance_rate": 40, "lead_rate": 25, "sales_rate": 8, "cpc": 2.75},
    "Healthcare": {"landing_cr": 15, "attendance_rate": 35, "lead_rate": 20, "sales_rate": 10, "cpc": 4.25},
    "Consulting": {"landing_cr": 30, "attendance_rate": 60, "lead_rate": 35, "sales_rate": 25, "cpc": 3.0}
}

with st.expander("Look up Industry Benchmarks"):
    selected_industry = st.selectbox("Select your industry:", list(industry_benchmarks.keys()))
    if selected_industry:
        bm = industry_benchmarks[selected_industry]
        st.markdown(f"**Landing Page CR:** {bm['landing_cr']}%")
        st.markdown(f"**Attendance Rate:** {bm['attendance_rate']}%")
        st.markdown(f"**Lead Rate:** {bm['lead_rate']}%")
        st.markdown(f"**Sales Rate:** {bm['sales_rate']}%")
        st.markdown(f"**Avg CPC:** ${bm['cpc']}")
        if st.button("Use these benchmarks"):
            st.session_state.use_benchmarks = True
            st.session_state.benchmark_values = bm

# --- Manual Input Mode ---
if mode == "Manual Input":
    use_benchmarks = st.session_state.get("use_benchmarks", False)
    bm_values = st.session_state.get("benchmark_values", benchmarks)

    with st.sidebar.expander("Budget & Cost"):
        budget = st.number_input("Total Ad Budget ($)", min_value=0.0, value=1000.0)
        cpc = st.number_input("Estimated Cost Per Click ($)", min_value=0.01, value=bm_values.get("cpc", 1.5))

    with st.sidebar.expander("Funnel Conversion Rates"):
        landing_cr = st.slider("Landing Page Conversion Rate (%)", 0, 100, bm_values.get("landing_cr", 25))
        attendance_rate = st.slider("Signup to Attendee Rate (%)", 0, 100, bm_values.get("attendance_rate", 50))
        lead_rate = st.slider("Attendee to Qualified Lead Rate (%)", 0, 100, bm_values.get("lead_rate", 30))
        sales_rate = st.slider("Lead to Sale Conversion Rate (%)", 0, 100, bm_values.get("sales_rate", 20))
        treat_all_as_leads = st.checkbox(
            "Treat all webinar attendees as qualified leads?",
            value=False,
            help="Use if every attendee is highly relevant or gets follow-up."
        )

    with st.sidebar.expander("Product Details"):
        avg_deal_value = st.number_input("Average Deal Value ($)", min_value=0.0, value=500.0)
        cogs_per_sale = st.number_input("Cost of Goods per Sale ($)", min_value=0.0, value=100.0)

    # --- Forecast Calculations ---
    clicks = budget / cpc
    signups = clicks * (landing_cr / 100)
    attendees = signups * (attendance_rate / 100)
    leads = attendees if treat_all_as_leads else attendees * (lead_rate / 100)
    sales = leads * (sales_rate / 100)
    revenue = sales * avg_deal_value
    roas = revenue / budget if budget > 0 else 0
    cost_per_attendee = budget / attendees if attendees > 0 else 0
    cost_per_lead = budget / leads if leads > 0 else 0
    total_cogs = sales * cogs_per_sale
    gross_profit = revenue - total_cogs
    net_profit = gross_profit - budget
    profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0

    data = {
        "Clicks": clicks,
        "Signups": signups,
        "Attendees": attendees,
        "Qualified Leads": leads,
        "Sales": sales,
        "Estimated Revenue": revenue,
        "ROAS": roas,
        "Cost Per Attendee": cost_per_attendee,
        "Cost Per Lead": cost_per_lead,
        "Total COGS": total_cogs,
        "Gross Profit": gross_profit,
        "Net Profit": net_profit,
        "Profit Margin %": profit_margin,
        "Conversion Rates": {
            "Landing Page CR": landing_cr,
            "Attendance Rate": attendance_rate,
            "Lead Rate": 100 if treat_all_as_leads else lead_rate,
            "Sales Rate": sales_rate
        }
    }

    st.markdown("## 📊 Forecast Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Clicks", f"{data['Clicks']:.0f}")
    col2.metric("Signups", f"{data['Signups']:.0f}")
    col3.metric("Attendees", f"{data['Attendees']:.0f}")
    col1.metric("Qualified Leads", f"{data['Qualified Leads']:.0f}")
    col2.metric("Sales", f"{data['Sales']:.0f}")
    col3.metric("Estimated Revenue", f"${data['Estimated Revenue']:.2f}")
    col1.metric("Cost per Attendee", f"${data['Cost Per Attendee']:.2f}")
    col2.metric("Cost per Lead", f"${data['Cost Per Lead']:.2f}", delta=f"vs benchmark: ${benchmarks['cpl']}")
    col3.metric("ROAS", f"{data['ROAS']:.2f}x")
    col1.metric("Total COGS", f"${data['Total COGS']:.2f}")
    col2.metric("Gross Profit", f"${data['Gross Profit']:.2f}")
    col3.metric("Net Profit", f"${data['Net Profit']:.2f}")
    st.metric("Profit Margin", f"{data['Profit Margin %']:.2f}%", delta=f"vs benchmark: {benchmarks['profit_margin']}%")

    st.markdown("---")
    st.markdown("### 🔽 Funnel Visualization")
    funnel_stages = ["Clicks", "Signups", "Attendees", "Qualified Leads", "Sales"]
    funnel_values = [
        data["Clicks"], data["Signups"], data["Attendees"], data["Qualified Leads"], data["Sales"]
    ]
    fig = go.Figure(go.Funnel(
        y=funnel_stages,
        x=funnel_values,
        textinfo="value+percent previous",
        marker={"color": "royalblue"}
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Conversion Rates vs Benchmarks")
    conversion_labels = list(data['Conversion Rates'].keys())
    user_rates = list(data['Conversion Rates'].values())
    benchmark_rates = [
        benchmarks['landing_cr'],
        benchmarks['attendance_rate'],
        benchmarks['lead_rate'],
        benchmarks['sales_rate']
    ]
    chart_df = pd.DataFrame({
        "Stage": conversion_labels,
        "Your Rates (%)": user_rates,
        "Benchmark (%)": benchmark_rates
    })
    chart = px.bar(chart_df, x="Stage", y=["Your Rates (%)", "Benchmark (%)"], barmode="group",
                   title="Your Conversion Rates vs Industry Benchmarks")
    st.plotly_chart(chart, use_container_width=True)

    st.markdown("### 💰 ROAS Performance")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=data['ROAS'],
        delta={'reference': benchmarks['roas']},
        gauge={'axis': {'range': [0, max(data['ROAS'] * 1.5, 5)]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, benchmarks['roas']], 'color': "lightgray"},
                   {'range': [benchmarks['roas'], data['ROAS']], 'color': "lightgreen"}
               ],
               'threshold': {
                   'line': {'color': "red", 'width': 4},
                   'thickness': 0.75,
                   'value': benchmarks['roas']
               }},
        title={'text': "Return on Ad Spend (ROAS)"}
    ))
    st.plotly_chart(gauge, use_container_width=True)

    st.markdown("---")
    st.markdown("###Download Your Forecast")
    export_df = pd.DataFrame([data])
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Forecast as CSV",
        data=csv,
        file_name="webinar_forecast.csv",
        mime="text/csv"
    )

