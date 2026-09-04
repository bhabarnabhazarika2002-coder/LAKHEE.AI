"""
LAKHEE - KHET KI DOST
Dashboard & Analytics Page  —  pure Streamlit, zero HTML/CSS/JS
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
from utils.data_models import (
    get_dashboard_stats, load_suppliers, load_farmer_requests, load_matches,
)


def render():
    st.title("📊 Dashboard & Analytics")
    st.markdown("Real-time overview of procurement activity across the LAKHEE platform.")
    st.divider()

    stats = get_dashboard_stats()
    suppliers = load_suppliers()
    requests = load_farmer_requests()
    matches = load_matches()

    # ── KPI Row ───────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("🏭 Total Suppliers", stats["total_suppliers"], help="All registered suppliers")
    k2.metric("✅ Active Suppliers", stats["active_suppliers"])
    k3.metric("🌾 Total Requests", stats["total_requests"])
    k4.metric("📢 Open Requests", stats["open_requests"])
    k5.metric("🔴 Critical Requests", stats["critical_requests"])
    k6.metric("🤝 AI Matches Made", stats["total_matches"])

    st.divider()

    # ── Charts Row 1 ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Supplier Inventory by Category")
        if suppliers:
            cat_counts = Counter(s.get("product_category", "Unknown") for s in suppliers)
            cat_data = dict(sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            bar_items = [(k, v) for k, v in cat_data.items()]
            df_cat = pd.DataFrame({"Category": [b[0] for b in bar_items], "Count": [b[1] for b in bar_items]})
            st.bar_chart(df_cat.set_index("Category"))
        else:
            st.info("No supplier data yet.")

    with col2:
        st.subheader("🌱 Farmer Requests by Crop Type")
        if requests:
            crop_counts = Counter(r.get("crop_type", "Unknown") for r in requests)
            crop_data = dict(sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            df_crop = pd.DataFrame({"Crop": list(crop_data.keys()), "Requests": list(crop_data.values())})
            st.bar_chart(df_crop.set_index("Crop"))
        else:
            st.info("No request data yet.")

    st.divider()

    # ── Charts Row 2 ─────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📍 Supplier Distribution by State")
        if suppliers:
            state_counts = Counter(s.get("state", "Unknown") for s in suppliers)
            state_data = dict(sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            df_state = pd.DataFrame({"State": list(state_counts.keys()), "Suppliers": list(state_counts.values())})
            st.bar_chart(df_state.set_index("State"))
        else:
            st.info("No supplier data yet.")

    with col4:
        st.subheader("⏰ Request Urgency Breakdown")
        if requests:
            urgency_counts = Counter(r.get("urgency", "Unknown")[:20] for r in requests)
            df_urg = pd.DataFrame({"Urgency": list(urgency_counts.keys()), "Count": list(urgency_counts.values())})
            st.bar_chart(df_urg.set_index("Urgency"))
        else:
            st.info("No request data yet.")

    st.divider()

    # ── Request Status Tracker ────────────────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📋 Request Status Distribution")
        if requests:
            status_counts = Counter(r.get("status", "Unknown") for r in requests)
            for status, count in status_counts.items():
                total = len(requests)
                pct = int(count / total * 100) if total else 0
                icon_map = {"Open": "🟡", "Matched": "🟢", "Closed": "⚫"}
                icon = icon_map.get(status, "🔵")
                st.markdown(f"{icon} **{status}** — {count} requests ({pct}%)")
                st.progress(pct / 100)
        else:
            st.info("No request data yet.")

    with col6:
        st.subheader("🤝 Recent AI Matches")
        if matches:
            for m in reversed(matches[-5:]):
                score = m.get("match_score", 0)
                badge = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                st.markdown(
                    f"{badge} **{m.get('request_id')}** → **{m.get('supplier_id')}** | "
                    f"Score: {score}/100 | {m.get('recommendation', '')}"
                )
                st.caption(
                    f"Farmer: {m.get('farmer_name', 'N/A')} | "
                    f"Supplier: {m.get('supplier_name', 'N/A')} | "
                    f"Product: {m.get('product', 'N/A')}"
                )
                st.divider()
        else:
            st.info("No matches yet. Run the AI Matching Engine to generate matches.")

    st.divider()

    # ── Recent Activity Feed ──────────────────────────────────────────────
    st.subheader("🕐 Recent Activity Feed")

    activities = []
    for s in suppliers[-5:]:
        activities.append({
            "time": s.get("registered_at", ""),
            "icon": "🏭",
            "text": f"New supplier registered: **{s.get('company_name')}** — {s.get('product_name')} ({s.get('state')})"
        })
    for r in requests[-5:]:
        activities.append({
            "time": r.get("posted_at", ""),
            "icon": "🌾",
            "text": f"New farmer request: **{r.get('farmer_name')}** needs {r.get('product_category_needed')} in {r.get('district')}, {r.get('state')} | {r.get('urgency', '')[:25]}"
        })
    for m in matches[-3:]:
        activities.append({
            "time": m.get("matched_at", ""),
            "icon": "🤖",
            "text": f"AI Match: {m.get('request_id')} ↔ {m.get('supplier_id')} | Score {m.get('match_score')}/100"
        })

    # Sort by time descending
    activities.sort(key=lambda x: x.get("time", ""), reverse=True)

    if activities:
        for act in activities[:10]:
            time_str = act.get("time", "")
            try:
                dt = datetime.fromisoformat(time_str)
                time_formatted = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                time_formatted = time_str[:16]
            st.markdown(f"{act['icon']} {act['text']}")
            st.caption(f"🕐 {time_formatted}")
    else:
        st.info("No activity yet. Start by registering a supplier or posting a farmer request.")
