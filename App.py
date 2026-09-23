import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# PAGE SETUP
# -----------------------------

st.set_page_config(
    page_title="Loan & Credit Card Simulator",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Loan & Credit Card Payment Simulator")
st.write(
    "Explore how different repayment strategies affect "
    "interest, payment time, and total repayment."
)

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------

st.sidebar.header("Loan Details")

loan_type = st.sidebar.selectbox(
    "Type",
    ["Loan", "Credit Card"]
)

amount = st.sidebar.number_input(
    "Amount (RM)",
    min_value=100.0,
    value=10000.0,
    step=500.0
)

annual_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.0,
    value=6.0,
    step=0.5
)

term_months = st.sidebar.number_input(
    "Loan Term (months)",
    min_value=1,
    value=60,
    step=1
)

strategy = st.sidebar.selectbox(
    "Payment Strategy",
    ["On-time", "Early", "Late"]
)

# -----------------------------
# CALCULATE REQUIRED PAYMENT
# -----------------------------

monthly_rate = annual_rate / 100 / 12

if monthly_rate > 0:
    required_payment = (
        amount
        * monthly_rate
        * (1 + monthly_rate) ** term_months
        / ((1 + monthly_rate) ** term_months - 1)
    )
else:
    required_payment = amount / term_months

# -----------------------------
# STRATEGY PAYMENT
# -----------------------------

if strategy == "On-time":
    monthly_payment = required_payment

elif strategy == "Early":
    monthly_payment = required_payment * 1.20

else:
    monthly_payment = required_payment * 0.80


# -----------------------------
# SIMULATION FUNCTION
# -----------------------------

def simulate_loan(amount, monthly_rate, monthly_payment):

    balance = amount

    months = []
    balances = []
    interest_paid = []
    principal_paid = []

    total_interest = 0
    month = 0

    while balance > 0 and month < 1000:

        month += 1

        interest = balance * monthly_rate

        payment = min(monthly_payment, balance + interest)

        principal = payment - interest

        balance -= principal

        if balance < 0:
            balance = 0

        total_interest += interest

        months.append(month)
        balances.append(balance)
        interest_paid.append(interest)
        principal_paid.append(principal)

    df = pd.DataFrame({
        "Month": months,
        "Remaining Balance": balances,
        "Interest": interest_paid,
        "Principal": principal_paid
    })

    total_repaid = amount + total_interest

    return df, total_interest, total_repaid


# -----------------------------
# CURRENT STRATEGY SIMULATION
# -----------------------------

df, total_interest, total_repaid = simulate_loan(
    amount,
    monthly_rate,
    monthly_payment
)

payoff_time = len(df)

# -----------------------------
# STRATEGY COMPARISON
# -----------------------------

strategies = {
    "Early": required_payment * 1.20,
    "On-time": required_payment,
    "Late": required_payment * 0.80
}

comparison = []

for name, payment in strategies.items():

    temp_df, interest, repaid = simulate_loan(
        amount,
        monthly_rate,
        payment
    )

    comparison.append({
        "Strategy": name,
        "Total Interest": interest,
        "Total Repaid": repaid,
        "Payoff Time": len(temp_df)
    })

comparison_df = pd.DataFrame(comparison)

# -----------------------------
# SUMMARY
# -----------------------------

st.subheader("📊 Current Scenario")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monthly Payment",
    f"RM {monthly_payment:,.2f}"
)

col2.metric(
    "Total Interest",
    f"RM {total_interest:,.2f}"
)

col3.metric(
    "Total Repaid",
    f"RM {total_repaid:,.2f}"
)

col4.metric(
    "Payoff Time",
    f"{payoff_time} months"
)

# -----------------------------
# VIEW 1
# -----------------------------

st.subheader("📈 View 1: Payment Schedule")

st.line_chart(
    df.set_index("Month")["Remaining Balance"]
)

st.caption(
    f"Remaining balance using the **{strategy}** payment strategy."
)

# -----------------------------
# VIEW 2
# -----------------------------

st.subheader("💹 View 2: Interest Comparison")

interest_chart = comparison_df.set_index(
    "Strategy"
)["Total Interest"]

st.bar_chart(interest_chart)

# -----------------------------
# COMPARISON TABLE
# -----------------------------

st.subheader("🔎 Strategy Comparison")

display_df = comparison_df.copy()

display_df["Total Interest"] = display_df["Total Interest"].apply(
    lambda x: f"RM {x:,.2f}"
)

display_df["Total Repaid"] = display_df["Total Repaid"].apply(
    lambda x: f"RM {x:,.2f}"
)

display_df["Payoff Time"] = display_df["Payoff Time"].apply(
    lambda x: f"{x} months"
)

st.dataframe(
    display_df,
    use_container_width=True
)