---

## title: "Customer Segmentation, Churn Prediction and Customer Lifetime Value" date: "22 November 2026"

## Summary

This project uses one retail dataset to answer three connected questions about customers.

1. **Who are they?** RFM values and K-Means group customers into four segments: Champions, Recent, At Risk and Lost.
2. **Who is likely to leave?** A gradient boosting churn model reaches a test ROC-AUC of 0.796. Predicted churn rises from 16% in Champions to 80% in Lost.
3. **Who is worth contacting first?** Predicted 12-month customer lifetime value (CLV) is combined with churn probability to rank customers by expected revenue at risk. As of the cutoff, predicted CLV totals £7.34M and expected revenue at risk is £1.80M.

A benchmark churn model on the separate IBM Telco dataset is included for comparison. The two datasets share no customers, so Telco results cannot be linked to the UCI segments.

## Data

### UCI Online Retail II (transactions)

Transactions from a UK-based online retailer. Cleaning steps:

| Step | Rows removed | Rows remaining |
| --- | --- | --- |
| Raw data |  | 1,067,371 |
| Missing Customer ID | 243,007 | 824,364 |
| Cancellations, quantity or price ≤ 0, and non-product lines (combined) | 21,720 | **802,644** |

The cleaned data holds 5,852 customers. Cancellation rows are removed, but the sales they reverse are kept. See Limitations.

The data was split at 10 September 2011. Features came from transactions before that date, and outcomes from the following 90 days, to 9 December 2011. That left **5,256 customers** who had bought before the cutoff. All segment, churn and CLV figures in this report use this split.

### IBM Telco Customer Churn (benchmark)

7,043 customers with 21 columns, of whom 26.5% churned. We dropped 11 rows with a blank `TotalCharges` value (new customers with zero tenure), leaving 7,032. An 80/20 stratified split gave 1,407 test customers.

## Method

**RFM segmentation.** For each customer we calculated:

- **Recency:** days since the last purchase at the cutoff.
- **Frequency:** number of distinct invoices before the cutoff.
- **Monetary:** total revenue before the cutoff, calculated as Quantity × Price.

We applied a log transform and standardized the three measures, then clustered customers into four groups with K-Means (random seed 42). The groups are named by median recency: the group with the most recent buyers is Champions, and the group with the least recent is Lost. An exploratory segmentation on the full period was also run but is not used in the results.

**Validation design.** To test whether the segments predict behavior, we rebuilt them using only data before the cutoff. Segments were not chosen based on the outcome.

**Churn model.** The label is "no purchase in the next 90 days." We compared logistic regression and gradient boosting, both with default settings, on one 80/20 stratified split. Each customer's churn probability comes from five-fold out-of-fold predictions, so no customer is scored by a model trained on them. A customer is flagged as at risk at a probability of 0.5.

**CLV model.** We used BG/NBD to predict purchase frequency and Gamma-Gamma to predict spend per order, with a weekly time unit and a 12-month horizon. CLV is expected orders multiplied by expected order value. Figures are undiscounted. Invoices above £50,000 were capped at £50,000 for the CLV calculation only. The churn model uses uncapped revenue.

**Expected revenue at risk** is churn probability multiplied by 12-month CLV. It ranks customers by how much revenue is likely to be lost if they leave. It is a prioritization score, not a forecast.

## Results

### Segments

Predicted churn and CLV by segment, as of the cutoff:

| Segment | Customers | Average predicted churn | Average CLV (£) | Total CLV (£) | Expected revenue at risk (£) |
| --- | --- | --- | --- | --- | --- |
| At Risk | 1,595 | 53% | 854 | 1,362,741 | 613,158 |
| Champions | 877 | 16% | 5,388 | 4,725,591 | 471,585 |
| Lost | 2,111 | 80% | 282 | 595,793 | 457,541 |
| Recent | 673 | 44% | 968 | 651,429 | 258,847 |
| **Total** | **5,256** | **56%** | **1,396** | **7,335,554** | **1,801,131** |

Average predicted churn rises from Champions to Lost, matching the segment ordering. This version does not print realized churn or spend by segment, so the predicted probabilities are the only segment-level churn figures reported here.

### Churn model

| Model | Test ROC-AUC |
| --- | --- |
| Logistic regression | 0.787 |
| **Gradient boosting** | **0.796** |

