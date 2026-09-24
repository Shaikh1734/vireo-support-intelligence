# AI/tool-use disclosure

## Used

- ChatGPT: architecture review, data-analysis reasoning, edge-case review, evaluation design, README/memo drafting and code-review assistance.
- Python/pandas: deterministic data cleaning, policy calculations and business arithmetic.
- scikit-learn: TF-IDF + logistic regression for category consistency validation; NMF for subtheme discovery.
- Streamlit: local review UI.

## Runtime cost

**₹0 in API/model calls.** The submitted runtime does not call a paid external LLM API.

## Prompts used during development

1. "Review this support-ticket brief and identify the smallest useful AI-assisted product that can be built in five hours. Separate deterministic business logic from model-dependent logic."
2. "Given Vireo's policy definitions, design an evaluation that distinguishes model disagreement from true business error and calls out where the source taxonomy itself is weak."
3. "Review the requested agent leaderboard against the support policy. Identify any measurement caveats and propose a transparent way to show workload without pretending closure count equals performance."

## What was discarded

- A chatbot interface: it did not answer the weekly-digest need.
- LLM-generated arithmetic: unnecessary and less auditable than pandas.
- A single agent ranking across tiers: conflicts with the stated Tier 2 measurement policy.
- Automatic refund/replacement recommendations: outside scope and operationally risky.
