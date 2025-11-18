import streamlit as st
import numpy as np
import pandas as pd
import json

# CPMM functions
def get_prices(x, y):
    """Calculate YES and NO prices based on CPMM formula"""
    total = x + y
    if total == 0:
        return 0.5, 0.5
    price_yes = y / total
    price_no = x / total
    return price_yes, price_no

def calc_cost_cpmm(x, y, direction, shares):
    """
    Calculate cost of buying shares in CPMM
    X * Y = K (constant)
    
    X = quantity of NO shares in the pool
    Y = quantity of YES shares in the pool
    
    When buying YES shares (delta_y):
    - Y_new = Y + delta_y (increases YES shares)
    - X_new = K / Y_new = (X * Y) / (Y + delta_y) (decreases NO shares)
    - Cost = X - X_new (paid by removing NO shares)
    
    When buying NO shares (delta_x):
    - X_new = X + delta_x (increases NO shares)
    - Y_new = K / X_new = (X * Y) / (X + delta_x) (decreases YES shares)
    - Cost = Y - Y_new (paid by removing YES shares)
    """
    k = x * y
    
    if k == 0:
        # Edge case: initialize with minimal liquidity
        k = 1.0
        x = 1.0
        y = 1.0
    
    if direction == "YES":
        # Buying YES shares: Y increases, X decreases
        y_new = y + shares
        x_new = k / y_new
        cost = x - x_new
    else:  # direction == "NO"
        # Buying NO shares: X increases, Y decreases
        x_new = x + shares
        y_new = k / x_new
        cost = y - y_new
    
    return cost, x_new, y_new

def dynamic_fee(x, y, base_fee=0.02):
    """Fee rate (can be made dynamic based on pool state if needed)"""
    return base_fee

def format_number(num):
    """Format number with thousand separators (Brazilian format: 1.000,00)"""
    # Format with comma as thousand separator and dot as decimal
    formatted = f"{num:,.2f}"
    # Replace comma with dot for thousands, and dot with comma for decimals
    parts = formatted.split(".")
    if len(parts) == 2:
        integer_part = parts[0].replace(",", ".")
        decimal_part = parts[1]
        return f"{integer_part},{decimal_part}"
    return formatted.replace(",", ".")

def format_price(price):
    """Format price with 2 decimal places and BRL currency (Brazilian format: 1.234,56 BRL)"""
    # Format number with Brazilian format and add BRL
    formatted_num = format_number(price)
    return f"{formatted_num} BRL"

# Streamlit UI
st.title("CPMM Simulator")

# Initialize session state
if 'initial_liquidity' not in st.session_state:
    st.session_state.initial_liquidity = 1000.0
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
if 'slider_key_counter' not in st.session_state:
    st.session_state.slider_key_counter = 0

# Parameters section
st.subheader("Parameters")
initial_liquidity = st.number_input("Initial Liquidity (X + Y)", value=st.session_state.initial_liquidity, step=100.0, min_value=100.0, key="initial_liquidity_input", help="Total initial liquidity in the pool")
st.session_state.initial_liquidity = initial_liquidity

base_fee_input = st.number_input("Base Fee Rate (%)", value=st.session_state.base_fee, step=0.1, key="base_fee_input")
st.session_state.base_fee = base_fee_input
base_fee = st.session_state.base_fee / 100

# Initial Probabilities
st.markdown("**Initial Probabilities:**")

# Handle reset button click - check BEFORE rendering slider
col_slider, col_reset = st.columns([4, 1])
with col_reset:
    st.markdown("<br>", unsafe_allow_html=True)  # Align button with slider
    if st.button("Reset", key="reset_prob_button", use_container_width=True, help="Reset to 50/50"):
        st.session_state.initial_prob_yes = 50.0
        # Increment counter to force slider recreation
        st.session_state.slider_key_counter += 1
        st.rerun()

with col_slider:
    initial_prob_yes = st.slider(
        "Initial Probability",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.initial_prob_yes,
        step=0.1,
        key=f"initial_prob_slider_{st.session_state.slider_key_counter}",
        help="Probability distribution: Left (YES) | Right (NO)"
    )

# Update session state with slider value
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
    if st.button("Import JSON", use_container_width=True):
        st.session_state.show_import_json = not st.session_state.show_import_json
        st.session_state.show_json_model = False

with col_model:
    if st.button("JSON Template", use_container_width=True):
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
    st.info("Copy the JSON above and use it in the import field.")

# Import JSON modal
if st.session_state.show_import_json:
    st.markdown("**Import Trades via JSON:**")
    json_input = st.text_area(
        "Paste JSON here:",
        height=200,
        key="json_input",
        help="Expected format: {\"trades\": [{\"direction\": \"YES\", \"shares\": 10}, ...]}"
    )
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("Confirm Import", use_container_width=True, type="primary"):
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
                        st.success(f"Imported {len(imported_trades)} trades successfully!")
                        st.rerun()
                    else:
                        st.error("No valid trades found in JSON.")
                else:
                    st.error("Invalid JSON format. Use the 'JSON Template' button to see the expected format.")
            except json.JSONDecodeError:
                st.error("Invalid JSON. Check the syntax.")
            except Exception as e:
                st.error(f"Error importing: {str(e)}")
    
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
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
# Calculate initial X and Y based on initial probabilities
# P(YES) = Y / (X + Y) => Y = P_yes * (X + Y)
# P(NO) = X / (X + Y) => X = P_no * (X + Y)
p_yes = initial_prob_yes / 100.0
p_no = initial_prob_no / 100.0

