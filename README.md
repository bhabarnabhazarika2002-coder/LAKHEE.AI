# 🌿 LAKHEE — KHET KI DOST
### *"Kisan ka vishwaas, Khet ki zaroorat, AI ka jaadu"*

> India's AI-Powered Procurement Matching Platform for Fertilizers & Agrochemicals

---

## 📋 Overview

**LAKHEE — KHET KI DOST** (Friend of the Farm) is a Streamlit-based AI procurement platform that connects **fertilizer and agrochemical suppliers** directly with **farmers in urgent need**, powered by **Google Gemini 1.5 Flash**.

The platform performs automatic intelligent matching based on:
- 🧪 **Chemical Composition** — Does the product address the crop/pest problem?
- 📍 **Geographic Location** — Is the supplier reachable within required distance?
- 📦 **Stock Availability** — Can the supplier fulfil the required quantity?
- 💰 **Price Compatibility** — Does the pricing fit the farmer's budget?
- 🌱 **Agronomic Suitability** — Is the product right for the crop and growth stage?

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd lakhee_platform
pip install -r requirements.txt
```

### 2. Get a Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** — it's free
4. Copy the key (starts with `AIza...`)

### 3. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### 4. Enter API Key in App

Open the **AI Matching Engine** page → enter your Gemini API Key in the sidebar.

---

## 🗂️ Project Structure

```
lakhee_platform/
├── app.py                          ← Main Streamlit entry point
├── requirements.txt                ← Python dependencies
├── .streamlit/
│   └── config.toml                 ← Theme configuration (green agri theme)
├── pages/
│   ├── __init__.py
│   ├── home.py                     ← Landing page with quick nav
│   ├── supplier_registration.py    ← Supplier inventory registration form
│   ├── farmer_requests.py          ← Farmer urgent request posting
│   ├── ai_matching.py              ← Gemini AI matching engine + chat
│   ├── dashboard.py                ← Analytics & KPI dashboard
│   └── admin_panel.py              ← Admin data management panel
├── utils/
│   ├── __init__.py
│   └── data_models.py              ← Data models, file I/O, session state
└── data/                           ← Auto-created JSON data storage
    ├── suppliers.json
    ├── farmer_requests.json
    └── matches.json
```

---

## 🧭 Platform Pages

| Page | Description |
|------|-------------|
| 🏠 **Home** | Landing page, feature overview, live stats, quick navigation |
| 🏭 **Supplier Registration** | Register inventory with product, composition, stock, pricing, location |
| 🌾 **Farmer Requests** | Post urgent requirements with crop, problem, urgency, quantity |
| 🤖 **AI Matching Engine** | Gemini-powered matching + AI advisory chat |
| 📊 **Dashboard** | Charts, KPIs, activity feed, match analytics |
| 🛡️ **Admin Panel** | Full data view, status management, JSON export |

---

## 🤖 AI Matching Engine — How It Works

1. **Pre-filter**: Quickly eliminates suppliers with wrong category, insufficient stock, or too-far location (no AI cost)
2. **Gemini Analysis**: Sends farmer request + candidate suppliers to Gemini 1.5 Flash
3. **Scoring**: Each supplier scored 0–100 across 5 dimensions
4. **Results**: Ranked matches with detailed reasoning per dimension
5. **Advisory Chat**: Ask LAKHEE AI any question about dosages, compatibility, alternatives

### Scoring Breakdown
| Dimension | Max Points |
|-----------|-----------|
| Chemical / product match to crop problem | 35 |
| Location proximity & delivery feasibility | 25 |
| Stock adequacy | 20 |
| Price vs budget | 10 |
| Certifications & reliability | 10 |

---

## 📦 Data Storage

Data is stored in local JSON files under `lakhee_platform/data/`:
- `suppliers.json` — All registered supplier inventory records
- `farmer_requests.json` — All farmer requests with status tracking
- `matches.json` — AI match audit trail

Records are exportable from the **Admin Panel** as JSON downloads.

---

## 🌱 Supported Products

**15 Product Categories:**
Nitrogen/Phosphorus/Potassium Fertilizers, NPK Compounds, Micronutrients, Organic & Bio-Fertilizers, Herbicides, Pesticides, Fungicides, Insecticides, Rodenticides, Plant Growth Regulators, Soil Conditioners, Foliar Sprays

**30+ Crop Types:**
Rice, Wheat, Maize, Sugarcane, Cotton, Soybean, Groundnut, Vegetables, Fruits, Plantation crops, and more

**All 31 Indian States/UTs** supported for geographic matching

---

## ⚠️ Disclaimer

LAKHEE is an AI-assisted decision support tool. Always verify product labels, safety data sheets (SDS), and comply with local regulations and CIB&RC guidelines before application. Consult a certified agronomist for critical crop decisions.

---

## 🔑 Environment Variables (Optional)

Instead of entering the API key in the UI each time, you can set:
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "AIza..."

# Or create a .env file (requires python-dotenv)
GOOGLE_API_KEY=AIza...
```

---

*Built with ❤️ for Indian Agriculture | Powered by Google Gemini 1.5 Flash & Streamlit*
