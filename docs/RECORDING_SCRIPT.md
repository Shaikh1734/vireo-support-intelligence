# 3-minute screen-recording script

## 0:00–0:30 — Start with the data problem

"The raw export has 12,528 rows but only 11,875 unique ticket IDs. The email warned us that old Freshdesk records were re-imported, so I deduplicated by ticket ID and preferred the current helpdesk record. That prevents migration artifacts from changing the weekly numbers."

## 0:30–1:10 — Show the weekly digest

Open the dashboard. Show the selected week, category distribution and Other-topic discovery.

"I kept the client's existing taxonomy for reporting, but I added local topic discovery inside Other. There are 1,691 Other tickets overall. A concrete recurring signal is 225 tickets mentioning cancellation together with a disabled or greyed control."

## 1:10–1:50 — Show the business outcome

"The KPI I chose is repeat contact, using Vireo's own 30-day definition. The cleaned dataset is at 12.36%. At 650 tickets per week, that's about 80 repeat contacts. A 10% target would remove about 15 contacts per week. At the client's ₹290 blended cost, the modeled opportunity is about ₹58K per quarter. That's a target, not claimed savings."

## 1:50–2:25 — Explain the pushback

Open the agent view.

"I did keep the requested tickets-closed view, but I did not mix every agent into one performance ranking. The policy says Tier 2 work is multi-touch and should be measured in resolution days, not tickets per week. So the tool shows Tier 1 volume separately and keeps Tier 2 separate."

## 2:25–3:00 — Validation + limitations

"For validation I used a stratified 2,375-ticket holdout against the existing category labels. The local classifier reached 82.6% agreement. The main weak area is Other and multi-issue tickets, so I expose the evidence and topic terms rather than treating the model as ground truth. I deliberately left out live integrations, automated refunds, and production auth because the five-hour window is better spent making the weekly digest correct and auditable."
