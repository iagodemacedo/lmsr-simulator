import streamlit as st
import numpy as np
import pandas as pd
import json

# LMSR functions
def calc_cost(q_yes, q_no, b):
    return b * np.log(np.exp(q_yes / b) + np.exp(q_no / b))

def dynamic_fee(q_yes, q_no, base_fee=0.02):
    return base_fee

def dynamic_b(q_yes, q_no, base_b=100, min_b=30):
    total = q_yes + q_no
    if total == 0:
        return base_b
    imbalance_ratio = abs(q_yes - q_no) / total
    # return max(min_b, base_b * (1 - 0.6 * imbalance_ratio))
    return base_b

# Streamlit UI
st.title("LMSR Simulator")

# Initialize session state
if 'base_b' not in st.session_state:
    st.session_state.base_b = 100
if 'base_fee' not in st.session_state:
    st.session_state.base_fee = 2.0
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'final_outcome' not in st.session_state:
    st.session_state.final_outcome = "YES"
if 'show_import_json' not in st.session_state:
    st.session_state.show_import_json = False
if 'show_json_model' not in st.session_state:
    st.session_state.show_json_model = False
if 'initial_prob_yes' not in st.session_state:
    st.session_state.initial_prob_yes = 50.0

# Parameters section
st.subheader("Parameters")
base_b = st.number_input("Base b Parameter", value=st.session_state.base_b, step=1, key="base_b_input")
st.session_state.base_b = base_b

base_fee_input = st.number_input("Base Fee Rate (%)", value=st.session_state.base_fee, step=0.1, key="base_fee_input")
st.session_state.base_fee = base_fee_input
base_fee = st.session_state.base_fee / 100

# Initial Probabilities
st.markdown("**Initial Probabilities:**")
col_slider, col_reset = st.columns([4, 1])
with col_slider:
    initial_prob_yes = st.slider(
        "Initial Probability",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.initial_prob_yes,
        step=0.1,
        key="initial_prob_slider",
        help="Probability distribution: Left (YES) | Right (NO)"
    )
with col_reset:
    st.markdown("<br>", unsafe_allow_html=True)  # Align button with slider
    if st.button("Reset", key="reset_prob_button", use_container_width=True, help="Reset to 50/50"):
        st.session_state.initial_prob_yes = 50.0
        st.rerun()

# Update session state with slider value (or reset value if button was clicked)
st.session_state.initial_prob_yes = initial_prob_yes
initial_prob_no = 100.0 - initial_prob_yes

# Display probability values
col_prob_yes, col_prob_no = st.columns(2)
with col_prob_yes:
    st.metric("YES", f"{initial_prob_yes:.1f}%")
with col_prob_no:
    st.metric("NO", f"{initial_prob_no:.1f}%")

# Visual separator
st.divider()

# Trades section
st.subheader("Trades")

# Import JSON buttons
col_import, col_model = st.columns(2)

with col_import:
    if st.button("Importar JSON", use_container_width=True):
        st.session_state.show_import_json = not st.session_state.show_import_json
        st.session_state.show_json_model = False

with col_model:
    if st.button("Modelo JSON", use_container_width=True):
        st.session_state.show_json_model = not st.session_state.show_json_model
        st.session_state.show_import_json = False

# Show JSON model
if st.session_state.show_json_model:
    json_model = {
        "trades": [
            {"direction": "YES", "shares": 10},
            {"direction": "NO", "shares": 5},
            {"direction": "YES", "shares": 20}
        ]
    }
    st.json(json_model)
    st.code(json.dumps(json_model, indent=2), language="json")
    st.info("Copie o JSON acima e use no campo de importação.")

# Import JSON modal
if st.session_state.show_import_json:
    st.markdown("**Importar Trades via JSON:**")
    json_input = st.text_area(
        "Cole o JSON aqui:",
        height=200,
        key="json_input",
        help="Formato esperado: {\"trades\": [{\"direction\": \"YES\", \"shares\": 10}, ...]}"
    )
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("Confirmar Importação", use_container_width=True, type="primary"):
            try:
                data = json.loads(json_input)
                if "trades" in data and isinstance(data["trades"], list):
                    imported_trades = []
                    for trade in data["trades"]:
                        if "direction" in trade and "shares" in trade:
                            direction = trade["direction"].upper()
                            if direction in ["YES", "NO"]:
                                shares = int(trade["shares"])
                                if shares > 0:
                                    imported_trades.append((direction, shares))
                    
                    if imported_trades:
                        st.session_state.trades = imported_trades
                        st.session_state.show_import_json = False
                        st.success(f"Importadas {len(imported_trades)} trades com sucesso!")
                        st.rerun()
                    else:
                        st.error("Nenhuma trade válida encontrada no JSON.")
                else:
                    st.error("Formato JSON inválido. Use o botão 'Modelo JSON' para ver o formato esperado.")
            except json.JSONDecodeError:
                st.error("JSON inválido. Verifique a sintaxe.")
            except Exception as e:
                st.error(f"Erro ao importar: {str(e)}")
    
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.show_import_json = False
            st.rerun()

# Display existing trades in a table
if st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades, columns=["Direction", "Shares"])
    st.dataframe(trades_df, height=200, use_container_width=True)
else:
    st.info("No trades added yet. Add a trade below or import via JSON.")

# Add new trade section
st.markdown("**Add New Trade:**")
col_dir, col_shares = st.columns(2)

