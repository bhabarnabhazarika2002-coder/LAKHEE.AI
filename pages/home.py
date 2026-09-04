"""
LAKHEE - KHET KI DOST
Home / Landing Page  —  pure Streamlit, zero HTML/CSS/JS
"""

import streamlit as st
from utils.data_models import get_dashboard_stats


def render():
    # ── Hero ─────────────────────────────────────────────────────────────
    st.title("🌿 LAKHEE — KHET KI DOST")
    st.subheader("*\"Kisan ka vishwaas, Khet ki zaroorat, AI ka jaadu\"*")
    st.caption("India's AI-Powered Procurement Platform for Fertilizers & Agrochemicals")
    st.divider()

    # ── Live KPI row ──────────────────────────────────────────────────────
    stats = get_dashboard_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏭 Registered Suppliers", stats["total_suppliers"])
    c2.metric("🌾 Farmer Requests",      stats["total_requests"])
    c3.metric("🔴 Critical Requests",    stats["critical_requests"])
    c4.metric("🤝 AI Matches Made",      stats["total_matches"])
    st.divider()

    # ── What is LAKHEE ────────────────────────────────────────────────────
    st.subheader("What is LAKHEE?")
    st.markdown(
        """
        **LAKHEE — KHET KI DOST** (Friend of the Farm) is a smart AI-powered procurement
        matching platform connecting **fertilizer and agrochemical suppliers** directly with
        **farmers in urgent need**.

        Powered by **Google Gemini 3.6 Flash**, LAKHEE analyses:
        - 🧪 **Chemical Composition** — Does the product address the farmer's crop problem?
        - 📍 **Geographic Location** — Is the supplier reachable within the required distance?
        - 📦 **Stock Availability** — Does the supplier have enough to meet the demand?
        - 💰 **Price Compatibility** — Does the pricing fit the farmer's budget?
        - 🌱 **Agronomic Suitability** — Is the product appropriate for the crop and growth stage?
        """
    )
    st.divider()

    # ── Feature overview ──────────────────────────────────────────────────
    st.subheader("Platform Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏭 Supplier Registration")
        st.markdown(
            """
            - Register fertilizer & agrochemical inventory
            - Specify NPK composition & active ingredients
            - Set stock quantity, price, delivery radius
            - Applicable crops & certifications
            - Real-time status management
            """
        )

    with col2:
        st.markdown("### 🌾 Farmer Request Portal")
        st.markdown(
            """
            - Post urgent procurement requirements
            - Describe crop problem in detail
            - Set urgency level (Critical → Normal)
            - Specify quantity & budget
            - Track request status live
            """
        )

    with col3:
        st.markdown("### 🤖 AI Matching Engine")
        st.markdown(
            """
            - Gemini 3.6 Flash analyses compatibility
            - Scores suppliers 0–100 with reasoning
            - Chemical & agronomic suitability check
            - Location proximity analysis
            - Interactive advisory chat
            """
        )

    st.divider()

    # ── How it works ──────────────────────────────────────────────────────
    st.subheader("How LAKHEE Works")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("### 1️⃣")
        st.markdown("**Supplier registers** fertilizer or agrochemical inventory with full product details.")
    with s2:
        st.markdown("### 2️⃣")
        st.markdown("**Farmer posts** an urgent request describing their crop problem and need.")
    with s3:
        st.markdown("### 3️⃣")
        st.markdown("**LAKHEE AI** analyses all suppliers and scores them based on match criteria.")
    with s4:
        st.markdown("### 4️⃣")
        st.markdown("**Best matches** are shown with detailed reasoning, contact info, and agronomic advice.")
    st.divider()

    # ── Quick navigation ──────────────────────────────────────────────────
    st.subheader("Quick Navigation")
    qn1, qn2, qn3, qn4 = st.columns(4)

    with qn1:
        if st.button("🏭 Register Supplier", width="stretch", type="primary"):
            st.session_state["active_page"] = "🏭 Supplier Registration"
            st.rerun()
    with qn2:
        if st.button("🌾 Post Request", width="stretch", type="primary"):
            st.session_state["active_page"] = "🌾 Farmer Requests"
            st.rerun()
    with qn3:
        if st.button("🤖 Run AI Match", width="stretch", type="primary"):
            st.session_state["active_page"] = "🤖 AI Matching Engine"
            st.rerun()
    with qn4:
        if st.button("📊 View Dashboard", width="stretch"):
            st.session_state["active_page"] = "📊 Dashboard"
            st.rerun()

    st.divider()
    st.caption(
        "⚠️ LAKHEE is an AI-assisted decision support platform. "
        "Always verify product labels, safety data sheets, and local regulations before use. "
        "Consult a certified agronomist for critical crop decisions."
    )
