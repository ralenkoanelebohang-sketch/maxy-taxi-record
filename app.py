"""
Maxy Taxi Transport - Business Records App
Daily / Weekly / Monthly records + Quotations + Invoices
Mobile-friendly web app (add to Android home screen)
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="MAXY TAXI | Business Records",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra professional dark theme matching Maxy Taxi brand (black + gold yellow)
st.markdown("""
<style>
    /* ===== GLOBAL ===== */
    .stApp {
        background: linear-gradient(160deg, #0a0a0a 0%, #121212 40%, #0d0d0d 100%);
        color: #e8e8e8;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #f5a623 !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px;
    }
    p, label, span, .stMarkdown { color: #d0d0d0; }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0c0c 0%, #161616 100%) !important;
        border-right: 2px solid #f5a62333;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #c8c8c8 !important;
        font-weight: 500;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        margin: 2px 0 !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #f5a623 !important;
        background: #f5a62315 !important;
    }
    /* Selected menu item - yellow glow like screenshot */
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 15px !important;
    }
    div[role="radiogroup"] label[data-baseweb="radio"] {
        background: transparent;
        border-radius: 10px;
        padding: 6px 10px;
        margin: 3px 0;
    }
    /* Active/selected styling */
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
        background: #f5a62318 !important;
        border: 1px solid #f5a62388 !important;
        box-shadow: 0 0 12px #f5a62344;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
        color: #f5a623 !important;
        font-weight: 600 !important;
    }

    /* ===== METRICS (cards) ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1a1a1a, #141414);
        border: 1px solid #2a2a2a;
        border-left: 4px solid #f5a623;
        border-radius: 10px;
        padding: 12px 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #f5a623 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.8px;
    }

    /* ===== BUTTONS ===== */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f5a623, #e09400) !important;
        color: #0a0a0a !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(245,166,35,0.35);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ffb83d, #f5a623) !important;
        box-shadow: 0 4px 14px rgba(245,166,35,0.5);
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background: #1f1f1f !important;
        color: #f5a623 !important;
        border: 1px solid #f5a62355 !important;
        border-radius: 8px !important;
    }

    /* ===== INPUTS ===== */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div,
    .stDateInput input, .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #f0f0f0 !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #f5a623 !important;
        box-shadow: 0 0 0 1px #f5a62355 !important;
    }
    /* Hide +/- steppers on number inputs */
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-testid="stNumberInput"] > div > div > div:last-child { display: none !important; }

    /* Red highlight strip for main daily entry fields */
    .maxy-red-box {
        border: 1.5px solid #e74c3c !important;
        border-radius: 10px !important;
        padding: 8px 10px !important;
        margin-bottom: 8px !important;
        background: #1a0a0a !important;
    }

    /* ===== DATAFRAMES / TABLES ===== */
    .stDataFrame {
        border: 1px solid #2a2a2a !important;
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    }
    .stDataFrame thead tr th {
        background: #1c1c1c !important;
        color: #f5a623 !important;
        font-weight: 700 !important;
    }
    .stDataFrame tbody tr {
        background: #141414 !important;
        color: #e0e0e0 !important;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background: #1a1a1a !important;
    }

    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background: #1a1a1a !important;
        border-radius: 8px !important;
        border: 1px solid #2a2a2a !important;
        color: #f5a623 !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background: #141414 !important;
        border: 1px solid #2a2a2a !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* ===== TABS / RADIO ===== */
    .stRadio > div { gap: 0.4rem; }

    /* ===== ALERTS ===== */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px !important;
    }

    /* ===== DIVIDERS ===== */
    hr {
        border: none !important;
        border-top: 1px solid #2a2a2a !important;
        margin: 1.2rem 0 !important;
    }

    /* ===== CAPTIONS ===== */
    .stCaption, small { color: #888 !important; }

    /* ===== DOWNLOAD BUTTONS ===== */
    .stDownloadButton > button {
        background: #1f1f1f !important;
        color: #f5a623 !important;
        border: 1px solid #f5a62366 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background: #f5a62322 !important;
        border-color: #f5a623 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== PASSWORD PROTECTION ==========
APP_PASSWORD = "MaxyTaxi2026"

def check_password():
    """Returns True if the user entered the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #1a1a1a, #111);
                    border: 1px solid #f5a62355; border-radius: 16px;
                    padding: 28px 22px 18px 22px; box-shadow: 0 8px 32px rgba(0,0,0,0.55);">
        """, unsafe_allow_html=True)
        logo_dark = os.path.join(os.path.dirname(__file__), "logo_on_black.jpg")
        logo_trans = os.path.join(os.path.dirname(__file__), "logo_transparent.png")
        logo_clean = os.path.join(os.path.dirname(__file__), "logo_clean.png")
        if os.path.exists(logo_dark):
            st.image(logo_dark, use_container_width=True)
        elif os.path.exists(logo_trans):
            st.image(logo_trans, use_container_width=True)
        elif os.path.exists(logo_clean):
            st.image(logo_clean, use_container_width=True)
        st.markdown("""
            <p style='text-align:center; color:#f5a623; font-size:11px; letter-spacing:2.5px;
                       margin: 10px 0 2px 0; font-weight:600;'>SAFE • QUICK • RELIABLE</p>
            <p style='text-align:center; color:#777; font-size:13px; margin: 14px 0 4px 0;'>Business Records Login</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="password_input",
                                 label_visibility="collapsed", placeholder="Enter password")
        if st.button("Login", type="primary", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
    st.stop()

# Run password check first
check_password()
# =========================================

DB_PATH = "maxy_taxi.db"
BUSINESS_NAME = "Maxy Taxi Transport"
BUSINESS_TAGLINE = "SAFE • QUICK • RELIABLE"
BUSINESS_LOCATION = "Puma House 12 United Nations Road, Maseru"
BUSINESS_PHONE = "+266 27333388 / 68335933"
BUSINESS_WHATSAPP = "+266 56432571"
BUSINESS_EMAIL = "maxytaxicab@gmail.com"
BUSINESS_TIN = ""            # Add your TIN later if needed
CURRENCY = "M"

# Monthly credit clients
CREDIT_CLIENTS = ["Alliance", "Lehae", "World Vision", "Waleslink", "LNLVIP"]

VEHICLES = [
    {"id": 1, "name": "Honda Fit 1", "plate": "A 940 BDL", "type": "Honda Fit"},
    {"id": 2, "name": "Honda Fit 2", "plate": "A 943 BDL", "type": "Honda Fit"},
    {"id": 3, "name": "Honda Fit 3", "plate": "A 945 BDL", "type": "Honda Fit"},
    {"id": 4, "name": "Honda Fit 4", "plate": "A 238 BGN", "type": "Honda Fit"},
    {"id": 5, "name": "Honda Fit 5", "plate": "A 765 BGR", "type": "Honda Fit"},
    {"id": 6, "name": "Toyota Alphard", "plate": "A 313 BCM", "type": "Alphard 7-seater"},
]

# Default driver per vehicle (auto-fills on Daily Entry; editable if driver changes car)
# Update these names anytime — the form will use them, or the last driver saved for that car
DEFAULT_DRIVERS = {
    "Honda Fit 1": "",
    "Honda Fit 2": "",
    "Honda Fit 3": "",
    "Honda Fit 4": "",
    "Honda Fit 5": "",
    "Toyota Alphard": "",
}

# ---------------------- DATABASE (SQLite local OR free cloud Postgres) ----------------------
@st.cache_resource
def _database_url_cached():
    """Cache secrets lookup — avoids re-reading on every query."""
    try:
        url = st.secrets.get("DATABASE_URL", None)
        if url:
            return str(url)
        if "postgres" in st.secrets and "url" in st.secrets["postgres"]:
            return str(st.secrets["postgres"]["url"])
    except Exception:
        pass
    return None


def _database_url():
    return _database_url_cached()


def using_cloud_db():
    return _database_url() is not None


def _adapt_sql(sql):
    """Convert SQLite-style ? placeholders to %s for Postgres."""
    if using_cloud_db():
        return sql.replace("?", "%s")
    return sql


# Track pooled connections by id (psycopg2 disallows arbitrary attributes on conn)
_POOLED_CONN_IDS = set()


@st.cache_resource
def _pg_pool():
    """Reuse a small connection pool — big speed win vs new SSL connect every query."""
    url = _database_url()
    if not url:
        return None
    try:
        from psycopg2 import pool as pg_pool
        return pg_pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=4,
            dsn=url,
            sslmode="require",
            connect_timeout=8,
        )
    except Exception:
        return None


def get_conn():
    url = _database_url()
    if url:
        import psycopg2
        p = _pg_pool()
        if p is not None:
            try:
                conn = p.getconn()
                try:
                    conn.autocommit = False
                except Exception:
                    pass
                _POOLED_CONN_IDS.add(id(conn))
                return conn
            except Exception:
                pass
        conn = psycopg2.connect(url, sslmode="require", connect_timeout=8)
        try:
            conn.autocommit = False
        except Exception:
            pass
        return conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def release_conn(conn):
    """Return pooled connection or close."""
    if conn is None:
        return
    try:
        cid = id(conn)
        if cid in _POOLED_CONN_IDS:
            _POOLED_CONN_IDS.discard(cid)
            p = _pg_pool()
            if p is not None:
                try:
                    p.putconn(conn)
                    return
                except Exception:
                    pass
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def clear_data_cache():
    """Call after any insert/update/delete so screens refresh."""
    try:
        load_all_records.clear()
    except Exception:
        pass


@st.cache_resource
def _init_db_once():
    """Run table setup only once per server process — avoids slow startup every click."""
    _init_db_impl()
    return True


def init_db():
    _init_db_once()


def _init_db_impl():
    conn = get_conn()
    c = conn.cursor()
    cloud = using_cloud_db()

    # Postgres: use autocommit so a failed ALTER does not abort later CREATE TABLE
    if cloud:
        try:
            conn.set_session(autocommit=True)
        except Exception:
            try:
                conn.autocommit = True
            except Exception:
                pass

    def run_sql(sql):
        try:
            c.execute(sql)
            if not cloud:
                conn.commit()
            return True
        except Exception:
            if not cloud:
                try:
                    conn.rollback()
                except Exception:
                    pass
            else:
                # With autocommit each statement is independent
                pass
            return False

    # Compatible DDL for SQLite and Postgres
    if cloud:
        id_col = "id SERIAL PRIMARY KEY"
        real_type = "DOUBLE PRECISION"
    else:
        id_col = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        real_type = "REAL"

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS daily_records (
            {id_col},
            record_date TEXT NOT NULL,
            vehicle_id INTEGER NOT NULL,
            vehicle_name TEXT,
            plate TEXT,
            cash_collected {real_type} DEFAULT 0,
            fuel_cost {real_type} DEFAULT 0,
            fuel_topup {real_type} DEFAULT 0,
            trips INTEGER DEFAULT 0,
            other_expenses {real_type} DEFAULT 0,
            expense_notes TEXT,
            driver_compensation {real_type} DEFAULT 40.0,
            credit_alliance {real_type} DEFAULT 0,
            credit_lehae {real_type} DEFAULT 0,
            credit_worldvision {real_type} DEFAULT 0,
            credit_waleslink {real_type} DEFAULT 0,
            credit_lnlvip {real_type} DEFAULT 0,
            driver_name TEXT,
            airtime {real_type} DEFAULT 10,
            duty TEXT DEFAULT 'Day',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add columns if missing (safe on both SQLite and Postgres)
    for col, default in [
        ("credit_alliance", "0"), ("credit_lehae", "0"), ("credit_worldvision", "0"),
        ("credit_waleslink", "0"), ("credit_lnlvip", "0"), ("fuel_topup", "0"),
        ("driver_compensation", "40"), ("airtime", "10"),
    ]:
        run_sql(f"ALTER TABLE daily_records ADD COLUMN {col} {real_type} DEFAULT {default}")
    run_sql("ALTER TABLE daily_records ADD COLUMN duty TEXT DEFAULT 'Day'")

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS clients (
            {id_col},
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            tin TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS quotations (
            {id_col},
            quote_number TEXT UNIQUE,
            client_id INTEGER,
            client_name TEXT,
            quote_date TEXT,
            valid_until TEXT,
            description TEXT,
            amount {real_type},
            status TEXT DEFAULT 'Draft',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS invoices (
            {id_col},
            invoice_number TEXT UNIQUE,
            client_id INTEGER,
            client_name TEXT,
            invoice_date TEXT,
            due_date TEXT,
            description TEXT,
            amount {real_type},
            amount_paid {real_type} DEFAULT 0,
            status TEXT DEFAULT 'Unpaid',
            related_quote_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Fixed monthly business expenses (rent, wifi, maintenance, salaries)
    run_sql(f"""
        CREATE TABLE IF NOT EXISTS monthly_expenses (
            {id_col},
            expense_month TEXT NOT NULL,
            rent {real_type} DEFAULT 0,
            wifi {real_type} DEFAULT 0,
            maintenance {real_type} DEFAULT 0,
            salaries {real_type} DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        if not cloud:
            conn.commit()
    except Exception:
        pass
    release_conn(conn)

def query_df(sql, params=()):
    conn = get_conn()
    sql = _adapt_sql(sql)
    try:
        df = pd.read_sql_query(sql, conn, params=params if params else None)
    finally:
        release_conn(conn)
    return df


def execute(sql, params=()):
    conn = get_conn()
    try:
        c = conn.cursor()
        sql = _adapt_sql(sql)
        c.execute(sql, params)
        conn.commit()
        last_id = None
        try:
            last_id = c.lastrowid
        except Exception:
            last_id = None
    finally:
        release_conn(conn)
    clear_data_cache()
    return last_id


@st.cache_data(ttl=60, show_spinner=False)
def load_all_records():
    """Cached full daily_records pull — speeds up Dashboard / Records / Fleet."""
    return query_df("SELECT * FROM daily_records")

# ---------------------- PDF HELPERS ----------------------
def create_pdf_buffer():
    buffer = BytesIO()
    return buffer

def generate_invoice_pdf(invoice, client=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=12*mm, leftMargin=12*mm,
                            topMargin=5*mm, bottomMargin=22*mm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER,
        spaceAfter=1*mm, textColor=colors.HexColor("#1a1a1a")
    )
    subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"), spaceAfter=1*mm
    )
    heading = ParagraphStyle(
        'Heading', parent=styles['Heading2'], fontSize=10, spaceBefore=2*mm, spaceAfter=1*mm
    )
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, leading=12)
    right = ParagraphStyle('Right', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, leading=12)

    # Letterhead banner + yellow bottom border
    header_path = os.path.join(os.path.dirname(__file__), "letterhead_header.png")
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(header_path):
        header = Image(header_path, width=186*mm, height=38*mm)
        header.hAlign = 'CENTER'
        elements.append(header)
    elif os.path.exists(logo_path):
        logo = Image(logo_path, width=70*mm, height=22*mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph(f"{BUSINESS_PHONE}  |  {BUSINESS_WHATSAPP}  |  {BUSINESS_EMAIL}", subtitle))
    else:
        elements.append(Paragraph("MAXY TAXI", title_style))
        elements.append(Paragraph("SAFE • QUICK • RELIABLE", subtitle))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#f5a623"), spaceBefore=1*mm, spaceAfter=4*mm))

    elements.append(Paragraph("INVOICE", ParagraphStyle('InvTitle', parent=styles['Heading1'],
                                                         fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
                                                         spaceAfter=2*mm)))
    elements.append(Spacer(1, 2*mm))

    # Meta info (Invoice No + Date only)
    meta_data = [
        [Paragraph(f"<b>Invoice No:</b> {invoice['invoice_number']}", normal),
         Paragraph(f"<b>Date:</b> {invoice['invoice_date']}", right)],
    ]
    meta_table = Table(meta_data, colWidths=[95*mm, 85*mm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 5*mm))

    # Invoice To
    elements.append(Paragraph("<b>INVOICE TO</b>", heading))
    client_name = invoice.get('client_name') or (client['name'] if client else "Cash / Walk-in")
    elements.append(Paragraph(client_name, normal))
    if client:
        if client.get('contact_person'):
            elements.append(Paragraph(f"Attn: {client['contact_person']}", normal))
        if client.get('phone'):
            elements.append(Paragraph(f"Phone: {client['phone']}", normal))
        if client.get('address'):
            elements.append(Paragraph(client['address'], normal))
        if client.get('tin'):
            elements.append(Paragraph(f"TIN: {client['tin']}", normal))
    elements.append(Spacer(1, 5*mm))

    # DESCRIPTION | QTY | AMOUNT table (no "Cost Breakdown" title)
    desc = invoice.get('description') or "Transport services"
    amount = float(invoice.get('amount') or 0)

    def _is_blank(v):
        s = str(v).strip().lower() if v is not None else ""
        return s in ("", "null", "none", "nan")

    lines = [ln.strip() for ln in str(desc).split("\n") if ln.strip()]
    header_style = ParagraphStyle('TH', parent=bold, textColor=colors.HexColor("#1a1a1a"))
    items_data = [
        [Paragraph("<b>DESCRIPTION</b>", header_style),
         Paragraph("<b>QTY</b>", header_style),
         Paragraph("<b>AMOUNT</b>", header_style)],
    ]

    parsed_total = 0.0
    has_breakdown = False
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        # Skip empty / null description rows
        if not parts or _is_blank(parts[0]):
            continue
        if len(parts) >= 3:
            if _is_blank(parts[2]):
                continue
            try:
                amt = float(parts[2].replace("M", "").replace(",", "").strip())
            except Exception:
                amt = 0.0
            if amt == 0 and _is_blank(parts[1]):
                continue
            has_breakdown = True
            parsed_total += amt
            qty = "" if _is_blank(parts[1]) else parts[1]
            items_data.append([
                Paragraph(parts[0], normal),
                Paragraph(qty, normal),
                Paragraph(f"M{amt:,.2f}", right),
            ])
        elif len(parts) == 2:
            if _is_blank(parts[1]):
                continue
            try:
                amt = float(parts[1].replace("M", "").replace(",", "").strip())
            except Exception:
                amt = 0.0
            has_breakdown = True
            parsed_total += amt
            items_data.append([
                Paragraph(parts[0], normal),
                Paragraph("", normal),
                Paragraph(f"M{amt:,.2f}", right),
            ])
        else:
            items_data.append([
                Paragraph(ln, normal),
                Paragraph("", normal),
                Paragraph("", right),
            ])

    # Spacing rows only if there is content
    for _ in range(2):
        items_data.append([Paragraph("<br/>", normal), Paragraph("", normal), Paragraph("", right)])

    total_amount = parsed_total if has_breakdown and parsed_total > 0 else amount
    items_data.append([
        Paragraph("", normal),
        Paragraph("<b>TOTAL</b>", bold),
        Paragraph(f"<b>M{total_amount:,.2f}</b>", ParagraphStyle('TotR', parent=right, fontSize=10)),
    ])

    items_table = Table(items_data, colWidths=[105*mm, 28*mm, 47*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f5a623")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        # No grid lines — clean professional look
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))

    # Banking details
    elements.append(Paragraph("<b>BANKING DETAILS</b>", heading))
    bank_style = ParagraphStyle('Bank', parent=normal, fontSize=9, leading=12)
    elements.append(Paragraph("<b>Bank:</b> Postbank &nbsp;&nbsp; <b>Account No:</b> 1017866800015 &nbsp;&nbsp; <b>Branch:</b> 500100", bank_style))
    elements.append(Paragraph("<b>Account Name:</b> Maxy Taxi Transport", bank_style))

    # Footer fixed at the very bottom of every page
    def _draw_inv_footer(canvas, doc_):
        canvas.saveState()
        page_w, _ = A4
        canvas.setStrokeColor(colors.HexColor("#f5a623"))
        canvas.setLineWidth(0.8)
        canvas.line(12*mm, 16*mm, page_w - 12*mm, 16*mm)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor("#1a1a1a"))
        canvas.drawCentredString(page_w/2, 10*mm, "Thank you for your Business")
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(page_w/2, 5.5*mm, "SAFE  •  QUICK  •  RELIABLE")
        canvas.restoreState()

    doc.build(elements, onFirstPage=_draw_inv_footer, onLaterPages=_draw_inv_footer)
    buffer.seek(0)
    return buffer

