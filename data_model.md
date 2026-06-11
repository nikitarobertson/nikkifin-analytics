## Metric Tree

```text
Monthly Recurring Revenue (MRR)
│
├── Active Subscribers
│   │
│   ├── New Subscribers
│   │   ├── Website Visitors
│   │   ├── Signup Rate
│   │   ├── Trial Conversion Rate
│   │   └── Paid Conversion Rate
│   │
│   ├── Retained Subscribers
│   │   ├── Retention Rate
│   │   ├── Product Engagement
│   │   ├── Feature Utilization
│   │   └── Customer Satisfaction
│   │
│   └── Reactivated Subscribers
│
└── Revenue Per Subscriber
    │
    ├── Subscription Revenue
    ├── Add-On Revenue
    └── Premium Adoption
```

---

### Executive KPI Framework

#### North Star

```text
MRR
```

#### Growth

```text
New Subscribers
Net Subscriber Growth
Activation Rate
Trial Conversion Rate
```

#### Engagement

```text
Monthly Active Users
Weekly Active Users
Sessions Per User
Feature Adoption
```

#### Utilization

```text
Investment Tool Usage
Tax Planning Usage
Credit Monitoring Usage
Add-On Adoption Rate
```

#### Retention

```text
Monthly Retention Rate
Subscriber Churn
Cohort Retention
Reactivation Rate
```

#### Financial

```text
MRR
ARR
Revenue Per Subscriber
LTV
Add-On Revenue
Premium Mix
```

---
**Core tables**

#### 1. dim_customers

One row per customer.

```text
  customer_id
  signup_date
  subscription_tier
  state
  acquisition_channel
```

---

#### 2. fact_funnel

Tracks movement through funnel.

  ```text
  customer_id
  visitor_date
  signup_date
  trial_start_date
  paid_date
  activation_date
```

---

#### 3. fact_subscriptions

Monthly revenue.

```text
  customer_id
  month
  subscription_tier
  subscription_revenue
  addon_revenue
  mrr
```

---

#### 4. fact_engagement

Product usage.

```text
  customer_id
  month
  sessions
  days_active
  features_used
```

---

#### 5. fact_utilization

Feature-specific utilization.

```text
  customer_id
  month
  investment_tool_used
  tax_planning_used
  credit_monitoring_used
```

---

#### 6. fact_retention

Customer status.

```text
  customer_id
  month
  active_flag
  churn_flag
  reactivated_flag
```

---

#### 7. fact_forecast_inputs

For scenario planning.

```text
  month
  expected_growth
  expected_retention
  expected_activation
```

---
#### 8. fact_budget

```text
  month
  budget_mrr
  budget_active_subscribers
  budget_new_subscribers
  budget_retention_rate
  budget_activation_rate
  budget_subscription_mix_essential
  budget_subscription_mix_plus
  budget_subscription_mix_premium
  budget_addon_revenue
```


### Executive Questions We Want To Answer

```text
1. What is driving MRR growth?
2. Which customer segments retain best?
3. Where are we losing users in the funnel?
4. Which features drive retention?
5. What is our projected MRR next quarter?
6. Why is revenue underperforming to budget?
7. Are we having less members than expected or is the subscription mix-shift the reason we're behind on MRR?
8. Are customers engaging with the product enough to support retention?
9. Which add-ons are driving expansion revenue?
10. What actions should leadership take this month based on metric movement?
```
