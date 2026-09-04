"""
LAKHEE - KHET KI DOST
Farmer Urgent Request Posting Page
"""

import streamlit as st
from datetime import date
from utils.data_models import (
    save_farmer_request, load_farmer_requests, update_request_status,
    INDIAN_STATES, PRODUCT_CATEGORIES, CROP_TYPES, URGENCY_LEVELS, UNITS
)


def render():
    st.title("🌾 Farmer Request Portal")
    st.markdown(
        "Post your urgent requirement for fertilizers or agrochemicals. "
        "Our AI will match you with the best nearby suppliers automatically."
    )
    st.divider()

    tab1, tab2 = st.tabs(["📢 Post New Request", "📋 My Requests"])

    # ── Tab 1: Post Request Form ──────────────────────────────────────────
    with tab1:
        with st.form("farmer_request_form", clear_on_submit=True):
            st.subheader("👨‍🌾 Farmer / Buyer Details")
            col1, col2 = st.columns(2)
            with col1:
                farmer_name = st.text_input(
                    "Farmer / Buyer Name *",
                    placeholder="e.g., Suresh Patil"
                )
                phone = st.text_input(
                    "Phone Number *",
                    placeholder="e.g., 9876543210"
                )
                state = st.selectbox("State *", ["-- Select State --"] + INDIAN_STATES)
            with col2:
                district = st.text_input(
                    "District / Village *",
                    placeholder="e.g., Amravati / Warud"
                )
                land_area = st.number_input(
                    "Land Area (in acres)",
                    min_value=0.1,
                    value=5.0,
                    step=0.5,
                    format="%.1f"
                )
                email = st.text_input(
                    "Email (optional)",
                    placeholder="e.g., farmer@example.com"
                )

            st.divider()
            st.subheader("🌱 Crop & Problem Details")

            col3, col4 = st.columns(2)
            with col3:
                crop_type = st.selectbox(
                    "Crop Type *",
                    ["-- Select Crop --"] + CROP_TYPES
                )
                crop_growth_stage = st.selectbox(
                    "Crop Growth Stage",
                    ["-- Select Stage --", "Seed / Germination", "Seedling",
                     "Vegetative", "Flowering / Budding", "Fruiting / Grain filling",
                     "Maturity / Harvest"]
                )
            with col4:
                problem_description = st.text_area(
                    "Problem / Issue Description *",
                    placeholder=(
                        "e.g., Yellowing of leaves indicating Nitrogen deficiency. "
                        "Pest attack on cotton crop — bollworm infestation visible."
                    ),
                    height=120
                )

            st.divider()
            st.subheader("📦 Product Requirement")

            col5, col6 = st.columns(2)
            with col5:
                product_category_needed = st.selectbox(
                    "Product Category Needed *",
                    ["-- Select Category --"] + PRODUCT_CATEGORIES
                )
                product_name_needed = st.text_input(
                    "Specific Product / Chemical Name (if known)",
                    placeholder="e.g., DAP, Urea, Chlorpyrifos, Carbendazim"
                )
                npk_requirement = st.text_input(
                    "Required NPK / Composition (if known)",
                    placeholder="e.g., 18-46-0, or High N content fertilizer"
                )
            with col6:
                quantity_needed = st.number_input(
                    "Quantity Needed *",
                    min_value=1.0,
                    value=50.0,
                    step=1.0
                )
                unit_needed = st.selectbox("Unit *", UNITS)
                budget_per_unit = st.number_input(
                    "Budget per Unit (₹) — approximate",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    format="%.0f",
                    help="Leave 0 if flexible"
                )

            st.divider()
            st.subheader("⏰ Urgency & Timeline")

            col7, col8 = st.columns(2)
            with col7:
                urgency = st.selectbox("Urgency Level *", URGENCY_LEVELS)
                required_by = st.date_input(
                    "Required By Date *",
                    value=date.today(),
                    min_value=date.today()
                )
            with col8:
                preferred_delivery = st.selectbox(
                    "Delivery Preference",
                    ["Delivery to Farm", "Will Pick Up", "Either"]
                )
                max_distance_km = st.number_input(
                    "Max Supplier Distance (km)",
                    min_value=10,
                    value=150,
                    step=10,
                    help="Maximum distance you're willing to source from"
                )

            additional_info = st.text_area(
                "Additional Information / Special Requirements",
                placeholder=(
                    "e.g., Need organic-certified product, "
                    "prefer suppliers with bulk discount, "
                    "require delivery to remote area"
                ),
                height=80
            )

            submitted = st.form_submit_button(
                "📢 Post Request", width="stretch", type="primary"
            )

            if submitted:
                errors = []
                if not farmer_name.strip():
                    errors.append("Farmer / Buyer Name is required.")
                if not phone.strip():
                    errors.append("Phone Number is required.")
                if state == "-- Select State --":
                    errors.append("Please select a State.")
                if not district.strip():
                    errors.append("District / Village is required.")
                if crop_type == "-- Select Crop --":
                    errors.append("Please select a Crop Type.")
                if not problem_description.strip():
                    errors.append("Problem / Issue Description is required.")
                if product_category_needed == "-- Select Category --":
                    errors.append("Please select a Product Category Needed.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    record = {
                        "farmer_name": farmer_name.strip(),
                        "phone": phone.strip(),
                        "email": email.strip(),
                        "state": state,
                        "district": district.strip(),
                        "land_area": land_area,
                        "crop_type": crop_type,
                        "crop_growth_stage": crop_growth_stage
                        if crop_growth_stage != "-- Select Stage --"
                        else "Not specified",
                        "problem_description": problem_description.strip(),
                        "product_category_needed": product_category_needed,
                        "product_name_needed": product_name_needed.strip(),
                        "npk_requirement": npk_requirement.strip(),
                        "quantity_needed": quantity_needed,
                        "unit_needed": unit_needed,
                        "budget_per_unit": budget_per_unit,
                        "urgency": urgency,
                        "required_by": str(required_by),
                        "preferred_delivery": preferred_delivery,
                        "max_distance_km": max_distance_km,
                        "additional_info": additional_info.strip(),
                    }
                    request_id = save_farmer_request(record)
                    st.session_state["last_request_id"] = request_id
                    st.success(
                        f"✅ Request posted successfully! Your Request ID: **{request_id}**\n\n"
                        f"Go to **AI Matching Engine** to find the best supplier matches."
                    )
                    st.balloons()

    # ── Tab 2: View All Requests ──────────────────────────────────────────
    with tab2:
        st.subheader("📋 All Farmer Requests")

        requests = load_farmer_requests()

        if not requests:
            st.info("No farmer requests posted yet. Use the **Post New Request** tab to add one.")
            return

        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_state = st.selectbox(
                "Filter by State", ["All"] + INDIAN_STATES, key="req_filter_state"
            )
        with col_f2:
            filter_urgency = st.selectbox(
                "Filter by Urgency",
                ["All"] + URGENCY_LEVELS,
                key="req_filter_urgency"
            )
        with col_f3:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Open", "Matched", "Closed"],
                key="req_filter_status"
            )

        filtered = requests
        if filter_state != "All":
            filtered = [r for r in filtered if r.get("state") == filter_state]
        if filter_urgency != "All":
            filtered = [r for r in filtered if r.get("urgency") == filter_urgency]
        if filter_status != "All":
            filtered = [r for r in filtered if r.get("status") == filter_status]

        st.markdown(f"**Showing {len(filtered)} of {len(requests)} requests**")
        st.divider()

        for req in reversed(filtered):
            urgency_icon = req.get("urgency", "")[:2]
            with st.expander(
                f"{urgency_icon} {req.get('crop_type', 'N/A')} — "
                f"{req.get('product_category_needed', '')} | "
                f"{req.get('district')}, {req.get('state')} | {req.get('id')}",
                expanded=False
            ):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Request ID:** `{req.get('id')}`")
                    st.markdown(f"**Farmer:** {req.get('farmer_name')}")
                    st.markdown(f"**Phone:** {req.get('phone')}")
                    st.markdown(f"**Location:** {req.get('district')}, {req.get('state')}")
                    st.markdown(f"**Land Area:** {req.get('land_area')} acres")
                with c2:
                    st.markdown(f"**Crop:** {req.get('crop_type')}")
                    st.markdown(f"**Stage:** {req.get('crop_growth_stage')}")
                    st.markdown(f"**Category Needed:** {req.get('product_category_needed')}")
                    st.markdown(f"**Product:** {req.get('product_name_needed', 'Any')}")
                    st.markdown(f"**NPK Required:** {req.get('npk_requirement', 'N/A')}")
                with c3:
                    st.markdown(
                        f"**Quantity:** {req.get('quantity_needed')} {req.get('unit_needed')}"
                    )
                    st.markdown(
                        f"**Budget:** {'₹' + str(req.get('budget_per_unit')) + '/unit' if req.get('budget_per_unit', 0) > 0 else 'Flexible'}"
                    )
                    st.markdown(f"**Urgency:** {req.get('urgency')}")
                    st.markdown(f"**Required By:** {req.get('required_by')}")
                    status_map = {"Open": "🟡", "Matched": "🟢", "Closed": "⚫"}
                    status_icon = status_map.get(req.get("status", "Open"), "🟡")
                    st.markdown(f"**Status:** {status_icon} {req.get('status')}")

                if req.get("problem_description"):
                    st.warning(f"🔍 **Problem:** {req.get('problem_description')}")
                if req.get("additional_info"):
                    st.info(f"📝 {req.get('additional_info')}")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if req.get("status") == "Open":
                        if st.button("✅ Mark as Matched", key=f"match_{req.get('id')}"):
                            update_request_status(req.get("id"), "Matched")
                            st.rerun()
                with col_btn2:
                    if req.get("status") != "Closed":
                        if st.button("🔒 Close Request", key=f"close_{req.get('id')}"):
                            update_request_status(req.get("id"), "Closed")
                            st.rerun()
