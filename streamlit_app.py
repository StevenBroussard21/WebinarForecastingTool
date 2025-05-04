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
backend_tab, forecast_tab, book_a_call_tab  = st.tabs(["CRM ROI Forecast", "Webinar Forecast", "Book A Call Forecast"])

# --------------------------
# TAB 1: Backend System ROI Forecast
# --------------------------
with backend_tab:
    sidebar, main = st.columns([1, 3])

    with sidebar:
        # View Mode Toggle
        st.markdown("### View Mode")
        time_view = st.radio("Show Forecast As:", ["Monthly", "Yearly"])
        multiplier = 12 if time_view == "Yearly" else 1

        # Reinvestment Style – Only visible for Yearly View
        if time_view == "Yearly":
            st.markdown("### Reinvestment Style")
            reinvest_mode = st.radio("Compounding Mode", ["Light", "Moderate", "Aggressive"])

        # CRM Lead Inputs
        st.markdown("### Backend Funnel Assumptions")
        total_crm_leads = st.number_input("Total Leads in CRM", value=2000, step=1)
        active_leads = st.number_input("Currently Engaged or Booked Leads", value=500, step=1)
        leads_to_reengage = total_crm_leads - active_leads

        # Funnel Rates
        st.markdown("### Funnel Conversion Rates")
        contact_rate = st.slider("Contact Rate (%)", 0, 100, 70)
        booking_rate = st.slider("Booking Rate (%)", 0, 100, 30)
        show_rate = st.slider("Show Rate (%)", 0, 100, 75)
        close_rate = st.slider("Close Rate (%)", 0, 100, 20)

        # Financial Assumptions
        st.markdown("### Revenue & Operational Costs")
        client_value = st.number_input("Client Value ($)", value=1500)
        monthly_tech_stack = st.number_input("Monthly Tech Stack ($)", value=900)
        team_members = st.number_input("Team Members", value=2)
        monthly_salary = st.number_input("Monthly Salary per Member ($)", value=5000)

        use_overhead = st.checkbox("Include Existing Overhead?")
        existing_overhead = st.number_input("Monthly Overhead ($)", value=2000) if use_overhead else 0

    with main:
        # Funnel Math
        contacted = leads_to_reengage * (contact_rate / 100)
        booked = contacted * (booking_rate / 100)
        showed = booked * (show_rate / 100)
        closed = showed * (close_rate / 100)

        # Financial Math
        revenue = closed * client_value * multiplier
        tech_cost = monthly_tech_stack * multiplier
        salary_cost = team_members * monthly_salary * multiplier
        overhead_cost = existing_overhead * multiplier
        total_cost = tech_cost + salary_cost + overhead_cost
        net_profit = revenue - total_cost
        roi = (net_profit / total_cost * 100) if total_cost else 0

        # Funnel Summary
        st.subheader(f"\U0001F4CA Re-engagement Funnel Results ({time_view} View)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Re-engagement Pool", f"{leads_to_reengage:,}")
        c2.metric("Contacted", f"{int(contacted):,}")
        c3.metric("Booked", f"{int(booked):,}")
        c1.metric("Showed", f"{int(showed):,}")
        c2.metric("Closed", f"{int(closed):,}")

        # Financial Summary
        st.subheader("\U0001F4B0 Financial Projection")
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"${revenue:,.2f}")
        c2.metric("Total Cost", f"${total_cost:,.2f}")
        c3.metric("Net Profit", f"${net_profit:,.2f}")
        st.metric("ROI", f"{roi:.2f}%")

        # Monthly ROI Tiers
        if time_view == "Monthly":
            base_monthly_roi = (net_profit / total_cost) if total_cost else 0
            light_roi = base_monthly_roi * 0.25 * 100
            moderate_roi = base_monthly_roi * 0.5 * 100
            aggressive_roi = base_monthly_roi * 100

            st.subheader("📊 Monthly ROI Range (Realization Levels)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Light (25%)", f"{light_roi:.2f}%")
            c2.metric("Moderate (50%)", f"{moderate_roi:.2f}%")
            c3.metric("Aggressive (100%)", f"{aggressive_roi:.2f}%")

            with st.expander("💡 Why both funnel conversion rates and ROI tiers matter"):
                st.markdown(f"""
                ### 📈 Funnel Logic Based on Your Inputs
                With your current funnel settings:
                - **Contact Rate:** {contact_rate}%  
                - **Booking Rate:** {booking_rate}%  
                - **Show Rate:** {show_rate}%  
                - **Close Rate:** {close_rate}%  

                Out of **{leads_to_reengage:,} leads**, you're projected to contact **{int(contacted):,}**, book **{int(booked):,}**,  
                have **{int(showed):,}** show up, and close **{int(closed):,}** — leading to **${revenue:,.2f}** in revenue and a base ROI of **{roi:.2f}%**.

                ### 🎯 Why We Still Show Light / Moderate / Aggressive ROI
                That full ROI represents your **maximum potential** if everything goes as planned. But in real-world execution:

                - Staff can miss follow-ups
                - Some booked leads may ghost
                - Not every close happens, even with good leads

                So we model 3 ROI scenarios to reflect execution realities:
                - **Light (25%)**: Poor follow-up, overwhelmed team
                - **Moderate (50%)**: Average performance, room to improve
                - **Aggressive (100%)**: Fully optimized with automation and follow-through

                ### 🧠 Use Case: Andre’s Offer
                - **Light**: Manual CRM use, limited team bandwidth  
                - **Moderate**: Some automation, consistent booking/show-up  
                - **Aggressive**: White-glove experience, high-quality bookings, trained closers  
                """)

        # Yearly Compounded ROI
        if time_view == "Yearly":
            base_monthly_roi = (net_profit / total_cost / 12) if total_cost else 0
            if reinvest_mode == "Light":
                r = base_monthly_roi * 0.25
            elif reinvest_mode == "Moderate":
                r = base_monthly_roi * 0.5
            else:
                r = base_monthly_roi

            compound_roi = ((1 + r) ** 12 - 1) * 100 if r > -1 else 0

            st.metric("Compounded ROI (12 mo)", f"{compound_roi:.2f}%")
            st.markdown("ℹ️ **What this means:** This assumes you reinvest part or all of your monthly profit every month for 12 months.")
            st.markdown("""
            **Formula:**  
            Compounded ROI = ((1 + monthly ROI) ^ 12 - 1) × 100  
            
            **Example:**  
            If monthly ROI = 25%  
            Compounded ROI = ((1 + 0.25) ^ 12 - 1) × 100 = ~1188%
            """)

        # Funnel Chart
        st.markdown("### Funnel Drop-Off Chart")
        funnel_df = pd.DataFrame({
            "Stage": ["Re-engagement Pool", "Contacted", "Booked", "Showed", "Closed"],
            "Volume": [leads_to_reengage, contacted, booked, showed, closed]
        })
        funnel_fig = px.bar(funnel_df, x="Stage", y="Volume", text_auto=True)
        st.plotly_chart(funnel_fig, use_container_width=True)

        # Revenue Breakdown Chart
        st.markdown("### Revenue Breakdown: Cost vs Net Profit")
        breakdown_df = pd.DataFrame({
            "Component": ["Tech Stack", "Salaries", "Overhead", "Net Profit"],
            "Value": [tech_cost, salary_cost, overhead_cost, net_profit]
        })
        stacked_fig = px.bar(
            breakdown_df,
            x=["Revenue"] * 4,
            y="Value",
            color="Component",
            text="Value",
            title="Revenue Allocation"
        )
        stacked_fig.update_layout(barmode="stack", xaxis_title=None, yaxis_title="$ Amount")
        st.plotly_chart(stacked_fig, use_container_width=True)

        # Strategy Summary
        if st.checkbox("Show Strategy Summary"):
            st.markdown(f"""
                ### Strategy Summary ({time_view} View)
                Out of **{total_crm_leads:,} leads in the CRM**, **{leads_to_reengage:,}** were identified for re-engagement.
                Through the backend funnel:
                - **{int(contacted):,}** contacted → **{int(booked):,}** booked → **{int(showed):,}** showed → **{int(closed):,}** clients closed
                - Revenue: **${revenue:,.2f}**, Cost: **${total_cost:,.2f}**, Net Profit: **${net_profit:,.2f}**, ROI: **{roi:.2f}%**
                {"- Compounded ROI (12 mo): **{:.2f}%**".format(compound_roi) if time_view == "Yearly" else ""}
            """)
