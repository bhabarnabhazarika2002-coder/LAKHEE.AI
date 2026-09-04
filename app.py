"""
LAKHEE — KHET KI DOST
Main Streamlit Application Entry Point  —  pure Streamlit, zero HTML/CSS/JS

Run with:
    cd lakhee_platform
    streamlit run app.py
"""

import sys
import os

# Make utils/ and pages/ importable when running from inside lakhee_platform/
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.data_models import init_session_state, get_dashboard_stats

# ──────────────────────────────────────────────
# Page configuration  (must be first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="LAKHEE — KHET KI DOST",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "## LAKHEE — KHET KI DOST\n"
            "AI-Powered Fertilizer & Agrochemical Procurement Platform for Indian Agriculture.\n\n"
            "Powered by Google Gemini 3.6 Flash."
        )
    },
)

# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
init_session_state()

# ──────────────────────────────────────────────
# Sidebar navigation
# ──────────────────────────────────────────────
PAGES = [
    "🏠 Home",
    "🏭 Supplier Registration",
    "🌾 Farmer Requests",
    "🤖 AI Matching Engine",
    "📊 Dashboard",
    "🛡️ Admin Panel",
]

with st.sidebar:
    st.markdown("## 🌿 LAKHEE")
    st.markdown("### KHET KI DOST")
    st.caption("AI Procurement Platform")
    st.divider()

    current_index = PAGES.index(
        st.session_state.get("active_page", "🏠 Home")
        if st.session_state.get("active_page", "🏠 Home") in PAGES
        else "🏠 Home"
    )

    selected_page = st.radio(
        "Navigation",
        PAGES,
        index=current_index,
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state["active_page"] = selected_page

    st.divider()

    # API key — stored in session state so all pages can access it
    st.subheader("🔑 Gemini API Key")
    api_key_input = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        placeholder="AIza...",
        key="gemini_api_key",
        help="Get a free key at https://aistudio.google.com/app/apikey",
    )
    if api_key_input:
        st.success("API Key loaded ✅")
    else:
        st.warning("Enter your Gemini API Key to use AI features.")

    st.divider()

    # Quick stats
    stats = get_dashboard_stats()
    st.markdown("### 📊 Quick Stats")
    st.markdown(f"- 🏭 Suppliers: **{stats['active_suppliers']}** active")
    st.markdown(f"- 📢 Open Requests: **{stats['open_requests']}**")
    st.markdown(f"- 🔴 Critical: **{stats['critical_requests']}**")
    st.markdown(f"- 🤝 Matches: **{stats['total_matches']}**")

    st.divider()
    st.caption("Version 2.0 | Powered by Gemini 3.6 Flash")
    st.caption("© 2025 LAKHEE Platform")

# ──────────────────────────────────────────────
# Page routing
# ──────────────────────────────────────────────
from pages import home, supplier_registration, farmer_requests, ai_matching, dashboard, admin_panel

page = st.session_state.get("active_page", "🏠 Home")

if page == "🏠 Home":
    home.render()
elif page == "🏭 Supplier Registration":
    supplier_registration.render()
elif page == "🌾 Farmer Requests":
    farmer_requests.render()
elif page == "🤖 AI Matching Engine":
    ai_matching.render()
elif page == "📊 Dashboard":
    dashboard.render()
elif page == "🛡️ Admin Panel":
    admin_panel.render()
