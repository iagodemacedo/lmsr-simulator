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

# Base b Parameter with slider and input
col1_b, col2_b = st.columns([3, 1])
with col1_b:
    base_b_slider = st.slider("Base b Parameter", 10, 1000, int(st.session_state.base_b), key="base_b_slider")
    st.session_state.base_b = base_b_slider
with col2_b:
    base_b = st.number_input("", min_value=10, max_value=1000, value=int(st.session_state.base_b), step=1, key="base_b_input", label_visibility="collapsed")
    st.session_state.base_b = base_b

# Base Fee Rate with slider and input
col1_fee, col2_fee = st.columns([3, 1])
with col1_fee:
    base_fee_slider = st.slider("Base Fee Rate (%)", 0.0, 10.0, st.session_state.base_fee, step=0.1, key="base_fee_slider")
    st.session_state.base_fee = float(base_fee_slider)
with col2_fee:
    base_fee_input = st.number_input("", min_value=0.0, max_value=10.0, value=st.session_state.base_fee, step=0.1, key="base_fee_input", label_visibility="collapsed")
    st.session_state.base_fee = base_fee_input
base_fee = st.session_state.base_fee / 100

# Number of Trades with slider and input
col1_trades, col2_trades = st.columns([3, 1])
with col1_trades:
    trade_count_slider = st.slider("Number of Trades", 1, 20, int(st.session_state.trade_count), key="trade_count_slider")
    st.session_state.trade_count = trade_count_slider
with col2_trades:
    trade_count = st.number_input("", min_value=1, max_value=20, value=int(st.session_state.trade_count), step=1, key="trade_count_input", label_visibility="collapsed")
    st.session_state.trade_count = trade_count

trades = []
for i in range(trade_count):
    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox(f"Trade {i+1} Direction", ["YES", "NO"], key=f"dir{i}")
    with col2:
        shares = st.number_input(f"Shares for Trade {i+1}", min_value=1, max_value=10000, value=10, step=1, key=f"sh{i}")
    trades.append((direction, shares))

final_outcome = st.selectbox("Final Outcome of Market", ["YES", "NO"])

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

# Results
st.subheader("Simulation Results")
df = pd.DataFrame(rows)
st.dataframe(df)

st.markdown(f"**Total Cost Paid:** {total_cost:.2f} USDC")
st.markdown(f"**Total Fees Earned:** {total_fee:.2f} USDC")
st.markdown(f"**Final Payout:** {payout:.2f} USDC")

net_worth = total_fee + total_cost - payout
st.markdown(f"**Net Worth:** {net_worth:.2f} USDC")
