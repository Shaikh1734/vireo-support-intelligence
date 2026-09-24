# Memo to Priya Raman — Vireo Audio Support Intelligence

**To:** Priya Raman, Head of Customer Experience  
**Subject:** What the 18-month support export is telling us

## The short version

The 18-month export contains 12,528 rows but only 11,875 unique ticket IDs. The overlap is a migration artifact: where a ticket exists in both systems, the analysis keeps the current helpdesk record.

The strongest operating metric I would use for the weekly digest is **30-day repeat contact**. On the cleaned dataset it is **12.36%**. At the volume you gave us — roughly **650 tickets/week** — that is about **80 repeat contacts/week**. A practical first target is **10%**, which would remove about **15 contacts/week**. Using the **₹290 blended cost/contact** from the latest email, that is approximately **₹58K/quarter** of potential contact-cost reduction. This is a target, not a claim that the tool itself has already saved the money.

## What the tool surfaces

The existing `Other` category contains **1,691 tickets (14.2%)**. Local topic discovery finds several recurring subthemes that are otherwise hidden by that bucket. One particularly concrete signal is **225 Other tickets mentioning cancellation plus a disabled/greyed cancellation control**. I would treat this as a product/support issue to investigate, not silently rewrite the source taxonomy.

The broader repeat-contact picture also points to product and delivery problems: Delivery & Shipping has a 15.5% repeat-contact rate; Audio Quality 14.6%; Charging & Battery 14.6%; and Connectivity 13.8%.

## Agent reporting

I included the requested tickets-closed view, but I would not call it a performance ranking. Your policy says Tier 2 cases are multi-touch and should be measured in resolution days rather than tickets closed per week. The tool therefore keeps Tier 2 separate instead of mixing it into a single league table.

## How reliable is it?

The category validation model reaches about **82.6% accuracy on a 2,375-ticket held-out sample** against the existing helpdesk categories. The biggest source of disagreement is `Other` and tickets containing multiple issues. That is why the product exposes the evidence and topic terms instead of presenting an AI label as fact.

## What I left out

I did not build live helpdesk integration, automated customer actions, or an employee performance score. Those would consume the five-hour window without directly answering the weekly-digest problem.

The result is intentionally small: run it on the export, inspect the weekly digest, drill into recurring themes, and use the workload view with the policy context attached.