def generate_quotation_pdf(quote, client=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=12*mm, leftMargin=12*mm,
                            topMargin=5*mm, bottomMargin=22*mm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER,
                                 spaceAfter=1*mm, textColor=colors.HexColor("#1a1a1a"))
    subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER,
                              textColor=colors.HexColor("#555555"), spaceAfter=1*mm)
    heading = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=10, spaceBefore=2*mm, spaceAfter=1*mm)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, leading=12)
    right = ParagraphStyle('Right', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9)

    # Letterhead banner + yellow bottom border
    header_path = os.path.join(os.path.dirname(__file__), "letterhead_header.png")
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(header_path):
        header = Image(header_path, width=186*mm, height=38*mm)
        header.hAlign = 'CENTER'
        elements.append(header)
    elif os.path.exists(logo_path):
        logo = Image(logo_path, width=70*mm, height=22*mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph(f"{BUSINESS_PHONE}  |  {BUSINESS_WHATSAPP}  |  {BUSINESS_EMAIL}", subtitle))
    else:
        elements.append(Paragraph("MAXY TAXI", title_style))
        elements.append(Paragraph("SAFE • QUICK • RELIABLE", subtitle))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#f5a623"), spaceBefore=1*mm, spaceAfter=4*mm))

    elements.append(Paragraph("QUOTATION", ParagraphStyle('QTitle', parent=styles['Heading1'],
                                                           fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
                                                           spaceAfter=2*mm)))
    elements.append(Spacer(1, 2*mm))

    # Only Quote No and Date (no Status / Valid Until)
    meta_data = [
        [Paragraph(f"<b>Quote No:</b> {quote['quote_number']}", normal),
         Paragraph(f"<b>Date:</b> {quote['quote_date']}", right)],
    ]
    meta_table = Table(meta_data, colWidths=[95*mm, 85*mm])
    meta_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 5*mm))

    elements.append(Paragraph("<b>PREPARED FOR</b>", heading))
    client_name = quote.get('client_name') or (client['name'] if client else "Prospective Client")
    elements.append(Paragraph(client_name, normal))
    if client:
        if client.get('contact_person'):
            elements.append(Paragraph(f"Attn: {client['contact_person']}", normal))
        if client.get('phone'):
            elements.append(Paragraph(f"Phone: {client['phone']}", normal))
        if client.get('address'):
            elements.append(Paragraph(client['address'], normal))
    elements.append(Spacer(1, 5*mm))

    desc = quote.get('description') or "Transport services"
    amount = float(quote.get('amount') or 0)

    def _is_blank(v):
        s = str(v).strip().lower() if v is not None else ""
        return s in ("", "null", "none", "nan")

    lines = [ln.strip() for ln in str(desc).split("\n") if ln.strip()]
    header_style = ParagraphStyle('QTH', parent=bold, textColor=colors.HexColor("#1a1a1a"))
    items_data = [
        [Paragraph("<b>DESCRIPTION</b>", header_style),
         Paragraph("<b>QTY</b>", header_style),
         Paragraph("<b>AMOUNT</b>", header_style)],
    ]
    parsed_total = 0.0
    has_breakdown = False
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        if not parts or _is_blank(parts[0]):
            continue
        if len(parts) >= 3:
            if _is_blank(parts[2]):
                continue
            try:
                amt = float(parts[2].replace("M", "").replace(",", "").strip())
            except Exception:
                amt = 0.0
            has_breakdown = True
            parsed_total += amt
            qty = "" if _is_blank(parts[1]) else parts[1]
            items_data.append([
                Paragraph(parts[0], normal),
                Paragraph(qty, normal),
                Paragraph(f"M{amt:,.2f}", right),
            ])
        elif len(parts) == 2:
            if _is_blank(parts[1]):
                continue
            try:
                amt = float(parts[1].replace("M", "").replace(",", "").strip())
            except Exception:
                amt = 0.0
            has_breakdown = True
            parsed_total += amt
            items_data.append([
                Paragraph(parts[0], normal),
                Paragraph("", normal),
                Paragraph(f"M{amt:,.2f}", right),
            ])
        else:
            items_data.append([Paragraph(ln, normal), Paragraph("", normal), Paragraph("", right)])

    for _ in range(3):
        items_data.append([Paragraph("<br/>", normal), Paragraph("", normal), Paragraph("", right)])

    total_amount = parsed_total if has_breakdown and parsed_total > 0 else amount
    items_data.append([
        Paragraph("", normal),
        Paragraph("<b>TOTAL</b>", bold),
        Paragraph(f"<b>M{total_amount:,.2f}</b>", ParagraphStyle('TotR', parent=right, fontSize=10)),
    ])

    items_table = Table(items_data, colWidths=[105*mm, 28*mm, 47*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f5a623")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        # No grid lines — clean professional look
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))

    if quote.get('notes'):
        elements.append(Paragraph("<b>Notes / Terms</b>", heading))
        elements.append(Paragraph(quote['notes'], normal))

    # Footer fixed at the very bottom of every page (never mid-page)
    def _draw_quote_footer(canvas, doc_):
        canvas.saveState()
        page_w, _ = A4
        # Soft gold line above footer
        canvas.setStrokeColor(colors.HexColor("#f5a623"))
        canvas.setLineWidth(0.8)
        canvas.line(12*mm, 16*mm, page_w - 12*mm, 16*mm)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(page_w/2, 10*mm, "This quotation is valid until the date shown. Prices are in Lesotho Loti (M).")
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor("#1a1a1a"))
        canvas.drawCentredString(page_w/2, 5.5*mm, "Thank you for considering Maxy Taxi Transport.")
        canvas.restoreState()

    doc.build(elements, onFirstPage=_draw_quote_footer, onLaterPages=_draw_quote_footer)
    buffer.seek(0)
    return buffer

