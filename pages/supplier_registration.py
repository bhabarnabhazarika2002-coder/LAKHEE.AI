"""
LAKHEE - KHET KI DOST
Supplier Inventory Registration Page
"""

import streamlit as st
from datetime import date
from utils.data_models import (
    save_supplier, load_suppliers, update_supplier_status,
    INDIAN_STATES, PRODUCT_CATEGORIES, UNITS
)


def render():
    st.title("🏭 Supplier Inventory Registration")
    st.markdown(
        "Register your fertilizer or agrochemical inventory so farmers in need can find you instantly."
    )
    st.divider()

    tab1, tab2 = st.tabs(["➕ Register New Inventory", "📋 My Registered Inventory"])

    # ── Tab 1: Registration Form ──────────────────────────────────────────
    with tab1:
        with st.form("supplier_registration_form", clear_on_submit=True):
            st.subheader("🏢 Company / Supplier Details")
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input(
                    "Company / Supplier Name *",
                    placeholder="e.g., Agro Solutions Pvt. Ltd."
                )
                contact_person = st.text_input(
                    "Contact Person Name *",
                    placeholder="e.g., Rajesh Kumar"
                )
                phone = st.text_input(
                    "Phone Number *",
                    placeholder="e.g., 9876543210"
                )
            with col2:
                email = st.text_input(
                    "Email Address",
                    placeholder="e.g., supplier@example.com"
                )
                state = st.selectbox("State *", ["-- Select State --"] + INDIAN_STATES)
                district = st.text_input(
                    "District / City *",
                    placeholder="e.g., Nashik"
                )

            st.divider()
            st.subheader("📦 Product Details")

            col3, col4 = st.columns(2)
            with col3:
                product_name = st.text_input(
                    "Product Brand / Trade Name *",
                    placeholder="e.g., Urea Super Grade, DAP Gold"
                )
                product_category = st.selectbox(
                    "Product Category *",
                    ["-- Select Category --"] + PRODUCT_CATEGORIES
                )
                generic_name = st.text_input(
                    "Generic / Chemical Name *",
                    placeholder="e.g., Urea (46% N), Diammonium Phosphate"
                )
            with col4:
                npk_composition = st.text_input(
                    "NPK / Chemical Composition",
                    placeholder="e.g., N:46%, P:0%, K:0% or 18-46-0"
                )
                active_ingredient = st.text_area(
                    "Active Ingredients / Key Compounds",
                    placeholder="e.g., Carbendazim 50% WP, Chlorpyrifos 20% EC",
                    height=100
                )
                applicable_crops = st.text_area(
                    "Applicable Crops",
                    placeholder="e.g., Rice, Wheat, Cotton, Vegetables",
                    height=68
                )

            st.divider()
            st.subheader("📊 Stock & Pricing")

            col5, col6, col7 = st.columns(3)
            with col5:
                quantity_available = st.number_input(
                    "Quantity Available *",
                    min_value=1.0,
                    value=100.0,
                    step=1.0
                )
                unit = st.selectbox("Unit *", UNITS)
            with col6:
                price_per_unit = st.number_input(
                    "Price per Unit (₹) *",
                    min_value=0.01,
                    value=500.0,
                    step=0.5,
                    format="%.2f"
                )
                min_order_qty = st.number_input(
                    "Minimum Order Quantity",
                    min_value=1.0,
                    value=10.0,
                    step=1.0
                )
            with col7:
                availability_till = st.date_input(
                    "Stock Available Till *",
                    value=date.today(),
                    min_value=date.today()
                )
                delivery_radius_km = st.number_input(
                    "Max Delivery Radius (km)",
                    min_value=0,
                    value=100,
                    step=10
                )

            certifications = st.text_input(
                "Certifications / Licenses",
                placeholder="e.g., BIS Certified, FSSAI, CIB&RC License No. XX-XXXX"
            )
            special_notes = st.text_area(
                "Special Notes / Storage Conditions",
                placeholder="e.g., Store in cool dry place, Bulk discounts available on orders > 500 kg",
                height=80
            )

            submitted = st.form_submit_button(
                "✅ Register Inventory", width="stretch", type="primary"
            )

            if submitted:
                # Validation
                errors = []
                if not company_name.strip():
                    errors.append("Company / Supplier Name is required.")
                if not contact_person.strip():
                    errors.append("Contact Person Name is required.")
                if not phone.strip():
                    errors.append("Phone Number is required.")
                if state == "-- Select State --":
                    errors.append("Please select a State.")
                if not district.strip():
                    errors.append("District / City is required.")
                if not product_name.strip():
                    errors.append("Product Brand / Trade Name is required.")
                if product_category == "-- Select Category --":
                    errors.append("Please select a Product Category.")
                if not generic_name.strip():
                    errors.append("Generic / Chemical Name is required.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    record = {
                        "company_name": company_name.strip(),
                        "contact_person": contact_person.strip(),
                        "phone": phone.strip(),
                        "email": email.strip(),
                        "state": state,
                        "district": district.strip(),
                        "product_name": product_name.strip(),
                        "product_category": product_category,
                        "generic_name": generic_name.strip(),
                        "npk_composition": npk_composition.strip(),
                        "active_ingredient": active_ingredient.strip(),
                        "applicable_crops": applicable_crops.strip(),
                        "quantity_available": quantity_available,
                        "unit": unit,
                        "price_per_unit": price_per_unit,
                        "min_order_qty": min_order_qty,
                        "availability_till": str(availability_till),
                        "delivery_radius_km": delivery_radius_km,
                        "certifications": certifications.strip(),
                        "special_notes": special_notes.strip(),
                    }
                    supplier_id = save_supplier(record)
                    st.session_state["last_supplier_id"] = supplier_id
                    st.success(f"✅ Inventory registered successfully! Your Supplier ID: **{supplier_id}**")
                    st.balloons()

    # ── Tab 2: View Registered Inventory ──────────────────────────────────
    with tab2:
        st.subheader("📋 All Registered Supplier Inventories")

        suppliers = load_suppliers()

        if not suppliers:
            st.info("No supplier inventories registered yet. Use the **Register New Inventory** tab to add one.")
            return

        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_state = st.selectbox(
                "Filter by State", ["All"] + INDIAN_STATES, key="sup_filter_state"
            )
        with col_f2:
            filter_cat = st.selectbox(
                "Filter by Category", ["All"] + PRODUCT_CATEGORIES, key="sup_filter_cat"
            )
        with col_f3:
            filter_status = st.selectbox(
                "Filter by Status", ["All", "Active", "Inactive"], key="sup_filter_status"
            )

        filtered = suppliers
        if filter_state != "All":
            filtered = [s for s in filtered if s.get("state") == filter_state]
        if filter_cat != "All":
            filtered = [s for s in filtered if s.get("product_category") == filter_cat]
        if filter_status != "All":
            filtered = [s for s in filtered if s.get("status") == filter_status]

        st.markdown(f"**Showing {len(filtered)} of {len(suppliers)} records**")
        st.divider()

        for sup in reversed(filtered):
            with st.expander(
                f"🏭 {sup.get('product_name', 'N/A')} — {sup.get('company_name', 'N/A')} | "
                f"{sup.get('state', '')} | {sup.get('id', '')}",
                expanded=False
            ):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Supplier ID:** `{sup.get('id')}`")
                    st.markdown(f"**Company:** {sup.get('company_name')}")
                    st.markdown(f"**Contact:** {sup.get('contact_person')}")
                    st.markdown(f"**Phone:** {sup.get('phone')}")
                    st.markdown(f"**Location:** {sup.get('district')}, {sup.get('state')}")
                with c2:
                    st.markdown(f"**Product:** {sup.get('product_name')}")
                    st.markdown(f"**Category:** {sup.get('product_category')}")
                    st.markdown(f"**Generic Name:** {sup.get('generic_name')}")
                    st.markdown(f"**NPK/Composition:** {sup.get('npk_composition', 'N/A')}")
                    st.markdown(f"**Active Ingredients:** {sup.get('active_ingredient', 'N/A')}")
                with c3:
                    st.markdown(
                        f"**Stock:** {sup.get('quantity_available')} {sup.get('unit')}"
                    )
                    st.markdown(f"**Price:** ₹{sup.get('price_per_unit')}/{sup.get('unit')}")
                    st.markdown(f"**Min Order:** {sup.get('min_order_qty')} {sup.get('unit')}")
                    st.markdown(f"**Available Till:** {sup.get('availability_till')}")
                    st.markdown(f"**Delivery Radius:** {sup.get('delivery_radius_km')} km")
                    status_color = "🟢" if sup.get("status") == "Active" else "🔴"
                    st.markdown(f"**Status:** {status_color} {sup.get('status')}")

                if sup.get("applicable_crops"):
                    st.markdown(f"**Applicable Crops:** {sup.get('applicable_crops')}")
                if sup.get("certifications"):
                    st.markdown(f"**Certifications:** {sup.get('certifications')}")
                if sup.get("special_notes"):
                    st.info(f"📝 {sup.get('special_notes')}")

                # Toggle status
                new_status = "Inactive" if sup.get("status") == "Active" else "Active"
                if st.button(
                    f"{'🔴 Mark Inactive' if sup.get('status') == 'Active' else '🟢 Mark Active'}",
                    key=f"toggle_{sup.get('id')}"
                ):
                    update_supplier_status(sup.get("id"), new_status)
                    st.rerun()
