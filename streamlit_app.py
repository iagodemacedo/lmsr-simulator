import streamlit as st
import numpy as np
import pandas as pd

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
if 'trade_count' not in st.session_state:
    st.session_state.trade_count = 10
if 'final_outcome' not in st.session_state:
    st.session_state.final_outcome = "YES"

# Parameters section
st.subheader("Parameters")
base_b = st.number_input("Base b Parameter", value=st.session_state.base_b, step=1, key="base_b_input")
st.session_state.base_b = base_b

base_fee_input = st.number_input("Base Fee Rate (%)", value=st.session_state.base_fee, step=0.1, key="base_fee_input")
st.session_state.base_fee = base_fee_input
base_fee = st.session_state.base_fee / 100

trade_count = st.number_input("Number of Trades", min_value=1, max_value=1000, value=int(st.session_state.trade_count), step=1, key="trade_count_input")
st.session_state.trade_count = trade_count

# Visual separator
st.divider()

# Trades section
st.subheader("Trades")

trades = []
for i in range(trade_count):
    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox(f"Trade {i+1} Direction", ["YES", "NO"], key=f"dir{i}")
    with col2:
        shares = st.number_input(f"Shares for Trade {i+1}", min_value=1, max_value=10000, value=10, step=1, key=f"sh{i}")
    trades.append((direction, shares))

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
q_yes = 0
q_no = 0
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