# --------------------------
# TAB 2: Webinar Forecast (Your Full Original Code)
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

        st.subheader("Forecast Summary")
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

        st.markdown("### Funnel Visualization")
        funnel_stages = ["Clicks", "Signups", "Attendees", "Qualified Leads", "Sales"]
        funnel_values = [clicks, signups, attendees, leads, sales]
        fig = go.Figure(go.Funnel(y=funnel_stages, x=funnel_values, textinfo="value+percent previous", marker={"color": "royalblue"}))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Conversion Rates vs Benchmarks")
        chart_df = pd.DataFrame({
            "Stage": ["Landing Page CR", "Attendance Rate", "Lead Rate", "Sales Rate"],
            "Your Rates (%)": [landing_cr, attendance_rate, 100 if treat_all_as_leads else lead_rate, sales_rate],
            "Benchmark (%)": [benchmarks['landing_cr'], benchmarks['attendance_rate'], benchmarks['lead_rate'], benchmarks['sales_rate']]
        })
        st.plotly_chart(px.bar(chart_df, x="Stage", y=["Your Rates (%)", "Benchmark (%)"], barmode="group"), use_container_width=True)

        st.markdown("### ROAS Performance")
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
# TAB 3: Book A Call Forecast
# --------------------------
with book_a_call_tab:
    sidebar, main = st.columns([1, 3])

    with sidebar:
        st.markdown("### Configure Your Book-a-Call Funnel")

        ad_spend = st.number_input("Monthly Ad Spend ($)", value=3000)
        cost_per_click = st.number_input("Average CPC ($)", value=2.50)

        with st.expander("Funnel Conversion Rates"):
            landing_page_rate = st.slider("Landing Page → Booked Call (%)", 0, 100, 10)
            show_rate = st.slider("Show Rate (%)", 0, 100, 70)
            close_rate = st.slider("Close Rate (%)", 0, 100, 20)

        with st.expander("Product & Revenue Details"):
            client_value = st.number_input("Client Value ($)", value=1500)

        with st.expander("📌 Forecast Accuracy Disclaimer", expanded=True):
            st.markdown("""
            #### ⚠️ Important Note on Forecast Accuracy
            This tool provides projected performance based on your inputs — but real-world ad performance varies due to:

            - 🎯 Targeting accuracy and audience quality
            - 📈 Seasonality or platform shifts
            - 🧪 Creative performance and ad fatigue
            - ⚙️ Booking system UX and mobile friendliness
            - ⏱ Attribution lag (leads convert after the month ends)

            **Why use this tool anyway?**
            - Creates directional models to guide spend and goals
            - Helps define baseline expectations and KPIs
            - Makes it easier to pivot after running a test campaign

            👉 After 2–4 weeks of ads, replace these assumptions with real data to re-forecast accurately.
            """)

    with main:
        # Funnel logic
        clicks = ad_spend / cost_per_click
        booked_calls = clicks * (landing_page_rate / 100)
        showed = booked_calls * (show_rate / 100)
        closed = showed * (close_rate / 100)

        revenue = closed * client_value
        net_profit = revenue - ad_spend
        roi = (net_profit / ad_spend * 100) if ad_spend else 0
        roas = revenue / ad_spend if ad_spend else 0

        # ROI tiers
        base_monthly_roi = net_profit / ad_spend if ad_spend else 0
        light_roi = base_monthly_roi * 0.25 * 100
        moderate_roi = base_monthly_roi * 0.5 * 100
        aggressive_roi = base_monthly_roi * 100

        st.subheader("📈 Forecast Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Booked Calls", f"{int(booked_calls):,}")
        col2.metric("Showed", f"{int(showed):,}")
        col3.metric("Closed Clients", f"{int(closed):,}")
        col1.metric("Revenue", f"${revenue:,.2f}")
        col2.metric("Net Profit", f"${net_profit:,.2f}")
        col3.metric("ROI", f"{roi:.2f}%")
        st.metric("ROAS", f"{roas:.2f}x")

        st.subheader("📊 Monthly ROI Range (Realization Levels)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Light (25%)", f"{light_roi:.2f}%")
        c2.metric("Moderate (50%)", f"{moderate_roi:.2f}%")
        c3.metric("Aggressive (100%)", f"{aggressive_roi:.2f}%")

        with st.expander("💡 Why ROI tiers still matter even with ad variables"):
            st.markdown(f"""
            Even though paid traffic performance is unpredictable at first, these ROI tiers give us a lens on **execution quality**:

            - **Light (25%)**: Poor show rate, low close rate, or weak follow-up
            - **Moderate (50%)**: Booking system works, follow-up is decent
            - **Aggressive (100%)**: Team executes well, shows up, closes well

            Based on your inputs:
            - **{int(clicks):,} clicks** → **{int(booked_calls):,} booked calls**
            - **{int(showed):,} showed** → **{int(closed):,} closed**
            - Full ROI: **{roi:.2f}%** | Realistic Range: **{light_roi:.2f}%–{aggressive_roi:.2f}%**
            """)