Gradient boosting is used as the main model because its test ROC-AUC is slightly higher. Both models were fit once with default settings, so the gap is small and within the usual variation between splits. It does not show that one model is clearly better. Precision and recall for the UCI model were not computed in this version.

### Customer lifetime value

**Validation.** We trained the purchase model on data before the final 90 days and tested it on those 90 days. The model predicted 3,648 repeat orders against 4,630 actual, underpredicting by about 21%. Customer-level correlation was 0.73. The model ranks customers reasonably well, but its volume predictions are conservative, so the CLV totals are likely understated.

### Dashboard

The Streamlit dashboard shows the segment summary, a churn-versus-value chart, and a contact list. The minimum churn probability slider sets which customers are shown. At the default 0.5, the dashboard shows 3,254 customers. At 0, it shows all 5,256.

The contact list ranks customers by expected revenue at risk. The top five at the time of writing were:

| Customer ID | Segment | Predicted churn | CLV (£) | Revenue at risk (£) |
| --- | --- | --- | --- | --- |
| 15749 | At Risk | 74% | 17,089 | 12,602 |
| 18102 | Champions | 5% | 224,404 | 10,395 |
| 14646 | Champions | 5% | 203,848 | 9,200 |
| 12346 | Champions | 49% | 18,563 | 9,148 |
| 14156 | Champions | 6% | 138,171 | 8,495 |

Several Champions in the top 50 have very high CLV and low predicted churn. Their CLV reflects many purchases, not a single large order, so the £50,000 cap does not reduce it. These customers have not yet been checked against their raw invoices, so treat the ranking as provisional until that is done.

### Benchmark: IBM Telco churn

| Model | Test ROC-AUC | Recall (churn) | Precision (churn) |
| --- | --- | --- | --- |
| Gradient boosting (default settings, 0.5 threshold) | 0.839 | 0.53 | 0.64 |

This version uses default settings and a 0.5 threshold, with no class weighting, so it catches only 53% of churners. The earlier tuned models in the complete analysis reached 74–76% recall at a lower threshold. The strongest Telco signals were not examined in this version.

## Recommendations

1. **Win back At Risk customers first.** They carry £613k of expected revenue at risk across 1,595 customers, with an average predicted churn of 53%.
2. **Protect Champions, but check the top accounts first.** Champions hold £4.7M of predicted CLV and have low predicted churn (16% on average). Before contacting the highest-value accounts, check their invoices (see Limitations).
3. **Move Recent customers toward Champions.** Their average CLV is £968, and their average predicted churn is 44%. Offers that encourage a second and third purchase could build a larger base of loyal customers.
4. **Keep retention spend on Lost customers low.** Their average CLV is £282 and their average predicted churn is 80%, so an expensive offer is unlikely to pay back.

## Limitations

- **Large orders are capped for CLV only.** The £50,000 cap does not reduce customers whose CLV comes from many large purchases. The churn model uses uncapped spend.
- **Revenue, not profit.** The dataset has no cost data, so CLV measures revenue. Margin would give a more accurate picture of value.
- **Undiscounted CLV.** Future revenue is not discounted, so the 12-month values are slightly higher than a discounted calculation would give.
- **Conservative volume.** The purchase model underpredicts orders by about 21% on the holdout test, so CLV totals are likely understated.
- **Churn model tuning.** Both models use default settings and a single split. Hyperparameters were not tuned, and precision and recall were not computed for the UCI model.
- **Label definition.** Churn is defined as no purchase in 90 days. Customers who buy less often than quarterly are counted as churned even if they are still active, so results may differ with a longer window.
- **Realized outcomes not reported.** This version does not show realized churn or future spend by segment.
- **Separate datasets.** The Telco benchmark and the UCI analysis use different customers, so Telco results cannot be linked to UCI segments.
- **Time period.** The UCI data covers roughly December 2009 to December 2011, so the results reflect that period.

## Next steps

1. Check the invoices of the top-ranked customers (for example 18102 and 14646) in the raw data before contacting them.
2. Add a printout of realized churn and future spend by segment, to test whether the segments predict behavior directly.
3. Add precision and recall for the UCI churn model at the chosen threshold.
4. Add profit margins, if available, to convert CLV from revenue to profit.
5. Discount future revenue to get a present-value CLV.
6. Test a 120-day churn window to check whether the results hold for less frequent buyers.
