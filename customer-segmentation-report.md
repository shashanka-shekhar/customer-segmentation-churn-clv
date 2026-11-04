# Customer Segmentation, Churn Prediction and Customer Lifetime Value

**Date:** 4 November 2026

## Summary

This project uses one retail dataset to answer three connected questions:

1. **Who are the customers?** RFM scoring and K-Means place 5,248 customers into four segments: Champions, Recent, At Risk and Lost.
2. **Do the segments predict future behaviour?** Yes. Churn rises from 16% in Champions to 80% in Lost, and 90-day spend falls by about 96%, from £2,082 to £82.
3. **Who should we contact first?** A gradient-boosting churn model (test ROC-AUC 0.789) and a 12-month customer lifetime value (CLV) model combine into a contact list ranked by expected revenue at risk. Predicted 12-month CLV is £7.15M, and expected revenue at risk is £1.81M. At Risk customers carry the largest share of that risk (£598k).

A tuned churn benchmark on the separate IBM Telco dataset is included for comparison. The two datasets share no customers.

## Data and cleaning

### UCI Online Retail II (transactions)

| Step | Lines removed | Lines remaining |
|---|---|---|
| Raw data | | 1,067,371 |
| Missing Customer ID | 243,007 | 824,364 |
| Cancellations matched to original orders | 15,562 fully, 119 partly | 799,385 sales lines |
| Non-product lines (postage, manual adjustments, bank charges, fees, discounts) | 2,795 (£232k) | 796,590 |

After cleaning, the data covers 5,839 customers.

**Cancellation matching.** Each cancellation was matched to an earlier order from the same customer for the same product at the same price, latest first, and the matched quantity was removed. Of 18,744 cancellation lines, 15,562 matched fully and 119 matched partly. The remaining 3,063 (16%) could not be matched: 2,070 had no earlier sale of that product to that customer, 866 had an earlier sale at a different price, and 127 had earlier sales already used up.

**Non-product lines.** Postage (£124k), manual adjustments (£79k), carriage (£13k), dotcom postage (£12k), stock adjustments (£4k), bank charges and discounts were removed, since they are not customer purchases.

### Validation design

To test whether the segments predict behaviour, the data was split at 10 September 2011. Features came from transactions before that date. The outcome was whether each customer bought in the following 90 days, to 9 December 2011. This left 5,248 customers who had bought before the cutoff. The churn rate at the cutoff was 56.5%.

### IBM Telco Customer Churn (benchmark)

7,043 customers. We dropped 11 rows with a blank `TotalCharges` value, leaving 7,032. An 80/20 stratified split gave 1,407 test customers.

## Method

**RFM segmentation.** For each customer: recency (days since last purchase), frequency (number of invoices) and monetary value (total revenue). The values were log-transformed, standardised and clustered with K-Means.

**Choosing the number of segments.** Silhouette scores were 0.436 for k=2, 0.346 for k=3, **0.364 for k=4** and 0.343 for k=5. k=2 scores highest but gives only two broad groups, so k=4 was chosen.

**Churn model.** The label is "no purchase in the next 90 days." Logistic regression and gradient boosting were tuned by grid search with five-fold stratified cross-validation. The classification threshold was chosen on training data only. Performance was checked with 25 repeated cross-validation folds, then on a held-out test set.

**CLV model.** BG/NBD predicts purchase frequency and Gamma-Gamma predicts spend per order, using weekly units and a 12-month horizon. CLV is expected orders multiplied by expected order value, calculated as of the cutoff and undiscounted. One invoice above £50,000 was capped for CLV, and this has no effect after cancellation matching.

**Expected revenue at risk** is churn probability multiplied by 12-month CLV. It ranks customers by the revenue likely to be lost if they leave. It is a prioritisation score, not a forecast.

## Results

### Segments predict future behaviour

| Segment | Customers | Median days since last purchase | Churn rate (next 90 days) | Mean spend, next 90 days (£) |
|---|---|---|---|---|
| Champions | 867 | 19 | 16% | 2,082 |
| Recent | 658 | 26 | 44% | 395 |
| At Risk | 1,610 | 163 | 53% | 329 |
| Lost | 2,113 | 326 | 80% | 82 |

### Churn model

| Model | Repeated CV ROC-AUC | Test ROC-AUC | Recall | Precision |
|---|---|---|---|---|
| Logistic regression | 0.788 ± 0.017 | 0.779 | 0.88 | 0.69 |
| **Gradient boosting** | **0.807 ± 0.016** | **0.789** | **0.90** | **0.70** |

Gradient boosting was selected as the main model. Its cross-validation and test scores are close, so it is not overfitting to one split.

**How much do the features add beyond recency?** A recency-only rule scores 0.755 on the test set. The full model adds about 0.03. Recency carries most of the churn signal.

**Practical use.** At the chosen threshold, the model catches 90% of customers who go quiet for 90 days, with 70% precision. A 50% cutoff flags 3,254 customers, holding about £847k of expected 12-month revenue at risk. The contact list uses that cutoff and ranks by expected revenue at risk.

### Customer lifetime value

| Segment | Customers | Average 12-month CLV (£) | Total 12-month CLV (£) | Expected revenue at risk (£) |
|---|---|---|---|---|
| Champions | 867 | 5,286 | 4,582,726 | 502,649 |
| Recent | 658 | 960 | 631,810 | 256,462 |
| At Risk | 1,610 | 837 | 1,346,871 | 597,782 |
| Lost | 2,113 | 278 | 586,616 | 448,303 |
| **Total** | **5,248** | **1,362** | **7,148,023** | **1,805,196** |

