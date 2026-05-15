import streamlit as st
import os
import json
from datetime import datetime
from ocr import extract_text_from_image
from parser import parse_receipt_with_gemini
from splitter import calculate_splits
from database import save_receipt, get_all_receipts, get_receipt_details, delete_receipt, get_summary_stats
from analytics import (
    create_spending_trend_chart,
    create_person_spending_chart,
    create_top_items_chart,
    create_spending_breakdown_pie,
    create_bill_distribution_chart
)

try:
    from streamlit_google_auth import Authenticate
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="SplitWise AI — Smart Bill Splitter",
    page_icon="💸",
    layout="wide"
)

# ── Authentication ───────────────────────────────────────
user_email = "local_user@example.com"
authenticator = None

if HAS_AUTH and os.path.exists('google_credentials.json'):
    authenticator = Authenticate(
        secret_credentials_path='google_credentials.json',
        cookie_name='splitwise_cookie',
        cookie_key='splitwise_signature_key',
        redirect_uri='http://localhost:8501',
        cookie_expiry_days=30
    )
    
    try:
        authenticator.check_authentification()
        if st.session_state.get('connected'):
            user_info = st.session_state.get('user_info', {})
            user_email = user_info.get('email', 'local_user@example.com')
            st.sidebar.markdown(f"**Logged in as:**<br>{user_email}", unsafe_allow_html=True)
            if st.sidebar.button("Logout"):
                authenticator.logout()
        else:
            st.sidebar.info("Not logged in — using local mode")
            authenticator.login()
    except Exception as e:
        st.sidebar.warning(f"Auth unavailable. Local mode.")

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap');

    /* ── Global Reset ── */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background:
            radial-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
            radial-gradient(ellipse 600px 600px at 10% 15%, rgba(124, 58, 237, 0.18) 0%, transparent 70%),
            radial-gradient(ellipse 500px 500px at 85% 25%, rgba(6, 182, 212, 0.12) 0%, transparent 70%),
            radial-gradient(ellipse 400px 400px at 50% 85%, rgba(124, 58, 237, 0.15) 0%, transparent 70%),
            radial-gradient(ellipse 350px 350px at 75% 70%, rgba(16, 185, 129, 0.10) 0%, transparent 70%),
            #0B0F1A;
        background-size: 22px 22px, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-attachment: fixed;
    }
    .stApp h1, .stApp h2, .stApp h3 { font-family: 'Outfit', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1440px !important;

    }

    /* ── Design System Label ── */
    .ds-label {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8; margin-bottom: 12px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    /* ── Hero ── */
    .hero {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 50%, #5B21B6 100%);
        border-radius: 12px; padding: 1.1rem 2rem; text-align: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.25);
    }
    .hero-title { font-family: 'Outfit', sans-serif; font-size: 1.7rem; font-weight: 800; color: white; margin: 0; letter-spacing: -0.03em; }
    .hero-sub { font-size: 0.78rem; color: rgba(255,255,255,0.7); margin-top: 0.15rem; letter-spacing: 0.03em; font-weight: 400; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 0 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0 !important; padding: 12px 20px !important;
        font-weight: 500 !important; font-size: 0.85rem !important;
        color: #94A3B8 !important; border-bottom: 2px solid transparent !important;
        background: transparent !important; transition: all 0.25s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #ffffff !important; }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important; font-weight: 700 !important;
        border-bottom: 2px solid #7C3AED !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ── 3-Column Dividers ── */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:last-child) {
        border-right: 1px solid rgba(255,255,255,0.06);
        padding-right: 24px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child) {
        padding-left: 24px !important;
    }

    /* ── Receipt Image Card ── */
    .receipt-img-card {
        border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
        overflow: hidden; margin-bottom: 16px;
    }
    .receipt-img-card img { border-radius: 12px; }

    /* ── Item Pill ── */
    .item-row {
        background: #1E2130; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 10px 14px; margin-bottom: 6px;
        display: flex; justify-content: space-between; align-items: center;
        font-size: 0.82rem; transition: border-color 0.2s ease;
    }
    .item-row:hover { border-color: rgba(124, 58, 237, 0.3); }
    .item-name { font-weight: 600; color: #ffffff; }
    .item-right { display: flex; gap: 8px; align-items: center; }
    .qty-badge {
        background: rgba(124, 58, 237, 0.2); color: #A78BFA;
        padding: 2px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 700;
    }
    .item-price { font-family: 'Outfit', sans-serif; font-weight: 700; color: #10B981; min-width: 55px; text-align: right; }

    /* ── GST Row ── */
    .gst-row {
        background: rgba(100, 116, 139, 0.08); border: 1px solid rgba(100, 116, 139, 0.15);
        border-radius: 12px; padding: 10px 14px; margin-top: 8px;
        display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;
    }
    .gst-label { font-weight: 500; color: #64748B; font-style: italic; }
    .gst-amount { font-weight: 600; color: #64748B; font-style: italic; }

    /* ── Total Row ── */
    .total-pill {
        background: linear-gradient(135deg, #7C3AED, #6D28D9);
        border-radius: 12px; padding: 16px 16px; margin-top: 12px;
        display: flex; justify-content: space-between; align-items: center;
        border-top: 1px solid rgba(124, 58, 237, 0.4);
    }
    .total-pill-label {
        font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.7);
        text-transform: uppercase; letter-spacing: 0.1em;
    }
    .total-pill-amount { font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 800; color: white; }

    /* ── Assignment Card (middle column) ── */
    .assign-card {
        background: #1A1F35; border: 1px solid rgba(255,255,255,0.06);
        border-left: 3px solid #7C3AED; border-radius: 8px;
        padding: 12px 16px; margin-bottom: 8px;
    }
    .assign-card-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px;
    }
    .assign-item-name { font-weight: 700; color: #ffffff; font-size: 0.85rem; }
    .assign-item-price { font-weight: 700; color: #10B981; font-size: 0.85rem; }

    /* ── Result Card ── */
    .result-card {
        background: #1E2130; border: 1px solid rgba(255,255,255,0.06);
        border-left: 3px solid #7C3AED; border-radius: 12px;
        padding: 20px; margin-bottom: 12px; transition: all 0.3s ease;
    }
    .result-card:hover { border-color: rgba(124, 58, 237, 0.3); box-shadow: 0 4px 20px rgba(124, 58, 237, 0.08); }
    .result-person {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8; margin-bottom: 6px;
    }
    .result-total { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; color: #10B981; line-height: 1.2; margin-bottom: 8px; }
    .result-detail { font-size: 12px; color: #64748B; line-height: 1.6; }
    .result-detail .gst-line { color: #F59E0B; font-style: italic; }

    /* ── Grand Total ── */
    .grand-total {
        background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.12));
        border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 12px;
        padding: 20px; text-align: center; margin-top: 16px;
    }
    .grand-label {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8;
    }
    .grand-amount { font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 4px; }

    /* ── Stat Card ── */
    .stat-card {
        background: #1E2130; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 20px; text-align: center;
    }
    .stat-value { font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: #7C3AED; }
    .stat-label {
        font-size: 11px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #94A3B8; margin-top: 6px;
    }

    /* ── Chart Card ── */
    .chart-card {
        background: #1E2130; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 16px; margin-bottom: 16px;
    }
    .chart-title {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8; margin-bottom: 12px;
    }

    /* ── History Card ── */
    .history-card {
        background: #1E2130; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .history-card:nth-child(even) { background: #161B2E; }
    .history-card:hover { border-color: rgba(124, 58, 237, 0.25); }
    .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .history-date { font-size: 11px; color: #64748B; font-weight: 500; letter-spacing: 0.02em; }
    .history-file { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; }
    .history-stats { display: flex; gap: 12px; font-size: 12px; color: #64748B; align-items: center; }
    .history-amount { font-weight: 700; color: #10B981; }
    .history-badge {
        background: rgba(124, 58, 237, 0.15); color: #A78BFA;
        padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
    }

    /* ── Empty State ── */
    .empty-state {
        text-align: center; padding: 3.5rem 1rem;
    }
    .empty-state .emoji { font-size: 2.5rem; margin-bottom: 12px; }
    .empty-state .msg { font-size: 14px; color: #64748B; font-weight: 500; }
    .empty-state .sub { font-size: 12px; color: #475569; margin-top: 4px; }

    /* ── Buttons: Calculate (gradient) ── */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        padding: 14px 1.2rem !important; font-weight: 700 !important;
        font-size: 15px !important; transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3) !important;
        letter-spacing: 0.02em !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stButton > button:hover {
        filter: brightness(1.1) !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Save Button (outlined) ── */
    .save-btn button {
        background: transparent !important;
        border: 2px solid #7C3AED !important; border-radius: 10px !important;
        color: #ffffff !important; padding: 12px 1.2rem !important;
        font-weight: 600 !important; font-size: 14px !important;
        box-shadow: none !important;
    }
    .save-btn button:hover {
        background: rgba(124, 58, 237, 0.12) !important;
        box-shadow: none !important; transform: none !important;
        filter: none !important;
    }

    /* ── Delete Button (small, subtle) ── */
    .del-btn button {
        background: transparent !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #EF4444 !important; font-size: 12px !important;
        padding: 6px 14px !important; box-shadow: none !important;
    }
    .del-btn button:hover {
        background: rgba(239, 68, 68, 0.1) !important;
        box-shadow: none !important; transform: none !important;
        filter: none !important;
    }

    /* ── Inputs ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(124, 58, 237, 0.25); border-radius: 12px; padding: 8px;
    }
    [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {
        border-radius: 8px !important; border: 1px solid #334155 !important;
        background: #161B2E !important; font-size: 0.82rem !important;
        color: #ffffff !important; transition: all 0.2s ease !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    [data-testid="stNumberInput"] input:focus, [data-testid="stTextInput"] input:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
    }
    [data-testid="stSelectbox"] > div > div {
        border-radius: 8px !important; border-color: #334155 !important;
        background: #161B2E !important;
    }
    .stAlert { border-radius: 10px !important; font-size: 0.8rem !important; }

    /* ── Section label (used in code) ── */
    .section-label {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8; margin: 16px 0 10px 0;
    }
    .col-header {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #94A3B8; margin-bottom: 12px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">💸 SplitWise AI</div>
    <div class="hero-sub">Upload receipts · AI extracts items & GST · Split bills · Track spending</div>
</div>
""", unsafe_allow_html=True)

# ── Main Tabs ────────────────────────────────────────────
tab_split, tab_analytics, tab_history = st.tabs(["🧾 Split a Bill", "📊 Analytics", "📁 History"])

# ═══════════════════════════════════════════════════════════
#   TAB 1: SPLIT A BILL
# ═══════════════════════════════════════════════════════════
with tab_split:
    uploaded_file = st.file_uploader(
        "Upload receipt image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if not uploaded_file:
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">📸</div>
            <div class="msg">Upload a receipt image to get started</div>
            <div class="sub">Supports JPG, JPEG, PNG</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"

        # ── Process (cached) ─────────────────────────────
        if st.session_state.get("file_key") != file_key:
            with st.status("🔍 Analyzing receipt...", expanded=True) as status:
                st.write("Running OCR...")
                raw_text = extract_text_from_image(uploaded_file)
                st.session_state["raw_text"] = raw_text

                st.write("AI extracting items, quantities & GST...")
                try:
                    parsed = parse_receipt_with_gemini(raw_text)
                except Exception as e:
                    st.error(f"Parsing failed: {e}")
                    st.stop()

                st.session_state["items"] = parsed["items"]
                st.session_state["gst"] = parsed["gst"]
                st.session_state["file_key"] = file_key
                st.session_state.pop("totals", None)  # Clear old results
                st.session_state.pop("saved", None)
                status.update(label=f"✅ Found {len(parsed['items'])} items · GST: ₹{parsed['gst']}", state="complete")

        raw_text = st.session_state["raw_text"]
        items = st.session_state["items"]
        gst = st.session_state["gst"]

        # ── 3-Column Layout ──────────────────────────────
        col_left, col_mid, col_right = st.columns([3, 4, 3], gap="large")

        # ═══ LEFT: Receipt & Items ═══
        with col_left:
            st.markdown('<div class="col-header">📸 Receipt</div>', unsafe_allow_html=True)
            st.markdown('<div class="receipt-img-card">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("🔧 Raw OCR", expanded=False):
                st.code(raw_text, language=None)

            st.markdown('<div class="section-label">Detected Items</div>', unsafe_allow_html=True)
            total_food = sum(item["price"] for item in items)

            for item in items:
                st.markdown(f"""
                <div class="item-row">
                    <span class="item-name">{item['item']}</span>
                    <div class="item-right">
                        <span class="qty-badge">×{item['quantity']}</span>
                        <span class="item-price">₹{item['price']}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

            if gst > 0:
                st.markdown(f"""
                <div class="gst-row">
                    <span class="gst-label">GST / Tax</span>
                    <span class="gst-amount">₹{gst:.2f}</span>
                </div>""", unsafe_allow_html=True)

            grand = total_food + gst
            st.markdown(f"""
            <div class="total-pill">
                <span class="total-pill-label">Total</span>
                <span class="total-pill-amount">₹{grand:.2f}</span>
            </div>""", unsafe_allow_html=True)

        # ═══ MIDDLE: Assignment ═══
        with col_mid:
            st.markdown('<div class="col-header">🍽️ Split Configuration</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">People</div>', unsafe_allow_html=True)
            num_people = st.number_input("Count", min_value=2, max_value=10, value=2, label_visibility="collapsed")

            people = []
            pcols = st.columns(min(int(num_people), 5))
            for i in range(int(num_people)):
                with pcols[i % len(pcols)]:
                    name = st.text_input(f"P{i+1}", value=f"Person {i+1}", key=f"person_{i}",
                                         label_visibility="collapsed", placeholder=f"Name {i+1}")
                    people.append(name)

            st.markdown('<div class="section-label">Assign Items</div>', unsafe_allow_html=True)
            assignments = {p: [] for p in people}

            for idx, item in enumerate(items):
                qty = item["quantity"]
                unit_price = item["unit_price"]

                st.markdown(f"""
                <div class="assign-card">
                    <div class="assign-card-header">
                        <span class="assign-item-name">{item['item']} (×{qty})</span>
                        <span class="assign-item-price">₹{item['price']}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                if qty == 1:
                    assignee = st.selectbox(f"Assign {item['item']}", options=["Split equally"] + people,
                                            key=f"item_{idx}", label_visibility="collapsed")
                    if assignee == "Split equally":
                        share = round(item["price"] / len(people), 2)
                        for p in people:
                            assignments[p].append({"item": item["item"], "price": share})
                    else:
                        assignments[assignee].append({"item": item["item"], "price": item["price"]})
                else:
                    st.caption(f"₹{unit_price}/each — assign units per person")
                    acols = st.columns(len(people))
                    assigned_so_far = 0
                    for pidx, person in enumerate(people):
                        with acols[pidx]:
                            count = st.number_input(person, min_value=0, max_value=qty,
                                                    value=0, key=f"item_{idx}_p{pidx}")
                            if count > 0:
                                assignments[person].append({
                                    "item": f"{item['item']} ×{count}",
                                    "price": round(unit_price * count, 2)
                                })
                            assigned_so_far += count

                    remaining = qty - assigned_so_far
                    if remaining > 0:
                        st.info(f"{remaining} unit(s) unassigned → split equally")
                        share = round((unit_price * remaining) / len(people), 2)
                        for p in people:
                            assignments[p].append({"item": f"{item['item']} (shared)", "price": share})

            st.markdown("")
            calculate = st.button("⚡ Calculate Split", use_container_width=True)

        # ═══ RIGHT: Results ═══
        with col_right:
            st.markdown('<div class="col-header">💰 Result</div>', unsafe_allow_html=True)

            if calculate:
                totals = calculate_splits(assignments, gst)
                st.session_state["totals"] = totals
                st.session_state["assignments"] = assignments

            if "totals" in st.session_state:
                totals = st.session_state["totals"]
                cur_assignments = st.session_state.get("assignments", assignments)
                grand_collected = 0

                for person, breakdown in totals.items():
                    person_items = cur_assignments.get(person, [])
                    items_bullets = "<br>".join([f"• {it['item']}" for it in person_items]) if person_items else "—"
                    gst_line = f'<span class="gst-line">+ ₹{breakdown["gst"]:.2f} GST</span><br>' if breakdown["gst"] > 0 else ""

                    card_html = f'<div class="result-card"><div class="result-person">{person}</div><div class="result-total">₹{breakdown["total"]:.2f}</div><div class="result-detail">Food: ₹{breakdown["food"]:.2f}<br>{gst_line}{items_bullets}</div></div>'
                    st.markdown(card_html, unsafe_allow_html=True)
                    grand_collected += breakdown["total"]

                st.markdown(f"""
                <div class="grand-total">
                    <div class="grand-label">Total Collected</div>
                    <div class="grand-amount">₹{grand_collected:.2f}</div>
                </div>""", unsafe_allow_html=True)

                if abs(grand_collected - grand) > 0.05:
                    st.warning(f"Rounding diff: Bill ₹{grand:.2f} vs Split ₹{grand_collected:.2f}")

                # Save to database
                st.markdown("")
                if not st.session_state.get("saved"):
                    st.markdown('<div class="save-btn">', unsafe_allow_html=True)
                    save_clicked = st.button("💾 Save to History", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if save_clicked:
                        try:
                            receipt_id = save_receipt(
                                user_email=user_email,
                                filename=uploaded_file.name,
                                upload_date=datetime.now().strftime("%Y-%m-%d"),
                                total_food=total_food,
                                gst=gst,
                                grand_total=grand,
                                num_items=len(items),
                                num_people=len(people),
                                raw_ocr_text=raw_text,
                                items=items,
                                splits_data=totals,
                                assignments=cur_assignments
                            )
                            st.session_state["saved"] = True
                            st.success(f"✅ Saved! (Receipt #{receipt_id})")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Save failed: {e}")
                else:
                    st.success("✅ Saved to history!")
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="emoji">📊</div>
                    <div class="msg">Assign items & click "Calculate Split"</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#   TAB 2: ANALYTICS
# ═══════════════════════════════════════════════════════════
with tab_analytics:
    stats = get_summary_stats(user_email)

    if stats["total_receipts"] == 0:
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">📊</div>
            <div class="msg">No data yet</div>
            <div class="sub">Split a bill and save it to see analytics</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Summary Stats ────────────────────────────────
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats['total_receipts']}</div>
                <div class="stat-label">Receipts</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">₹{stats['total_spent']:.0f}</div>
                <div class="stat-label">Total Spent</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">₹{stats['avg_bill']:.0f}</div>
                <div class="stat-label">Avg Bill</div>
            </div>""", unsafe_allow_html=True)
        with s4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats['unique_people']}</div>
                <div class="stat-label">People</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # ── Charts Row 1 ────────────────────────────────
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown('<div class="chart-title">📈 Spending Over Time</div>', unsafe_allow_html=True)
            fig = create_spending_trend_chart(user_email)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch2:
            st.markdown('<div class="chart-title">👥 Per-Person Spending</div>', unsafe_allow_html=True)
            fig = create_person_spending_chart(user_email)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── Charts Row 2 ────────────────────────────────
        ch3, ch4, ch5 = st.columns([1.2, 0.8, 1])

        with ch3:
            st.markdown('<div class="chart-title">🏆 Most Ordered Items</div>', unsafe_allow_html=True)
            fig = create_top_items_chart(user_email)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch4:
            st.markdown('<div class="chart-title">🍕 Food vs Tax</div>', unsafe_allow_html=True)
            fig = create_spending_breakdown_pie(user_email)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch5:
            st.markdown('<div class="chart-title">📊 Bill Distribution</div>', unsafe_allow_html=True)
            fig = create_bill_distribution_chart(user_email)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════
#   TAB 3: HISTORY
# ═══════════════════════════════════════════════════════════
with tab_history:
    receipts = get_all_receipts(user_email)

    if not receipts:
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">📋</div>
            <div class="msg">No splits yet</div>
            <div class="sub">Split a bill and save it to build your history</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-label">{len(receipts)} receipt(s) saved</div>', unsafe_allow_html=True)

        for receipt in receipts:
            st.markdown(f"""
            <div class="history-card">
                <div class="history-header">
                    <span class="history-file">📄 {receipt['filename']}</span>
                    <span class="history-date">{receipt['upload_date']}</span>
                </div>
                <div class="history-stats">
                    <span>{receipt['num_items']} items</span>
                    <span>{receipt['num_people']} people</span>
                    <span>GST: ₹{receipt['gst']:.2f}</span>
                    <span class="history-amount">₹{receipt['grand_total']:.2f}</span>
                    <span class="history-badge">Settled</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expandable details
            with st.expander(f"View details — Receipt #{receipt['id']}", expanded=False):
                details = get_receipt_details(receipt["id"], user_email)

                if not details:
                    st.error("Receipt not found or you don't have permission.")
                    continue

                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    st.markdown("**Items:**")
                    for it in details["items"]:
                        st.write(f"- {it['item_name']} ×{it['quantity']} — ₹{it['total_price']}")

                with dcol2:
                    st.markdown("**Split:**")
                    for sp in details["splits"]:
                        gst_txt = f" + ₹{sp['gst_amount']:.2f} GST" if sp["gst_amount"] > 0 else ""
                        st.write(f"- **{sp['person_name']}**: ₹{sp['total_amount']:.2f} (food ₹{sp['food_amount']:.2f}{gst_txt})")

                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button(f"🗑️ Delete", key=f"del_{receipt['id']}"):
                    delete_receipt(receipt["id"], user_email)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)