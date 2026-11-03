# Customer Segmentation, Churn Prediction and Customer Lifetime Value

An end-to-end customer analytics project on UK online retail transactions. It segments customers with RFM and K-Means, predicts 90-day churn, estimates 12-month customer lifetime value (CLV), and ranks which customers to contact first in an interactive dashboard.

## Key results

| Area | Result |
|---|---|
| Data cleaned | 1,067,371 raw rows → 805,549 clean transactions, 5,878 customers |
| Segments (K-Means, k=4, silhouette 0.365) | Champions, Recent, At Risk, Lost |
| Segments predict behavior | Churn rises from 16% (Champions) to 80% (Lost) over the next 90 days |
| Churn model (gradient boosting) | Test ROC-AUC 0.817; 95% recall, 69% precision at tuned threshold |
| Recency-only baseline | Test ROC-AUC 0.772 |
| Predicted 12-month CLV (as of cutoff) | £7.46M total; Champions hold about 65% |
| Expected revenue at risk | £1.93M; At Risk segment carries the most (£626k) |
| CLV validation (90-day holdout) | Correlation 0.73; model underpredicts order volume by about 21% |
| Benchmark: IBM Telco churn (tuned) | Test ROC-AUC 0.839 (gradient boosting), 0.834 (logistic regression); tenure-only 0.747 |

## Dataset

- **UCI Online Retail II:** transactions from a UK-based online retailer, December 2009 to December 2011. Download from the UCI Machine Learning Repository and save as `data/raw/online_retail_II.csv`.
- **IBM Telco Customer Churn:** 7,043 customers with contract, service and billing fields. Download from Kaggle and save as `data/raw/telco_churn.csv`.

The two datasets share no customers, so the Telco model is a benchmark, not part of the segmentation analysis.

## Method

1. **Cleaning** (`src/01_clean.py`): drop rows without a Customer ID, remove cancellations (invoices starting with "C"), and remove rows with zero or negative quantity or price.
2. **RFM segmentation** (`src/02_rfm_segments.py`): recency, frequency and monetary value per customer, log-transformed and standardized, clustered with K-Means. k was chosen by silhouette score.
3. **Churn model** (`src/03_churn_uci.py`): features come from transactions before a cutoff (10 September 2011). The outcome is no purchase in the following 90 days. Logistic regression and gradient boosting are tuned with grid search and repeated cross-validation, and the threshold is chosen on training data only. Segments are rebuilt from pre-cutoff data and checked against the outcome.
4. **Benchmark** (`src/04_churn_telco.py`): the same tuning method on the Telco dataset.
5. **CLV** (`src/05_clv.py`): BG/NBD predicts purchase frequency and Gamma-Gamma predicts spend per order, as of the cutoff. Expected revenue at risk is churn probability times CLV. Single invoices above £50,000 are capped for CLV.
6. **Dashboard** (`app.py`): a Streamlit app to filter segments and churn risk, view the segment summary, and download a ranked contact list.

## Repository structure

```
customer-segmentation-churn/
├── data/
│   ├── raw/                  # not committed: online_retail_II.csv, telco_churn.csv
│   └── processed/            # created by the scripts
├── src/
│   ├── 01_clean.py
│   ├── 02_rfm_segments.py
│   ├── 03_churn_uci.py
│   ├── 04_churn_telco.py
│   └── 05_clv.py
├── app.py
├── requirements.txt
└── README.md
```

## Setup and run

```bash
pip install -r requirements.txt

python src/01_clean.py
python src/02_rfm_segments.py      # optional, exploratory
python src/03_churn_uci.py
python src/04_churn_telco.py
python src/05_clv.py
streamlit run app.py
```

## Data notes

- One invoice (581483, 9 December 2011) contains 80,995 units of a single item at £2.08, a total of £168,469.60. This looks like a data-entry error, and it's capped for CLV. It also falls in the churn outcome window, which inflates spend for one customer. It should be checked against the raw data before any figures are used externally.
- Cancellations are removed, but they are not paired with the orders they cancel. This affects a small number of customers and is a known limitation.

## Limitations

- **Revenue, not profit.** The dataset has no cost data, so CLV measures revenue.
- **Undiscounted CLV.** Future revenue is not discounted.
- **Conservative volume.** The purchase model underpredicts orders by about 21% on the holdout test, so CLV totals are likely understated.
- **Recency dominates churn.** Most of the churn signal comes from recency alone.
- **Churn definition.** No purchase in 90 days may count customers who buy less than quarterly as churned. Results may differ with a longer window.
- **Separate datasets.** Telco results cannot be linked to UCI segments or CLV.
- **Time period.** The results reflect December 2009 to December 2011.

## Next steps

- Verify the 80,995-unit invoice and pair cancellations with their original orders in the cleaning step.
- Add profit margins to convert CLV from revenue to profit.
- Discount future revenue to get present-value CLV.
- Test a 120-day churn window.

## Tech stack

Python, pandas, NumPy, scikit-learn, lifetimes, Streamlit