# ---------------------- UI HELPERS ----------------------
def money(x):
    try:
        return f"M {float(x):,.2f}"
    except:
        return "M 0.00"

def parse_amount(s, default=0.0):
    """Parse typed amount; blank → default. Whole numbers become x.00 style floats."""
    if s is None:
        return float(default)
    t = str(s).strip().replace(",", "").replace("M", "").replace("m", "")
    if t == "":
        return float(default)
    try:
        return round(float(t), 2)
    except Exception:
        return float(default)


def format_amount(x):
    """Always show two decimal places (e.g. 200 → 200.00)."""
    try:
        return f"{float(x):.2f}"
    except Exception:
        return "0.00"

def vehicle_options():
    return {f"{v['name']} ({v['plate']})": v for v in VEHICLES}

# Financial Year: June 2026 – May 2027
FY_MONTHS = [
    (2026, 6, "June 2026"),
    (2026, 7, "July 2026"),
    (2026, 8, "August 2026"),
    (2026, 9, "September 2026"),
    (2026, 10, "October 2026"),
    (2026, 11, "November 2026"),
    (2026, 12, "December 2026"),
    (2027, 1, "January 2027"),
    (2027, 2, "February 2027"),
    (2027, 3, "March 2027"),
    (2027, 4, "April 2027"),
    (2027, 5, "May 2027"),
]

def get_fy_label(dt):
    """Return FY month label for a datetime"""
    y, m = dt.year, dt.month
    for fy_y, fy_m, label in FY_MONTHS:
        if y == fy_y and m == fy_m:
            return label
    return None

def total_credits_row(row):
    return (float(row.get('credit_alliance') or 0) +
            float(row.get('credit_lehae') or 0) +
            float(row.get('credit_worldvision') or 0) +
            float(row.get('credit_waleslink') or 0) +
            float(row.get('credit_lnlvip') or 0))

def prepare_records_df():
    df = load_all_records()
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['record_date'] = pd.to_datetime(df['record_date'], errors='coerce')
    df['fy_month'] = df['record_date'].apply(get_fy_label)
    df['credits'] = df.apply(total_credits_row, axis=1)
    for col, default in [
        ('fuel_topup', 0), ('driver_compensation', 0), ('airtime', 0),
        ('other_expenses', 0), ('fuel_cost', 0), ('cash_collected', 0),
    ]:
        if col not in df.columns:
            df[col] = default
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default)
    if 'duty' not in df.columns:
        df['duty'] = 'Day'
    df['duty'] = df['duty'].fillna('Day').astype(str).replace('', 'Day')
    return df

