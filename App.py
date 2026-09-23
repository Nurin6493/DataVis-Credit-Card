import streamlit as st
import pandas as pd

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Loan & Credit Card Simulator",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Loan & Credit Card Payment Simulator")

st.write(
    "Explore how different repayment strategies affect "
    "interest, payment time, total repayment, and borrowing cost."
)

# ============================================================
# SIDEBAR INPUTS
# ============================================================

st.sidebar.header("📋 Payment Details")

# Loan or Credit Card
loan_type = st.sidebar.selectbox(
    "Type",
    ["Loan", "Credit Card"]
)

# Amount
amount = st.sidebar.number_input(
    "Amount (RM)",
    min_value=100.0,
    value=10000.0,
    step=500.0
)

# Annual interest rate
annual_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.0,
    value=6.0,
    step=0.5
)

# Loan term
term_months = st.sidebar.number_input(
    "Loan Term (months)",
    min_value=1,
    value=60,
    step=1
)

# ============================================================
# CALCULATE REQUIRED MONTHLY PAYMENT
# ============================================================

monthly_rate = annual_rate / 100 / 12

if monthly_rate > 0:

    required_payment = (
        amount
        * monthly_rate
        * (1 + monthly_rate) ** term_months
        / (
            (1 + monthly_rate) ** term_months - 1
        )
    )

else:

    required_payment = amount / term_months


# ============================================================
# MONTHLY PAYMENT INPUT
# ============================================================

st.sidebar.write(
    f"Required payment for selected term: "
    f"**RM {required_payment:,.2f}**"
)

monthly_payment = st.sidebar.number_input(
    "Monthly Payment (RM)",
    min_value=10.0,
    value=float(round(required_payment, 2)),
    step=50.0
)

# ============================================================
# PAYMENT STRATEGY
# ============================================================

strategy = st.sidebar.selectbox(
    "Payment Behavior",
    [
        "On-time",
        "Early",
        "Late"
    ]
)

# ============================================================
# PAYMENT STRATEGY CALCULATION
# ============================================================

if strategy == "On-time":

    actual_payment = monthly_payment

elif strategy == "Early":

    # Pay 20% more than the selected monthly payment
    actual_payment = monthly_payment * 1.20

else:

    # Pay 20% less than the selected monthly payment
    actual_payment = monthly_payment * 0.80


# ============================================================
# LOAN / CREDIT CARD INFORMATION
# ============================================================

if loan_type == "Loan":

    st.sidebar.info(
        "🏦 Loan selected\n\n"
        "The simulation uses a fixed monthly payment "
        "and reduces the balance over time."
    )

else:

    st.sidebar.info(
        "💳 Credit Card selected\n\n"
        "The simulation applies monthly interest to "
        "the remaining balance."
    )


# ============================================================
# SIMULATION FUNCTION
# ============================================================

def simulate_loan(
    amount,
    monthly_rate,
    monthly_payment
):

    balance = amount

    months = []
    balances = []
    interest_paid = []
    principal_paid = []
    payments = []

    total_interest = 0

    month = 0

    # Safety check
    if monthly_payment <= amount * monthly_rate:

        return None, None, None

    while balance > 0 and month < 1000:

        month += 1

        # Calculate monthly interest
        interest = balance * monthly_rate

        # Make sure final payment does not exceed
        # remaining balance + interest
        payment = min(
            monthly_payment,
            balance + interest
        )

        # Principal portion
        principal = payment - interest

        # Update balance
        balance -= principal

        if balance < 0:
            balance = 0

        # Add interest
        total_interest += interest

        # Store results
        months.append(month)
        balances.append(balance)
        interest_paid.append(interest)
        principal_paid.append(principal)
        payments.append(payment)

    # Create dataframe
    df = pd.DataFrame({
        "Month": months,
        "Payment": payments,
        "Interest": interest_paid,
        "Principal": principal_paid,
        "Remaining Balance": balances
    })

    # Total amount repaid
    total_repaid = amount + total_interest

    return df, total_interest, total_repaid


