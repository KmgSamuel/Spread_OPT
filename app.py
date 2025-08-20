import streamlit as st
import pandas as pd
from src.scoring import score_deal_row, aggregate_scores
from src.models import DealInput, factor_columns, required_columns
import plotly.express as px

st.set_page_config(page_title="VC Copilot • Above the Crowd Edition", layout="wide")

st.title("Venture Capitalist Copilot — Above the Crowd Edition")
st.caption("Encodes Bill Gurley marketplace and pricing frameworks into a practical deal evaluator.")

with st.expander("About this tool", expanded=False):
    st.markdown(
        """
        This hackathon app translates key Bill Gurley essays into a scoring rubric:
        - All Markets Are Not Created Equal (10 marketplace factors)
        - A Rake Too Far (optimal platform pricing / take rate)
        - Money Out of Nowhere (marketplace wealth creation; value unlock)

        Provide a single deal via the form or upload a CSV to compare multiple deals.
        """
    )

# Sidebar: weighting controls
st.sidebar.header("Weights")
weights = {
    "marketplace": st.sidebar.slider("Marketplace quality", 0.0, 3.0, 1.0, 0.1),
    "pricing_power": st.sidebar.slider("Pricing power / rake", 0.0, 3.0, 1.0, 0.1),
    "network_effects": st.sidebar.slider("Network effects & routing power", 0.0, 3.0, 1.0, 0.1),
    "unit_economics": st.sidebar.slider("Unit economics & payback", 0.0, 3.0, 1.0, 0.1),
    "value_unlock": st.sidebar.slider("Wealth creation / value unlock", 0.0, 3.0, 1.0, 0.1),
    "risk": st.sidebar.slider("Risk deductions", 0.0, 3.0, 1.0, 0.1),
}

st.sidebar.divider()
st.sidebar.download_button(
    label="Download sample CSV",
    data=open("sample_data/deals.csv", "rb").read(),
    file_name="deals_sample.csv",
    mime="text/csv",
)

# Tabs: single deal vs batch upload
single_tab, batch_tab = st.tabs(["Single Deal", "Batch Upload"]) 

with single_tab:
    st.subheader("Single deal input")
    with st.form("deal_form"):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Company name", value="Acme Market")
            sector = st.text_input("Sector", value="Marketplace")
            stage = st.selectbox("Stage", ["Pre-Seed", "Seed", "Series A", "Series B+"])
            geo = st.text_input("Geo", value="US")
            take_rate = st.number_input("Take rate / rake (%)", min_value=0.0, max_value=90.0, value=15.0, step=0.5)
            rake_sensitivity = st.slider("Customer sensitivity to rake (0=low,10=high)", 0, 10, 4)
            routing_power = st.slider("Routing power (0-10)", 0, 10, 6)
            network_strength = st.slider("Network effects strength (0-10)", 0, 10, 7)
            disintermediate_risk = st.slider("Disintermediation risk (0-10)", 0, 10, 3)
        with cols[1]:
            # 10 marketplace factors proxy inputs (0-10)
            fragmentation = st.slider("Supplier fragmentation (0-10)", 0, 10, 7)
            frequency = st.slider("Transaction frequency (0-10)", 0, 10, 6)
            take_rate_room = st.slider("Room for take rate (0-10)", 0, 10, 6)
            standardization = st.slider("Standardization / trust (0-10)", 0, 10, 6)
            geographic_density = st.slider("Geographic density (0-10)", 0, 10, 7)
            payment_flow = st.slider("Payment flow visibility (0-10)", 0, 10, 8)
            regulatory_risk = st.slider("Regulatory risk (0-10; high is worse)", 0, 10, 4)
            leakage_risk = st.slider("Leakage risk (0-10; high is worse)", 0, 10, 3)
            commoditization_risk = st.slider("Commoditization risk (0-10; high is worse)", 0, 10, 4)
            capital_intensity = st.slider("Capital intensity (0-10; high is worse)", 0, 10, 5)
            cac_payback_months = st.number_input("CAC payback (months)", min_value=0, max_value=120, value=12)
            ltv_cac = st.number_input("LTV/CAC", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
            contribution_margin = st.number_input("Contribution margin (%)", min_value=-100.0, max_value=100.0, value=20.0, step=0.5)
            value_unlock_index = st.slider("Value unlock vs status quo (0-10)", 0, 10, 6)
        submitted = st.form_submit_button("Score deal")

    if submitted:
        row = {
            "name": name,
            "sector": sector,
            "stage": stage,
            "geo": geo,
            "take_rate": take_rate,
            "rake_sensitivity": rake_sensitivity,
            "routing_power": routing_power,
            "network_strength": network_strength,
            "disintermediate_risk": disintermediate_risk,
            "fragmentation": fragmentation,
            "frequency": frequency,
            "take_rate_room": take_rate_room,
            "standardization": standardization,
            "geographic_density": geographic_density,
            "payment_flow": payment_flow,
            "regulatory_risk": regulatory_risk,
            "leakage_risk": leakage_risk,
            "commoditization_risk": commoditization_risk,
            "capital_intensity": capital_intensity,
            "cac_payback_months": cac_payback_months,
            "ltv_cac": ltv_cac,
            "contribution_margin": contribution_margin,
            "value_unlock_index": value_unlock_index,
        }
        di = DealInput(**row)
        scored = score_deal_row(di, weights)
        st.success(f"Overall score: {scored['overall']:.1f}/100")
        st.json({k: v for k, v in scored.items() if k != 'overall'})

        # Radar chart of sub-scores
        radar_df = pd.DataFrame({
            "dimension": [
                "Marketplace",
                "PricingPower",
                "NetworkEffects",
                "UnitEconomics",
                "ValueUnlock",
                "RiskAdj",
            ],
            "score": [
                scored["marketplace"],
                scored["pricing_power"],
                scored["network_effects"],
                scored["unit_economics"],
                scored["value_unlock"],
                scored["risk_adj"],
            ],
        })
        fig = px.line_polar(radar_df, r="score", theta="dimension", line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

with batch_tab:
    st.subheader("Batch evaluate via CSV upload")
    st.markdown("Expected columns:")
    st.code(", ".join(required_columns()))
    file = st.file_uploader("Upload CSV", type=["csv"]) 
    if file:
        df = pd.read_csv(file)
        missing = set(required_columns()) - set(df.columns)
        if missing:
            st.error(f"Missing columns: {sorted(list(missing))}")
        else:
            scored_df = aggregate_scores(df, weights)
            st.dataframe(scored_df.sort_values("overall", ascending=False), use_container_width=True)
            st.download_button("Download scored CSV", scored_df.to_csv(index=False), file_name="scored_deals.csv")

            fig2 = px.histogram(scored_df, x="overall", nbins=20, title="Overall score distribution")
            st.plotly_chart(fig2, use_container_width=True)