# ---------------------- PAGES ----------------------
def page_dashboard():
    # Logo header
    logo_dark = os.path.join(os.path.dirname(__file__), "logo_on_black.jpg")
    logo_trans = os.path.join(os.path.dirname(__file__), "logo_transparent.png")
    logo_clean = os.path.join(os.path.dirname(__file__), "logo_clean.png")
    col_l, col_t = st.columns([1, 3])
    with col_l:
        if os.path.exists(logo_dark):
            st.image(logo_dark, use_container_width=True)
        elif os.path.exists(logo_trans):
            st.image(logo_trans, use_container_width=True)
        elif os.path.exists(logo_clean):
            st.image(logo_clean, use_container_width=True)
    with col_t:
        st.header("Dashboard")
        st.caption("Financial Year 2026 – 2027 (June to May)")

    df = prepare_records_df()
    today = date.today()

    # Quick today / week cards
    if not df.empty:
        today_df = df[df['record_date'].dt.date == today]
        week_start = today - timedelta(days=today.weekday())
        week_df = df[df['record_date'].dt.date >= week_start]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Today Cash", money(today_df['cash_collected'].sum()))
        c2.metric("This Week Cash", money(week_df['cash_collected'].sum()))
        c3.metric("Today Credits", money(today_df['credits'].sum()))
        c4.metric("Today Fuel + Top-up", money(today_df['fuel_cost'].sum() + today_df['fuel_topup'].sum()))
    else:
        st.info("No daily records yet. Go to Daily Entry to start logging.")

    # ===== SELECT ONE MONTH =====
    st.subheader("Monthly Summary")
    month_options = [label for _, _, label in FY_MONTHS]
    # Default to current month if in FY, else June 2026
    default_idx = 0
    for i, (y, m, label) in enumerate(FY_MONTHS):
        if today.year == y and today.month == m:
            default_idx = i
            break
    sel_month = st.selectbox("Select month", month_options, index=default_idx)

    if df.empty:
        st.info("No data for the financial year yet.")
    else:
        y, m, _ = next((yy, mm, ll) for yy, mm, ll in FY_MONTHS if ll == sel_month)
        mdf = df[(df['record_date'].dt.year == y) & (df['record_date'].dt.month == m)]

        cash = mdf['cash_collected'].sum() if not mdf.empty else 0
        credits = mdf['credits'].sum() if not mdf.empty else 0
        fuel = mdf['fuel_cost'].sum() if not mdf.empty else 0
        topup = mdf['fuel_topup'].sum() if not mdf.empty else 0
        driver_comp = mdf['driver_compensation'].sum() if not mdf.empty else 0
        airtime = mdf['airtime'].sum() if not mdf.empty else 0
        other = mdf['other_expenses'].sum() if not mdf.empty else 0
        trips = int(mdf['trips'].sum()) if not mdf.empty else 0
        revenue = cash + credits
        expenses = fuel + topup + driver_comp + airtime + other
        net = revenue - expenses

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Cash", money(cash))
        c2.metric("Total Credits", money(credits))
        c3.metric("Total Revenue", money(revenue))
        c4.metric("Total Expenses", money(expenses))

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Fuel Cost", money(fuel))
        c6.metric("Fuel Top-up", money(topup))
        c7.metric("Driver Comp", money(driver_comp))
        c8.metric("Airtime", money(airtime))

        c9, c10, c11 = st.columns(3)
        c9.metric("Other Expenses", money(other))
        c10.metric("Trips", trips)
        c11.metric("Net", money(net))

        # Per vehicle for selected month
        if not mdf.empty:
            st.markdown(f"**{sel_month} by Vehicle**")
            by_veh = mdf.groupby('vehicle_name').agg({
                'cash_collected': 'sum',
                'credits': 'sum',
                'fuel_cost': 'sum',
                'fuel_topup': 'sum',
                'driver_compensation': 'sum',
                'airtime': 'sum',
                'other_expenses': 'sum',
                'trips': 'sum',
            }).reset_index()
            by_veh['Net'] = (by_veh['cash_collected'] + by_veh['credits']
                             - by_veh['fuel_cost'] - by_veh['fuel_topup']
                             - by_veh['driver_compensation'] - by_veh['airtime']
                             - by_veh['other_expenses'])
            by_veh.columns = ['Vehicle', 'Cash', 'Credits', 'Fuel', 'Top-up', 'Driver Comp', 'Airtime', 'Other', 'Trips', 'Net']
            st.dataframe(
                by_veh.style.format({
                    'Cash': 'M {:,.0f}', 'Credits': 'M {:,.0f}',
                    'Fuel': 'M {:,.0f}', 'Top-up': 'M {:,.0f}',
                    'Driver Comp': 'M {:,.0f}', 'Airtime': 'M {:,.0f}',
                    'Other': 'M {:,.0f}', 'Net': 'M {:,.0f}',
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"No records for {sel_month} yet.")

    # Recent invoices
    st.subheader("Recent Invoices")
    inv_df = query_df("SELECT invoice_number, client_name, invoice_date, amount, amount_paid, status FROM invoices ORDER BY id DESC LIMIT 5")
    if not inv_df.empty:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No invoices yet.")

def _auto_driver_for(vehicle_name, plate):
    """Last saved driver for this car, else DEFAULT_DRIVERS mapping."""
    try:
        df = query_df(
            "SELECT driver_name FROM daily_records WHERE plate = ? AND driver_name IS NOT NULL AND TRIM(driver_name) != '' ORDER BY id DESC LIMIT 1",
            (plate,),
        )
        if not df.empty and str(df.iloc[0]['driver_name']).strip():
            return str(df.iloc[0]['driver_name']).strip()
    except Exception:
        pass
    return DEFAULT_DRIVERS.get(vehicle_name, "")


def page_daily_entry():
    st.header("Daily Entry")
    st.caption("Type whole amounts (e.g. 200) — saved as 200.00 · max 2 entries per car per day")

    veh_dict = vehicle_options()
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        record_date = st.date_input("Date", value=date.today(), key="de_date")
    with r1c2:
        vehicle_label = st.selectbox("Vehicle", list(veh_dict.keys()), key="de_vehicle")
    vehicle = veh_dict[vehicle_label]
    auto_driver = _auto_driver_for(vehicle['name'], vehicle['plate'])

    # How many records already for this car on this date?
    try:
        existing = query_df(
            "SELECT id, duty, cash_collected, fuel_cost, driver_name FROM daily_records WHERE record_date = ? AND plate = ? ORDER BY id",
            (record_date.isoformat(), vehicle['plate']),
        )
        same_day_count = len(existing)
    except Exception:
        existing = pd.DataFrame()
        same_day_count = 0

    if same_day_count >= 2:
        st.error(
            f"Already **{same_day_count}** records for **{vehicle['name']}** on **{record_date}**. "
            "Limit is 2 per car per day. Check **Records → Edit** if one was a mistake."
        )
        if not existing.empty:
            st.dataframe(existing, use_container_width=True, hide_index=True)
    elif same_day_count == 1:
        st.warning(
            f"There is already **1** record for **{vehicle['name']}** on **{record_date}**. "
            "You can save one more (e.g. Day + Night). A third entry will be blocked."
        )

    with st.form("daily_form", clear_on_submit=True):
        # Required daily fields — red border, same line
        st.markdown("""
        <style>
        div[data-testid="stForm"] div[data-testid="column"]:has(input) input {
            border-radius: 8px !important;
        }
        </style>
        <div style="border:1.5px solid #e74c3c; border-radius:10px; padding:10px 8px 4px 8px; margin-bottom:10px;">
          <p style="color:#e74c3c; font-size:12px; font-weight:700; margin:0 0 6px 0;">MAIN DAILY FIGURES</p>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            cash_s = st.text_input("Cash (M)", value="", placeholder="e.g. 200")
        with r2:
            fuel_s = st.text_input("Fuel cost (M)", value="", placeholder="e.g. 150")
        with r3:
            topup_s = st.text_input("Fuel top-up (M)", value="", placeholder="Office")
        with r4:
            trips_s = st.text_input("Trips", value="", placeholder="e.g. 5")
        with r5:
            duty = st.selectbox("Duty", ["Day", "Night"], index=0)

        a1, a2, a3 = st.columns(3)
        with a1:
            driver = st.text_input("Driver name", value=auto_driver, help="Auto from this car — edit if different driver")
        with a2:
            dcomp_s = st.text_input("Driver comp (M)", value="40", placeholder="40.00")
        with a3:
            airtime_s = st.text_input("Airtime (M)", value="10", placeholder="10.00")

        st.markdown("**Monthly credits / contracts**")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            ca_s = st.text_input("Alliance", value="", placeholder="0")
        with c2:
            cl_s = st.text_input("Lehae", value="", placeholder="0")
        with c3:
            cw_s = st.text_input("World Vision", value="", placeholder="0")
        with c4:
            cwa_s = st.text_input("Waleslink", value="", placeholder="0")
        with c5:
            cln_s = st.text_input("LNLVIP", value="", placeholder="0")

        e1, e2 = st.columns(2)
        with e1:
            other_s = st.text_input("Other expenses (M)", value="", placeholder="Amount")
        with e2:
            exp_notes = st.text_input("Expense notes", value="")

        submitted = st.form_submit_button("Save Record", use_container_width=True, type="primary")

        if submitted:
            # Re-check limit at save time
            try:
                chk = query_df(
                    "SELECT COUNT(*) AS n FROM daily_records WHERE record_date = ? AND plate = ?",
                    (record_date.isoformat(), vehicle['plate']),
                )
                n_now = int(chk.iloc[0]['n']) if not chk.empty else 0
            except Exception:
                n_now = 0

            if n_now >= 2:
                st.error(
                    f"Cannot save: already {n_now} records for {vehicle['name']} on {record_date}. "
                    "Delete or edit an existing one under Records."
                )
            else:
                trips = int(parse_amount(trips_s, 0))
                cash = parse_amount(cash_s)
                fuel_cost = parse_amount(fuel_s)
                fuel_topup = parse_amount(topup_s)
                driver_comp = parse_amount(dcomp_s, 40.0)
                airtime = parse_amount(airtime_s, 10.0)
                credit_alliance = parse_amount(ca_s)
                credit_lehae = parse_amount(cl_s)
                credit_worldvision = parse_amount(cw_s)
                credit_waleslink = parse_amount(cwa_s)
                credit_lnlvip = parse_amount(cln_s)
                other_exp = parse_amount(other_s)

                execute("""
                    INSERT INTO daily_records 
                    (record_date, vehicle_id, vehicle_name, plate, cash_collected, fuel_cost, fuel_topup,
                     trips, other_expenses, expense_notes, driver_compensation, airtime, duty,
                     credit_alliance, credit_lehae, credit_worldvision, credit_waleslink, credit_lnlvip,
                     driver_name, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_date.isoformat(), vehicle['id'], vehicle['name'], vehicle['plate'],
                    cash, fuel_cost, fuel_topup, trips, other_exp, exp_notes, driver_comp, airtime, duty,
                    credit_alliance, credit_lehae, credit_worldvision, credit_waleslink, credit_lnlvip,
                    driver, duty
                ))
                DEFAULT_DRIVERS[vehicle['name']] = driver
                st.success(
                    f"Saved · {vehicle['name']} · {record_date} · {duty} · "
                    f"Cash {format_amount(cash)} · Fuel {format_amount(fuel_cost)}"
                )
                st.rerun()

    # Last 5 saved records (always visible for quick check / edit path)
    st.markdown("---")
    st.subheader("Last 5 records")
    try:
        recent = query_df(
            "SELECT id, record_date, vehicle_name, driver_name, duty, trips, "
            "cash_collected, fuel_cost, fuel_topup, driver_compensation, airtime "
            "FROM daily_records ORDER BY id DESC LIMIT 5"
        )
    except Exception:
        recent = pd.DataFrame()
    if recent.empty:
        st.caption("No records yet.")
    else:
        show = recent.copy()
        for col in ['cash_collected', 'fuel_cost', 'fuel_topup', 'driver_compensation', 'airtime']:
            if col in show.columns:
                show[col] = show[col].apply(lambda x: format_amount(x))
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.caption("To correct a mistake: open **Records** → Edit or Delete.")

def page_records():
    st.header("All Daily Records")
    st.caption("Financial Year 2026 – 2027 (June to May)")

    df = prepare_records_df()
    if df.empty:
        st.info("No records yet.")
        return

    # Month selector
    month_labels = ["All months"] + [label for _, _, label in FY_MONTHS]
    sel_month = st.selectbox("Select month", month_labels)

    vehicles = ["All"] + sorted(df['vehicle_name'].unique().tolist())
    sel_veh = st.selectbox("Vehicle", vehicles)

    filtered = df.copy()
    if sel_month != "All months":
        filtered = filtered[filtered['fy_month'] == sel_month]
    if sel_veh != "All":
        filtered = filtered[filtered['vehicle_name'] == sel_veh]

    filtered = filtered.sort_values(['record_date', 'vehicle_name'])

    # Group by date with coloured borders for same-day records
    if filtered.empty:
        st.info("No records for this filter.")
    else:
        # Alternate yellow / red borders for consecutive date groups
        date_groups = list(filtered.groupby(filtered['record_date'].dt.date, sort=True))
        border_colors = ["#f5a623", "#e74c3c"]  # yellow, red

        for i, (day, gdf) in enumerate(date_groups):
            color = border_colors[i % 2]
            if hasattr(day, 'strftime'):
                day_str = day.strftime("%Y-%m-%d")
                weekday = day.strftime("%A").upper()
            else:
                day_str = str(day)
                try:
                    weekday = pd.to_datetime(day).strftime("%A").upper()
                except Exception:
                    weekday = ""
            count = len(gdf)

            st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 10px; padding: 10px 12px;
                        margin-bottom: 12px; background: #141414;">
                <p style="color:{color}; font-weight:700; margin:0 0 6px 0; font-size:13px;">
                    📅 {day_str} &nbsp;·&nbsp; {weekday} &nbsp;·&nbsp; {count} vehicle{"s" if count != 1 else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)

            show_cols = ['vehicle_name', 'driver_name', 'duty', 'trips', 'cash_collected',
                         'fuel_cost', 'fuel_topup', 'driver_compensation', 'airtime',
                         'credits', 'other_expenses']
            display = gdf[[c for c in show_cols if c in gdf.columns]].copy()
            st.dataframe(
                display.style.format({
                    'cash_collected': 'M {:,.0f}',
                    'fuel_cost': 'M {:,.0f}',
                    'fuel_topup': 'M {:,.0f}',
                    'driver_compensation': 'M {:,.0f}',
                    'airtime': 'M {:,.0f}',
                    'credits': 'M {:,.0f}',
                    'other_expenses': 'M {:,.0f}',
                }),
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            f"**Totals:** Cash {money(filtered['cash_collected'].sum())} | "
            f"Credits {money(filtered['credits'].sum())} | "
            f"Fuel {money(filtered['fuel_cost'].sum())} | "
            f"Top-up {money(filtered['fuel_topup'].sum())} | "
            f"Driver Comp {money(filtered['driver_compensation'].sum())}"
        )

    # ===== EDIT / DELETE RECORD =====
    st.markdown("---")
    st.subheader("Last 5 records")
    try:
        recent5 = query_df(
            "SELECT id, record_date, vehicle_name, driver_name, duty, trips, "
            "cash_collected, fuel_cost, driver_compensation, airtime "
            "FROM daily_records ORDER BY id DESC LIMIT 5"
        )
    except Exception:
        recent5 = pd.DataFrame()
    if not recent5.empty:
        rshow = recent5.copy()
        for col in ['cash_collected', 'fuel_cost', 'driver_compensation', 'airtime']:
            if col in rshow.columns:
                rshow[col] = rshow[col].apply(lambda x: format_amount(x))
        st.dataframe(rshow, use_container_width=True, hide_index=True)
    else:
        st.caption("No records yet.")

    st.subheader("Edit or Delete a Record")
    st.caption("Select a record to correct a mistake or remove it.")

    if not filtered.empty:
        options = []
        id_map = {}
        row_map = {}
        for _, row in filtered.iterrows():
            dstr = row['record_date'].strftime('%Y-%m-%d') if hasattr(row['record_date'], 'strftime') else str(row['record_date'])
            label = f"ID {row['id']} | {dstr} | {row['vehicle_name']} | Cash: M{row['cash_collected']:,.0f} | Fuel: M{row['fuel_cost']:,.0f}"
            options.append(label)
            id_map[label] = int(row['id'])
            row_map[label] = row

        selected_label = st.selectbox("Select record", options)
        selected_id = id_map[selected_label]
        selected_row = row_map[selected_label]

        col_edit, col_del = st.columns(2)

        with col_edit:
            with st.expander("Edit Record", expanded=False):
                with st.form("edit_record_form"):
                    current_date = selected_row['record_date']
                    if hasattr(current_date, 'date'):
                        current_date = current_date.date()
                    elif isinstance(current_date, str):
                        current_date = pd.to_datetime(current_date).date()
                    e_date = st.date_input("Date", value=current_date)

                    veh_dict = vehicle_options()
                    current_plate = str(selected_row.get('plate') or "")
                    current_label = next(
                        (k for k, v in veh_dict.items() if v.get('plate') == current_plate),
                        list(veh_dict.keys())[0]
                    )
                    e_vehicle_label = st.selectbox(
                        "Vehicle",
                        list(veh_dict.keys()),
                        index=list(veh_dict.keys()).index(current_label) if current_label in veh_dict else 0
                    )
                    e_vehicle = veh_dict[e_vehicle_label]

                    ea1, ea2, ea3, ea4 = st.columns(4)
                    with ea1:
                        e_driver = st.text_input("Driver name", value=str(selected_row.get('driver_name') or ""))
                    with ea2:
                        cur_duty = str(selected_row.get('duty') or selected_row.get('notes') or "Day")
                        if cur_duty not in ("Day", "Night"):
                            cur_duty = "Day"
                        e_duty = st.selectbox("Duty", ["Day", "Night"], index=0 if cur_duty == "Day" else 1)
                    with ea3:
                        e_trips = st.number_input("Trips", value=int(selected_row.get('trips') or 0), min_value=0, step=1)
                    with ea4:
                        e_cash = st.number_input("Cash (M)", value=float(selected_row.get('cash_collected') or 0), min_value=0.0, step=50.0, format="%.2f")

                    eb1, eb2, eb3, eb4 = st.columns(4)
                    with eb1:
                        e_fuel = st.number_input("Fuel (M)", value=float(selected_row.get('fuel_cost') or 0), min_value=0.0, step=10.0, format="%.2f")
                    with eb2:
                        e_topup = st.number_input("Top-up (M)", value=float(selected_row.get('fuel_topup') or 0), min_value=0.0, step=10.0, format="%.2f")
                    with eb3:
                        e_dcomp = st.number_input("Driver comp (M)", value=float(selected_row.get('driver_compensation') or 40), min_value=0.0, step=5.0, format="%.2f")
                    with eb4:
                        e_airtime = st.number_input("Airtime (M)", value=float(selected_row.get('airtime') or 10), min_value=0.0, step=1.0, format="%.2f")

                    e_other = st.number_input("Other expenses (M)", value=float(selected_row.get('other_expenses') or 0), min_value=0.0, step=10.0, format="%.2f")
                    e_alliance = st.number_input("Alliance (M)", value=float(selected_row.get('credit_alliance') or 0), min_value=0.0, step=50.0, format="%.2f")
                    e_lehae = st.number_input("Lehae (M)", value=float(selected_row.get('credit_lehae') or 0), min_value=0.0, step=50.0, format="%.2f")
                    e_wv = st.number_input("World Vision (M)", value=float(selected_row.get('credit_worldvision') or 0), min_value=0.0, step=50.0, format="%.2f")
                    e_wales = st.number_input("Waleslink (M)", value=float(selected_row.get('credit_waleslink') or 0), min_value=0.0, step=50.0, format="%.2f")
                    e_lnl = st.number_input("LNLVIP (M)", value=float(selected_row.get('credit_lnlvip') or 0), min_value=0.0, step=50.0, format="%.2f")

                    if st.form_submit_button("Save Changes", type="primary"):
                        execute("""
                            UPDATE daily_records SET
                                record_date=?, vehicle_id=?, vehicle_name=?, plate=?,
                                cash_collected=?, fuel_cost=?, fuel_topup=?, driver_compensation=?,
                                airtime=?, duty=?, trips=?, other_expenses=?,
                                credit_alliance=?, credit_lehae=?, credit_worldvision=?,
                                credit_waleslink=?, credit_lnlvip=?,
                                driver_name=?, notes=?
                            WHERE id=?
                        """, (
                            e_date.isoformat(),
                            e_vehicle['id'], e_vehicle['name'], e_vehicle['plate'],
                            e_cash, e_fuel, e_topup, e_dcomp, e_airtime, e_duty, e_trips, e_other,
                            e_alliance, e_lehae, e_wv, e_wales, e_lnl,
                            e_driver, e_duty, selected_id
                        ))
                        st.success(f"Record ID {selected_id} updated · {e_date} · {e_duty}")
                        st.rerun()

        with col_del:
            st.markdown("**Delete Record**")
            st.caption("This cannot be undone.")
            if st.button("Delete Record", type="primary"):
                execute("DELETE FROM daily_records WHERE id = ?", (selected_id,))
                st.success(f"Record ID {selected_id} has been deleted.")
                st.rerun()

    st.markdown("---")
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "maxy_taxi_records.csv", "text/csv")

def page_vehicles():
    st.header("Fleet")
    st.caption("Financial Year 2026 – 2027 (June to May)")

    df = prepare_records_df()
    month_options = [label for _, _, label in FY_MONTHS]
    sel_month = st.selectbox("Select month", month_options, key="fleet_month")
    y, m, _ = next((yy, mm, ll) for yy, mm, ll in FY_MONTHS if ll == sel_month)

    for v in VEHICLES:
        with st.expander(f"{v['name']} — {v['plate']}", expanded=False):
            vdf = df[df['plate'] == v['plate']] if not df.empty else pd.DataFrame()
            if vdf.empty:
                st.caption("No records yet for this vehicle.")
                continue

            mdf = vdf[(vdf['record_date'].dt.year == y) & (vdf['record_date'].dt.month == m)]
            if mdf.empty:
                st.caption(f"No records for {sel_month}.")
                continue

            cash = mdf['cash_collected'].sum()
            credits = mdf['credits'].sum()
            fuel = mdf['fuel_cost'].sum()
            topup = mdf['fuel_topup'].sum()
            dcomp = mdf['driver_compensation'].sum()
            other = mdf['other_expenses'].sum()
            trips = int(mdf['trips'].sum())
            net = cash + credits - fuel - topup - dcomp - other

            c1, c2, c3 = st.columns(3)
            c1.metric("Cash", money(cash))
            c2.metric("Credits", money(credits))
            c3.metric("Net", money(net))
            c4, c5, c6 = st.columns(3)
            c4.metric("Fuel", money(fuel))
            c5.metric("Top-up", money(topup))
            c6.metric("Driver Comp", money(dcomp))
            st.caption(f"Other expenses: {money(other)} | Trips: {trips}")

def page_clients():
    st.header("Clients")
    st.caption("Financial Year 2026 – 2027 (June to May)")

    # Credits for selected month
    st.subheader("Credits Summary")
    df = prepare_records_df()
    month_options = [label for _, _, label in FY_MONTHS]
    sel_month = st.selectbox("Select month", month_options, key="clients_month")

    if df.empty:
        st.info("No credit data yet.")
    else:
        y, m, _ = next((yy, mm, ll) for yy, mm, ll in FY_MONTHS if ll == sel_month)
        mdf = df[(df['record_date'].dt.year == y) & (df['record_date'].dt.month == m)]
        alliance = mdf['credit_alliance'].sum() if not mdf.empty else 0
        lehae = mdf['credit_lehae'].sum() if not mdf.empty else 0
        wv = mdf['credit_worldvision'].sum() if not mdf.empty else 0
        wales = mdf['credit_waleslink'].sum() if not mdf.empty else 0
        lnl = mdf['credit_lnlvip'].sum() if not mdf.empty else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Alliance", money(alliance))
        c2.metric("Lehae", money(lehae))
        c3.metric("World Vision", money(wv))
        c4, c5, c6 = st.columns(3)
        c4.metric("Waleslink", money(wales))
        c5.metric("LNLVIP", money(lnl))
        c6.metric("Total Credits", money(alliance + lehae + wv + wales + lnl))

    st.markdown("---")
    st.subheader("Client Directory")
    with st.expander("Add New Client", expanded=False):
        with st.form("client_form"):
            name = st.text_input("Client / Company Name *")
            contact = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            tin = st.text_input("TIN (optional)")
            notes = st.text_area("Notes")
            if st.form_submit_button("Save Client"):
                if name.strip():
                    execute("""
                        INSERT INTO clients (name, contact_person, phone, email, address, tin, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name.strip(), contact, phone, email, address, tin, notes))
                    st.success(f"Client '{name}' saved.")
                    st.rerun()
                else:
                    st.error("Name is required.")

    clients = query_df("SELECT * FROM clients ORDER BY name")
    if clients.empty:
        st.info("No clients saved yet. Add one above.")
    else:
        st.dataframe(clients[['id', 'name', 'contact_person', 'phone', 'email', 'tin']], use_container_width=True, hide_index=True)

def page_quotations():
    st.header("Quotations")

    with st.expander("Create New Quotation", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client / Company Name *", placeholder="Type any client name", key="qt_client")
            quote_date = st.date_input("Quote Date", value=date.today(), key="qt_date")
        with c2:
            status = st.selectbox("Status", ["Draft", "Sent", "Accepted", "Rejected", "Expired"], key="qt_status")
            notes = st.text_input("Notes / Terms (optional)", placeholder="Payment terms, inclusions...", key="qt_notes")

        st.markdown("""
        <div style="background:#1a1a1a; border:1px solid #f5a62355; border-radius:10px; padding:10px 12px; margin:10px 0 6px 0;">
            <p style="color:#f5a623; font-weight:700; margin:0; letter-spacing:1px; font-size:13px;">
                DESCRIPTION &nbsp;&nbsp;|&nbsp;&nbsp; QTY &nbsp;&nbsp;|&nbsp;&nbsp; AMOUNT (M)
            </p>
        </div>
        """, unsafe_allow_html=True)

        if "qt_lines" not in st.session_state:
            st.session_state.qt_lines = pd.DataFrame({
                "DESCRIPTION": ["", "", ""],
                "QTY": [None, None, None],
                "AMOUNT (M)": [None, None, None],
            })

        edited_qt = st.data_editor(
            st.session_state.qt_lines,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="qt_line_editor",
            column_config={
                "DESCRIPTION": st.column_config.TextColumn("DESCRIPTION", width="large"),
                "QTY": st.column_config.NumberColumn("QTY", min_value=0, step=1, format="%d"),
                "AMOUNT (M)": st.column_config.NumberColumn("AMOUNT (M)", min_value=0.0, step=50.0, format="%.2f"),
            }
        )
        st.session_state.qt_lines = edited_qt

        try:
            qt_total = float(pd.to_numeric(edited_qt["AMOUNT (M)"], errors="coerce").fillna(0).sum())
        except Exception:
            qt_total = 0.0
        st.metric("Total from table", money(qt_total))

        if st.button("Create Quotation", type="primary", use_container_width=True):
            if not client_name.strip():
                st.error("Client name is required.")
            else:
                lines = []
                for _, r in edited_qt.iterrows():
                    desc = str(r.get("DESCRIPTION") or "").strip()
                    if not desc or desc.lower() in ("null", "none", "nan"):
                        continue
                    qty = r.get("QTY")
                    amt = r.get("AMOUNT (M)")
                    if pd.isna(amt) and pd.isna(qty):
                        continue
                    qty_s = "" if pd.isna(qty) else str(int(qty))
                    amt_s = "0" if pd.isna(amt) else str(float(amt))
                    lines.append(f"{desc} | {qty_s} | {amt_s}")
                description = "\n".join(lines) if lines else "Transport services"
                total_amount = qt_total if qt_total > 0 else 0.0

                year = date.today().year
                last = query_df("SELECT quote_number FROM quotations WHERE quote_number LIKE ? ORDER BY id DESC LIMIT 1",
                                (f"QT-{year}-%",))
                if last.empty:
                    num = 1
                else:
                    try:
                        num = int(last.iloc[0]['quote_number'].split("-")[-1]) + 1
                    except Exception:
                        num = 1
                quote_number = f"QT-{year}-{num:04d}"
                valid_until = (quote_date + timedelta(days=14)).isoformat()

                execute("""
                    INSERT INTO quotations (quote_number, client_id, client_name, quote_date, valid_until,
                                            description, amount, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (quote_number, None, client_name.strip(), quote_date.isoformat(), valid_until,
                      description, total_amount, status, notes or ""))
                st.session_state.qt_lines = pd.DataFrame({
                    "DESCRIPTION": ["", "", ""],
                    "QTY": [None, None, None],
                    "AMOUNT (M)": [None, None, None],
                })
                st.success(f"Quotation {quote_number} created!")
                st.rerun()

    # List
    st.subheader("All Quotations")
    qdf = query_df("SELECT id, quote_number, client_name, quote_date, valid_until, amount, status FROM quotations ORDER BY id DESC")
    if qdf.empty:
        st.info("No quotations yet.")
    else:
        st.dataframe(qdf, use_container_width=True, hide_index=True)

        # Generate PDF
        st.markdown("### Download PDF")
        selected = st.selectbox("Select quotation", qdf['quote_number'].tolist())
        if selected:
            qrow = query_df("SELECT * FROM quotations WHERE quote_number = ?", (selected,)).iloc[0].to_dict()
            client = None
            if qrow.get('client_id'):
                cdf = query_df("SELECT * FROM clients WHERE id = ?", (qrow['client_id'],))
                if not cdf.empty:
                    client = cdf.iloc[0].to_dict()
            pdf_buf = generate_quotation_pdf(qrow, client)
            st.download_button(
                f"⬇️ Download {selected}.pdf",
                data=pdf_buf,
                file_name=f"{selected}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def page_invoices():
    st.header("Invoices")

    with st.expander("Create New Invoice", expanded=True):
        quotes = query_df("SELECT id, quote_number, client_name, amount, description FROM quotations WHERE status = 'Accepted' ORDER BY id DESC")
        quote_options = {"— None —": None}
        for _, r in quotes.iterrows():
            quote_options[f"{r['quote_number']} ({r['client_name'] or '—'} – M{r['amount']:,.0f})"] = r['id']

        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client / Company Name *", placeholder="Type any client name", key="inv_client")
            inv_date = st.date_input("Invoice Date", value=date.today(), key="inv_date")
            due_days = st.number_input("Due in (days)", min_value=0, value=30, key="inv_due")
        with c2:
            related_quote = st.selectbox("Link to Quotation (optional)", list(quote_options.keys()), key="inv_quote")
            status = st.selectbox("Status", ["Unpaid", "Partial", "Paid", "Overdue", "Cancelled"], key="inv_status")

        # Extendable cost breakdown table
        st.markdown("""
        <div style="background:#1a1a1a; border:1px solid #f5a62355; border-radius:10px; padding:10px 12px; margin:10px 0 6px 0;">
            <p style="color:#f5a623; font-weight:700; margin:0; letter-spacing:1px; font-size:13px;">
                DESCRIPTION &nbsp;&nbsp;|&nbsp;&nbsp; QTY &nbsp;&nbsp;|&nbsp;&nbsp; AMOUNT (M)
            </p>
        </div>
        """, unsafe_allow_html=True)

        if "inv_lines" not in st.session_state:
            st.session_state.inv_lines = pd.DataFrame({
                "DESCRIPTION": ["", "", ""],
                "QTY": [None, None, None],
                "AMOUNT (M)": [None, None, None],
            })

        edited_inv = st.data_editor(
            st.session_state.inv_lines,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="inv_line_editor",
            column_config={
                "DESCRIPTION": st.column_config.TextColumn("DESCRIPTION", width="large"),
                "QTY": st.column_config.NumberColumn("QTY", min_value=0, step=1, format="%d"),
                "AMOUNT (M)": st.column_config.NumberColumn("AMOUNT (M)", min_value=0.0, step=50.0, format="%.2f"),
            }
        )
        st.session_state.inv_lines = edited_inv

        # Auto total from table
        try:
            auto_total = float(pd.to_numeric(edited_inv["AMOUNT (M)"], errors="coerce").fillna(0).sum())
        except Exception:
            auto_total = 0.0
        st.metric("Total from table", money(auto_total))

        if st.button("Create Invoice", type="primary", use_container_width=True):
            if not client_name.strip():
                st.error("Client name is required.")
            else:
                # Build description lines for PDF
                lines = []
                for _, r in edited_inv.iterrows():
                    desc = str(r.get("DESCRIPTION") or "").strip()
                    if not desc or desc.lower() in ("null", "none", "nan"):
                        continue
                    qty = r.get("QTY")
                    amt = r.get("AMOUNT (M)")
                    if pd.isna(amt) and pd.isna(qty):
                        continue
                    qty_s = "" if pd.isna(qty) else str(int(qty))
                    amt_s = "0" if pd.isna(amt) else str(float(amt))
                    lines.append(f"{desc} | {qty_s} | {amt_s}")
                description = "\n".join(lines) if lines else "Transport services"
                total_amount = auto_total if auto_total > 0 else 0.0

                year = date.today().year
                last = query_df("SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
                                (f"INV-{year}-%",))
                if last.empty:
                    num = 1
                else:
                    try:
                        num = int(last.iloc[0]['invoice_number'].split("-")[-1]) + 1
                    except Exception:
                        num = 1
                inv_number = f"INV-{year}-{num:04d}"
                due_date = (inv_date + timedelta(days=int(due_days))).isoformat()
                qid = quote_options[related_quote]

                execute("""
                    INSERT INTO invoices (invoice_number, client_id, client_name, invoice_date, due_date,
                                          description, amount, amount_paid, status, related_quote_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inv_number, None, client_name.strip(), inv_date.isoformat(), due_date,
                      description, total_amount, 0.0, status, qid, ""))
                st.session_state.inv_lines = pd.DataFrame({
                    "DESCRIPTION": ["", "", ""],
                    "QTY": [None, None, None],
                    "AMOUNT (M)": [None, None, None],
                })
                st.success(f"Invoice {inv_number} created!")
                st.rerun()

    st.subheader("All Invoices")
    idf = query_df("""
        SELECT id, invoice_number, client_name, invoice_date, due_date, amount, amount_paid, status
        FROM invoices ORDER BY id DESC
    """)
    if idf.empty:
        st.info("No invoices yet.")
    else:
        idf['Balance'] = idf['amount'] - idf['amount_paid']
        st.dataframe(idf, use_container_width=True, hide_index=True)

        st.markdown("### Download PDF / Update Payment")
        selected = st.selectbox("Select invoice", idf['invoice_number'].tolist(), key="inv_sel")
        if selected:
            irow = query_df("SELECT * FROM invoices WHERE invoice_number = ?", (selected,)).iloc[0].to_dict()
            client = None
            if irow.get('client_id'):
                cdf = query_df("SELECT * FROM clients WHERE id = ?", (irow['client_id'],))
                if not cdf.empty:
                    client = cdf.iloc[0].to_dict()

            col_a, col_b = st.columns(2)
            with col_a:
                pdf_buf = generate_invoice_pdf(irow, client)
                st.download_button(
                    f"⬇️ Download {selected}.pdf",
                    data=pdf_buf,
                    file_name=f"{selected}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col_b:
                new_paid = st.number_input("Update amount paid", value=float(irow['amount_paid']), min_value=0.0, format="%.2f")
                new_status = st.selectbox("Update status", ["Unpaid", "Partial", "Paid", "Overdue", "Cancelled"],
                                          index=["Unpaid", "Partial", "Paid", "Overdue", "Cancelled"].index(irow['status']))
                if st.button("Update Payment / Status"):
                    execute("UPDATE invoices SET amount_paid = ?, status = ? WHERE invoice_number = ?",
                            (new_paid, new_status, selected))
                    st.success("Updated!")
                    st.rerun()

def _restore_dataframe(df, table_name, skip_cols=None):
    """Insert rows from a backup dataframe into a table. Returns count inserted."""
    if df is None or df.empty:
        return 0
    skip_cols = {str(x).lower() for x in (skip_cols or set())}
    df = df.copy()
    # Normalise headers: strip + lowercase (matches Postgres column names)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    conn = get_conn()
    if using_cloud_db():
        existing = pd.read_sql_query(
            "SELECT column_name AS name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s",
            conn, params=(table_name,)
        )
    else:
        existing = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
    table_cols = {str(n).lower() for n in existing['name'].tolist()}
    use_cols = [c for c in df.columns if c in table_cols and c not in skip_cols]
    if not use_cols:
        conn.close()
        return 0
    df = df[use_cols]
    df = df.where(pd.notnull(df), None)
    ph = "%s" if using_cloud_db() else "?"
    placeholders = ", ".join([ph] * len(use_cols))
    col_list = ", ".join(use_cols)
    sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"
    count = 0
    errors = 0
    c = conn.cursor()
    for _, row in df.iterrows():
        values = []
        for col in use_cols:
            v = row[col]
            try:
                if pd.isna(v):
                    values.append(None)
                else:
                    # Dates → text ISO
                    if hasattr(v, "isoformat"):
                        values.append(v.isoformat()[:10] if col.endswith("date") or col == "record_date" else v.isoformat())
                    else:
                        values.append(v)
            except Exception:
                values.append(v)
        try:
            c.execute(sql, tuple(values))
            count += 1
        except Exception:
            errors += 1
            try:
                conn.rollback()
            except Exception:
                pass
            continue
    try:
        conn.commit()
    except Exception:
        pass
    release_conn(conn)
    clear_data_cache()
    return count


def page_monthly_expenses():
    st.header("Monthly Expenses")
    st.caption("Rent, WiFi, maintenance, salaries · Financial year June–May")

    # Month picker (same FY labels)
    month_labels = [label for _, _, label in FY_MONTHS]
    sel_month = st.selectbox("Month", month_labels, key="me_month")

    # Existing row for this month
    existing = query_df("SELECT * FROM monthly_expenses WHERE expense_month = ?", (sel_month,))
    if not existing.empty:
        row = existing.iloc[0]
        rent0 = float(row.get("rent") or 0)
        wifi0 = float(row.get("wifi") or 0)
        maint0 = float(row.get("maintenance") or 0)
        sal0 = float(row.get("salaries") or 0)
        notes0 = str(row.get("notes") or "")
    else:
        rent0 = wifi0 = maint0 = sal0 = 0.0
        notes0 = ""

    # Driver compensation total from daily records for this month
    df = prepare_records_df()
    if not df.empty:
        mdf = df[df["fy_month"] == sel_month]
        driver_comp_total = float(mdf["driver_compensation"].sum()) if not mdf.empty else 0.0
    else:
        driver_comp_total = 0.0

    st.markdown("**Fixed monthly costs**")
    c1, c2 = st.columns(2)
    with c1:
        rent_s = st.text_input("Rent (M)", value=format_amount(rent0) if rent0 else "", placeholder="0.00")
        wifi_s = st.text_input("WiFi (M)", value=format_amount(wifi0) if wifi0 else "", placeholder="0.00")
    with c2:
        maint_s = st.text_input("Maintenance (M)", value=format_amount(maint0) if maint0 else "", placeholder="0.00")
        sal_s = st.text_input("Monthly salaries (M)", value=format_amount(sal0) if sal0 else "", placeholder="0.00")
    notes = st.text_input("Notes", value=notes0)

    rent = parse_amount(rent_s)
    wifi = parse_amount(wifi_s)
    maint = parse_amount(maint_s)
    salaries = parse_amount(sal_s)
    fixed_total = rent + wifi + maint + salaries
    staff_total = driver_comp_total + salaries

    m1, m2, m3 = st.columns(3)
    m1.metric("Fixed monthly total", money(fixed_total))
    m2.metric("Driver compensation (from daily)", money(driver_comp_total))
    m3.metric("Staff total (comp + salary)", money(staff_total))

    if st.button("Save monthly expenses", type="primary", use_container_width=True):
        if not existing.empty:
            execute(
                "UPDATE monthly_expenses SET rent=?, wifi=?, maintenance=?, salaries=?, notes=? WHERE expense_month=?",
                (rent, wifi, maint, salaries, notes, sel_month),
            )
        else:
            execute(
                "INSERT INTO monthly_expenses (expense_month, rent, wifi, maintenance, salaries, notes) VALUES (?,?,?,?,?,?)",
                (sel_month, rent, wifi, maint, salaries, notes),
            )
        st.success(f"Saved expenses for {sel_month}")
        st.rerun()

    st.markdown("---")
    st.subheader("All months")
    all_me = query_df("SELECT expense_month, rent, wifi, maintenance, salaries, notes FROM monthly_expenses ORDER BY expense_month")
    if all_me.empty:
        st.info("No monthly expenses saved yet.")
    else:
        all_me["fixed_total"] = (
            all_me["rent"].fillna(0) + all_me["wifi"].fillna(0)
            + all_me["maintenance"].fillna(0) + all_me["salaries"].fillna(0)
        )
        st.dataframe(all_me, use_container_width=True, hide_index=True)


def page_export():
    st.header("Backup & Export")

    if using_cloud_db():
        st.markdown("""
        <div style="border: 1px solid #2ecc71; border-radius: 10px; padding: 16px; background: #0d1f14; margin-bottom: 20px;">
            <p style="color:#2ecc71; font-weight:700; margin:0 0 8px 0;">Cloud database connected</p>
            <p style="color:#ddd; font-size:13px; margin:0; line-height:1.5;">
            Your records are stored in a permanent free cloud database.
            The app can sleep — your data will still be there when you come back.
            Still download a weekly Excel backup to Google Drive as a second safety copy.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border: 1px solid #f5a623; border-radius: 10px; padding: 16px; background: #1a1508; margin-bottom: 20px;">
            <p style="color:#f5a623; font-weight:700; margin:0 0 8px 0;">Local storage only (can be wiped when app sleeps)</p>
            <p style="color:#ddd; font-size:13px; margin:0; line-height:1.5;">
            Cloud database is not connected yet. Follow the setup steps below (free Supabase),
            or keep downloading a Full Backup to Google Drive after every data entry day.
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Set up free permanent cloud database (Supabase)", expanded=True):
            st.markdown("""
**About 10–15 minutes · Free forever for this size of business**

1. Open [https://supabase.com](https://supabase.com) and create a free account  
2. Click **New project** → choose a name (e.g. `maxy-taxi`) → set a database password → create  
3. Wait until the project is ready (green)  
4. Left menu → **Project Settings** (gear) → **Database**  
5. Under **Connection string** choose **URI**  
6. Copy the URI and replace `[YOUR-PASSWORD]` with the password you set  
7. Open your app on **share.streamlit.io** → top-right **⋯** → **Settings** → **Secrets**  
8. Paste exactly this (one line, with your real URI):

```toml
DATABASE_URL = "postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-xxxxx.pooler.supabase.com:6543/postgres"
```

9. Click **Save** → wait for the app to reboot  
10. Open **Backup / Export** again — you should see **Cloud database connected**  
11. Use **Restore from backup** to load your Google Drive Excel file into the cloud  

After that, data survives sleep and restarts.
            """)

    # ---------- RESTORE ----------
    st.subheader("Restore from backup")
    st.caption("Download your Excel file from Google Drive first, then upload it here.")
    uploaded = st.file_uploader(
        "Upload Maxy Taxi backup (.xlsx or .csv)",
        type=["xlsx", "xls", "csv"],
        key="restore_upload"
    )
    replace_all = st.checkbox(
        "Clear existing data before restore (recommended if the app is empty)",
        value=True
    )

    if uploaded is not None:
        st.info(f"File ready: **{uploaded.name}** ({uploaded.size} bytes)")
        if st.button("Restore now", type="primary", use_container_width=True):
            try:
                name = uploaded.name.lower()
                sheets = {}
                if name.endswith(".csv"):
                    sheets["Daily Records"] = pd.read_csv(uploaded)
                else:
                    # Read bytes so Streamlit mobile uploads work reliably
                    data = uploaded.getvalue()
                    xl = pd.ExcelFile(BytesIO(data))
                    for sheet in xl.sheet_names:
                        sheets[sheet] = pd.read_excel(xl, sheet_name=sheet)

                st.write("Sheets found:", ", ".join(sheets.keys()) if sheets else "(none)")

                if replace_all:
                    conn = get_conn()
                    cur = conn.cursor()
                    for t in ["daily_records", "clients", "quotations", "invoices"]:
                        try:
                            cur.execute(f"DELETE FROM {t}")
                        except Exception as del_err:
                            st.warning(f"Could not clear {t}: {del_err}")
                    conn.commit()
                    conn.close()

                # Map possible sheet names (flexible)
                def find_sheet(options):
                    for s in sheets:
                        if s.strip().lower() in options:
                            return sheets[s]
                    return None

                daily_df = find_sheet({"daily records", "daily_records", "records", "daily"})
                # If only one sheet and no name match, use it as daily records
                if daily_df is None and len(sheets) == 1:
                    daily_df = list(sheets.values())[0]
                    st.info("Using the only sheet in the file as Daily Records.")

                n_rec = _restore_dataframe(daily_df, "daily_records", skip_cols={"id"})
                n_cli = _restore_dataframe(
                    find_sheet({"clients", "client"}),
                    "clients",
                    skip_cols={"id"}
                )
                n_qt = _restore_dataframe(
                    find_sheet({"quotations", "quotes", "quotation"}),
                    "quotations",
                    skip_cols={"id"}
                )
                n_inv = _restore_dataframe(
                    find_sheet({"invoices", "invoice"}),
                    "invoices",
                    skip_cols={"id"}
                )

                if n_rec + n_cli + n_qt + n_inv == 0:
                    st.error(
                        "No rows were imported. Check that your Excel has a sheet named "
                        "**Daily Records** (or one sheet with columns like record_date, vehicle_name, cash_collected)."
                    )
                else:
                    st.success(
                        f"Restore complete!\n\n"
                        f"- Daily records: **{n_rec}**\n"
                        f"- Clients: **{n_cli}**\n"
                        f"- Quotations: **{n_qt}**\n"
                        f"- Invoices: **{n_inv}**"
                    )
                    st.balloons()
            except Exception as e:
                st.error(f"Restore failed: {e}")
                import traceback
                st.code(traceback.format_exc())

    st.markdown("---")

    # ---------- DOWNLOAD ----------
    st.subheader("Download backups")
    df_rec = query_df("SELECT * FROM daily_records")
    if not df_rec.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Daily Records (CSV)",
                df_rec.to_csv(index=False).encode(),
                "maxy_daily_records.csv",
                use_container_width=True
            )
        with col2:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_rec.to_excel(writer, sheet_name="Daily Records", index=False)
                query_df("SELECT * FROM clients").to_excel(writer, sheet_name="Clients", index=False)
                query_df("SELECT * FROM quotations").to_excel(writer, sheet_name="Quotations", index=False)
                query_df("SELECT * FROM invoices").to_excel(writer, sheet_name="Invoices", index=False)
            buffer.seek(0)
            st.download_button(
                "Full Backup (Excel)",
                buffer,
                f"maxy_taxi_backup_{date.today().isoformat()}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        st.success("Tip: Save every backup to your Google Drive folder so you can restore anytime.")
    else:
        st.info("No data in the app right now. Use **Restore from backup** above to bring your data back.")

    st.markdown("---")
    st.subheader("Make the app private")
    st.markdown("""
    1. Open your live app  
    2. Click the **⋯** menu (top right) → **Settings**  
    3. Go to **Sharing**  
    4. Choose **Only specific people can view this app**  
    5. Add your email and Save  
    """)
    st.caption("Password protection is already active. Making it private adds a second layer of security.")

# ---------------------- MAIN ----------------------
def main():
    init_db()

    # Professional Sidebar - logo icon only + yellow borders
    st.sidebar.markdown("""
    <div style="border: 2px solid #f5a623; border-radius: 12px; padding: 14px; margin-bottom: 12px; background: #111;">
    """, unsafe_allow_html=True)

    logo_dark = os.path.join(os.path.dirname(__file__), "logo_on_black.jpg")
    logo_trans = os.path.join(os.path.dirname(__file__), "logo_transparent.png")
    logo_clean = os.path.join(os.path.dirname(__file__), "logo_clean.png")
    if os.path.exists(logo_dark):
        st.sidebar.image(logo_dark, use_container_width=True)
    elif os.path.exists(logo_trans):
        st.sidebar.image(logo_trans, use_container_width=True)
    elif os.path.exists(logo_clean):
        st.sidebar.image(logo_clean, use_container_width=True)
    else:
        st.sidebar.markdown("<h3 style='color:#f5a623; text-align:center; margin:0;'>MAXY TAXI</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("""
        <p style="text-align:center; color:#f5a623; font-size:11px; letter-spacing:1.5px; margin:6px 0 0 0; font-weight:600;">
        SAFE • QUICK • RELIABLE
        </p>
    </div>
    """, unsafe_allow_html=True)

    pages = {
        "Dashboard": page_dashboard,
        "Daily Entry": page_daily_entry,
        "Records": page_records,
        "Fleet": page_vehicles,
        "Clients": page_clients,
        "Monthly Expenses": page_monthly_expenses,
        "Quotations": page_quotations,
        "Invoices": page_invoices,
        "Backup / Export": page_export,
    }

    menu_labels = {
        "Dashboard": "Dashboard",
        "Daily Entry": "Daily Entry",
        "Records": "Records",
        "Fleet": "Fleet",
        "Clients": "Clients",
        "Monthly Expenses": "Monthly Expenses",
        "Quotations": "Quotations",
        "Invoices": "Invoices",
        "Backup / Export": "Backup / Export",
    }
    choice = st.sidebar.radio("Menu", list(pages.keys()), label_visibility="collapsed",
                              format_func=lambda x: menu_labels.get(x, x))

    st.sidebar.markdown("""
    <div style="border: 2px solid #f5a623; border-radius: 10px; padding: 12px; margin-top: 14px; background: #111;">
        <p style="color:#f5a623; font-weight:bold; margin:0 0 8px 0; font-size:13px;">Contact</p>
        <p style="color:#ddd; font-size:12px; margin:3px 0;">📞 +266 27333388 / 68335933</p>
        <p style="color:#ddd; font-size:12px; margin:3px 0;">💬 +266 56432571</p>
        <p style="color:#ddd; font-size:12px; margin:3px 0;">✉️ maxytaxicab@gmail.com</p>
        <p style="color:#ddd; font-size:12px; margin:8px 0 0 0;">📍 Puma House 12<br>United Nations Road, Maseru</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<p style='text-align:center; color:#666; font-size:11px; margin-top:12px;'>5× Honda Fit + Alphard</p>", unsafe_allow_html=True)

    pages[choice]()

if __name__ == "__main__":
    main()