# ============================================================
# CURRENT STRATEGY SIMULATION
# ============================================================

df, total_interest, total_repaid = simulate_loan(
    amount,
    monthly_rate,
    actual_payment
)

# ============================================================
# HANDLE INVALID PAYMENT
# ============================================================

if df is None:

    st.error(
        "⚠️ The monthly payment is too low to cover "
        "the interest. Please increase the monthly payment."
    )

    st.stop()


# ============================================================
# PAYOFF TIME
# ============================================================

payoff_time = len(df)


# ============================================================
# ADDITIONAL COST
# ============================================================

additional_cost = total_repaid - amount


# ============================================================
# STRATEGY COMPARISON
# ============================================================

strategies = {

    "Early": monthly_payment * 1.20,

    "On-time": monthly_payment,

    "Late": monthly_payment * 0.80
}

comparison = []

for name, payment in strategies.items():

    temp_df, interest, repaid = simulate_loan(
        amount,
        monthly_rate,
        payment
    )

    # If payment cannot cover monthly interest
    if temp_df is None:

        comparison.append({
            "Strategy": name,
            "Monthly Payment": payment,
            "Total Interest": float("inf"),
            "Total Repaid": float("inf"),
            "Payoff Time": "Not paid off"
        })

    else:

        comparison.append({
            "Strategy": name,
            "Monthly Payment": payment,
            "Total Interest": interest,
            "Total Repaid": repaid,
            "Payoff Time": len(temp_df)
        })


comparison_df = pd.DataFrame(comparison)


# ============================================================
# BASELINE: ON-TIME INTEREST
# ============================================================

on_time_interest = comparison_df.loc[
    comparison_df["Strategy"] == "On-time",
    "Total Interest"
].iloc[0]


# ============================================================
# SAVINGS / EXTRA COST
# ============================================================

interest_difference = (
    total_interest - on_time_interest
)


# ============================================================
# SUMMARY
# ============================================================

st.subheader("📊 Current Scenario")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monthly Payment",
    f"RM {actual_payment:,.2f}"
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
    "Time to Payoff",
    f"{payoff_time} months"
)


# ============================================================
# STRATEGY IMPACT MESSAGE
# ============================================================

st.subheader("💡 Repayment Impact")

if strategy == "Early":

    savings = abs(interest_difference)

    st.success(
        f"💰 Early repayment reduces the repayment period "
        f"and saves approximately **RM {savings:,.2f}** "
        f"in interest compared with the on-time scenario."
    )

elif strategy == "Late":

    extra_cost = abs(interest_difference)

    st.warning(
        f"⏰ Late repayment increases the repayment period "
        f"and costs approximately **RM {extra_cost:,.2f}** "
        f"more in interest compared with the on-time scenario."
    )

else:

    st.info(
        "✅ On-time repayment is being used as the baseline "
        "for comparing the other repayment strategies."
    )


# ============================================================
# VIEW 1 — PAYMENT SCHEDULE
# ============================================================

st.subheader("📈 View 1: Payment Schedule")

st.write(
    f"Remaining balance for the **{strategy}** "
    f"repayment strategy."
)

st.line_chart(
    df.set_index("Month")[
        "Remaining Balance"
    ]
)


# ============================================================
# PAYMENT DATA TABLE
# ============================================================

with st.expander("🔎 View Payment Schedule Data"):

    display_schedule = df.copy()

    display_schedule["Payment"] = (
        display_schedule["Payment"]
        .map(lambda x: f"RM {x:,.2f}")
    )

    display_schedule["Interest"] = (
        display_schedule["Interest"]
        .map(lambda x: f"RM {x:,.2f}")
    )

    display_schedule["Principal"] = (
        display_schedule["Principal"]
        .map(lambda x: f"RM {x:,.2f}")
    )

    display_schedule["Remaining Balance"] = (
        display_schedule["Remaining Balance"]
        .map(lambda x: f"RM {x:,.2f}")
    )

    st.dataframe(
        display_schedule,
        use_container_width=True
    )