# Initialize pool with probabilities
total_liquidity = initial_liquidity
x = p_no * total_liquidity  # NO shares
y = p_yes * total_liquidity  # YES shares

# Ensure minimum liquidity to avoid division by zero
if x == 0:
    x = 0.01
if y == 0:
    y = 0.01

k = x * y  # Constant product

total_cost = 0
total_fee = 0
rows = []
x_current = x
y_current = y
k_current = k
total_shares_yes = 0  # Total YES shares bought by user
total_shares_no = 0   # Total NO shares bought by user

# Display initial state
st.markdown("### 📊 Initial Pool State")
st.divider()

price_yes_init, price_no_init = get_prices(x_current, y_current)

# Organize in two rows: first row for quantities, second row for prices
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Quantities:**")
    st.metric("X (NO Shares)", format_number(x_current))
    st.metric("Y (YES Shares)", format_number(y_current))
    
with col2:
    st.markdown("**Liquidity:**")
    st.metric("K (Constant)", format_number(k_current))
    
with col3:
    st.markdown("**Prices:**")
    st.metric("Price YES", format_price(price_yes_init))
    st.metric("Price NO", format_price(price_no_init))

st.divider()

for direction, shares in trades:
    # Calculate cost and new pool state
    cost, x_new, y_new = calc_cost_cpmm(x_current, y_current, direction, shares)
    
    # Apply fee
    fee_rate = dynamic_fee(x_current, y_current, base_fee)
    fee = cost * fee_rate
    cost_after_fee = cost + fee  # User pays cost + fee
    
    total_cost += cost_after_fee
    total_fee += fee
    
    # Track shares bought by user
    if direction == "YES":
        total_shares_yes += shares
    else:
        total_shares_no += shares
    
    # Update pool state
    x_current = x_new
    y_current = y_new
    k_current = x_current * y_current
    
    # Calculate current prices
    price_yes_curr, price_no_curr = get_prices(x_current, y_current)
    
    avg_price = cost_after_fee / shares if shares > 0 else 0
    
    rows.append({
        "Direction": direction,
        "Shares": shares,
        "X (NO)": format_number(x_current),
        "Y (YES)": format_number(y_current),
        "K": format_number(k_current),
        "Price YES": format_price(price_yes_curr),
        "Price NO": format_price(price_no_curr),
        "Fee Rate": f"{fee_rate*100:.2f}%",
        "Cost Paid": format_price(cost_after_fee),
        "Avg. Price": format_price(avg_price),
        "Fee Earned": format_price(fee)
    })

# Final payout: user receives shares of the winning outcome
# In CPMM, payout is the number of shares the user owns of the winning outcome
payout = total_shares_yes if final_outcome == "YES" else total_shares_no
# Net worth = Total Cost Paid + Total Fees - Payout
# Assuming each share is worth 1 BRL at payout
net_worth = total_cost + total_fee - payout

# Results
st.subheader("Simulation Results")

if not trades:
    st.warning("No trades to simulate. Please add trades above.")
else:
    # Summary before table
    st.markdown("### 💰 Financial Summary")
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    with col_sum1:
        st.metric("Total Cost Paid", format_price(total_cost))
    with col_sum2:
        st.metric("Total Fees Earned", format_price(total_fee))
    with col_sum3:
        # Payout as monetary value (each share worth 1 BRL)
        payout_value = payout  # Each share is worth 1 BRL
        st.metric(f"Payout ({final_outcome})", format_price(payout_value))
    
    st.divider()
    
    # Final pool state
    st.markdown("### 📊 Final Pool State")
    price_yes_final, price_no_final = get_prices(x_current, y_current)
    
    # Organize in two rows: first row for quantities, second row for prices
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("**Quantities:**")
        st.metric("X (NO Shares)", format_number(x_current))
        st.metric("Y (YES Shares)", format_number(y_current))
        
    with col_f2:
        st.markdown("**Liquidity:**")
        st.metric("K (Constant)", format_number(k_current))
        
    with col_f3:
        st.markdown("**Prices:**")
        st.metric("Price YES", format_price(price_yes_final))
        st.metric("Price NO", format_price(price_no_final))
    
    st.divider()

    # Net Worth with conditional color
    st.markdown("### 📈 Net Worth")
    net_worth_color = "red" if net_worth < 0 else "green"
    st.markdown(f"<span style='color:{net_worth_color}; font-size: 1.5em; font-weight: bold'>{format_price(net_worth)}</span>", unsafe_allow_html=True)

    # Table with scroll (showing approximately 10 rows)
    df = pd.DataFrame(rows)
    st.dataframe(df, height=400)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6c757d; font-size: 0.8em;">By Iago Macedo</p>',
    unsafe_allow_html=True
)
