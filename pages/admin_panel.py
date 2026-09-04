"""
LAKHEE - KHET KI DOST
Admin Panel Page  —  pure Streamlit, zero HTML/CSS/JS
"""

import streamlit as st
import json
import pandas as pd
from utils.data_models import (
    load_suppliers, load_farmer_requests, load_matches,
    update_supplier_status, update_request_status,
)


def render():
    st.title("🛡️ Admin Panel")
    st.markdown("Full data management and audit view for platform administrators.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🏭 Supplier Data", "🌾 Request Data", "🤝 Match Audit Trail"])

    # ── Tab 1: Suppliers ──────────────────────────────────────────────────
    with tab1:
        st.subheader("All Registered Supplier Inventories")
        suppliers = load_suppliers()

        if not suppliers:
            st.info("No suppliers registered yet.")
        else:
            # Summary metrics
            active = [s for s in suppliers if s.get("status") == "Active"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Suppliers", len(suppliers))
            c2.metric("Active", len(active))
            c3.metric("Inactive", len(suppliers) - len(active))

            # Export raw JSON
            if st.button("📥 Export Supplier Data (JSON)", key="export_sup"):
                st.download_button(
                    label="⬇️ Download suppliers.json",
                    data=json.dumps(suppliers, indent=2, default=str),
                    file_name="lakhee_suppliers.json",
                    mime="application/json"
                )

            st.divider()

            # Table view using st.dataframe
            df = pd.DataFrame(suppliers)
            display_cols = [
                "id", "company_name", "product_name", "product_category",
                "state", "district", "quantity_available", "unit",
                "price_per_unit", "availability_till", "status", "registered_at"
            ]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Detailed View / Manage Status")
            for sup in reversed(suppliers):
                with st.expander(
                    f"{'🟢' if sup.get('status') == 'Active' else '🔴'} "
                    f"{sup.get('id')} — {sup.get('product_name')} | {sup.get('company_name')}"
                ):
                    st.json(sup)
                    new_status = "Inactive" if sup.get("status") == "Active" else "Active"
                    if st.button(
                        f"Toggle to {new_status}",
                        key=f"admin_toggle_sup_{sup.get('id')}"
                    ):
                        update_supplier_status(sup.get("id"), new_status)
                        st.rerun()

    # ── Tab 2: Farmer Requests ────────────────────────────────────────────
    with tab2:
        st.subheader("All Farmer Requests")
        requests = load_farmer_requests()

        if not requests:
            st.info("No farmer requests posted yet.")
        else:
            open_r = [r for r in requests if r.get("status") == "Open"]
            matched_r = [r for r in requests if r.get("status") == "Matched"]
            closed_r = [r for r in requests if r.get("status") == "Closed"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", len(requests))
            c2.metric("Open", len(open_r))
            c3.metric("Matched", len(matched_r))
            c4.metric("Closed", len(closed_r))

            if st.button("📥 Export Request Data (JSON)", key="export_req"):
                st.download_button(
                    label="⬇️ Download farmer_requests.json",
                    data=json.dumps(requests, indent=2, default=str),
                    file_name="lakhee_farmer_requests.json",
                    mime="application/json"
                )

            st.divider()
            df = pd.DataFrame(requests)
            display_cols = [
                "id", "farmer_name", "crop_type", "product_category_needed",
                "state", "district", "quantity_needed", "unit_needed",
                "urgency", "required_by", "status", "posted_at"
            ]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Detailed View / Manage Status")
            for req in reversed(requests):
                urgency_icon = req.get("urgency", "")[:2]
                with st.expander(
                    f"{urgency_icon} {req.get('id')} — {req.get('crop_type')} | "
                    f"{req.get('farmer_name')} | Status: {req.get('status')}"
                ):
                    st.json(req)
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if req.get("status") != "Open":
                            if st.button("🔁 Reopen", key=f"admin_reopen_{req.get('id')}"):
                                update_request_status(req.get("id"), "Open")
                                st.rerun()
                    with col_btn2:
                        if req.get("status") != "Matched":
                            if st.button("✅ Mark Matched", key=f"admin_match_{req.get('id')}"):
                                update_request_status(req.get("id"), "Matched")
                                st.rerun()
                    with col_btn3:
                        if req.get("status") != "Closed":
                            if st.button("🔒 Close", key=f"admin_close_{req.get('id')}"):
                                update_request_status(req.get("id"), "Closed")
                                st.rerun()

    # ── Tab 3: Match Audit Trail ──────────────────────────────────────────
    with tab3:
        st.subheader("AI Match Audit Trail")
        matches = load_matches()

        if not matches:
            st.info("No matches generated yet. Use the AI Matching Engine to generate matches.")
        else:
            # Export
            if st.button("📥 Export Match Data (JSON)", key="export_matches"):
                st.download_button(
                    label="⬇️ Download matches.json",
                    data=json.dumps(matches, indent=2, default=str),
                    file_name="lakhee_matches.json",
                    mime="application/json"
                )

            # Summary
            avg_score = sum(m.get("match_score", 0) for m in matches) / len(matches)
            high_quality = [m for m in matches if m.get("match_score", 0) >= 80]
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Matches", len(matches))
            c2.metric("High Quality (≥80)", len(high_quality))
            c3.metric("Avg Match Score", f"{avg_score:.1f}/100")

            st.divider()
            df = pd.DataFrame(matches)
            display_cols = [
                "id", "request_id", "supplier_id", "match_score",
                "recommendation", "farmer_name", "supplier_name", "product", "matched_at"
            ]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Match Details")
            for match in reversed(matches):
                score = match.get("match_score", 0)
                badge = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                with st.expander(
                    f"{badge} {match.get('id')} | Score: {score}/100 | "
                    f"Req: {match.get('request_id')} → Sup: {match.get('supplier_id')}"
                ):
                    st.json(match)
