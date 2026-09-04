"""
LAKHEE - KHET KI DOST
AI-Powered Matching Engine using Google Gemini 3.6 Flash
Pure Streamlit — zero HTML/CSS/JS
"""

import json
import streamlit as st
from google import genai
from utils.data_models import (
    load_suppliers, load_farmer_requests, save_match, load_matches,
    update_request_status,
)

# ──────────────────────────────────────────────
# Gemini client & model
# ──────────────────────────────────────────────

MODEL_ID = "gemini-3.6-flash"


def _get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


# ──────────────────────────────────────────────
# State proximity lookup
# ──────────────────────────────────────────────

STATE_NEIGHBOURS: dict = {
    "Maharashtra":    ["Gujarat", "Madhya Pradesh", "Chhattisgarh", "Telangana", "Andhra Pradesh", "Karnataka", "Goa"],
    "Punjab":         ["Haryana", "Himachal Pradesh", "Jammu & Kashmir", "Rajasthan"],
    "Uttar Pradesh":  ["Bihar", "Jharkhand", "Chhattisgarh", "Madhya Pradesh", "Rajasthan", "Haryana", "Uttarakhand", "Delhi"],
    "Rajasthan":      ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Gujarat"],
    "Gujarat":        ["Rajasthan", "Madhya Pradesh", "Maharashtra"],
    "Haryana":        ["Punjab", "Himachal Pradesh", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Delhi"],
    "Madhya Pradesh": ["Rajasthan", "Gujarat", "Maharashtra", "Chhattisgarh", "Uttar Pradesh"],
    "Bihar":          ["Uttar Pradesh", "Jharkhand", "West Bengal"],
    "West Bengal":    ["Bihar", "Jharkhand", "Odisha", "Assam", "Sikkim"],
    "Tamil Nadu":     ["Kerala", "Karnataka", "Andhra Pradesh", "Telangana"],
    "Karnataka":      ["Goa", "Maharashtra", "Telangana", "Andhra Pradesh", "Tamil Nadu", "Kerala"],
    "Andhra Pradesh": ["Telangana", "Karnataka", "Tamil Nadu", "Odisha", "Chhattisgarh"],
    "Telangana":      ["Maharashtra", "Chhattisgarh", "Andhra Pradesh", "Karnataka"],
    "Kerala":         ["Tamil Nadu", "Karnataka"],
    "Odisha":         ["West Bengal", "Jharkhand", "Chhattisgarh", "Andhra Pradesh"],
    "Assam":          ["West Bengal", "Meghalaya", "Nagaland", "Manipur", "Mizoram", "Tripura", "Arunachal Pradesh"],
    "Chhattisgarh":   ["Madhya Pradesh", "Maharashtra", "Telangana", "Andhra Pradesh", "Odisha", "Jharkhand", "Uttar Pradesh"],
    "Jharkhand":      ["Bihar", "West Bengal", "Odisha", "Chhattisgarh", "Uttar Pradesh"],
    "Himachal Pradesh": ["Jammu & Kashmir", "Punjab", "Haryana", "Uttarakhand"],
    "Uttarakhand":    ["Himachal Pradesh", "Uttar Pradesh"],
    "Delhi":          ["Haryana", "Uttar Pradesh"],
}


def _location_score(farmer_state: str, supplier_state: str, radius_km: int) -> int:
    """Return 0–40 location proximity score."""
    if farmer_state == supplier_state:
        return 40
    if supplier_state in STATE_NEIGHBOURS.get(farmer_state, []):
        return 25 if radius_km >= 200 else 20
    return 10 if radius_km >= 500 else 0


# ──────────────────────────────────────────────
# Pre-filter (no AI cost)
# ──────────────────────────────────────────────

def _prefilter_suppliers(request: dict, suppliers: list) -> list:
    """Return candidates passing basic category / location / stock checks."""
    req_category  = request.get("product_category_needed", "")
    farmer_state  = request.get("state", "")
    req_qty       = float(request.get("quantity_needed", 0))
    name_keywords = [
        kw for kw in (request.get("product_name_needed", "") or "").split()
        if len(kw) > 3
    ]

    candidates = []
    for sup in suppliers:
        if sup.get("status") != "Active":
            continue
        # Category check — include if exact match or keyword hit in product/generic name
        if sup.get("product_category") != req_category:
            combined = (sup.get("product_name", "") + " " + sup.get("generic_name", "")).lower()
            if not any(kw.lower() in combined for kw in name_keywords):
                continue
        # Stock must be at least 50 % of need
        if float(sup.get("quantity_available", 0)) < req_qty * 0.5:
            continue
        # Location — must be same state or neighbour state
        loc = _location_score(farmer_state, sup.get("state", ""), int(sup.get("delivery_radius_km", 0)))
        if loc == 0:
            continue
        candidates.append(sup)

    return candidates


# ──────────────────────────────────────────────
# Gemini prompt builder
# ──────────────────────────────────────────────

def _build_prompt(request: dict, candidates: list) -> str:
    req_json = json.dumps({
        "farmer_name":            request.get("farmer_name"),
        "crop":                   request.get("crop_type"),
        "growth_stage":           request.get("crop_growth_stage"),
        "problem":                request.get("problem_description"),
        "product_category_needed":request.get("product_category_needed"),
        "product_name_needed":    request.get("product_name_needed"),
        "npk_requirement":        request.get("npk_requirement"),
        "quantity_needed":        f"{request.get('quantity_needed')} {request.get('unit_needed')}",
        "budget_per_unit_inr":    request.get("budget_per_unit"),
        "location":               f"{request.get('district')}, {request.get('state')}",
        "urgency":                request.get("urgency"),
        "required_by":            request.get("required_by"),
    }, indent=2)

    suppliers_json = json.dumps([
        {
            "id":                 s.get("id"),
            "company":            s.get("company_name"),
            "product":            s.get("product_name"),
            "category":           s.get("product_category"),
            "generic_name":       s.get("generic_name"),
            "npk_composition":    s.get("npk_composition"),
            "active_ingredients": s.get("active_ingredient"),
            "applicable_crops":   s.get("applicable_crops"),
            "quantity_available": f"{s.get('quantity_available')} {s.get('unit')}",
            "price_per_unit_inr": s.get("price_per_unit"),
            "min_order_qty":      f"{s.get('min_order_qty')} {s.get('unit')}",
            "available_till":     s.get("availability_till"),
            "location":           f"{s.get('district')}, {s.get('state')}",
            "delivery_radius_km": s.get("delivery_radius_km"),
            "certifications":     s.get("certifications"),
        }
        for s in candidates
    ], indent=2)

    return f"""You are LAKHEE — an expert AI procurement assistant for Indian agriculture.
Analyse the farmer's requirement and score each supplier 0-100.

FARMER REQUEST:
{req_json}

CANDIDATE SUPPLIERS:
{suppliers_json}

For EACH supplier return a JSON array (pure JSON, no markdown) with this exact schema:
[
  {{
    "supplier_id": "SUP-XXXX",
    "match_score": <integer 0-100>,
    "recommendation": "<Buy / Consider / Skip>",
    "chemical_compatibility": "<does composition meet the crop/problem need>",
    "location_suitability": "<proximity and delivery feasibility>",
    "stock_adequacy": "<is available stock sufficient>",
    "price_assessment": "<value for money vs budget>",
    "agronomic_advice": "<1-2 sentences specific to crop/problem>",
    "risk_flags": "<warnings: expiry risk, misuse, substitution needed, etc.>",
    "summary": "<2-3 line overall recommendation>"
  }}
]

Scoring:
- Chemical/product match to crop problem : 0-35 pts
- Location proximity & delivery          : 0-25 pts
- Stock adequacy                         : 0-20 pts
- Price vs budget                        : 0-10 pts
- Certifications & reliability           : 0-10 pts

Return ONLY the JSON array. No prose, no markdown fences."""


# ──────────────────────────────────────────────
# Gemini API calls
# ──────────────────────────────────────────────

def _run_matching(api_key: str, request: dict, candidates: list) -> list:
    client   = _get_client(api_key)
    response = client.models.generate_content(model=MODEL_ID, contents=_build_prompt(request, candidates))
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _run_chat(api_key: str, context: str, question: str) -> str:
    client = _get_client(api_key)
    prompt = (
        "You are LAKHEE — a knowledgeable AI agri-procurement advisor for Indian farmers.\n\n"
        f"Context:\n{context}\n\n"
        f"Farmer's question: {question}\n\n"
        "Answer in clear practical terms. Include dosage rates, safety precautions, or alternatives "
        "where relevant. Keep under 300 words. Mix Hindi terms where helpful for Indian farmers."
    )
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text.strip()


# ──────────────────────────────────────────────
# Page render
# ──────────────────────────────────────────────

def render():
    st.title("🤖 AI Matching Engine")
    st.markdown(
        "Powered by **Google Gemini 3.6 Flash** — matches farmer requests with supplier inventory "
        "based on chemical compatibility, location proximity, stock availability, and price."
    )
    st.divider()

    # Read API key from session state (set in sidebar in app.py)
    api_key = st.session_state.get("gemini_api_key", "").strip()

    if not api_key:
        st.warning("⚠️ Enter your **Gemini API Key** in the left sidebar to use AI features.")
        st.stop()

    tab_match, tab_results, tab_chat = st.tabs(
        ["🔍 Run AI Match", "📊 Match Results", "💬 AI Advisory Chat"]
    )

    # ── Tab 1 : Run AI Match ──────────────────────────────────────────────
    with tab_match:
        st.subheader("🔍 Select a Farmer Request to Match")

        requests      = load_farmer_requests()
        open_requests = [r for r in requests if r.get("status") == "Open"]

        if not open_requests:
            st.info("No open farmer requests. Go to **Farmer Requests** to post one.")
        else:
            options = {
                f"{r['id']} — {r['crop_type']} | {r['product_category_needed']} | "
                f"{r['district']}, {r['state']} | {r.get('urgency','')[:15]}": r
                for r in reversed(open_requests)
            }
            selected_label   = st.selectbox("Choose Farmer Request", list(options.keys()))
            selected_request = options[selected_label]

            with st.expander("📋 Selected Request Details", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Farmer",   selected_request.get("farmer_name"))
                c1.metric("Crop",     selected_request.get("crop_type"))
                c2.metric("Product",  selected_request.get("product_category_needed"))
                c2.metric("Quantity", f"{selected_request.get('quantity_needed')} {selected_request.get('unit_needed')}")
                c3.metric("Location", f"{selected_request.get('district')}, {selected_request.get('state')}")
                c3.metric("Urgency",  selected_request.get("urgency", "")[:30])
                if selected_request.get("problem_description"):
                    st.warning(f"🔍 **Problem:** {selected_request['problem_description']}")

            suppliers        = load_suppliers()
            active_suppliers = [s for s in suppliers if s.get("status") == "Active"]
            candidates       = _prefilter_suppliers(selected_request, active_suppliers)

            m1, m2 = st.columns(2)
            m1.metric("Active Suppliers in DB",       len(active_suppliers))
            m2.metric("Candidates After Pre-filter",  len(candidates))

            if not candidates:
                st.warning(
                    "⚠️ No candidate suppliers found after pre-filtering. "
                    "Register suppliers for the required category and nearby state."
                )
            elif st.button("🚀 Run AI Match Analysis", width="stretch", type="primary"):
                with st.spinner("🤖 LAKHEE AI is analysing matches — please wait…"):
                    try:
                        results = _run_matching(api_key, selected_request, candidates)

                        supplier_map = {s["id"]: s for s in candidates}
                        enriched = sorted(
                            [{**r, "supplier_data": supplier_map.get(r.get("supplier_id"), {})} for r in results],
                            key=lambda x: x.get("match_score", 0),
                            reverse=True,
                        )

                        st.session_state["match_results"]  = enriched
                        st.session_state["match_request"]  = selected_request
                        st.session_state["ai_chat_context"] = json.dumps(
                            {"request": selected_request, "top_matches": enriched[:3]},
                            indent=2, default=str,
                        )

                        # Persist best match if score ≥ 60
                        if enriched and enriched[0].get("match_score", 0) >= 60:
                            save_match({
                                "request_id":    selected_request.get("id"),
                                "supplier_id":   enriched[0].get("supplier_id"),
                                "match_score":   enriched[0].get("match_score"),
                                "recommendation":enriched[0].get("recommendation"),
                                "summary":       enriched[0].get("summary"),
                                "farmer_name":   selected_request.get("farmer_name"),
                                "supplier_name": enriched[0].get("supplier_data", {}).get("company_name"),
                                "product":       enriched[0].get("supplier_data", {}).get("product_name"),
                            })
                            update_request_status(selected_request.get("id"), "Matched")

                        st.success(
                            f"✅ Analysis complete! **{len(enriched)}** match(es) found. "
                            "Switch to the **Match Results** tab."
                        )
                    except json.JSONDecodeError as je:
                        st.error(f"❌ JSON parse error in Gemini response: {je}")
                    except Exception as e:
                        st.error(f"❌ Error running AI match: {e}")

    # ── Tab 2 : Match Results ─────────────────────────────────────────────
    with tab_results:
        st.subheader("📊 AI Match Results")

        results       = st.session_state.get("match_results", [])
        match_request = st.session_state.get("match_request", {})

        if not results:
            st.info("No results yet. Run an AI Match from the **Run AI Match** tab.")
        else:
            st.markdown(
                f"**Request:** {match_request.get('id')} — "
                f"{match_request.get('crop_type')} | "
                f"{match_request.get('district')}, {match_request.get('state')}"
            )
            st.divider()

            for idx, result in enumerate(results):
                score = result.get("match_score", 0)
                rec   = result.get("recommendation", "")
                sup   = result.get("supplier_data", {})

                badge = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                rank  = ("🥇 BEST MATCH" if idx == 0
                         else ("🥈 2nd Best" if idx == 1
                               else ("🥉 3rd" if idx == 2 else f"#{idx+1}")))

                with st.expander(
                    f"{badge} {rank} — {sup.get('product_name','N/A')} by "
                    f"{sup.get('company_name','N/A')} | Score: {score}/100 | {rec}",
                    expanded=(idx == 0),
                ):
                    left, right = st.columns([1, 2])
                    with left:
                        st.metric("Match Score",    f"{score}/100")
                        st.metric("Recommendation", rec)
                        st.markdown(f"**Supplier ID:** `{result.get('supplier_id')}`")
                        st.markdown(f"**Company:** {sup.get('company_name')}")
                        st.markdown(f"**Phone:** {sup.get('phone')}")
                        st.markdown(f"**Location:** {sup.get('district')}, {sup.get('state')}")
                        st.markdown(f"**Price:** ₹{sup.get('price_per_unit')}/{sup.get('unit')}")
                        st.markdown(f"**Stock:** {sup.get('quantity_available')} {sup.get('unit')}")

                    with right:
                        st.markdown("### 🤖 AI Analysis")
                        a, b = st.columns(2)
                        with a:
                            st.markdown("**🧪 Chemical Compatibility**")
                            st.info(result.get("chemical_compatibility", "N/A"))
                            st.markdown("**📦 Stock Adequacy**")
                            st.info(result.get("stock_adequacy", "N/A"))
                            st.markdown("**💰 Price Assessment**")
                            st.info(result.get("price_assessment", "N/A"))
                        with b:
                            st.markdown("**📍 Location Suitability**")
                            st.info(result.get("location_suitability", "N/A"))
                            st.markdown("**🌱 Agronomic Advice**")
                            st.success(result.get("agronomic_advice", "N/A"))
                            if result.get("risk_flags"):
                                st.markdown("**⚠️ Risk Flags**")
                                st.warning(result.get("risk_flags"))
                        st.markdown("**📝 Summary**")
                        st.write(result.get("summary", "N/A"))

    # ── Tab 3 : AI Advisory Chat ──────────────────────────────────────────
    with tab_chat:
        st.subheader("💬 Ask LAKHEE AI — Your Agri Advisor")
        st.markdown(
            "Ask anything about fertilizer dosages, pest control, product compatibility, "
            "or procurement advice."
        )

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input(
            "Ask LAKHEE AI… e.g., What is the correct dosage of DAP for wheat?"
        )

        if user_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("LAKHEE is thinking…"):
                    try:
                        context = st.session_state.get(
                            "ai_chat_context",
                            "No specific procurement context loaded. Answer generally.",
                        )
                        answer = _run_chat(api_key, context, user_input)
                        st.write(answer)
                        st.session_state["chat_history"].append(
                            {"role": "assistant", "content": answer}
                        )
                    except Exception as e:
                        err = f"❌ Error: {e}"
                        st.error(err)
                        st.session_state["chat_history"].append(
                            {"role": "assistant", "content": err}
                        )

        if st.session_state.get("chat_history"):
            if st.button("🗑️ Clear Chat History"):
                st.session_state["chat_history"] = []
                st.rerun()