**Validation.** The purchase model was fitted on data before the final 90 days and tested on those 90 days. It predicted 3,632 repeat orders against 4,616 actual, an underprediction of about 21%. Customer-level correlation was 0.73. The model ranks customers well, but its volume predictions are conservative, so the CLV totals are likely understated.

**Top 20 contacts.** Customers with at least a 50% churn probability, ranked by expected revenue at risk. None of these customers has a large order flag.

| Rank | Customer ID | Segment | Churn probability | 12-month CLV (£) | Expected revenue at risk (£) |
|---|---|---|---|---|---|
| 1 | 18087 | Champions | 54% | 4,242 | 2,270 |
| 2 | 17850 | Champions | 62% | 3,470 | 2,151 |
| 3 | 18251 | At Risk | 69% | 2,851 | 1,969 |
| 4 | 12755 | At Risk | 54% | 3,462 | 1,852 |
| 5 | 15786 | At Risk | 58% | 2,993 | 1,744 |
| 6 | 14439 | At Risk | 55% | 3,007 | 1,654 |
| 7 | 13902 | At Risk | 84% | 1,692 | 1,426 |
| 8 | 13135 | At Risk | 64% | 1,927 | 1,234 |
| 9 | 12378 | At Risk | 56% | 2,163 | 1,213 |
| 10 | 14134 | At Risk | 73% | 1,605 | 1,167 |
| 11 | 12625 | At Risk | 51% | 2,127 | 1,076 |
| 12 | 12497 | At Risk | 63% | 1,692 | 1,073 |
| 13 | 17044 | At Risk | 61% | 1,712 | 1,046 |
| 14 | 15332 | At Risk | 51% | 2,039 | 1,031 |
| 15 | 14096 | Recent | 56% | 1,696 | 957 |
| 16 | 14091 | At Risk | 92% | 906 | 834 |
| 17 | 18079 | At Risk | 51% | 1,615 | 823 |
| 18 | 12578 | At Risk | 60% | 1,312 | 782 |
| 19 | 15480 | Recent | 54% | 1,435 | 770 |
| 20 | 12798 | At Risk | 58% | 1,316 | 767 |

Two customers are worth a closer look before outreach. 17850 is a Champion at 62% churn, a high-value customer who may be drifting away. 14091 has a 92% churn probability but a modest CLV of £906, so the expected loss is small despite the risk.

### Benchmark: IBM Telco churn

| Model | Repeated CV ROC-AUC | Test ROC-AUC | Recall | Precision |
|---|---|---|---|---|
| Logistic regression (tuned) | 0.847 ± 0.008 | 0.834 | 0.74 | 0.52 |
| Gradient boosting (tuned) | 0.850 ± 0.007 | 0.839 | 0.76 | 0.52 |
| Tenure only (baseline) | | 0.747 | | |

The two tuned models are effectively tied, so logistic regression is preferred because its coefficients are easier to explain. The full model adds about 0.09 over tenure alone. The strongest signals were tenure, monthly charges, month-to-month contracts, missing online security and tech support, electronic check payments, and fibre optic service.

## Recommendations

1. **Win back At Risk customers first.** They carry the largest expected revenue at risk (£598k) across 1,610 customers, with a 53% churn rate.
2. **Protect Champions.** They hold about 64% of predicted CLV (£4.6M). Their churn rate is low, but at 16% roughly 140 could leave in any quarter, and each one is worth about £5,300.
3. **Move Recent customers towards Champions.** Their average CLV is £960, and at 44% churn they are at a critical point. Offers that encourage a second and third purchase could build a larger loyal base.
4. **Keep retention spend on Lost customers low.** Their 90-day spend averages £82 and their churn rate is 80%, so an expensive offer is unlikely to pay back.

## Limitations

- **Revenue, not profit.** The dataset has no cost data, so CLV measures revenue. Margin would give a more accurate picture of value.
- **Undiscounted CLV.** Future revenue is not discounted, so the 12-month values are slightly higher than a discounted calculation would give.
- **Conservative volume.** The purchase model underpredicts orders by about 21% on the holdout test, so CLV totals are likely understated.
- **Unmatched cancellations.** 3,063 cancellation lines (16%) could not be matched to an original order. Most had no earlier sale of that product to that customer, which suggests the original order was recorded without a Customer ID and was dropped at the start.
- **Non-product lines excluded.** Postage, fees and manual adjustments (£232k) were removed. Shipping income is excluded from customer value, so CLV measures product revenue only.
- **Recency dominates churn.** Most of the churn signal comes from recency alone. The full model adds a modest improvement.
- **Churn definition.** Churn means no purchase in 90 days. Customers who buy less often than quarterly are counted as churned even if they are still active, so results may differ with a longer window.
- **Separate datasets.** The Telco benchmark and the UCI analysis use different customers, so Telco results cannot be linked to UCI segments.
- **Time period.** The UCI data covers December 2009 to December 2011, so results reflect that period.

## Next steps

1. Investigate the unmatched cancellations, including originals recorded without a Customer ID.
2. Add profit margins, if available, to convert CLV from revenue to profit.
3. Discount future revenue to get a present-value CLV.
4. Test a 120-day churn window to check whether results hold for less frequent buyers.