# ============================================================
# CSV DOWNLOAD
# ============================================================

csv_data = df.to_csv(index=False)

st.download_button(
    label="📥 Download Payment Schedule as CSV",
    data=csv_data,
    file_name="payment_schedule.csv",
    mime="text/csv"
)


# ============================================================
# VIEW 2 — INTEREST COMPARISON
# ============================================================

st.subheader("💹 View 2: Total Interest Comparison")

st.write(
    "Compare the total interest paid under "
    "Early, On-time, and Late repayment strategies."
)

interest_chart = comparison_df.set_index(
    "Strategy"
)["Total Interest"]

st.bar_chart(
    interest_chart
)


# ============================================================
# VIEW 3 — TOTAL COST
# ============================================================

st.subheader("💰 View 3: Total Repayment Cost")

cost_chart = comparison_df.set_index(
    "Strategy"
)["Total Repaid"]

st.bar_chart(
    cost_chart
)

st.caption(
    "Total repayment = original amount borrowed + total interest."
)


# ============================================================
# VIEW 4 — PRINCIPAL VS INTEREST
# ============================================================

st.subheader("📊 View 4: Principal vs Interest")

principal_amount = amount

interest_amount = total_interest

principal_interest_df = pd.DataFrame({
    "Amount": [
        principal_amount,
        interest_amount
    ]
}, index=[
    "Original Principal",
    "Interest"
])

st.bar_chart(
    principal_interest_df
)


# ============================================================
# STRATEGY COMPARISON TABLE
# ============================================================

st.subheader("🔎 Strategy Comparison")

display_df = comparison_df.copy()

display_df["Monthly Payment"] = (
    display_df["Monthly Payment"]
    .map(lambda x: f"RM {x:,.2f}")
)

display_df["Total Interest"] = (
    display_df["Total Interest"]
    .map(
        lambda x:
        "Not available"
        if x == float("inf")
        else f"RM {x:,.2f}"
    )
)

display_df["Total Repaid"] = (
    display_df["Total Repaid"]
    .map(
        lambda x:
        "Not available"
        if x == float("inf")
        else f"RM {x:,.2f}"
    )
)

display_df["Payoff Time"] = (
    display_df["Payoff Time"]
    .map(
        lambda x:
        x
        if isinstance(x, str)
        else f"{x} months"
    )
)

st.dataframe(
    display_df,
    use_container_width=True
)


# ============================================================
# LOAN VS CREDIT CARD EXPLANATION
# ============================================================

st.subheader("🏦 Loan vs 💳 Credit Card")

if loan_type == "Loan":

    st.write(
        """
        **Loan scenario**

        The simulator uses a fixed repayment structure.
        The user selects the loan amount, interest rate,
        loan term, and monthly payment.

        Increasing the payment generally reduces the
        repayment period and the total interest paid.
        """
    )

else:

    st.write(
        """
        **Credit Card scenario**

        The simulator applies monthly interest to the
        remaining balance.

        Paying more than the selected monthly payment
        reduces the balance faster, while paying less
        increases the repayment period and interest cost.
        """
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

st.subheader("📝 Scenario Summary")

st.write(
    f"""
    **Payment Type:** {loan_type}

    **Amount:** RM {amount:,.2f}

    **Annual Interest Rate:** {annual_rate:.2f}%

    **Selected Monthly Payment:** RM {monthly_payment:,.2f}

    **Payment Behavior:** {strategy}

    **Actual Monthly Payment:** RM {actual_payment:,.2f}

    **Total Interest:** RM {total_interest:,.2f}

    **Total Amount Repaid:** RM {total_repaid:,.2f}

    **Time to Payoff:** {payoff_time} months

    **Additional Cost Above Principal:** RM {additional_cost:,.2f}
    """
)

st.caption(
    "This simulator is for educational purposes and uses "
    "simplified repayment assumptions."
)