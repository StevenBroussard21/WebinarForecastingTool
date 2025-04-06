import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io


st.markdown("# Campaign Planning Suite")
st.markdown("Use this tool to forecast webinar campaign outcomes and profitability based on ad spend, conversion rates, and product details.")

# Tabs
forecast_tab, planner_tab, pacing_tab  = st.tabs(["Webinar Forecast", "Multi-Channel Budget Planner", "Timeline + Spend Tracker"])

# --------------------------
# TAB 1: Webinar Forecast (Your Full Original Code)
# --------------------------
with forecast_tab:
    # Sidebar Input Section
    st.sidebar.title("[Webinar Sidebar]: Configure Your Campaign")
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
        funnel_values = [data[s] for s in funnel_stages]
        fig = go.Figure(go.Funnel(y=funnel_stages, x=funnel_values, textinfo="value+percent previous", marker={"color": "royalblue"}))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Conversion Rates vs Benchmarks")
        conversion_labels = list(data['Conversion Rates'].keys())
        user_rates = list(data['Conversion Rates'].values())
        benchmark_rates = [benchmarks['landing_cr'], benchmarks['attendance_rate'], benchmarks['lead_rate'], benchmarks['sales_rate']]
        chart_df = pd.DataFrame({"Stage": conversion_labels, "Your Rates (%)": user_rates, "Benchmark (%)": benchmark_rates})
        chart = px.bar(chart_df, x="Stage", y=["Your Rates (%)", "Benchmark (%)"], barmode="group", title="Your Conversion Rates vs Industry Benchmarks")
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
        st.markdown("### Download Your Forecast")
        export_df = pd.DataFrame([data])
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Forecast as CSV", data=csv, file_name="webinar_forecast.csv", mime="text/csv")

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
    st.sidebar.title("[Timeline Sidebar]: Timeline Settings")
    duration_weeks = st.sidebar.slider("Campaign Duration (Weeks)", min_value=1, max_value=12, value=4)
    total_budget = st.sidebar.number_input("Total Campaign Budget ($)", min_value=0.0, value=10000.0)
    pacing_strategy = st.sidebar.selectbox("Pacing Strategy", ["Flat", "Front-loaded", "Back-loaded"])
    cost_per_result = st.sidebar.number_input("Estimated Cost per Result ($)", min_value=0.01, value=25.0)
    kpi_goal = st.sidebar.selectbox("Conversion Type", ["Clicks", "Leads", "Sales"])

    # Calculate pacing weights
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

    chart = px.line(df, x="Week", y=["Planned Spend ($)", f"Forecasted {kpi_goal}"], markers=True, title="Spend and Forecasted Results Over Time")
    st.plotly_chart(chart, use_container_width=True)

    st.download_button("Download Timeline Forecast as CSV", df.to_csv(index=False).encode("utf-8"), file_name="timeline_forecast.csv")

