# Vireo Support Intelligence

A small local-first tool for the Vireo Audio support-ticket assessment.

## What it does

1. Deduplicates migrated helpdesk exports by `ticket_id`, preferring the current `helpdesk` copy.
2. Calculates Vireo-policy metrics: first-response SLA breach and 30-day repeat contact.
3. Builds a weekly complaint digest from the existing ticket taxonomy.
4. Uses local TF-IDF + logistic regression as an AI/ML validation layer for category consistency.
5. Uses local NMF topic modeling to discover recurring subthemes inside the broad `Other` bucket.
6. Shows agent closure volume with team/tier context. Tier 2 is not treated as a volume leaderboard because Vireo's policy says Tier 2 work is multi-touch and should be measured in resolution days.
7. Produces CSV/JSON outputs for handoff.

## Run on a clean machine

Python 3.10+ is recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python run.py
streamlit run app.py
```

Open the local Streamlit URL shown by the command.

The supplied task CSVs belong in `data/` with these names:

- tickets.csv
- agents.csv
- customers.csv
- orders.csv
- products.csv

## Important implementation decision

The raw export contains duplicate ticket IDs because the old Freshdesk export and current helpdesk export overlap. The email thread explicitly warns about this. The pipeline keeps the current `helpdesk` row when both exist. In this pack that produces 11,875 unique tickets from 12,528 raw rows.

## Business goal

The observed 30-day repeat-contact rate is 12.36%. A proposed operating target is 10%. At Vireo's stated 650 tickets/week and ₹290 blended contact cost, that target corresponds to roughly 15.4 fewer repeat contacts/week and about ₹57.9K/quarter of potential contact-cost reduction. This is a target/business case, not claimed realized savings.

## Validation

The local category model uses a stratified 80/20 holdout against the helpdesk's existing category labels. On this dataset it reaches about 84.0% agreement/accuracy on the held-out sample (2,375 tickets), with a 16.0% disagreement rate. This is not a gold-standard human label set; it is a consistency check against the source taxonomy. The main weak class is `Other`, which is precisely why the tool uses topic discovery rather than trusting the taxonomy blindly.

## AI usage

No paid runtime API calls are required. The runtime AI/ML components are scikit-learn models. ChatGPT was used during development to reason about the architecture, edge cases, evaluation design and submission wording. No customer data or API key is required by the application.

## Deliberate scope limits

- No real-time helpdesk integration.
- No automatic refunds/replacements.
- No automated employee performance score.
- No production auth/RBAC layer.
- No LLM-generated business arithmetic.

The assessment is time-boxed; deterministic calculations stay in Python and AI/ML is used where it adds signal discovery or validation.
