
import os
import numpy as np
import pandas as pd

np.random.seed(42)

OUTPUT_DIR = "data/generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

N_CUSTOMERS = 50_000
MONTHS = pd.date_range("2023-01-01", "2025-12-01", freq="MS")

tiers = ["Essential", "Plus", "Premium"]
tier_prices = {"Essential": 10, "Plus": 25, "Premium": 50}

channels = ["Organic", "Paid Search", "Referral", "Partner", "Social"]
states = ["NY", "NJ", "CA", "TX", "FL", "GA", "IL"]

customers = pd.DataFrame({
    "customer_id": range(1, N_CUSTOMERS + 1),
    "signup_date": pd.to_datetime(
        np.random.choice(pd.date_range("2023-01-01", "2025-10-31"), N_CUSTOMERS)
    ),
    "acquisition_channel": np.random.choice(
        channels, N_CUSTOMERS, p=[0.25, 0.30, 0.18, 0.15, 0.12]
    ),
    "state": np.random.choice(states, N_CUSTOMERS),
    "subscription_tier": np.random.choice(
        tiers, N_CUSTOMERS, p=[0.55, 0.32, 0.13]
    )
})

customers["customer_segment"] = np.random.choice(
    ["Budget Builder", "Investor", "Family Planner", "Credit Improver"],
    N_CUSTOMERS,
    p=[0.35, 0.25, 0.20, 0.20]
)

customers.to_csv(f"{OUTPUT_DIR}/dim_customers.csv", index=False)

# Funnel
funnel = customers[["customer_id", "signup_date", "acquisition_channel"]].copy()
funnel["visitor_date"] = funnel["signup_date"] - pd.to_timedelta(
    np.random.randint(0, 21, N_CUSTOMERS), unit="D"
)
funnel["trial_start_date"] = funnel["signup_date"] + pd.to_timedelta(
    np.random.randint(0, 5, N_CUSTOMERS), unit="D"
)

channel_paid_prob = {
    "Organic": 0.62,
    "Paid Search": 0.48,
    "Referral": 0.72,
    "Partner": 0.64,
    "Social": 0.44,
}

funnel["paid_conversion_probability"] = funnel["acquisition_channel"].map(channel_paid_prob)
funnel["converted_to_paid"] = (
    np.random.rand(N_CUSTOMERS) < funnel["paid_conversion_probability"]
).astype(int)

funnel["paid_date"] = np.where(
    funnel["converted_to_paid"] == 1,
    funnel["trial_start_date"] + pd.to_timedelta(np.random.randint(7, 21, N_CUSTOMERS), unit="D"),
    pd.NaT
)

funnel["activation_date"] = np.where(
    funnel["converted_to_paid"] == 1,
    pd.to_datetime(funnel["paid_date"]) + pd.to_timedelta(np.random.randint(0, 14, N_CUSTOMERS), unit="D"),
    pd.NaT
)

funnel = funnel.drop(columns=["paid_conversion_probability"])
funnel.to_csv(f"{OUTPUT_DIR}/fact_funnel.csv", index=False)

# Monthly customer facts
rows = []

retention_base = {
    "Essential": 0.91,
    "Plus": 0.94,
    "Premium": 0.965,
}

channel_retention_adj = {
    "Organic": 0.01,
    "Paid Search": -0.025,
    "Referral": 0.02,
    "Partner": 0.005,
    "Social": -0.015,
}

