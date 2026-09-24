from pathlib import Path
import pandas as pd
from src.vireo_support import dedupe_tickets, add_metrics

def test_dedupe_prefers_helpdesk():
    d = pd.DataFrame([
        {'ticket_id':'x','source_system':'legacy_fd','created_at':'2025-01-01','first_response_at':'2025-01-01 00:10','resolved_at':'2025-01-01 01:00','channel':'chat','customer_id':'c','category':'Other','customer_message':'a','agent_notes':''},
        {'ticket_id':'x','source_system':'helpdesk','created_at':'2025-01-01','first_response_at':'2025-01-01 00:05','resolved_at':'2025-01-01 00:30','channel':'chat','customer_id':'c','category':'Other','customer_message':'a','agent_notes':''},
    ])
    out = dedupe_tickets(d)
    assert len(out) == 1
    assert out.iloc[0].source_system == 'helpdesk'

def test_metrics_adds_policy_columns():
    d = pd.DataFrame([
        {'ticket_id':'x','source_system':'helpdesk','created_at':'2025-01-01 00:00','first_response_at':'2025-01-01 00:20','resolved_at':'2025-01-01 01:00','channel':'chat','customer_id':'c','category':'Other','csat_score':None,'customer_message':'a','agent_notes':''},
    ])
    out = add_metrics(d)
    assert bool(out.iloc[0].sla_breach)