with col_dir:
    new_direction = st.selectbox("Trade Direction", ["YES", "NO"], key="new_trade_direction")

with col_shares:
    new_shares = st.number_input("Shares", min_value=1, value=10, step=1, key="new_trade_shares")

if st.button("Add Trade", use_container_width=True, type="primary"):
    st.session_state.trades.append((new_direction, new_shares))
    st.rerun()

trades = st.session_state.trades

# Final Outcome buttons
st.markdown("**Final Outcome of Market:**")

yes_selected = st.session_state.final_outcome == "YES"
no_selected = st.session_state.final_outcome == "NO"

# CSS to style buttons based on selection state
st.markdown(f"""
<style>
    /* Style for YES button - both primary and secondary */
    div[data-testid="column"]:first-of-type button {{
        background-color: {'#28a745' if yes_selected else '#f8f9fa'} !important;
        color: {'white' if yes_selected else '#6c757d'} !important;
        border: 2px solid {'#28a745' if yes_selected else '#dee2e6'} !important;
        font-weight: {'bold' if yes_selected else 'normal'} !important;
    }}
    div[data-testid="column"]:first-of-type button:hover {{
        background-color: {'#218838' if yes_selected else '#e9ecef'} !important;
        border-color: {'#1e7e34' if yes_selected else '#adb5bd'} !important;
    }}
    /* Style for NO button - both primary and secondary */
    div[data-testid="column"]:last-of-type button {{
        background-color: {'#dc3545' if no_selected else '#f8f9fa'} !important;
        color: {'white' if no_selected else '#6c757d'} !important;
        border: 2px solid {'#dc3545' if no_selected else '#dee2e6'} !important;
        font-weight: {'bold' if no_selected else 'normal'} !important;
    }}
    div[data-testid="column"]:last-of-type button:hover {{
        background-color: {'#c82333' if no_selected else '#e9ecef'} !important;
        border-color: {'#bd2130' if no_selected else '#adb5bd'} !important;
    }}
</style>
""", unsafe_allow_html=True)

col_yes, col_no = st.columns(2)

with col_yes:
    # Use type="primary" when selected to make it more visible
    button_type = "primary" if yes_selected else "secondary"
    if st.button("YES", key="btn_yes", use_container_width=True, type=button_type):
        st.session_state.final_outcome = "YES"
        st.rerun()

with col_no:
    # Use type="primary" when selected to make it more visible
    button_type = "primary" if no_selected else "secondary"
    if st.button("NO", key="btn_no", use_container_width=True, type=button_type):
        st.session_state.final_outcome = "NO"
        st.rerun()

final_outcome = st.session_state.final_outcome

# Simulation logic
# Calculate initial q_yes and q_no based on initial probabilities
# P(YES) = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))
# If we set q_no = 0 as reference: q_yes = b * ln(p_yes / p_no)
p_yes = initial_prob_yes / 100.0
p_no = initial_prob_no / 100.0

if p_yes > 0 and p_no > 0:
    q_yes = base_b * np.log(p_yes / p_no)
    q_no = 0.0
elif p_yes == 0:
    # Extreme case: 0% YES probability
    q_yes = -base_b * 10  # Very negative
    q_no = 0.0
elif p_no == 0:
    # Extreme case: 100% YES probability
    q_yes = base_b * 10  # Very positive
    q_no = 0.0
else:
    # Default: 50/50
    q_yes = 0.0
    q_no = 0.0

total_cost = 0
total_fee = 0
rows = []

for direction, shares in trades:
    b_now = dynamic_b(q_yes, q_no, base_b)
    cost_before = calc_cost(q_yes, q_no, b_now)

    if direction == "YES":
        q_yes_new = q_yes + shares
        q_no_new = q_no
    else:
        q_yes_new = q_yes
        q_no_new = q_no + shares

    cost_after = calc_cost(q_yes_new, q_no_new, b_now)
    cost = cost_after - cost_before
    fee_rate = dynamic_fee(q_yes, q_no, base_fee)
    fee = cost * fee_rate

    total_cost += cost
    total_fee += fee
    q_yes, q_no = q_yes_new, q_no_new

    avg_price = cost / shares if shares > 0 else 0
    
    rows.append({
        "Direction": direction,
        "Shares": shares,
        "b Used": round(b_now, 2),
        "Fee Rate": round(fee_rate, 4),
        "Cost Paid": round(cost, 4),
        "Avg. Price": round(avg_price, 4),
        "Fee Earned": round(fee, 4)
    })

payout = q_yes if final_outcome == "YES" else q_no
net_worth = total_fee + total_cost - payout

# Results
st.subheader("Simulation Results")

if not trades:
    st.warning("No trades to simulate. Please add trades above.")
else:
    # Summary before table
    st.markdown(f"**Total Cost Paid:** {total_cost:.2f} BRL")
    st.markdown(f"**Total Fees Earned:** {total_fee:.2f} BRL")
    st.markdown(f"**Final Payout:** {payout:.2f} BRL")

    # Net Worth with conditional color
    net_worth_color = "red" if net_worth < 0 else "green"
    st.markdown(f"**Net Worth:** <span style='color:{net_worth_color}'>{net_worth:.2f} BRL</span>", unsafe_allow_html=True)

    # Table with scroll (showing approximately 10 rows)
    df = pd.DataFrame(rows)
    st.dataframe(df, height=400)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6c757d; font-size: 0.8em;">Por Iago Macedo</p>',
    unsafe_allow_html=True
)
