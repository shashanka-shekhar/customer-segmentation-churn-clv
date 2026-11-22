# Customer Segmentation, Churn Prediction and Customer Lifetime Value

This project segments retail customers, predicts which ones are likely to churn, estimates their 12-month customer lifetime value (CLV), and ranks them by expected revenue at risk. A Streamlit dashboard shows the results and a contact list.

It uses two datasets:

- **UCI Online Retail II** (transactions from a UK online retailer), for segmentation, churn and CLV.
- **IBM Telco Customer Churn** (separate customers), as a churn benchmark. The two datasets share no customers, so Telco results are not linked to the UCI segments.

## Method

1. **Cleaning.** Remove rows without a Customer ID, cancellation rows, rows with non-positive quantity or price, and non-product lines such as postage and fees.
2. **Segmentation.** Compute recency, frequency and monetary value per customer, log-transform and standardize them, and cluster with K-Means (k = 4). Segments are named Champions, Recent, At Risk and Lost by median recency.
3. **Churn model.** The cutoff is 90 days before the last transaction. Features use only earlier transactions; the label is "no purchase in the next 90 days". Logistic regression and gradient boosting are compared on a holdout split. Each customer's score is out-of-fold, so no customer is scored by a model trained on them.
4. **CLV.** BG/NBD predicts purchase frequency and Gamma-Gamma predicts spend per order, over a 12-month horizon. Invoices above £50,000 are capped for the CLV calculation only.
5. **Expected revenue at risk.** Churn probability multiplied by 12-month CLV.
6. **Validation.** A holdout check compares predicted and actual repeat orders for the final 90 days.

## Results

Figures are from the final notebook run, as of 10 September 2011 (5,256 customers).

| Segment | Customers | Avg predicted churn | Expected revenue at risk (£) |
| --- | --- | --- | --- |
| At Risk | 1,595 | 53% | 613,158 |
| Champions | 877 | 16% | 471,585 |
| Lost | 2,111 | 80% | 457,541 |
| Recent | 673 | 44% | 258,847 |

- Churn model test ROC-AUC: 0.796 (gradient boosting), 0.787 (logistic regression).
- Telco benchmark test ROC-AUC: 0.839.
- The CLV purchase model underpredicts repeat orders by about 21% on the holdout check, so CLV totals are likely understated.

See `docs/customer-segmentation-report-final.docx` for the full write-up.

## Repository layout

```
.
├── notebooks/
│   └── customer_segmentation_churn.ipynb   # full pipeline: cleaning, segmentation, churn, CLV, validation
├── app.py                                   # Streamlit dashboard
├── data/
│   └── raw/                                 # place the two raw datasets here (not included)
├── docs/
│   └── customer-segmentation-report-final.docx
└── README.md
```

## Setup

Python 3 with the following packages:

```
pip install numpy pandas scikit-learn lifetimes streamlit jupyter
```

## Data

Download the raw files and place them in `data/raw/`:

- `online_retail_II.csv` from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- `WA_Fn-UseC_-Telco-Customer-Churn.csv`, the IBM Telco Customer Churn sample dataset

## Running

1. **Set paths.** The first cell of the notebook defines `RAW_UCI`, `RAW_TELCO` and `OUT_DIR`. The notebook was written for Windows paths, so update them to match your machine. `OUT_DIR` must exist and is where the output CSVs are written.
2. **Run the notebook** from top to bottom. It writes `customer_scores_final.csv` to `OUT_DIR`.
3. **Launch the dashboard:**\
   streamlit run app.py\
   The `SCORES` variable at the top of `app.py` must point to the same `customer_scores_final.csv`. Restart Streamlit after rerunning the notebook, because the data is cached.

## Dashboard

- **Summary cards:** customer count, average churn, number at 50% or higher, and total expected revenue at risk.
- **Segment summary:** counts, average churn, total CLV and revenue at risk by segment.
- **Churn vs value chart:** each customer plotted by churn probability and log10 CLV.
- **Contact list:** top 50 customers by expected revenue at risk, with a CSV download of the full ranked list.
- **Minimum churn slider:** filters customers by churn probability. The default is 0.5; set it to 0 to see everyone.

## Known limitations

- **Churn model uses default settings** and one holdout split. Precision and recall for the UCI model are not reported.
- **CLV is revenue, not profit,** and is undiscounted.
- **Realized churn by segment** is not reported; the segment figures above are predicted probabilities.
- **Hardcoded Windows paths** in the notebook and `app.py`.

## Status

Work in progress. The known limitations above are the main open items.
