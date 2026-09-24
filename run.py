from pathlib import Path
from src.vireo_support import build_snapshot

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    snap = build_snapshot(root / 'data', root / 'outputs')
    print('Vireo Support Intelligence run complete.')
    print(f"Deduped tickets: {snap['business']['deduped_tickets']:,}")
    print(f"Repeat-contact rate: {snap['business']['repeat_rate']:.1%}")
    print(f"SLA breach rate: {snap['business']['sla_breach_rate']:.1%}")
    print(f"Potential quarterly contact-cost reduction at 10% repeat target: ₹{snap['business']['quarterly_saving_inr']:,.0f}")
