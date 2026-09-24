from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion
from sklearn.metrics import accuracy_score

CHANNEL_TARGET_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}
CHANNEL_COST = {"chat": 210, "email": 260, "voice": 520, "social": 240}
BLENDED_COST = 290  # Client-provided latest blended contact cost from email thread.
WEEKLY_VOLUME = 650
TARGET_REPEAT_RATE = 0.10


def load_data(data_dir: str | Path) -> Dict[str, pd.DataFrame]:
    data_dir = Path(data_dir)
    names = ["tickets", "agents", "customers", "orders", "products"]
    return {n: pd.read_csv(data_dir / f"{n}.csv") for n in names}


def dedupe_tickets(tickets: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate migration duplicates, preferring the current helpdesk copy."""
    t = tickets.copy()
    t["_helpdesk"] = (t["source_system"].eq("helpdesk")).astype(int)
    t = t.sort_values(["ticket_id", "_helpdesk", "created_at"])
    t = t.drop_duplicates("ticket_id", keep="last").drop(columns="_helpdesk")
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c] = pd.to_datetime(t[c], errors="coerce")
    return t


def add_metrics(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c] = pd.to_datetime(t[c], errors="coerce")
    t["first_response_mins"] = (
        t["first_response_at"] - t["created_at"]
    ).dt.total_seconds() / 60
    t["response_target_mins"] = t["channel"].map(CHANNEL_TARGET_MIN)
    t["sla_breach"] = t["first_response_mins"] > t["response_target_mins"]
    t["channel_cost_inr"] = t["channel"].map(CHANNEL_COST)
    t = t.sort_values(["customer_id", "category", "resolved_at", "created_at"])
    t["previous_resolution"] = t.groupby(["customer_id", "category"])["resolved_at"].shift(1)
    gap_days = (t["created_at"] - t["previous_resolution"]).dt.total_seconds() / 86400
    t["repeat_contact"] = gap_days.between(0, 30, inclusive="both")
    t["week"] = t["created_at"].dt.to_period("W-MON").astype(str)
    t["month"] = t["created_at"].dt.to_period("M").astype(str)
    t["text"] = (t["customer_message"].fillna("") + " " + t["agent_notes"].fillna("")).str.replace(r"\s+", " ", regex=True).str.strip()
    return t


def business_metrics(t: pd.DataFrame) -> dict:
    repeat = float(t["repeat_contact"].mean())
    current_weekly_repeat = WEEKLY_VOLUME * repeat
    target_weekly_repeat = WEEKLY_VOLUME * TARGET_REPEAT_RATE
    reduction = max(0.0, current_weekly_repeat - target_weekly_repeat)
    weekly_saving = reduction * BLENDED_COST
    quarterly_saving = weekly_saving * 13
    return {
        "deduped_tickets": int(len(t)),
        "raw_rows": int(len(t)),
        "repeat_rate": repeat,
        "repeat_contacts": int(t["repeat_contact"].sum()),
        "sla_breach_rate": float(t["sla_breach"].mean()),
        "csat_response_rate": float(t["csat_score"].notna().mean()),
        "other_share": float(t["category"].eq("Other").mean()),
        "current_weekly_repeat_contacts": current_weekly_repeat,
        "target_weekly_repeat_contacts": target_weekly_repeat,
        "weekly_contact_reduction": reduction,
        "weekly_saving_inr": weekly_saving,
        "quarterly_saving_inr": quarterly_saving,
    }


def discover_topics(t: pd.DataFrame, category: str = "Other", n_topics: int = 8, n_words: int = 10) -> pd.DataFrame:
    d = t[t["category"].eq(category)].copy()
    if len(d) < n_topics * 5:
        return pd.DataFrame(columns=["topic", "keywords", "tickets"])
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), min_df=5, max_features=5000, sublinear_tf=True
    )
    X = vectorizer.fit_transform(d["text"])
    model = NMF(n_components=n_topics, random_state=42, init="nndsvda", max_iter=500)
    W = model.fit_transform(X)
    terms = vectorizer.get_feature_names_out()
    rows = []
    for i, comp in enumerate(model.components_):
        top = comp.argsort()[-n_words:][::-1]
        rows.append({"topic": i + 1, "keywords": ", ".join(terms[top]), "tickets": int((W.argmax(axis=1) == i).sum())})
    return pd.DataFrame(rows).sort_values("tickets", ascending=False).reset_index(drop=True)


def train_category_model(t: pd.DataFrame):
    """Train a lightweight local NLP classifier using the helpdesk category as the reference label."""
    X_train, X_test, y_train, y_test = train_test_split(
        t["text"], t["category"], test_size=0.20, random_state=42, stratify=t["category"]
    )
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=50000, sublinear_tf=True)),
    ])
    A = features.fit_transform(X_train)
    B = features.transform(X_test)
    model = LogisticRegression(max_iter=1000, C=3, class_weight="balanced")
    model.fit(A, y_train)
    pred = model.predict(B)
    return model, features, {"sample_size": len(y_test), "accuracy": float(accuracy_score(y_test, pred)), "error_rate": float(1 - accuracy_score(y_test, pred))}


def weekly_digest(t: pd.DataFrame, week: str | None = None) -> dict:
    if week is None:
        counts = t.groupby("week").size()
        # Prefer the latest complete-looking week rather than the partial final export week.
        threshold = max(50, int(counts.median() * 0.75))
        candidates = counts[counts >= threshold]
        week = str(candidates.index.max() if len(candidates) else counts.index.max())
    d = t[t["week"].eq(week)].copy()
    cat = d["category"].value_counts().rename_axis("category").reset_index(name="tickets")
    top_other = discover_topics(d, "Other", n_topics=min(5, max(2, d[d.category.eq("Other")].shape[0] // 30))) if d[d.category.eq("Other")].shape[0] >= 30 else pd.DataFrame()
    return {
        "week": week,
        "tickets": int(len(d)),
        "repeat_rate": float(d.repeat_contact.mean()) if len(d) else 0.0,
        "sla_breach_rate": float(d.sla_breach.mean()) if len(d) else 0.0,
        "top_categories": cat.head(8).to_dict("records"),
        "other_topics": top_other.to_dict("records") if not top_other.empty else [],
    }


def agent_table(t: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    base = t.groupby("agent_id").agg(
        tickets_closed=("ticket_id", "size"),
        repeat_contacts=("repeat_contact", "sum"),
        sla_breaches=("sla_breach", "sum"),
        avg_first_response_mins=("first_response_mins", "mean"),
        csat_responses=("csat_score", lambda x: x.notna().sum()),
        avg_csat=("csat_score", "mean"),
    ).reset_index()
    meta = agents[["agent_id", "name", "team", "tier", "site", "shift"]].drop_duplicates("agent_id")
    out = meta.merge(base, on="agent_id", how="left").fillna(0)
    out["repeat_rate"] = out["repeat_contacts"] / out["tickets_closed"].replace(0, np.nan)
    out["sla_breach_rate"] = out["sla_breaches"] / out["tickets_closed"].replace(0, np.nan)
    return out.sort_values(["tier", "tickets_closed"], ascending=[True, False])


def cancellation_signal(t: pd.DataFrame) -> dict:
    d = t[t.category.eq("Other")].copy()
    text = d["customer_message"].fillna("").str.lower()
    mask = text.str.contains(r"cancel|cancellation", regex=True) & text.str.contains(
        r"grey|gray|disable|button|unable|cannot|can't", regex=True
    )
    return {"other_tickets": int(len(d)), "signal_tickets": int(mask.sum()), "share_of_other": float(mask.mean()) if len(d) else 0.0}


def build_snapshot(data_dir: str | Path, output_dir: str | Path) -> dict:
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    raw = load_data(data_dir)
    raw_rows = len(raw["tickets"])
    t = add_metrics(dedupe_tickets(raw["tickets"]))
    bm = business_metrics(t); bm["raw_rows"] = raw_rows
    topics = discover_topics(t)
    agents = agent_table(t, raw["agents"])
    signal = cancellation_signal(t)
    model, features, evalm = train_category_model(t)
    # Weekly digest for latest available week
    digest = weekly_digest(t)
    snapshot = {"business": bm, "cancellation_signal": signal, "model_evaluation": evalm, "latest_digest": digest}
    (output_dir / "metrics.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    topics.to_csv(output_dir / "other_topics.csv", index=False)
    agents.to_csv(output_dir / "agent_leaderboard.csv", index=False)
    t.groupby("category").size().rename("tickets").sort_values(ascending=False).to_csv(output_dir / "category_counts.csv")
    t.groupby("month").agg(tickets=("ticket_id","size"), repeat_rate=("repeat_contact","mean"), sla_breach_rate=("sla_breach","mean")).to_csv(output_dir / "monthly_trends.csv")
    return snapshot
