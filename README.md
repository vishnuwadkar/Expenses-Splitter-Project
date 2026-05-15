<div align="center">

# 💸 SplitWise AI

**An AI-powered web application that digitizes receipts, intelligently parses line items, and calculates proportional bill splits with granular tax distribution.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🚀 Overview

SplitWise AI eliminates the headache of manually splitting restaurant bills. Simply upload a photo of your receipt, and the app uses Computer Vision (EasyOCR) and Large Language Models (Google Gemini) to extract items, prices, and quantities. It then allows you to assign specific items to individuals and calculates the exact amount owed, including a **proportional distribution of GST/taxes** based on individual consumption.

The app features a multi-tenant architecture with Google OAuth, allowing users to save their split history and view personal financial analytics in a beautifully designed, glassmorphism-inspired UI.

## ✨ Features

- **📸 AI Receipt Parsing:** Extracts messy unstructured text from receipt images and structures it into JSON.
- **🧮 Proportional Splitting:** Stop splitting taxes evenly. The app calculates exactly how much tax each person owes based on their specific food orders.
- **📊 Data Analytics Dashboard:** Interactive Plotly charts showing spending trends, per-person expenditure, and top ordered items.
- **🔐 Secure Multi-Tenancy:** Google OAuth 2.0 ensures that your receipt history and analytics are private to your account.
- **🎨 Premium UI/UX:** Custom CSS injections provide a modern, responsive 3-column layout with bespoke typography (Outfit & Plus Jakarta Sans).

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Custom CSS/HTML, Plotly
- **Backend:** Python
- **AI / Computer Vision:** EasyOCR (PyTorch), Google Gemini 1.5 Pro API
- **Database:** SQLite
- **Authentication:** `streamlit-google-auth` (OAuth 2.0)

## 💻 Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/vishnuwadkar/Expenses-Splitter-Project.git
cd Expenses-Splitter-Project
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and add your Google Gemini API Key:
```env
GEMINI_API_KEY="your_api_key_here"
```

*(Optional)* To enable Google Login locally, add your `google_credentials.json` OAuth file to the root directory.

### 5. Run the Application
```bash
python -m streamlit run app.py
```

## ☁️ Deployment (Streamlit Community Cloud)

1. Connect your GitHub repository to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Set the main file path to `app.py`.
3. In **Advanced Settings -> Secrets**, add your API key and Google credentials as a TOML string:
```toml
GEMINI_API_KEY = "your_api_key_here"

[google_credentials]
json_string = """
{
  "web": {
    "client_id": "...",
    "project_id": "...",
    ...
  }
}
"""
```
4. Click Deploy. (Note: EasyOCR initialization is optimized with `@st.cache_resource` to prevent OOM crashes on free-tier servers).

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
