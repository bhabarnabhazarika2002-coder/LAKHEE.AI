"""
LAKHEE - KHET KI DOST
Core data models and session state management
"""

import json
import os
from datetime import datetime
from pathlib import Path
import streamlit as st

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
SUPPLIER_FILE = DATA_DIR / "suppliers.json"
FARMER_FILE = DATA_DIR / "farmer_requests.json"
MATCHES_FILE = DATA_DIR / "matches.json"

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Jammu & Kashmir", "Ladakh"
]

PRODUCT_CATEGORIES = [
    "Nitrogen Fertilizer", "Phosphorus Fertilizer", "Potassium Fertilizer",
    "NPK Compound Fertilizer", "Micronutrient Fertilizer", "Organic Fertilizer",
    "Bio-Fertilizer", "Herbicide", "Pesticide", "Fungicide", "Insecticide",
    "Rodenticide", "Plant Growth Regulator", "Soil Conditioner", "Foliar Spray"
]

CROP_TYPES = [
    "Rice (Paddy)", "Wheat", "Maize (Corn)", "Sugarcane", "Cotton",
    "Soybean", "Groundnut", "Mustard/Rapeseed", "Sunflower", "Chickpea",
    "Lentil (Masoor)", "Green Gram (Moong)", "Black Gram (Urad)", "Pigeon Pea (Arhar)",
    "Potato", "Onion", "Tomato", "Brinjal", "Cauliflower", "Cabbage",
    "Mango", "Banana", "Grapes", "Apple", "Citrus Fruits",
    "Tea", "Coffee", "Jute", "Tobacco", "Mixed Crops"
]

URGENCY_LEVELS = ["🔴 Critical (Within 24 hrs)", "🟠 High (Within 3 days)", "🟡 Medium (Within 1 week)", "🟢 Normal (Within 2 weeks)"]

UNITS = ["kg", "tonnes", "litres", "ml", "bags (50kg)", "bags (25kg)", "drums (200L)"]


# ──────────────────────────────────────────────
# File I/O helpers
# ──────────────────────────────────────────────

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filepath: Path) -> list:
    _ensure_data_dir()
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_json(filepath: Path, data: list):
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ──────────────────────────────────────────────
# Supplier helpers
# ──────────────────────────────────────────────

def load_suppliers() -> list:
    return _load_json(SUPPLIER_FILE)


def save_supplier(record: dict):
    data = load_suppliers()
    record["id"] = f"SUP-{len(data)+1:04d}"
    record["registered_at"] = datetime.now().isoformat()
    record["status"] = "Active"
    data.append(record)
    _save_json(SUPPLIER_FILE, data)
    return record["id"]


def update_supplier_status(supplier_id: str, status: str):
    data = load_suppliers()
    for item in data:
        if item.get("id") == supplier_id:
            item["status"] = status
            break
    _save_json(SUPPLIER_FILE, data)


# ──────────────────────────────────────────────
# Farmer request helpers
# ──────────────────────────────────────────────

def load_farmer_requests() -> list:
    return _load_json(FARMER_FILE)


def save_farmer_request(record: dict):
    data = load_farmer_requests()
    record["id"] = f"REQ-{len(data)+1:04d}"
    record["posted_at"] = datetime.now().isoformat()
    record["status"] = "Open"
    data.append(record)
    _save_json(FARMER_FILE, data)
    return record["id"]


def update_request_status(request_id: str, status: str):
    data = load_farmer_requests()
    for item in data:
        if item.get("id") == request_id:
            item["status"] = status
            break
    _save_json(FARMER_FILE, data)


# ──────────────────────────────────────────────
# Match helpers
# ──────────────────────────────────────────────

def load_matches() -> list:
    return _load_json(MATCHES_FILE)


def save_match(record: dict):
    data = load_matches()
    record["id"] = f"MATCH-{len(data)+1:04d}"
    record["matched_at"] = datetime.now().isoformat()
    data.append(record)
    _save_json(MATCHES_FILE, data)
    return record["id"]


# ──────────────────────────────────────────────
# Session state initialisation
# ──────────────────────────────────────────────

def init_session_state():
    defaults = {
        "active_page": "🏠 Home",
        "match_results": [],
        "last_supplier_id": None,
        "last_request_id": None,
        "ai_analysis_cache": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ──────────────────────────────────────────────
# Dashboard stats
# ──────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    suppliers = load_suppliers()
    requests = load_farmer_requests()
    matches = load_matches()

    active_suppliers = [s for s in suppliers if s.get("status") == "Active"]
    open_requests = [r for r in requests if r.get("status") == "Open"]
    critical_requests = [r for r in open_requests if "Critical" in r.get("urgency", "")]

    return {
        "total_suppliers": len(suppliers),
        "active_suppliers": len(active_suppliers),
        "total_requests": len(requests),
        "open_requests": len(open_requests),
        "critical_requests": len(critical_requests),
        "total_matches": len(matches),
        "successful_matches": len([m for m in matches if m.get("match_score", 0) >= 70]),
    }
