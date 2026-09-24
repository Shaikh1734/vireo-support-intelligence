from pathlib import Path
import pandas as pd
import streamlit as st
from src.vireo_support import load_data, dedupe_tickets, add_metrics, business_metrics, discover_topics, agent_table, weekly_digest, cancellation_signal

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Vireo Support Intelligence', layout='wide')

@st.cache_data

def load_all():
    raw = load_data(ROOT / 'data')
    t = add_metrics(dedupe_tickets(raw['tickets']))
    return raw, t

raw, t = load_all()
bm = business_metrics(t)

st.title('Vireo Support Intelligence')
st.caption('Weekly complaint intelligence + workload view. Local-first: no API key required.')

c1,c2,c3,c4 = st.columns(4)
c1.metric('Tickets after migration dedupe', f"{len(t):,}")
c2.metric('Repeat-contact rate', f"{bm['repeat_rate']:.1%}")
c3.metric('First-response breach', f"{bm['sla_breach_rate']:.1%}")
c4.metric('Other category', f"{bm['other_share']:.1%}")

st.divider()

st.subheader('Business outcome')
st.write(f"Target repeat-contact rate: **10%** (current **{bm['repeat_rate']:.1%}**). At Vireo's stated 650 tickets/week and ₹290/contact, reaching 10% would remove about **{bm['weekly_contact_reduction']:.1f} contacts/week**, worth approximately **₹{bm['quarterly_saving_inr']:,.0f}/quarter** in contact cost. This is a business case, not realized savings.")

st.subheader('Weekly digest')
weeks = sorted(t['week'].dropna().unique(), reverse=True)
week = st.selectbox('Week', weeks)
dig = weekly_digest(t, week)
left,right = st.columns(2)
with left:
    st.write(f"**{dig['tickets']:,} tickets** | repeat {dig['repeat_rate']:.1%} | SLA breach {dig['sla_breach_rate']:.1%}")
    st.dataframe(pd.DataFrame(dig['top_categories']), use_container_width=True, hide_index=True)
with right:
    st.write('AI/ML-discovered subthemes inside **Other**')
    st.dataframe(pd.DataFrame(dig['other_topics']), use_container_width=True, hide_index=True)

sig = cancellation_signal(t)
st.info(f"Taxonomy signal: **{sig['signal_tickets']}** Other-category tickets mention cancellation + a disabled/greyed control ({sig['share_of_other']:.1%} of Other). This is surfaced as a candidate subtheme rather than silently rewriting the source taxonomy.")

st.divider()
st.subheader('Agent workload — not a performance ranking')
st.caption('Tier 1 is shown by closure volume. Tier 2 is separated because Vireo policy says Tier 2 work is multi-touch and should be measured in resolution days, not tickets/week.')
ag = agent_table(t, raw['agents'])
for tier in sorted(ag['tier'].unique()):
    st.write(f'**Tier {int(tier)}**')
    cols=['agent_id','name','team','site','shift','tickets_closed','repeat_rate','sla_breach_rate','avg_first_response_mins','avg_csat']
    st.dataframe(ag[ag.tier.eq(tier)][cols].head(20), use_container_width=True, hide_index=True)

st.divider()
st.subheader('Trend')
monthly = t.groupby('month').agg(tickets=('ticket_id','size'), repeat_rate=('repeat_contact','mean'), sla_breach_rate=('sla_breach','mean')).reset_index()
st.line_chart(monthly.set_index('month')[['repeat_rate','sla_breach_rate']])

st.caption('Method: current helpdesk rows are preferred over legacy_fd duplicates by ticket_id. Numeric calculations are deterministic pandas logic. Local ML uses TF-IDF + logistic regression for category validation and NMF for subtheme discovery.')
