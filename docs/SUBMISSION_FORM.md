# Vireo Audio — submission form draft

## What did you build, and what business outcome does it move? State the number and the money.

I built a local-first Support Intelligence tool that cleans the migrated ticket export, produces a weekly complaint digest, discovers recurring subthemes inside the broad `Other` category, calculates repeat-contact/SLA metrics, and shows agent workload with tier context.

The main business KPI is 30-day repeat contact. The cleaned dataset is at **12.36%**. I propose a first target of **10%**. At Vireo's stated ~650 tickets/week, that is about **15.4 fewer repeat contacts/week**. Using the **₹290 blended contact cost** in the client email, the potential contact-cost reduction is approximately **₹4.45K/week or ₹57.9K/quarter**. This is a target/business case, not realized savings.

A concrete finding is that `Other` contains 1,691 tickets (14.2%); 225 of those mention cancellation together with a disabled/greyed control, making it a candidate product/support issue worth investigating.

## What does one run cost, and what would a month cost at Vireo's volume (roughly 650 tickets a week)? Show the arithmetic.

**Runtime model/API cost: ₹0.** The submitted runtime uses local pandas/scikit-learn models and makes no paid API calls.

At roughly 650 tickets/week, about 2,600 tickets/month, the external model-call cost remains **2,600 × ₹0 = ₹0/month**. Compute cost depends on the machine and is not included because no cloud compute is required.

## How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.

I used a stratified 80/20 holdout of **2,375 tickets** against the existing helpdesk category labels. The local TF-IDF + logistic-regression model reached **82.6% accuracy**, so the disagreement/error rate against the source taxonomy was **16.0%**.

This is a consistency check, not a human gold standard. The model is weakest on `Other` and on tickets containing multiple issues. The tool therefore keeps the source category visible and uses topic discovery to expose recurring subthemes instead of pretending the model's label is ground truth.

## Did you change, narrow, or push back on the client's ask? What, when, and why.

Yes. I kept the requested agent closure view, but I did not present it as a single "best agent" ranking. The support policy explicitly says Tier 2 cases are multi-touch and should be measured in resolution days, not tickets closed per week. I separated Tier 2 from Tier 1 volume reporting so the requested workload view does not become a misleading performance score.

## What is wrong with what you are handing us? Be specific.

- The subtheme discovery is local NLP, not a human-reviewed taxonomy; some topics can be noisy.
- The 84% validation number measures agreement with the existing helpdesk category, not a perfect human gold standard.
- Multi-issue tickets can still receive one dominant theme.
- The tool is a batch export workflow, not a live helpdesk integration.
- The ₹58K/quarter figure is a modeled opportunity, not realized savings.
- Customer-facing actions are intentionally not automated.

## What did you deliberately leave out, and why that rather than something else?

I left out live helpdesk integration, automated refunds/replacements, production auth/RBAC, and a composite employee performance score. The five-hour window makes these lower-value than getting the data cleaning, weekly digest, evidence trail, and policy-aware workload view correct.

## Anything you built or found that nobody asked for?

Yes. I added a taxonomy-gap signal inside `Other`. There are **225 tickets** mentioning cancellation together with a disabled/greyed control. This is not a replacement for the source category; it is a recurring subtheme that the weekly digest can surface for product/support investigation.

## What did you use AI for? Which tools/models, where they helped, where they wasted your time, what you threw away.

I used ChatGPT during development for architecture review, edge-case analysis, evaluation design and code review. The runtime uses scikit-learn rather than a paid external LLM, so the submitted tool has **₹0 model/API cost** and is reproducible from the README.

The most useful AI assistance was challenging the initial idea of treating ticket volume as an agent-quality score and separating deterministic business calculations from model output. I discarded a chatbot-style interface, LLM-generated arithmetic, and a single cross-tier agent ranking because they did not improve the client's core decision.

**Screen recording:** [paste public Google Drive link]

## Your Public Google Drive Link

[paste link]

## Someone picks this up on Monday and you are unreachable. The three things they need to know.

1. Run `pip install -r requirements.txt`, then `python run.py` and `streamlit run app.py`.
2. The pipeline deduplicates migrated ticket IDs, preferring the current `helpdesk` record; the cleaned dataset contains 11,875 unique tickets.
3. The main decision metric is repeat contact: 12.36% observed, with a 10% target and an estimated ₹57.9K/quarter contact-cost opportunity at 650 tickets/week and ₹290/contact.

## Honest hours spent.

**5 hours**

## Github Repo Link

[paste public GitHub URL]