for _, c in customers.iterrows():
    paid_date = pd.to_datetime(funnel.loc[funnel["customer_id"] == c["customer_id"], "paid_date"].iloc[0])

    if pd.isna(paid_date):
        continue

    start_month = paid_date.to_period("M").to_timestamp()
    active = True
    reactivated = False

    for month in MONTHS:
        if month < start_month:
            continue

        if active:
            tier = c["subscription_tier"]
            retention_probability = retention_base[tier] + channel_retention_adj[c["acquisition_channel"]]
            retention_probability = min(max(retention_probability, 0.75), 0.99)

            churned = np.random.rand() > retention_probability

            sessions = np.random.poisson(
                {"Essential": 5, "Plus": 9, "Premium": 14}[tier]
            )

            days_active = min(sessions, np.random.randint(1, 22))
            features_used = np.random.randint(1, {"Essential": 4, "Plus": 6, "Premium": 8}[tier])

            investment_used = int(np.random.rand() < {"Essential": 0.12, "Plus": 0.28, "Premium": 0.48}[tier])
            tax_used = int(np.random.rand() < {"Essential": 0.08, "Plus": 0.20, "Premium": 0.36}[tier])
            credit_used = int(np.random.rand() < {"Essential": 0.18, "Plus": 0.30, "Premium": 0.42}[tier])

            addon_revenue = (
                investment_used * 15
                + tax_used * 20
                + credit_used * 10
            )

            rows.append({
                "customer_id": c["customer_id"],
                "month": month,
                "subscription_tier": tier,
                "subscription_revenue": tier_prices[tier],
                "addon_revenue": addon_revenue,
                "mrr": tier_prices[tier] + addon_revenue,
                "sessions": sessions,
                "days_active": days_active,
                "features_used": features_used,
                "investment_tool_used": investment_used,
                "tax_planning_used": tax_used,
                "credit_monitoring_used": credit_used,
                "active_flag": 1,
                "churn_flag": int(churned),
                "reactivated_flag": int(reactivated),
            })

            if churned:
                active = False
                reactivated = False

        else:
            # Small chance of reactivation later
            if np.random.rand() < 0.025:
                active = True
                reactivated = True

monthly = pd.DataFrame(rows)

fact_subscriptions = monthly[
    ["customer_id", "month", "subscription_tier", "subscription_revenue", "addon_revenue", "mrr"]
]
fact_engagement = monthly[
    ["customer_id", "month", "sessions", "days_active", "features_used"]
]
fact_utilization = monthly[
    ["customer_id", "month", "investment_tool_used", "tax_planning_used", "credit_monitoring_used"]
]
fact_retention = monthly[
    ["customer_id", "month", "active_flag", "churn_flag", "reactivated_flag"]
]

fact_subscriptions.to_csv(f"{OUTPUT_DIR}/fact_subscriptions.csv", index=False)
fact_engagement.to_csv(f"{OUTPUT_DIR}/fact_engagement.csv", index=False)
fact_utilization.to_csv(f"{OUTPUT_DIR}/fact_utilization.csv", index=False)
fact_retention.to_csv(f"{OUTPUT_DIR}/fact_retention.csv", index=False)

# Forecast inputs
forecast_inputs = pd.DataFrame({
    "month": MONTHS,
    "expected_growth": np.linspace(0.08, 0.14, len(MONTHS)),
    "expected_retention": np.linspace(0.92, 0.95, len(MONTHS)),
    "expected_activation": np.linspace(0.50, 0.62, len(MONTHS)),
})
forecast_inputs.to_csv(f"{OUTPUT_DIR}/fact_forecast_inputs.csv", index=False)

# Budget
actual_monthly = fact_subscriptions.groupby("month").agg(
    actual_mrr=("mrr", "sum"),
    actual_active_subscribers=("customer_id", "nunique"),
).reset_index()

budget = actual_monthly.copy()
budget["budget_mrr"] = budget["actual_mrr"] * np.random.normal(1.08, 0.04, len(budget))
budget["budget_active_subscribers"] = (
    budget["actual_active_subscribers"] * np.random.normal(1.05, 0.03, len(budget))
).round()

budget["budget_new_subscribers"] = np.random.randint(700, 1800, len(budget))
budget["budget_retention_rate"] = np.random.uniform(0.92, 0.96, len(budget))
budget["budget_activation_rate"] = np.random.uniform(0.50, 0.65, len(budget))

budget["budget_subscription_mix_essential"] = np.random.uniform(0.48, 0.55, len(budget))
budget["budget_subscription_mix_plus"] = np.random.uniform(0.30, 0.36, len(budget))
budget["budget_subscription_mix_premium"] = (
    1
    - budget["budget_subscription_mix_essential"]
    - budget["budget_subscription_mix_plus"]
)

budget["budget_addon_revenue"] = budget["budget_mrr"] * np.random.uniform(0.18, 0.28, len(budget))

budget = budget[
    [
        "month",
        "budget_mrr",
        "budget_active_subscribers",
        "budget_new_subscribers",
        "budget_retention_rate",
        "budget_activation_rate",
        "budget_subscription_mix_essential",
        "budget_subscription_mix_plus",
        "budget_subscription_mix_premium",
        "budget_addon_revenue",
    ]
]

budget.to_csv(f"{OUTPUT_DIR}/fact_budget.csv", index=False)

print("Synthetic NovaFin data generated successfully.")
print(f"Customers: {len(customers):,}")
print(f"Monthly subscription rows: {len(fact_subscriptions):,}")