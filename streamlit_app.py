import streamlit as st
import numpy as np
import pandas as pd

# LMSR functions
def calc_cost(q_yes, q_no, b):
    return b * np.log(np.exp(q_yes / b) + np.exp(q_no / b))

def dynamic_fee(q_yes, q_no, base_fee=0.02, max_fee=0.1):
    total = q_yes + q_no
    if total == 0:
        return base_fee
    imbalance_ratio = abs(q_yes - q_no) / total
    return min(base_fee + 1.5 * imbalance_ratio * (max_fee - base_fee), max_fee)

def dynamic_b(q_yes, q_no, base_b=100, min_b=30):
    total = q_yes + q_no
    if total == 0:
        return base_b
    imbalance_ratio = abs(q_yes - q_no) / total
    # return max(min_b, base_b * (1 - 0.6 * imbalance_ratio))
    return base_b

# Streamlit UI
st.title("LMSR Simulator")

base_b = st.slider("Base b Parameter", 10, 1000, 100)
base_fee = st.slider("Base Fee Rate (%)", 0, 10, 2) / 100
max_fee = st.slider("Max Fee Rate (%)", 1, 20, 10) / 100

trade_count = st.slider("Number of Trades", 1, 20, 10)

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
    fee_rate = dynamic_fee(q_yes, q_no, base_fee, max_fee)
    fee = cost * fee_rate

    total_cost += cost
    total_fee += fee
    q_yes, q_no = q_yes_new, q_no_new

    rows.append({
        "Direction": direction,
        "Shares": shares,
        "b Used": round(b_now, 2),
        "Fee Rate": round(fee_rate, 4),
        "Cost Paid": round(cost, 4),
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
