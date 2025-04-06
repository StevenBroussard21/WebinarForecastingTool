import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(page_title="Campaign Planning Suite", layout="wide")

# ==== BRANDING: Logo + CSS Styling ====
from PIL import Image
import os

logo_path = "evenshore agency logo (2).png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=200)
else:
    st.warning("⚠️ Branding logo not found. Please upload 'evenshore_agency_logo.png' to the app directory.")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1500px;
            margin: auto;
        }

        .stButton>button {
            background: linear-gradient(90deg, #FDBB2D, #F25C26);
            border: none;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }

        .stDownloadButton>button {
            background: #F25C26;
            border: none;
            color: white;
            border-radius: 6px;
        }

        .stMetric {
            background: #fff3e6;
            border-radius: 12px;
            padding: 0.75rem;
        }

        h1, h2, h3 {
            color: #F25C26;
        }

        .stTabs [role="tablist"] > div[aria-selected="true"] {
            border-bottom: 3px solid #F25C26;
            color: #F25C26;
        }
    </style>
""", unsafe_allow_html=True)



# Inject layout styling for full-width and padding
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1500px;
            margin: auto;
        }
        .element-container:has(.stRadio) {
            margin-bottom: 0.5rem !important;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .stMetric {
            margin-bottom: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("# Campaign Planning Suite")
st.markdown("Use this tool to forecast webinar campaign outcomes and profitability based on ad spend, conversion rates, and product details.")

# Tabs
forecast_tab, planner_tab, pacing_tab, retargeting_tab  = st.tabs(["Webinar Forecast", "Multi-Channel Budget Planner", "Timeline + Spend Tracker", "Retargeting ROI Estimator"])

# --------------------------
# TAB 1: Webinar Forecast (Your Full Original Code)
# --------------------------
with forecast_tab:
    sidebar, main = st.columns([1, 3])

    with sidebar:
        st.markdown("### Configure Your Campaign")
        mode = st.radio("Input Method", ["Manual Input", "Upload CSV Data"])

        benchmarks = {
            "landing_cr": 25, "attendance_rate": 40, "lead_rate": 25,
            "sales_rate": 15, "roas": 3.0, "cpl": 30, "profit_margin": 25
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

        use_benchmarks = st.session_state.get("use_benchmarks", False)
        bm_values = st.session_state.get("benchmark_values", benchmarks)

        with st.expander("Budget & Cost"):
            budget = st.number_input("Total Ad Budget ($)", min_value=0.0, value=1000.0)
            cpc = st.number_input("Estimated Cost Per Click ($)", min_value=0.01, value=bm_values.get("cpc", 1.5))

        with st.expander("Funnel Conversion Rates"):
            landing_cr = st.slider("Landing Page Conversion Rate (%)", 0, 100, bm_values.get("landing_cr", 25))
            attendance_rate = st.slider("Signup to Attendee Rate (%)", 0, 100, bm_values.get("attendance_rate", 50))
            lead_rate = st.slider("Attendee to Qualified Lead Rate (%)", 0, 100, bm_values.get("lead_rate", 30))
            sales_rate = st.slider("Lead to Sale Conversion Rate (%)", 0, 100, bm_values.get("sales_rate", 20))
            treat_all_as_leads = st.checkbox("Treat all webinar attendees as qualified leads?", value=False)

        with st.expander("Product Details"):
            avg_deal_value = st.number_input("Average Deal Value ($)", min_value=0.0, value=500.0)
            cogs_per_sale = st.number_input("Cost of Goods per Sale ($)", min_value=0.0, value=100.0)

    with main:
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
            "Profit Margin %": profit_margin
        }

        st.subheader("📊 Forecast Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Clicks", f"{clicks:.0f}")
        col2.metric("Signups", f"{signups:.0f}")
        col3.metric("Attendees", f"{attendees:.0f}")
        col1.metric("Qualified Leads", f"{leads:.0f}")
        col2.metric("Sales", f"{sales:.0f}")
        col3.metric("Estimated Revenue", f"${revenue:,.2f}")
        col1.metric("Cost per Attendee", f"${cost_per_attendee:.2f}")
        col2.metric("Cost per Lead", f"${cost_per_lead:.2f}", delta=f"vs benchmark: ${benchmarks['cpl']}")
        col3.metric("ROAS", f"{roas:.2f}x")
        col1.metric("Total COGS", f"${total_cogs:.2f}")
        col2.metric("Gross Profit", f"${gross_profit:.2f}")
        col3.metric("Net Profit", f"${net_profit:.2f}")
        st.metric("Profit Margin", f"{profit_margin:.2f}%", delta=f"vs benchmark: {benchmarks['profit_margin']}%")

        st.markdown("### 🔽 Funnel Visualization")
        funnel_stages = ["Clicks", "Signups", "Attendees", "Qualified Leads", "Sales"]
        funnel_values = [clicks, signups, attendees, leads, sales]
        fig = go.Figure(go.Funnel(y=funnel_stages, x=funnel_values, textinfo="value+percent previous", marker={"color": "royalblue"}))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Conversion Rates vs Benchmarks")
        chart_df = pd.DataFrame({
            "Stage": ["Landing Page CR", "Attendance Rate", "Lead Rate", "Sales Rate"],
            "Your Rates (%)": [landing_cr, attendance_rate, 100 if treat_all_as_leads else lead_rate, sales_rate],
            "Benchmark (%)": [benchmarks['landing_cr'], benchmarks['attendance_rate'], benchmarks['lead_rate'], benchmarks['sales_rate']]
        })
        st.plotly_chart(px.bar(chart_df, x="Stage", y=["Your Rates (%)", "Benchmark (%)"], barmode="group"), use_container_width=True)

        st.markdown("### 💰 ROAS Performance")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=roas,
            delta={'reference': benchmarks['roas']},
            gauge={
                'axis': {'range': [0, max(roas * 1.5, 5)]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, benchmarks['roas']], 'color': "lightgray"},
                    {'range': [benchmarks['roas'], roas], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': benchmarks['roas']
                }
            },
            title={'text': "Return on Ad Spend (ROAS)"}
        ))
        st.plotly_chart(gauge, use_container_width=True)

        st.download_button(
            "Download Forecast as CSV",
            pd.DataFrame([data]).to_csv(index=False).encode('utf-8'),
            file_name="webinar_forecast.csv"
        )


# --------------------------
# TAB 2: Multi-Channel Budget Planner
# --------------------------
with planner_tab:
    st.markdown("## Multi-Channel Budget Planner")
    st.markdown("Distribute your ad budget across platforms and forecast performance based on campaign KPIs.")

    total_budget = st.number_input("Total Campaign Budget ($)", min_value=0.0, value=5000.0)
    kpi_goal = st.selectbox("Select your campaign goal:", ["Clicks", "Leads", "Sales", "Impressions"])

    channels = ["Meta", "Google", "LinkedIn", "YouTube", "TikTok"]
    allocations = {}
    col1, col2 = st.columns(2)
    for i, ch in enumerate(channels):
        with (col1 if i % 2 == 0 else col2):
            allocations[ch] = st.slider(f"{ch} Allocation (%)", 0, 100, 20)

    if sum(allocations.values()) != 100:
        st.warning(f"Your allocations add up to {sum(allocations.values())}%. Please adjust to 100%.")
    else:
        st.success("✅ Allocation adds up to 100%")

        default_kpis = {
            "Clicks": {"Meta": 2.5, "Google": 3.0, "LinkedIn": 4.0, "YouTube": 2.8, "TikTok": 2.0},
            "Leads": {"Meta": 30, "Google": 40, "LinkedIn": 80, "YouTube": 35, "TikTok": 25},
            "Sales": {"Meta": 100, "Google": 120, "LinkedIn": 200, "YouTube": 110, "TikTok": 90},
            "Impressions": {"Meta": 6, "Google": 7, "LinkedIn": 9, "YouTube": 5, "TikTok": 4}
        }

        st.markdown("### Customize Cost per Result")
        enable_roi = st.checkbox("Estimate revenue and ROI?")

        use_roi_values = {}
        if enable_roi:
            st.caption("Enter the value per lead or sale for each platform.")
            for ch in channels:
                if kpi_goal == "Sales":
                    use_roi_values[ch] = st.number_input(
                        f"{ch} - Average Order Value ($)",
                        min_value=1.0,
                        value=250.0,
                        step=10.0,
                        key=f"roi_sale_{ch}"
                    )
                elif kpi_goal == "Leads":
                    use_roi_values[ch] = st.number_input(
                        f"{ch} - Value per Lead ($)",
                        min_value=1.0,
                        value=50.0,
                        step=5.0,
                        key=f"roi_lead_{ch}"
                    )

        results = []
        total_forecast = 0
        total_revenue = 0
        total_roi = 0
        roi_count = 0

        for ch in channels:
            cost = st.number_input(
                f"{ch} - Cost per {kpi_goal}",
                value=float(default_kpis[kpi_goal][ch]),
                min_value=0.01,
                step=0.01,
                key=f"cost_{ch}"
            )
            budget_ch = (allocations[ch] / 100) * total_budget
            forecast = (budget_ch / cost) * 1000 if kpi_goal == "Impressions" else budget_ch / cost
            total_forecast += forecast

            cost_per_result = budget_ch / forecast if forecast > 0 else 0
            break_even_cpr = None
            roi = None
            revenue = None
            warning_msg = ""

            if enable_roi and ch in use_roi_values:
                break_even_cpr = use_roi_values[ch]
                revenue = forecast * break_even_cpr
                roi = ((revenue - budget_ch) / budget_ch * 100) if budget_ch > 0 else 0
                total_revenue += revenue
                total_roi += roi
                roi_count += 1
                if roi < 0:
                    warning_msg = "⚠️ Negative ROI"

            results.append({
                "Channel": ch,
                "Allocated Budget ($)": round(budget_ch, 2),
                f"Cost per {kpi_goal}": round(cost, 2),
                f"Forecasted {kpi_goal}": int(forecast),
                "Cost per Result ($)": round(cost_per_result, 2),
                "Break-even CPR ($)": round(break_even_cpr, 2) if break_even_cpr else None,
                "Estimated Revenue ($)": round(revenue, 2) if revenue else None,
                "ROI (%)": round(roi, 2) if roi is not None else None,
                "Notes": warning_msg
            })

        result_df = pd.DataFrame(results)

        def highlight_expensive(s):
            return ["background-color: #ffe6e6" if (s["Break-even CPR ($)"] is not None and s["Cost per Result ($)"] > s["Break-even CPR ($)"]) else "" for i in s.index]

        st.markdown("### 📊 Forecasted Performance by Channel")
        styled_df = result_df.style.apply(highlight_expensive, axis=1)
        st.dataframe(styled_df)

        st.markdown(f"### 📈 Total Forecasted {kpi_goal}: **{int(total_forecast):,}**")

        if enable_roi:
            avg_roi = total_roi / roi_count if roi_count > 0 else 0
            st.metric("Total Estimated Revenue", f"${total_revenue:,.2f}")
            st.metric("Average ROI Across Channels", f"{avg_roi:.2f}%")

        chart = px.bar(result_df, x="Channel", y=f"Forecasted {kpi_goal}", color="Channel", title=f"Forecasted {kpi_goal} by Channel")
        st.plotly_chart(chart, use_container_width=True)

        cost_chart = px.bar(result_df, x="Channel", y="Cost per Result ($)", color="Channel", title="Cost per Result by Channel")
        st.plotly_chart(cost_chart, use_container_width=True)

        csv_out = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Channel KPI Forecast as CSV", data=csv_out, file_name="kpi_budget_forecast.csv", mime="text/csv")

# =============================
# TAB 3: Campaign Timeline + Spend Tracker
# =============================
with pacing_tab:
    st.markdown("## 🗓️ Campaign Timeline + Spend Tracker")

    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.markdown("### Configure Timeline")
        duration_weeks = st.slider("Campaign Duration (Weeks)", min_value=1, max_value=12, value=4)
        total_budget = st.number_input("Total Campaign Budget ($)", min_value=0.0, value=10000.0)
        pacing_strategy = st.selectbox("Pacing Strategy", ["Flat", "Front-loaded", "Back-loaded"])
        cost_per_result = st.number_input("Estimated Cost per Result ($)", min_value=0.01, value=25.0)
        kpi_goal = st.selectbox("Conversion Type", ["Clicks", "Leads", "Sales"])

    with right_col:
        # Generate pacing weights
        if pacing_strategy == "Flat":
            pacing_weights = [1] * duration_weeks
        elif pacing_strategy == "Front-loaded":
            pacing_weights = list(reversed(range(1, duration_weeks + 1)))
        elif pacing_strategy == "Back-loaded":
            pacing_weights = list(range(1, duration_weeks + 1))

        total_weight = sum(pacing_weights)
        weekly_spend = [(w / total_weight) * total_budget for w in pacing_weights]
        weekly_results = [s / cost_per_result for s in weekly_spend]

        df = pd.DataFrame({
            "Week": [f"Week {i+1}" for i in range(duration_weeks)],
            "Planned Spend ($)": weekly_spend,
            f"Forecasted {kpi_goal}": weekly_results
        })
        df["Cumulative Spend"] = df["Planned Spend ($)"].cumsum()
        df["Cumulative Results"] = df[f"Forecasted {kpi_goal}"].cumsum()

        st.subheader("📅 Weekly Spend & Results Forecast")
        st.dataframe(df.style.format({
            "Planned Spend ($)": "${:,.2f}",
            f"Forecasted {kpi_goal}": "{:.0f}",
            "Cumulative Spend": "${:,.2f}",
            "Cumulative Results": "{:.0f}"
        }), use_container_width=True)

        chart = px.line(df, x="Week", y=["Planned Spend ($)", f"Forecasted {kpi_goal}"], markers=True,
                        title="Spend and Forecasted Results Over Time")
        st.plotly_chart(chart, use_container_width=True)

        st.download_button("Download Timeline Forecast as CSV", df.to_csv(index=False).encode("utf-8"),
                           file_name="timeline_forecast.csv")
# =============================
# TAB 4: Retargeting RIO Estimator
# =============================

with st.tab("Retargeting ROI Estimator"):
    st.markdown("## 🧠 Retargeting ROI Estimator (Advanced)")

    # === Section 1: Actual Campaign Recap ===
    st.markdown("### 📌 Actual Campaign Recap")
    col1, col2, col3 = st.columns(3)

    with col1:
        impressions = st.number_input("Total Impressions", value=100000)
        clicks = st.number_input("Total Clicks", value=5000)

    with col2:
        conversions = st.number_input("Total Conversions", value=700)
        spend = st.number_input("Total Spend ($)", value=6000.0)

    with col3:
        revenue = st.number_input("Total Revenue ($)", value=18000.0)
        roas = revenue / spend if spend > 0 else 0
        st.metric("ROAS", f"{roas:.2f}x")

    st.markdown("### 📊 Funnel Visualization")
    funnel_data = pd.DataFrame({
        "Stage": ["Impressions", "Clicks", "Conversions"],
        "Users": [impressions, clicks, conversions]
    })
    st.bar_chart(funnel_data.set_index("Stage"))

    st.divider()

    # === Section 2: Retargeting Strategy Builder ===
    st.markdown("### 🧱 Retargeting Strategy Builder")

    st.markdown("#### Strategy Inputs")
    num_strategies = st.slider("Number of strategies to compare", 1, 3, 2)
    strategy_data = []

    for i in range(num_strategies):
        st.subheader(f"Strategy {i+1}")
        c1, c2, c3 = st.columns(3)
        with c1:
            audience = st.selectbox(f"Audience Segment (Strategy {i+1})", ["Cart Abandoners", "Page Viewers", "Previous Purchasers"], key=f"aud_{i}")
            channel = st.selectbox(f"Channel (Strategy {i+1})", ["Display", "Social", "Email", "SMS"], key=f"chan_{i}")
        with c2:
            frequency = st.slider(f"Ad Frequency/Week (Strategy {i+1})", 1, 14, 3, key=f"freq_{i}")
            duration = st.slider(f"Duration (Days) (Strategy {i+1})", 1, 30, 7, key=f"dur_{i}")
        with c3:
            budget_pct = st.slider(f"Budget Allocation % (Strategy {i+1})", 0, 100, 25, key=f"bud_{i}")
            message_style = st.selectbox(f"CTA Style (Strategy {i+1})", ["Urgency", "Educational", "Offer-Based"], key=f"cta_{i}")

        strategy_data.append({
            "Strategy": f"Strategy {i+1}",
            "Audience": audience,
            "Channel": channel,
            "Frequency": frequency,
            "Duration": duration,
            "Budget %": budget_pct,
            "CTA Style": message_style
        })

    st.markdown("#### 📋 Strategy Comparison Table")
    st.dataframe(pd.DataFrame(strategy_data))

    st.markdown("#### 📈 Strategy Allocation Chart")
    chart_df = pd.DataFrame(strategy_data)
    pie_chart = px.pie(chart_df, names="Strategy", values="Budget %", title="Budget Allocation Across Strategies")
    st.plotly_chart(pie_chart, use_container_width=True)

    st.divider()

    # === Section 3: Performance Scenarios (Placeholder for now) ===
    st.markdown("### 📊 Retargeting Performance Scenarios")
    st.info("Simulate recovered conversions, CPA improvements, and ROAS lift.")

    st.divider()

    # === Section 4: Organic Retargeting (Placeholder for now) ===
    st.markdown("### 📬 Organic Retargeting")
    st.info("Estimate impact from email and SMS campaigns.")

    st.divider()

    # === Section 5: Insight Recommendations (Placeholder for now) ===
    st.markdown("### 💡 Insight Recommendations")
    st.info("Insights and budget recommendations based on performance and benchmarks.")
