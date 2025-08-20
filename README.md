# Spread_OPT — VC Copilot (Above the Crowd Edition)

An opinionated, hackathon-ready Venture Capital assistant that encodes Bill Gurley’s Above the Crowd frameworks into a practical deal evaluator. Use it to score single deals or batch-evaluate a CSV, visualize strengths, and export results.

## Features

- **Marketplace quality scoring** based on “All Markets Are Not Created Equal (10 factors).”
- **Pricing power / take-rate fitness** guided by “A Rake Too Far.”
- **Network effects & routing power** heuristics.
- **Unit economics** normalization (CAC payback, LTV/CAC, contribution margin).
- **Value unlock (wealth creation)** proxy inspired by “Money Out of Nowhere.”
- **Risk adjustments** (regulatory, disintermediation, leakage, commoditization, capital intensity).
- **Batch CSV evaluation** with downloadable results and visualizations.

## Quickstart

1) Recommended Python version: 3.11

Some data packages (e.g., pandas) may not have prebuilt wheels yet for Python 3.13. For best compatibility, use Python 3.11.

If you have the Windows Python launcher, you can target 3.11 explicitly.

2) Create a virtual environment (Windows PowerShell):

```powershell
# Prefer 3.11 if available
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies:

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

4) Run the app:

```powershell
streamlit run app.py
```

## How scoring maps to Above the Crowd

- **Marketplace quality**: Proxies for fragmentation, frequency, standardization/trust, geographic density, payment flow visibility; subtract risks like regulatory burden, leakage, commoditization, and capital intensity. Reference: `src/scoring.py::_marketplace_score`.
- **Pricing power (rake)**: Balances take-rate “room,” customer sensitivity to fees, and the risk of pushing the rake too far. Reference: `src/scoring.py::_pricing_power_score`.
- **Network effects & routing power**: Positive weight on routing/network strength, negative on disintermediation risk. Reference: `src/scoring.py::_network_effects_score`.
- **Unit economics**: Heuristics for CAC payback, LTV/CAC, and contribution margin. Reference: `src/scoring.py::_unit_econ_score`.
- **Value unlock**: Proxy for the magnitude of new surplus created vs. status quo. Reference: `src/scoring.py::_value_unlock_score`.
- **Risk adjustment**: Deductive blend of key risks to produce a risk-adjusted score. Reference: `src/scoring.py::_risk_adjustment`.

Weights for each dimension are adjustable in the Streamlit sidebar.

## CSV schema

The app expects these columns (see `src/models.py:required_columns()`):

```
name,sector,stage,geo,
take_rate,rake_sensitivity,routing_power,network_strength,disintermediate_risk,
fragmentation,frequency,take_rate_room,standardization,geographic_density,payment_flow,
regulatory_risk,leakage_risk,commoditization_risk,capital_intensity,
cac_payback_months,ltv_cac,contribution_margin,
value_unlock_index
```

Use `sample_data/deals.csv` as a reference starting point.

## Repo structure

```
app.py                     # Streamlit UI
requirements.txt
sample_data/deals.csv
src/
  __init__.py
  models.py               # Pydantic DealInput and schema helpers
  scoring.py              # Scoring functions & batch aggregator
```

## Notes and limitations

- This is a heuristic model for hackathon/demo use, not investment advice.
- The mapping from essays to numeric scores uses pragmatic proxies. Adjust `src/scoring.py` as needed for your thesis.
- Some categories (e.g., category-specific optimal take rates) are simplified.

## Credits

- Inspired by Bill Gurley’s Above the Crowd essays:
  - All Markets Are Not Created Equal (10 Factors)
  - A Rake Too Far (Optimal Platform Pricing)
  - Money Out of Nowhere (Marketplace Wealth Creation)

