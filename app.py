import streamlit as st
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

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="SplitWise AI — Smart Bill Splitter",
    page_icon="💸",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.2rem 2rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-title { font-size: 1.8rem; font-weight: 800; color: white; margin: 0; }
    .hero-sub { font-size: 0.85rem; color: rgba(255,255,255,0.8); margin-top: 0.2rem; }

    /* Column header */
    .col-header {
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1.2px; color: #a5b4fc; margin-bottom: 0.8rem;
        padding-bottom: 0.5rem; border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }

    /* Section label */
    .section-label { font-size: 0.95rem; font-weight: 700; color: #e2e8f0; margin: 0.8rem 0 0.5rem 0; }

    /* Item row */
    .item-row {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px; padding: 0.55rem 0.9rem; margin-bottom: 0.35rem;
        display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;
    }
    .item-row:hover { border-color: rgba(102, 126, 234, 0.3); background: rgba(255,255,255,0.06); }
    .item-name { font-weight: 600; color: #e2e8f0; }
    .item-right { display: flex; gap: 0.5rem; align-items: center; }
    .qty-badge {
        background: rgba(102, 126, 234, 0.2); color: #a5b4fc;
        padding: 0.12rem 0.45rem; border-radius: 6px; font-size: 0.68rem; font-weight: 700;
    }
    .item-price { font-weight: 700; color: #a5b4fc; min-width: 50px; text-align: right; }

    /* GST row */
    .gst-row {
        background: rgba(234, 179, 8, 0.08); border: 1px solid rgba(234, 179, 8, 0.2);
        border-radius: 10px; padding: 0.55rem 0.9rem; margin-top: 0.4rem;
        display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;
    }
    .gst-label { font-weight: 600; color: #fbbf24; }
    .gst-amount { font-weight: 700; color: #fbbf24; }

    /* Total pill */
    .total-pill {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px; padding: 0.7rem 1rem; margin-top: 0.6rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .total-pill-label { font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; }
    .total-pill-amount { font-size: 1.2rem; font-weight: 800; color: white; }

    /* Result card */
    .result-card {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 1rem; margin-bottom: 0.6rem;
        transition: all 0.3s ease;
    }
    .result-card:hover { border-color: rgba(102, 126, 234, 0.35); box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1); }
    .result-person { font-size: 0.82rem; font-weight: 600; color: #cbd5e1; margin-bottom: 0.4rem; }
    .result-total {
        font-size: 1.5rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.3rem;
    }
    .result-detail { font-size: 0.7rem; color: rgba(255,255,255,0.4); line-height: 1.4; }
    .result-detail span { color: #fbbf24; font-weight: 600; }

    /* Grand total */
    .grand-total {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 14px; padding: 0.8rem 1.2rem; text-align: center;
        margin-top: 0.8rem; box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
    }
    .grand-label { font-size: 0.65rem; color: rgba(255,255,255,0.7); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .grand-amount { font-size: 1.6rem; font-weight: 800; color: white; }

    /* Stat card */
    .stat-card {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 1.2rem; text-align: center;
    }
    .stat-value {
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 0.3rem; font-weight: 500; }

    /* Chart section */
    .chart-title { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; margin: 1rem 0 0.5rem 0; }

    /* History card */
    .history-card {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
        transition: all 0.3s ease;
    }
    .history-card:hover { border-color: rgba(102, 126, 234, 0.3); }
    .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; }
    .history-date { font-size: 0.72rem; color: rgba(255,255,255,0.4); }
    .history-file { font-weight: 600; color: #e2e8f0; font-size: 0.9rem; }
    .history-stats { display: flex; gap: 1rem; font-size: 0.75rem; color: rgba(255,255,255,0.5); }
    .history-amount { font-weight: 700; color: #a5b4fc; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important; font-weight: 700 !important;
        font-size: 0.85rem !important; transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important; }

    /* Inputs */
    [data-testid="stFileUploader"] { border: 2px dashed rgba(102, 126, 234, 0.3); border-radius: 12px; padding: 0.5rem; }
    [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {
        border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(255,255,255,0.04) !important; font-size: 0.82rem !important;
    }
    [data-testid="stSelectbox"] > div > div { border-radius: 8px !important; }
    .stAlert { border-radius: 10px !important; font-size: 0.8rem !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important; padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
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
        <div style="text-align:center; padding:2.5rem 1rem; color:rgba(255,255,255,0.3);">
            <div style="font-size:2.5rem; margin-bottom:0.4rem;">📸</div>
            <div style="font-size:0.95rem; font-weight:500;">Upload a receipt image to get started</div>
            <div style="font-size:0.75rem; margin-top:0.2rem;">Supports JPG, JPEG, PNG</div>
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
        col_left, col_mid, col_right = st.columns([1, 1.5, 1.3], gap="large")

        # ═══ LEFT: Receipt & Items ═══
        with col_left:
            st.markdown('<div class="col-header">📸 Receipt</div>', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)

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

                st.markdown(f"**{item['item']}** — ₹{item['price']} (×{qty})")

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
                    items_text = ", ".join([it["item"] for it in person_items]) if person_items else "—"
                    gst_text = f" + <span>₹{breakdown['gst']:.2f} GST</span>" if breakdown["gst"] > 0 else ""

                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-person">{person}</div>
                        <div class="result-total">₹{breakdown['total']:.2f}</div>
                        <div class="result-detail">
                            Food: ₹{breakdown['food']:.2f}{gst_text}<br>{items_text}
                        </div>
                    </div>""", unsafe_allow_html=True)
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
                    if st.button("💾 Save to History", use_container_width=True):
                        try:
                            receipt_id = save_receipt(
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
                <div style="text-align:center; padding:2.5rem 1rem; color:rgba(255,255,255,0.25);">
                    <div style="font-size:2.2rem; margin-bottom:0.4rem;">📊</div>
                    <div style="font-size:0.85rem; font-weight:500;">Assign items & click "Calculate Split"</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#   TAB 2: ANALYTICS
# ═══════════════════════════════════════════════════════════
with tab_analytics:
    stats = get_summary_stats()

    if stats["total_receipts"] == 0:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem; color:rgba(255,255,255,0.3);">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">📊</div>
            <div style="font-size:1rem; font-weight:500;">No data yet</div>
            <div style="font-size:0.8rem; margin-top:0.3rem;">Split a bill and save it to see analytics</div>
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
            fig = create_spending_trend_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch2:
            st.markdown('<div class="chart-title">👥 Per-Person Spending</div>', unsafe_allow_html=True)
            fig = create_person_spending_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── Charts Row 2 ────────────────────────────────
        ch3, ch4, ch5 = st.columns([1.2, 0.8, 1])

        with ch3:
            st.markdown('<div class="chart-title">🏆 Most Ordered Items</div>', unsafe_allow_html=True)
            fig = create_top_items_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch4:
            st.markdown('<div class="chart-title">🍕 Food vs Tax</div>', unsafe_allow_html=True)
            fig = create_spending_breakdown_pie()
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch5:
            st.markdown('<div class="chart-title">📊 Bill Distribution</div>', unsafe_allow_html=True)
            fig = create_bill_distribution_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════
#   TAB 3: HISTORY
# ═══════════════════════════════════════════════════════════
with tab_history:
    receipts = get_all_receipts()

    if not receipts:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem; color:rgba(255,255,255,0.3);">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">📁</div>
            <div style="font-size:1rem; font-weight:500;">No receipts saved yet</div>
            <div style="font-size:0.8rem; margin-top:0.3rem;">Split a bill and save it to build your history</div>
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
                    <span class="history-amount">Total: ₹{receipt['grand_total']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expandable details
            with st.expander(f"View details — Receipt #{receipt['id']}", expanded=False):
                details = get_receipt_details(receipt["id"])

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

                if st.button(f"🗑️ Delete", key=f"del_{receipt['id']}"):
                    delete_receipt(receipt["id"])
                    st.rerun()