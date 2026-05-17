import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import (
    get_spending_over_time,
    get_per_person_spending,
    get_top_items,
    get_summary_stats,
    get_all_receipts
)


def create_spending_trend_chart(user_email):
    """Line chart of spending over time."""
    data = get_spending_over_time(user_email)
    if not data:
        return None

    df = pd.DataFrame(data)
    df["upload_date"] = pd.to_datetime(df["upload_date"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["upload_date"],
        y=df["total"],
        mode="lines+markers",
        name="Total Spent",
        line=dict(color="#7C3AED", width=3),
        marker=dict(size=8, color="#A78BFA"),
        fill="tozeroy",
        fillcolor="rgba(124, 58, 237, 0.1)"
    ))

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Amount (₹)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    return fig


def create_person_spending_chart(user_email):
    """Horizontal bar chart of per-person spending."""
    data = get_per_person_spending(user_email)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["person_name"],
        x=df["total_food"],
        name="Food",
        orientation="h",
        marker_color="#7C3AED"
    ))
    fig.add_trace(go.Bar(
        y=df["person_name"],
        x=df["total_gst"],
        name="GST",
        orientation="h",
        marker_color="#F59E0B"
    ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Total Spent (₹)",
        yaxis_title=None,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
        height=max(200, len(data) * 50 + 80),
        margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    return fig


def create_top_items_chart(user_email):
    """Bar chart of most ordered items."""
    data = get_top_items(user_email, 10)
    if not data:
        return None

    df = pd.DataFrame(data)
    df = df.sort_values("total_qty", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["item_name"],
        x=df["total_qty"],
        orientation="h",
        marker=dict(
            color=df["total_qty"],
            colorscale=[[0, "#7C3AED"], [1, "#06B6D4"]],
        ),
        text=df["total_qty"],
        textposition="auto",
        textfont=dict(color="white", size=11)
    ))

    fig.update_layout(
        xaxis_title="Times Ordered",
        yaxis_title=None,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
        height=max(250, len(data) * 35 + 80),
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    return fig


def create_spending_breakdown_pie(user_email):
    """Pie chart of food vs GST breakdown."""
    stats = get_summary_stats(user_email)
    if stats["total_receipts"] == 0:
        return None

    food = stats["total_spent"] - stats["total_gst"]
    gst = stats["total_gst"]

    fig = go.Figure(data=[go.Pie(
        labels=["Food & Drinks", "GST / Tax"],
        values=[food, gst],
        hole=0.55,
        marker=dict(colors=["#7C3AED", "#F59E0B"]),
        textinfo="label+percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>₹%{value:.2f}<br>%{percent}<extra></extra>"
    )])

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        annotations=[dict(
            text=f"₹{food + gst:.0f}",
            x=0.5, y=0.5,
            font_size=18, font_color="#e2e8f0", font_family="Inter",
            showarrow=False
        )]
    )
    return fig


def create_bill_distribution_chart(user_email):
    """Histogram of bill amounts."""
    receipts = get_all_receipts(user_email)
    if not receipts:
        return None

    df = pd.DataFrame(receipts)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["grand_total"],
        nbinsx=15,
        marker_color="#7C3AED",
        opacity=0.8
    ))

    fig.update_layout(
        xaxis_title="Bill Amount (₹)",
        yaxis_title="Frequency",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
        height=250,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    return fig
