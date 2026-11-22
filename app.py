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

    /* ===== DATAFRAMES / TABLES (gold + green brand) ===== */
    .stDataFrame {
        border: 1px solid #f5a62355 !important;
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 4px 18px rgba(245,166,35,0.12);
    }
    .stDataFrame thead tr th,
    .stDataFrame [data-testid="stDataFrameResizable"] th {
        background: linear-gradient(90deg, #2a1f0a 0%, #1a2e1a 100%) !important;
        color: #ffd700 !important;
        font-weight: 800 !important;
        border-bottom: 2px solid #f5a623 !important;
    }
    .stDataFrame tbody tr {
        background: #141210 !important;
        color: #f0e6c8 !important;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background: #1a2418 !important;
    }
    .stDataFrame tbody tr:hover {
        background: #243020 !important;
    }
    .stDataFrame tbody td {
        border-color: #2a3020 !important;
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

    # Clean Christmas-inspired login (no screenshots) — gold + festive accents
    st.markdown("""
    <style>
    .stApp {
        background:
          radial-gradient(ellipse 120% 70% at 50% -15%, #3d2a0a 0%, transparent 50%),
          radial-gradient(ellipse at bottom, #140808 0%, #050505 65%) !important;
    }
    .xmas-card {
        max-width: 400px;
        margin: 5vh auto 0 auto;
        padding: 26px 20px 18px 20px;
        border-radius: 20px;
        background: linear-gradient(165deg, rgba(45,32,12,0.97) 0%, rgba(12,10,8,0.99) 100%);
        border: 1px solid #c9a22755;
        box-shadow: 0 0 50px rgba(201,162,39,0.12), 0 14px 40px rgba(0,0,0,0.55);
        text-align: center;
    }
    .xmas-hat { font-size: 34px; line-height: 1; margin-bottom: -4px; }
    .xmas-name {
        font-size: 26px; font-weight: 800; color: #ffd700;
        letter-spacing: 1px; margin: 6px 0 2px 0;
        text-shadow: 0 0 16px rgba(255,215,0,0.3);
    }
    .xmas-tag {
        color: #e8d5a3; font-size: 11px; letter-spacing: 3px;
        font-weight: 700; margin: 0 0 12px 0;
    }
    .xmas-label { color: #c9a227; font-size: 12px; margin: 0 0 4px 0; }
    .xmas-footer {
        text-align: center; color: #7a6a48; font-size: 11px; margin-top: 16px;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #ffd700 0%, #c9a227 55%, #a67c00 100%) !important;
        color: #1a1200 !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 22px rgba(245, 196, 50, 0.4) !important;
        height: 3.1rem !important;
    }
    .stTextInput input {
        background: rgba(15,12,8,0.92) !important;
        border: 1px solid #c9a22788 !important;
        border-radius: 12px !important;
        color: #f5e6c8 !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([0.5, 2, 0.5])
    with col_b:
        st.markdown('<div class="xmas-card">', unsafe_allow_html=True)
        st.markdown('<div class="xmas-hat">🎅</div>', unsafe_allow_html=True)

        logo = os.path.join(os.path.dirname(__file__), "logo_on_black.jpg")
        logo2 = os.path.join(os.path.dirname(__file__), "logo_icon.jpg")
        logo3 = os.path.join(os.path.dirname(__file__), "logo_clean.png")
        if os.path.exists(logo):
            st.image(logo, use_container_width=True)
        elif os.path.exists(logo2):
            st.image(logo2, use_container_width=True)
        elif os.path.exists(logo3):
            st.image(logo3, use_container_width=True)

        st.markdown("""
            <p class="xmas-name">Maxy Taxi</p>
            <p class="xmas-tag">SAFE · QUICK · RELIABLE</p>
            <p class="xmas-label">Business Records Login</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            key="password_input",
            label_visibility="collapsed",
            placeholder="Enter password",
        )
        if st.button("Login", type="primary", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
        st.markdown(
            "<p class='xmas-footer'>Maxy Taxi Transport · Maseru · Merry Christmas</p>",
            unsafe_allow_html=True,
        )
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
BUSINESS_TIN = "200062844-2"
CURRENCY = "M"

# Monthly credit clients
CREDIT_CLIENTS = ["Alliance", "Lehae", "World Vision", "Waleslink", "LNLVIP"]

VEHICLES = [
    {"id": 1, "name": "Honda Fit 1", "plate": "A 940 BDL", "type": "Honda Fit",
     "phones": ["+266 58551514"], "role": "work"},
    {"id": 2, "name": "Honda Fit 2", "plate": "A 943 BDL", "type": "Honda Fit",
     "phones": ["+266 63299587", "+266 58658977"], "role": "work"},
    {"id": 3, "name": "Honda Fit 3", "plate": "A 945 BDL", "type": "Honda Fit",
     "phones": ["+266 50030354", "+266 63050399"], "role": "work"},
    {"id": 4, "name": "Honda Fit 4", "plate": "A 238 BGN", "type": "Honda Fit",
     "phones": ["+266 59591257", "+266 63751338"], "role": "work"},
    {"id": 5, "name": "Honda Fit 5", "plate": "A 765 BGR", "type": "Honda Fit",
     "phones": ["+266 58493642", "+266 62909197"], "role": "work"},
    {"id": 6, "name": "Toyota Alphard", "plate": "A 313 BCM", "type": "Alphard 7-seater",
     "phones": [], "role": "office"},
]

# Official Lesotho Petrol 95 pump prices (M/litre) — Petroleum Fund
LESOTHO_PETROL_95 = {
    "June 2026": 26.20,
    "July 2026": 23.85,
    "August 2026": 24.05,
    "September 2026": 24.80,
    "October 2026": 28.60,
    "November 2026": 29.25,
}

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
    for fn in (load_all_records, prepare_records_df):
        try:
            fn.clear()
        except Exception:
            pass


@st.cache_resource
def _init_db_once():
    """Run table setup only once per server process — avoids slow startup every click."""
    _init_db_impl()
    return True


def init_db():
    _init_db_once()
    # Only ensure extra tables once per session
    if not st.session_state.get("_extra_tables_ok"):
        ensure_extra_tables()
        st.session_state["_extra_tables_ok"] = True


def ensure_extra_tables():
    """Create incidents / parts tables if missing (fixes UndefinedTable after deploy)."""
    cloud = using_cloud_db()
    real_type = "DOUBLE PRECISION" if cloud else "REAL"
    id_col = "id SERIAL PRIMARY KEY" if cloud else "id INTEGER PRIMARY KEY AUTOINCREMENT"
    conn = get_conn()
    try:
        if cloud:
            try:
                conn.set_session(autocommit=True)
            except Exception:
                try:
                    conn.autocommit = True
                except Exception:
                    pass
        c = conn.cursor()
        for sql in [
            f"""CREATE TABLE IF NOT EXISTS incidents (
                {id_col}, incident_date TEXT NOT NULL, vehicle_name TEXT, plate TEXT,
                category TEXT, amount {real_type} DEFAULT 0, notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""",
            f"""CREATE TABLE IF NOT EXISTS parts_workshop (
                {id_col}, entry_date TEXT NOT NULL, vehicle_name TEXT, plate TEXT,
                item TEXT, amount {real_type} DEFAULT 0, notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""",
            """CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )""",
            f"""CREATE TABLE IF NOT EXISTS receipts (
                {id_col},
                receipt_number TEXT UNIQUE,
                receipt_date TEXT,
                received_from TEXT,
                description TEXT,
                amount {real_type} DEFAULT 0,
                payment_method TEXT DEFAULT 'Cash',
                related_invoice TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
        ]:
            try:
                c.execute(sql)
                if not cloud:
                    conn.commit()
            except Exception:
                if not cloud:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
    finally:
        release_conn(conn)


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

    # Fixed monthly business expenses
    run_sql(f"""
        CREATE TABLE IF NOT EXISTS monthly_expenses (
            {id_col},
            expense_month TEXT NOT NULL,
            rent {real_type} DEFAULT 0,
            wifi {real_type} DEFAULT 0,
            maintenance {real_type} DEFAULT 0,
            salaries {real_type} DEFAULT 0,
            car_wash {real_type} DEFAULT 0,
            miscellaneous {real_type} DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    run_sql(f"ALTER TABLE monthly_expenses ADD COLUMN car_wash {real_type} DEFAULT 0")
    run_sql(f"ALTER TABLE monthly_expenses ADD COLUMN miscellaneous {real_type} DEFAULT 0")

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS incidents (
            {id_col},
            incident_date TEXT NOT NULL,
            vehicle_name TEXT,
            plate TEXT,
            category TEXT,
            amount {real_type} DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    run_sql(f"""
        CREATE TABLE IF NOT EXISTS parts_workshop (
            {id_col},
            entry_date TEXT NOT NULL,
            vehicle_name TEXT,
            plate TEXT,
            item TEXT,
            amount {real_type} DEFAULT 0,
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


@st.cache_data(ttl=300, show_spinner=False)
def load_all_records():
    """Cached full daily_records pull — speeds up Dashboard / Records / Fleet."""
    return query_df("SELECT * FROM daily_records")

# ---------------------- PDF HELPERS ----------------------
def create_pdf_buffer():
    buffer = BytesIO()
    return buffer

def _pdf_letterhead_elements(styles=None):
    """Official Maxi Taxi letterhead — gold line only, no black bars."""
    elements = []
    base = os.path.dirname(__file__)
    for name, w, h in (
        ("letterhead_header.png", 186*mm, 40*mm),
        ("letterhead_clean.jpg", 186*mm, 38*mm),
        ("letterhead_banner.jpg", 186*mm, 36*mm),
    ):
        path = os.path.join(base, name)
        if os.path.exists(path):
            img = Image(path, width=w, height=h)
            img.hAlign = "CENTER"
            elements.append(img)
            break
    else:
        styles = styles or getSampleStyleSheet()
        elements.append(Paragraph(
            "<b>MAXY TAXI</b>",
            ParagraphStyle("LH", parent=styles["Heading1"], fontSize=14, alignment=TA_CENTER),
        ))
    elements.append(HRFlowable(
        width="100%", thickness=1.5, color=colors.HexColor("#f5a623"),
        spaceBefore=2*mm, spaceAfter=4*mm,
    ))
    return elements


def _pdf_draw_watermark(canvas, doc=None):
    """Large centred pin+car watermark — big, middle of A4, clearly visible."""
    canvas.saveState()
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "watermark_taxi.png")
    if not os.path.exists(path):
        for name in ("logo_pin.png", "logo_clean.png"):
            pth = os.path.join(base, name)
            if os.path.exists(pth):
                path = pth
                break
    page_w, page_h = A4
    if path and os.path.exists(path):
        try:
            # Large centred pin covering middle of page
            w, h = 155*mm, 200*mm
            x = (page_w - w) / 2.0
            y = (page_h - h) / 2.0
            canvas.drawImage(
                path, x, y, width=w, height=h,
                mask="auto", preserveAspectRatio=True,
            )
        except Exception:
            pass
    canvas.restoreState()


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

    elements.extend(_pdf_letterhead_elements(styles))

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

    # Pad body to about 5 lines (no grid lines) — extra rows if user enters more
    body_rows = max(0, len(items_data) - 1)  # exclude header
    while body_rows < 5:
        items_data.append([Paragraph("&nbsp;", normal), Paragraph("", normal), Paragraph("", right)])
        body_rows += 1

    total_amount = parsed_total if has_breakdown and parsed_total > 0 else amount
    items_data.append([
        Paragraph("", normal),
        Paragraph("<b>TOTAL</b>", bold),
        Paragraph(f"<b>M{total_amount:,.2f}</b>", ParagraphStyle('TotR', parent=right, fontSize=10)),
    ])

    elements.extend(_pdf_banking_elements(styles))
    items_table = Table(items_data, colWidths=[105*mm, 28*mm, 47*mm])
    items_table.setStyle(_pdf_line_table_style())
    elements.append(items_table)

    def _draw_inv_footer(canvas, doc_):
        _pdf_draw_page_chrome(canvas, doc_, "Maxy Taxi - Maseru - Invoice")

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

    elements.extend(_pdf_letterhead_elements(styles))

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

    body_rows = max(0, len(items_data) - 1)
    while body_rows < 5:
        items_data.append([Paragraph("&nbsp;", normal), Paragraph("", normal), Paragraph("", right)])
        body_rows += 1

    total_amount = parsed_total if has_breakdown and parsed_total > 0 else amount
    items_data.append([
        Paragraph("", normal),
        Paragraph("<b>TOTAL</b>", bold),
        Paragraph(f"<b>M{total_amount:,.2f}</b>", ParagraphStyle('TotR', parent=right, fontSize=10)),
    ])

    elements.extend(_pdf_banking_elements(styles))
    items_table = Table(items_data, colWidths=[105*mm, 28*mm, 47*mm])
    items_table.setStyle(_pdf_line_table_style())
    elements.append(items_table)

    if quote.get("notes"):
        elements.append(Paragraph("<b>Notes / Terms</b>", heading))
        elements.append(Paragraph(quote["notes"], normal))

    def _draw_quote_footer(canvas, doc_):
        _pdf_draw_page_chrome(canvas, doc_, "Maxy Taxi - Maseru - Quotation")

    doc.build(elements, onFirstPage=_draw_quote_footer, onLaterPages=_draw_quote_footer)
    buffer.seek(0)
    return buffer


def _pdf_line_table_style():
    """Professional table: gold header, no cell grid lines, soft total row."""
    gold = colors.HexColor("#f5a623")
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), gold),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("BACKGROUND", (0, 1), (-1, -2), colors.white),
        ("BACKGROUND", (1, -1), (-1, -1), colors.HexColor("#fff8e6")),
        ("LINEABOVE", (0, -1), (-1, -1), 1.0, gold),
        ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Gold side lines only (no full grid)
        ("LINEBEFORE", (0, 0), (0, -1), 1.5, gold),
        ("LINEAFTER", (-1, 0), (-1, -1), 1.5, gold),
    ])


def _pdf_banking_elements(styles=None):
    """White banking card, yellow left border — above description table."""
    styles = styles or getSampleStyleSheet()
    title = ParagraphStyle(
        "BankTitle", parent=styles["Normal"], fontSize=9, leading=12,
        textColor=colors.HexColor("#c47a00"), fontName="Helvetica-Bold",
    )
    body = ParagraphStyle(
        "BankBody", parent=styles["Normal"], fontSize=9, leading=12,
        textColor=colors.HexColor("#1a1a1a"),
    )
    tin = BUSINESS_TIN or "—"
    inner = [
        [Paragraph("BANKING DETAILS", title)],
        [Paragraph("Postbank  ·  Acc no <b>1017866800015</b>  ·  Branch <b>500100</b>", body)],
        [Paragraph(f"Maxy Taxi  ·  TIN <b>{tin}</b>", body)],
    ]
    box = Table(inner, colWidths=[180*mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 2),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, colors.HexColor("#f5a623")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e0d0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [box, Spacer(1, 4*mm)]


def _pdf_draw_page_chrome(canvas, doc_, footer_label="Maxy Taxi - Maseru"):
    """Watermark + clean gold footer (banking is above the items table)."""
    _pdf_draw_watermark(canvas, doc_)
    canvas.saveState()
    page_w, _ = A4
    canvas.setStrokeColor(colors.HexColor("#f5a623"))
    canvas.setLineWidth(1.2)
    canvas.line(15*mm, 16*mm, page_w - 15*mm, 16*mm)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(colors.HexColor("#1a1a1a"))
    canvas.drawCentredString(page_w/2, 10*mm, "Thank you for your Business")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawCentredString(page_w/2, 5.5*mm, footer_label)
    canvas.restoreState()


def generate_receipt_pdf(receipt):
    """Receipt PDF — same clean letterhead/table style as invoices (restored)."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=12*mm, leftMargin=12*mm,
        topMargin=5*mm, bottomMargin=22*mm,
    )
    styles = getSampleStyleSheet()
    elements = []

    normal = ParagraphStyle("Normal", parent=styles["Normal"], fontSize=10, leading=13)
    right = ParagraphStyle("Right", parent=styles["Normal"], fontSize=10, alignment=TA_RIGHT)
    bold = ParagraphStyle("Bold", parent=styles["Normal"], fontSize=10, leading=13)
    bold_right = ParagraphStyle("BoldRight", parent=styles["Normal"], fontSize=10, leading=13, alignment=TA_RIGHT)

    elements.extend(_pdf_letterhead_elements(styles))
    elements.append(Paragraph(
        "RECEIPT",
        ParagraphStyle("RTitle", parent=styles["Heading1"], fontSize=13, alignment=TA_CENTER,
                       textColor=colors.HexColor("#1a1a1a"), spaceAfter=3*mm),
    ))
    elements.append(Spacer(1, 2*mm))

    gold = colors.HexColor("#f5a623")
    left_style = ParagraphStyle("MetaL", parent=normal, fontSize=9, leading=13)
    right_style = ParagraphStyle("MetaR", parent=normal, fontSize=9, leading=13)
    left_box = Table([
        [Paragraph(f"<b>Receipt No</b><br/>{receipt.get('receipt_number', '')}", left_style)],
        [Paragraph(f"<b>Payment</b><br/>{receipt.get('payment_method', 'Cash')}", left_style)],
        [Paragraph(f"<b>Received from</b><br/>{receipt.get('received_from', '')}", left_style)],
    ], colWidths=[88*mm])
    left_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, gold),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e0d0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    right_box = Table([
        [Paragraph(f"<b>Date</b><br/>{receipt.get('receipt_date', '')}", right_style)],
        [Paragraph(f"<b>Related invoice</b><br/>{receipt.get('related_invoice') or '—'}", right_style)],
    ], colWidths=[88*mm])
    right_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, gold),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e0d0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    meta_row = Table([[left_box, right_box]], colWidths=[90*mm, 90*mm])
    meta_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(meta_row)
    elements.append(Spacer(1, 4*mm))

    lines = []
    raw = str(receipt.get("description") or "").strip()
    total = float(receipt.get("amount") or 0)
    if raw:
        for line in raw.split("\n"):
            line = line.strip()
            if not line or line.lower() in ("null", "none"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                desc, qty, amt = parts[0], parts[1], parts[2]
                try:
                    amt_f = float(str(amt).replace(",", "").replace("M", "").strip() or 0)
                except Exception:
                    amt_f = 0.0
                lines.append([desc, qty, f"M {amt_f:,.2f}"])
            else:
                lines.append([line, "", ""])
    if not lines:
        lines.append([raw or "Transport services", "1", f"M {total:,.2f}"])
    while len(lines) < 5:
        lines.append(["", "", ""])

    data = [[
        Paragraph("<b>DESCRIPTION</b>", bold),
        Paragraph("<b>QTY</b>", bold),
        Paragraph("<b>AMOUNT</b>", bold_right),
    ]]
    for r in lines:
        data.append([
            Paragraph(str(r[0]) if r[0] else "&nbsp;", normal),
            Paragraph(str(r[1]), normal),
            Paragraph(str(r[2]), right),
        ])
    data.append([
        "",
        Paragraph("<b>TOTAL RECEIVED</b>", bold),
        Paragraph(f"<b>M {total:,.2f}</b>", bold_right),
    ])

    elements.extend(_pdf_banking_elements(styles))
    tbl = Table(data, colWidths=[105*mm, 28*mm, 47*mm])
    tbl.setStyle(_pdf_line_table_style())
    elements.append(tbl)

    def _footer(canvas, doc_):
        _pdf_draw_page_chrome(canvas, doc_, "Maxy Taxi - Maseru - Official Receipt")

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer



def generate_weekly_summary_pdf(monday, sunday, wdf, byv, cash, credits, fuel, topup, dcomp, airtime, other, trips, net):
    """Simple branded weekly summary PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=14*mm, rightMargin=14*mm, topMargin=12*mm, bottomMargin=14*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("WT", parent=styles["Heading1"], fontSize=14, textColor=colors.HexColor("#1a1a1a"), alignment=TA_CENTER)
    normal = ParagraphStyle("WN", parent=styles["Normal"], fontSize=9, leading=12)
    elements = []

    elements.extend(_pdf_letterhead_elements(styles))
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(f"<b>Weekly Summary</b> · {monday.isoformat()} → {sunday.isoformat()}", title))
    elements.append(Spacer(1, 3*mm))

    summary = [
        ["Cash", money(cash), "Credits", money(credits)],
        ["Fuel", money(fuel), "Top-up", money(topup)],
        ["Driver comp", money(dcomp), "Airtime", money(airtime)],
        ["Other", money(other), "Trips", str(int(trips))],
        ["Net", money(net), "", ""],
    ]
    t = Table(summary, colWidths=[35*mm, 40*mm, 35*mm, 40*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, -1), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#c9a227")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#c9a227")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("<b>By registration</b>", normal))
    elements.append(Spacer(1, 2*mm))

    if byv is not None and not byv.empty:
        cols = list(byv.columns)
        data = [cols] + [[str(x) for x in row] for row in byv.values.tolist()]
        tw = Table(data, repeatRows=1)
        tw.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#f5a623")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f3e8")]),
        ]))
        elements.append(tw)

    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("Maxy Taxi · Sole trader · Maseru", normal))
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


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

@st.cache_data(ttl=300, show_spinner=False)
def prepare_records_df():
    """Cached processed daily records — avoid re-parse every widget click."""
    df = load_all_records()
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['record_date'] = pd.to_datetime(df['record_date'], errors='coerce')
    df['fy_month'] = df['record_date'].apply(get_fy_label)
    # Vectorized credits sum when columns exist
    credit_cols = [c for c in (
        'credit_alliance', 'credit_lehae', 'credit_worldvision',
        'credit_waleslink', 'credit_lnlvip',
    ) if c in df.columns]
    if credit_cols:
        df['credits'] = df[credit_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)
    else:
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
def _get_meta(key, default=""):
    try:
        df = query_df("SELECT value FROM app_meta WHERE key = ?", (key,))
        if not df.empty:
            return str(df.iloc[0]["value"] or default)
    except Exception:
        pass
    return default


def _set_meta(key, value):
    try:
        ensure_extra_tables()
        existing = query_df("SELECT key FROM app_meta WHERE key = ?", (key,))
        if existing is not None and not existing.empty:
            execute("UPDATE app_meta SET value = ? WHERE key = ?", (str(value), key))
        else:
            execute("INSERT INTO app_meta (key, value) VALUES (?, ?)", (key, str(value)))
    except Exception:
        pass


def page_dashboard():
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
        st.caption("Financial Year 2026 – 2027 (June to May) · Sole trader")

    # Backup reminder (red)
    last_bak = _get_meta("last_backup_date", "")
    if last_bak:
        try:
            lb = date.fromisoformat(last_bak[:10])
            days = (date.today() - lb).days
            if days > 7:
                st.markdown(
                    f"<p style='color:#e74c3c;font-weight:800;font-size:15px;'>"
                    f"⚠ BACKUP OVERDUE — last Excel backup was {days} days ago ({lb.isoformat()}). "
                    f"Go to Backup / Export and download a fresh copy.</p>",
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                "<p style='color:#e74c3c;font-weight:800;'>⚠ BACKUP REMINDER — download a weekly Excel backup.</p>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<p style='color:#e74c3c;font-weight:800;font-size:15px;'>"
            "⚠ NO BACKUP RECORDED YET — go to Backup / Export and download Excel this week.</p>",
            unsafe_allow_html=True,
        )

    df = prepare_records_df()
    today = date.today()
    monday, sunday = _week_bounds(today)

    # ===== TODAY + THIS WEEK STRIP =====
    st.markdown("### Today & this week")
    if df.empty:
        st.info("No daily records yet. Go to Daily Entry to start logging.")
    else:
        today_df = df[df["record_date"].dt.date == today]
        week_df = df[(df["record_date"].dt.date >= monday) & (df["record_date"].dt.date <= sunday)]

        t_cash = float(today_df["cash_collected"].sum())
        t_cred = float(today_df["credits"].sum())
        t_fuel = float(today_df["fuel_cost"].sum() + today_df["fuel_topup"].sum())
        t_trips = int(today_df["trips"].sum()) if not today_df.empty else 0
        t_exp = float(
            today_df["fuel_cost"].sum() + today_df["fuel_topup"].sum()
            + today_df["driver_compensation"].sum() + today_df["airtime"].sum()
            + today_df["other_expenses"].sum()
        )
        t_net = t_cash + t_cred - t_exp

        w_cash = float(week_df["cash_collected"].sum())
        w_cred = float(week_df["credits"].sum())
        w_fuel = float(week_df["fuel_cost"].sum() + week_df["fuel_topup"].sum())
        w_trips = int(week_df["trips"].sum()) if not week_df.empty else 0
        w_exp = float(
            week_df["fuel_cost"].sum() + week_df["fuel_topup"].sum()
            + week_df["driver_compensation"].sum() + week_df["airtime"].sum()
            + week_df["other_expenses"].sum()
        )
        w_net = w_cash + w_cred - w_exp

        st.markdown(
            f"<div style='border:1px solid #f5a62355;border-radius:12px;padding:12px;margin-bottom:10px;background:#141210;'>"
            f"<b style='color:#f5a623;'>TODAY</b> &nbsp; "
            f"Cash <b>{money(t_cash)}</b> &nbsp;·&nbsp; Credits <b>{money(t_cred)}</b> &nbsp;·&nbsp; "
            f"Fuel <b>{money(t_fuel)}</b> &nbsp;·&nbsp; Trips <b>{t_trips}</b> &nbsp;·&nbsp; "
            f"Net <b style='color:#2ecc71;'>{money(t_net)}</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='border:1px solid #2ecc7155;border-radius:12px;padding:12px;margin-bottom:12px;background:#101810;'>"
            f"<b style='color:#2ecc71;'>THIS WEEK</b> ({monday} → {sunday}) &nbsp; "
            f"Cash <b>{money(w_cash)}</b> &nbsp;·&nbsp; Credits <b>{money(w_cred)}</b> &nbsp;·&nbsp; "
            f"Fuel <b>{money(w_fuel)}</b> &nbsp;·&nbsp; Trips <b>{w_trips}</b> &nbsp;·&nbsp; "
            f"Net <b style='color:#2ecc71;'>{money(w_net)}</b></div>",
            unsafe_allow_html=True,
        )

        # Credit vs cash split (this week + selected later month)
        s1, s2 = st.columns(2)
        s1.metric("Week street cash", money(w_cash))
        s2.metric("Week contract credits", money(w_cred))

        # WhatsApp copy text
        wa = (
            f"Maxy Taxi week {monday.strftime('%d %b')}–{sunday.strftime('%d %b')}: "
            f"cash {money(w_cash)}, credits {money(w_cred)}, fuel {money(w_fuel)}, "
            f"trips {w_trips}, net {money(w_net)}"
        )
        st.text_area("WhatsApp summary (copy)", value=wa, height=70, key="dash_wa")

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
            # Prefer registration numbers
            if "plate" in mdf.columns:
                mdf2 = mdf.copy()
                mdf2["reg"] = mdf2["plate"].fillna(mdf2["vehicle_name"])
                by_veh = mdf2.groupby("reg").agg({
                    "cash_collected": "sum", "credits": "sum", "fuel_cost": "sum",
                    "fuel_topup": "sum", "driver_compensation": "sum", "airtime": "sum",
                    "other_expenses": "sum", "trips": "sum",
                }).reset_index()
            by_veh["Net"] = (by_veh["cash_collected"] + by_veh["credits"]
                             - by_veh["fuel_cost"] - by_veh["fuel_topup"]
                             - by_veh["driver_compensation"] - by_veh["airtime"]
                             - by_veh["other_expenses"])
            by_veh.columns = ["Registration", "Cash", "Credits", "Fuel", "Top-up", "Driver Comp", "Airtime", "Other", "Trips", "Net"]
            st.dataframe(by_veh, use_container_width=True, hide_index=True)

            # Fuel efficiency by plate (uses Lesotho petrol 95 for month)
            price = LESOTHO_PETROL_95.get(sel_month)
            if price and not mdf.empty:
                st.markdown(f"**Fuel efficiency** (Petrol 95 ≈ M{price:.2f}/L)")
                fe = mdf.copy()
                fe["reg"] = fe["plate"].fillna(fe["vehicle_name"]) if "plate" in fe.columns else fe["vehicle_name"]
                fe["fuel_spend"] = fe["fuel_cost"].fillna(0) + fe["fuel_topup"].fillna(0)
                g = fe.groupby("reg").agg(fuel_spend=("fuel_spend", "sum"), trips=("trips", "sum")).reset_index()
                g["Est. litres"] = (g["fuel_spend"] / price).round(1)
                g["M per trip"] = g.apply(lambda r: (r["fuel_spend"] / r["trips"]) if r["trips"] else 0, axis=1).round(1)
                g = g.sort_values("M per trip", ascending=False)
                g.columns = ["Registration", "Fuel+top-up (M)", "Trips", "Est. litres", "M per trip"]
                st.dataframe(g, use_container_width=True, hide_index=True)
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
    labels = list(veh_dict.keys())

    r0c1, r0c2, r0c3 = st.columns(3)
    with r0c1:
        record_date = st.date_input("Date", value=date.today(), key="de_date")
    with r0c2:
        duty = st.selectbox("Duty", ["Day", "Night"], key="de_duty")
    with r0c3:
        # Night → auto-select roster car (still changeable)
        default_idx = 0
        if duty == "Night":
            mon, _ = _week_bounds(record_date)
            _, night_plate = _night_car_for_week(mon)
            for i, lab in enumerate(labels):
                if night_plate.replace(" ", "") in lab.replace(" ", ""):
                    default_idx = i
                    break
            st.markdown(
                f"<p style='color:#f5a623;font-size:12px;margin:0;'>Night roster: <b>{night_plate}</b></p>",
                unsafe_allow_html=True,
            )
        vehicle_label = st.selectbox("Vehicle", labels, index=default_idx, key="de_vehicle")
    vehicle = veh_dict[vehicle_label]
    auto_driver = _auto_driver_for(vehicle["name"], vehicle["plate"])

    try:
        existing = query_df(
            "SELECT id, duty, cash_collected, fuel_cost, driver_name FROM daily_records WHERE record_date = ? AND plate = ? ORDER BY id",
            (record_date.isoformat(), vehicle["plate"]),
        )
        same_day_count = len(existing)
    except Exception:
        existing = pd.DataFrame()
        same_day_count = 0

    if same_day_count >= 2:
        st.markdown(
            f"<p style='color:#e74c3c;font-weight:800;font-size:15px;'>"
            f"⚠ ALREADY {same_day_count} RECORDS for {vehicle['plate']} on {record_date}. "
            f"LIMIT IS 2 PER CAR PER DAY. Check Records → Edit if one was a mistake.</p>",
            unsafe_allow_html=True,
        )
        if not existing.empty:
            st.dataframe(existing, use_container_width=True, hide_index=True)
    elif same_day_count == 1:
        st.markdown(
            f"<p style='color:#e74c3c;font-weight:700;font-size:14px;'>"
            f"⚠ ALREADY 1 RECORD for {vehicle['plate']} on {record_date}. "
            f"You can save one more (e.g. Day + Night). A third entry will be blocked.</p>",
            unsafe_allow_html=True,
        )

    with st.form("daily_form", clear_on_submit=True):
        st.markdown("""
        <div style="border:1.5px solid #e74c3c; border-radius:10px; padding:10px 8px 4px 8px; margin-bottom:10px;">
          <p style="color:#e74c3c; font-size:12px; font-weight:700; margin:0 0 6px 0;">MAIN DAILY FIGURES</p>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            cash_s = st.text_input("Cash (M)", value="", placeholder="e.g. 200")
        with r2:
            fuel_s = st.text_input("Fuel cost (M)", value="", placeholder="e.g. 150")
        with r3:
            topup_s = st.text_input("Fuel top-up (M)", value="", placeholder="Office")
        with r4:
            trips_s = st.text_input("Trips", value="", placeholder="e.g. 5")

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

                execute("""
                    INSERT INTO daily_records 
                    (record_date, vehicle_id, vehicle_name, plate, cash_collected, fuel_cost, fuel_topup,
                     trips, other_expenses, expense_notes, driver_compensation, airtime, duty,
                     credit_alliance, credit_lehae, credit_worldvision, credit_waleslink, credit_lnlvip,
                     driver_name, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_date.isoformat(), vehicle['id'], vehicle['name'], vehicle['plate'],
                    cash, fuel_cost, fuel_topup, trips, 0.0, "", driver_comp, airtime, duty,
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

    plates = ["All"] + sorted([p for p in df['plate'].dropna().unique().tolist() if p])
    sel_veh = st.selectbox("Registration number", plates)

    filtered = df.copy()
    if sel_month != "All months":
        filtered = filtered[filtered['fy_month'] == sel_month]
    if sel_veh != "All":
        filtered = filtered[filtered['plate'] == sel_veh]

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

            # Line 1 — date
            st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 10px; padding: 10px 12px;
                        margin-bottom: 8px; background: #141414;">
                <p style="color:{color}; font-weight:700; margin:0; font-size:13px;">
                    📅 {day_str} &nbsp;·&nbsp; {weekday} &nbsp;·&nbsp; {count} vehicle{"s" if count != 1 else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Single stable table (no green box) — columns fixed, no horizontal jump
            show_cols = ['plate', 'driver_name', 'duty', 'trips', 'cash_collected',
                         'fuel_cost', 'fuel_topup', 'driver_compensation', 'airtime', 'credits']
            display = gdf[[c for c in show_cols if c in gdf.columns]].copy()
            display = display.rename(columns={
                "plate": "Reg",
                "driver_name": "Driver",
                "cash_collected": "Cash",
                "fuel_cost": "Petrol",
                "fuel_topup": "Top-up",
                "driver_compensation": "Comp",
                "airtime": "Airtime",
                "credits": "Credits",
            })
            # Format money columns as strings so mobile table stays stable
            for col in ["Cash", "Petrol", "Top-up", "Comp", "Airtime", "Credits"]:
                if col in display.columns:
                    display[col] = display[col].apply(lambda x: f"M {float(x or 0):,.0f}")
            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
                column_config={c: st.column_config.TextColumn(c, width="small") for c in display.columns},
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

    st.subheader("Credits · Paid / Unpaid")
    df = prepare_records_df()
    month_options = [label for _, _, label in FY_MONTHS]
    sel_month = st.selectbox("Select month", month_options, key="clients_month")

    try:
        execute("""
            CREATE TABLE IF NOT EXISTS client_pay_status (
                company_name TEXT PRIMARY KEY,
                status TEXT DEFAULT 'Unpaid'
            )
        """)
    except Exception:
        pass

    # Amounts for selected month
    amounts = {
        "Alliance": 0.0, "Lehae": 0.0, "World Vision": 0.0,
        "Waleslink": 0.0, "LNLVIP": 0.0,
    }
    if df is not None and not df.empty:
        y, m, _ = next((yy, mm, ll) for yy, mm, ll in FY_MONTHS if ll == sel_month)
        mdf = df[(df["record_date"].dt.year == y) & (df["record_date"].dt.month == m)]
        if not mdf.empty:
            amounts["Alliance"] = float(mdf["credit_alliance"].sum()) if "credit_alliance" in mdf.columns else 0.0
            amounts["Lehae"] = float(mdf["credit_lehae"].sum()) if "credit_lehae" in mdf.columns else 0.0
            amounts["World Vision"] = float(mdf["credit_worldvision"].sum()) if "credit_worldvision" in mdf.columns else 0.0
            amounts["Waleslink"] = float(mdf["credit_waleslink"].sum()) if "credit_waleslink" in mdf.columns else 0.0
            amounts["LNLVIP"] = float(mdf["credit_lnlvip"].sum()) if "credit_lnlvip" in mdf.columns else 0.0

    status_df = query_df("SELECT company_name, status FROM client_pay_status")
    status_map = {}
    if status_df is not None and not status_df.empty:
        for _, r in status_df.iterrows():
            status_map[str(r["company_name"])] = str(r["status"] or "Unpaid")

    total = 0.0
    for cname, amt in amounts.items():
        total += amt
        cur = status_map.get(cname, "Unpaid")
        is_paid = cur.lower() == "paid"
        label = "Paid" if is_paid else "Unpaid"
        border = "#2ecc71" if is_paid else "#e74c3c"
        st.markdown(
            f"""
            <div style="border-left:5px solid {border}; background:#141414; border-radius:10px;
                        padding:14px 16px; margin:10px 0;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <p style="color:#aaa;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">{cname}</p>
                  <p style="color:#ffffff;font-weight:700;font-size:22px;margin:0;">{money(amt)}</p>
                </div>
                <span style="color:{border};font-weight:800;font-size:14px;">{label}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        btn = f"Mark {cname} as {'Unpaid' if is_paid else 'Paid'}"
        if st.button(btn, key=f"pay_toggle_{cname}", use_container_width=True):
            new_st = "Unpaid" if is_paid else "Paid"
            try:
                execute(
                    "INSERT INTO client_pay_status (company_name, status) VALUES (?, ?) "
                    "ON CONFLICT (company_name) DO UPDATE SET status = EXCLUDED.status",
                    (cname, new_st),
                )
            except Exception:
                existing = query_df("SELECT company_name FROM client_pay_status WHERE company_name = ?", (cname,))
                if existing is not None and not existing.empty:
                    execute("UPDATE client_pay_status SET status = ? WHERE company_name = ?", (new_st, cname))
                else:
                    execute("INSERT INTO client_pay_status (company_name, status) VALUES (?, ?)", (cname, new_st))
            st.rerun()

    st.markdown(
        f"""
        <div style="border-left:5px solid #f5a623; background:#141414; border-radius:10px;
                    padding:14px 16px; margin:10px 0;">
          <p style="color:#aaa;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">Total credits</p>
          <p style="color:#ffffff;font-weight:800;font-size:22px;margin:0;">{money(total)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        # Attach payment status to directory names
        def _client_status(name):
            if inv is None or inv.empty:
                return "—"
            sub = inv[inv["client_name"].astype(str).str.lower() == str(name).lower()]
            if sub.empty:
                sub = inv[inv["client_name"].astype(str).str.contains(str(name), case=False, na=False)]
            if sub.empty:
                return "No invoice"
            total = float(pd.to_numeric(sub["amount"], errors="coerce").fillna(0).sum())
            paid = float(pd.to_numeric(sub["amount_paid"], errors="coerce").fillna(0).sum())
            outstanding = total - paid
            if outstanding <= 0.01 and total > 0:
                return "✅ Paid"
            if paid > 0:
                return "🟠 Partial"
            return "🔴 Outstanding"

        cshow = clients[['name', 'contact_person', 'phone', 'email', 'tin']].copy()
        cshow["Payment status"] = cshow["name"].apply(_client_status)
        st.dataframe(cshow, use_container_width=True, hide_index=True)

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

        # data_editor keeps its own state via key — do NOT write back every run (that wipes first edit)
        _qt_seed = pd.DataFrame({
            "DESCRIPTION": ["", "", ""],
            "QTY": [None, None, None],
            "AMOUNT (M)": [None, None, None],
        })
        edited_qt = st.data_editor(
            _qt_seed,
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
                if "qt_line_editor" in st.session_state:
                    del st.session_state["qt_line_editor"]
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
            st.markdown("### Edit or delete quotation")
            e_client = st.text_input("Client name", value=str(qrow.get("client_name") or ""), key="q_edit_client")
            e_amt = st.number_input("Amount", value=float(qrow.get("amount") or 0), min_value=0.0, format="%.2f", key="q_edit_amt")
            e_status = st.selectbox(
                "Status",
                ["Draft", "Sent", "Accepted", "Rejected", "Expired"],
                index=max(0, ["Draft", "Sent", "Accepted", "Rejected", "Expired"].index(qrow.get("status")) if qrow.get("status") in ["Draft", "Sent", "Accepted", "Rejected", "Expired"] else 0),
                key="q_edit_status",
            )
            e_desc = st.text_area("Description / lines", value=str(qrow.get("description") or ""), key="q_edit_desc")
            cqe1, cqe2 = st.columns(2)
            with cqe1:
                if st.button("Save quotation edits", type="primary", use_container_width=True, key="q_save"):
                    execute(
                        "UPDATE quotations SET client_name=?, amount=?, status=?, description=? WHERE quote_number=?",
                        (e_client, e_amt, e_status, e_desc, selected),
                    )
                    st.success("Quotation updated")
                    st.rerun()
            with cqe2:
                if st.button("Delete quotation", use_container_width=True, key="q_del"):
                    execute("DELETE FROM quotations WHERE quote_number=?", (selected,))
                    st.success("Quotation deleted")
                    st.rerun()

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

        # data_editor keeps its own state via key — do NOT write back every run
        _inv_seed = pd.DataFrame({
            "DESCRIPTION": ["", "", ""],
            "QTY": [None, None, None],
            "AMOUNT (M)": [None, None, None],
        })
        edited_inv = st.data_editor(
            _inv_seed,
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
                if "inv_line_editor" in st.session_state:
                    del st.session_state["inv_line_editor"]
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

            st.markdown("### Edit or delete invoice")
            ie_client = st.text_input("Client name", value=str(irow.get("client_name") or ""), key="i_edit_client")
            ie_amt = st.number_input("Invoice amount", value=float(irow.get("amount") or 0), min_value=0.0, format="%.2f", key="i_edit_amt")
            ie_desc = st.text_area("Description / lines", value=str(irow.get("description") or ""), key="i_edit_desc")
            cie1, cie2 = st.columns(2)
            with cie1:
                if st.button("Save invoice edits", type="primary", use_container_width=True, key="i_save"):
                    execute(
                        "UPDATE invoices SET client_name=?, amount=?, description=? WHERE invoice_number=?",
                        (ie_client, ie_amt, ie_desc, selected),
                    )
                    st.success("Invoice updated")
                    st.rerun()
            with cie2:
                if st.button("Delete invoice", use_container_width=True, key="i_del"):
                    execute("DELETE FROM invoices WHERE invoice_number=?", (selected,))
                    st.success("Invoice deleted")
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
    st.caption("Fixed costs · incidents & fines · parts & workshop")

    tab_fixed, tab_inc, tab_parts = st.tabs(
        ["Fixed monthly", "Incidents & fines", "Parts & workshop"]
    )

    with tab_fixed:
        month_labels = [label for _, _, label in FY_MONTHS]
        sel_month = st.selectbox("Month", month_labels, key="me_month")

        # Ensure extra columns exist
        for col in ("stationery", "vehicle_instalment"):
            try:
                execute(f"ALTER TABLE monthly_expenses ADD COLUMN {col} DOUBLE PRECISION DEFAULT 0")
            except Exception:
                try:
                    execute(f"ALTER TABLE monthly_expenses ADD COLUMN {col} REAL DEFAULT 0")
                except Exception:
                    pass

        existing = query_df("SELECT * FROM monthly_expenses WHERE expense_month = ?", (sel_month,))
        if not existing.empty:
            row = existing.iloc[0]
            rent0 = float(row.get("rent") or 0)
            wifi0 = float(row.get("wifi") or 0)
            sal0 = float(row.get("salaries") or 0)
            wash0 = float(row.get("car_wash") or 0)
            stat0 = float(row.get("stationery") or 0)
            inst0 = float(row.get("vehicle_instalment") or 0)
            misc0 = float(row.get("miscellaneous") or 0)
            notes0 = str(row.get("notes") or "")
        else:
            rent0 = wifi0 = sal0 = wash0 = stat0 = inst0 = misc0 = 0.0
            notes0 = ""

        df = prepare_records_df()
        if not df.empty:
            mdf = df[df["fy_month"] == sel_month]
            driver_comp_total = float(mdf["driver_compensation"].sum()) if not mdf.empty else 0.0
        else:
            driver_comp_total = 0.0

        c1, c2, c3 = st.columns(3)
        with c1:
            rent_s = st.text_input("Rent (M)", value=format_amount(rent0) if rent0 else "", placeholder="0.00")
            wifi_s = st.text_input("WiFi (M)", value=format_amount(wifi0) if wifi0 else "", placeholder="0.00")
        with c2:
            sal_s = st.text_input("Monthly salaries (M)", value=format_amount(sal0) if sal0 else "", placeholder="0.00")
            wash_s = st.text_input("Car wash (M)", value=format_amount(wash0) if wash0 else "", placeholder="0.00")
        with c3:
            stat_s = st.text_input("Stationery (M)", value=format_amount(stat0) if stat0 else "", placeholder="0.00")
            misc_s = st.text_input("Miscellaneous (M)", value=format_amount(misc0) if misc0 else "", placeholder="0.00")
        st.markdown("**Asset (cab purchase / instalment)**")
        veh_opts = ["— None —"] + [f"{v['name']} · {v['plate']}" for v in VEHICLES]
        # Restore previous selection from notes if saved as Asset: ...
        default_veh = "— None —"
        if notes0 and "Asset:" in notes0:
            for opt in veh_opts:
                if opt != "— None —" and opt.split("·")[-1].strip() in notes0:
                    default_veh = opt
                    break
        asset_veh = st.selectbox(
            "Select vehicle",
            veh_opts,
            index=veh_opts.index(default_veh) if default_veh in veh_opts else 0,
            key="fixed_asset_veh",
        )
        inst_s = st.text_input(
            "Asset amount (M)",
            value=format_amount(inst0) if inst0 else "",
            placeholder="Amount paid this month for this vehicle",
            key="fixed_asset_amt",
        )
        notes = st.text_input("Notes", value=notes0)

        rent = parse_amount(rent_s)
        wifi = parse_amount(wifi_s)
        salaries = parse_amount(sal_s)
        car_wash = parse_amount(wash_s)
        stationery = parse_amount(stat_s)
        vehicle_instalment = parse_amount(inst_s)
        miscellaneous = parse_amount(misc_s)
        fixed_total = rent + wifi + salaries + car_wash + stationery + vehicle_instalment + miscellaneous
        staff_total = driver_comp_total + salaries
        # Tag notes with selected asset vehicle
        save_notes = notes or ""
        if asset_veh and asset_veh != "— None —":
            tag = f"Asset: {asset_veh}"
            if "Asset:" in save_notes:
                # replace existing Asset: line prefix
                parts = [ln for ln in save_notes.split(" | ") if not ln.startswith("Asset:")]
                save_notes = " | ".join([tag] + parts) if parts else tag
            else:
                save_notes = f"{tag} | {save_notes}" if save_notes else tag

        m1, m2, m3 = st.columns(3)
        m1.metric("Fixed monthly total", money(fixed_total))
        m2.metric("Driver compensation (daily)", money(driver_comp_total))
        m3.metric("Staff total (comp + salary)", money(staff_total))
        if asset_veh != "— None —" and vehicle_instalment:
            st.caption(f"Asset this month: **{asset_veh}** · {money(vehicle_instalment)}")

        if st.button("Save fixed costs", type="primary", use_container_width=True):
            if not existing.empty:
                execute(
                    "UPDATE monthly_expenses SET rent=?, wifi=?, salaries=?, car_wash=?, stationery=?, vehicle_instalment=?, miscellaneous=?, notes=?, maintenance=0 WHERE expense_month=?",
                    (rent, wifi, salaries, car_wash, stationery, vehicle_instalment, miscellaneous, save_notes, sel_month),
                )
            else:
                execute(
                    "INSERT INTO monthly_expenses (expense_month, rent, wifi, maintenance, salaries, car_wash, stationery, vehicle_instalment, miscellaneous, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (sel_month, rent, wifi, 0, salaries, car_wash, stationery, vehicle_instalment, miscellaneous, save_notes),
                )
            st.success(f"Saved fixed costs for {sel_month}")
            st.rerun()

        all_me = query_df(
            "SELECT expense_month, rent, wifi, salaries, car_wash, stationery, vehicle_instalment, miscellaneous "
            "FROM monthly_expenses ORDER BY expense_month"
        )
        if not all_me.empty:
            st.dataframe(all_me, use_container_width=True, hide_index=True)


    with tab_inc:
        st.markdown("**Log a fine, accident, damage or police cost**")
        month_labels_i = ["All months"] + [label for _, _, label in FY_MONTHS]
        sel_inc_month = st.selectbox("Month filter", month_labels_i, key="inc_month_filter")
        with st.form("incident_form"):
            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input("Date", value=date.today(), key="inc_date")
                veh = st.selectbox("Vehicle", [v["name"] for v in VEHICLES] + ["Various (all fleet)"], key="inc_veh")
            with c2:
                cat = st.selectbox("Category", ["Fine", "Accident", "Damage", "Police", "Other"], key="inc_cat")
                amt_s = st.text_input("Amount (M)", value="", placeholder="0.00", key="inc_amt")
            notes_i = st.text_input("Notes", key="inc_notes")
            if st.form_submit_button("Save incident", type="primary"):
                ensure_extra_tables()
                if veh == "Various (all fleet)":
                    plate = "VARIOUS"
                else:
                    plate = next((v["plate"] for v in VEHICLES if v["name"] == veh), "")
                execute(
                    "INSERT INTO incidents (incident_date, vehicle_name, plate, category, amount, notes) VALUES (?,?,?,?,?,?)",
                    (d.isoformat(), veh, plate, cat, parse_amount(amt_s), notes_i),
                )
                st.success("Incident saved")
                st.rerun()
        try:
            idf = query_df(
                "SELECT id, incident_date, vehicle_name, plate, category, amount, notes FROM incidents ORDER BY id DESC LIMIT 100"
            )
            if idf.empty:
                st.info("No incidents yet.")
            else:
                if sel_inc_month != "All months":
                    # Filter by FY month label
                    idf["_d"] = pd.to_datetime(idf["incident_date"], errors="coerce")
                    idf = idf[idf["_d"].apply(
                        lambda x: next((lab for y, m, lab in FY_MONTHS if x.year == y and x.month == m), "") == sel_inc_month
                        if pd.notna(x) else False
                    )]
                    idf = idf.drop(columns=["_d"], errors="ignore")
                st.dataframe(idf.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)
                st.metric("Total incidents (filtered)", money(pd.to_numeric(idf["amount"], errors="coerce").fillna(0).sum()))
        except Exception:
            ensure_extra_tables()
            st.info("Incidents table ready — save your first entry.")

    with tab_parts:
        st.markdown("**Parts, workshop & mechanical**")
        month_labels_p = ["All months"] + [label for _, _, label in FY_MONTHS]
        sel_parts_month = st.selectbox("Month filter", month_labels_p, key="parts_month_filter")
        veh_opts = [v["name"] for v in VEHICLES] + ["Various (all fleet)"]
        with st.form("parts_form"):
            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input("Date", value=date.today(), key="parts_date")
                veh = st.selectbox("Vehicle", veh_opts, key="parts_veh")
            with c2:
                item = st.selectbox(
                    "Item / type",
                    ["Tyre", "Battery", "Brakes", "Oil / service", "Mechanical fee", "Body / panel", "Electrical", "Other"],
                    key="parts_item",
                )
                amt_s = st.text_input("Amount (M)", value="", placeholder="0.00", key="parts_amt")
            notes_p = st.text_input("Notes", key="parts_notes")
            if st.form_submit_button("Save parts / workshop", type="primary"):
                ensure_extra_tables()
                if veh == "Various (all fleet)":
                    plate = "VARIOUS"
                else:
                    plate = next((v["plate"] for v in VEHICLES if v["name"] == veh), "")
                execute(
                    "INSERT INTO parts_workshop (entry_date, vehicle_name, plate, item, amount, notes) VALUES (?,?,?,?,?,?)",
                    (d.isoformat(), veh, plate, item, parse_amount(amt_s), notes_p),
                )
                st.success("Parts / workshop saved")
                st.rerun()
        try:
            pdf = query_df(
                "SELECT id, entry_date, vehicle_name, plate, item, amount, notes FROM parts_workshop ORDER BY id DESC LIMIT 80"
            )
            if pdf.empty:
                st.info("No parts / workshop entries yet.")
            else:
                if sel_parts_month != "All months":
                    pdf["_d"] = pd.to_datetime(pdf["entry_date"], errors="coerce")
                    pdf = pdf[pdf["_d"].apply(
                        lambda x: next((lab for y, m, lab in FY_MONTHS if x.year == y and x.month == m), "") == sel_parts_month
                        if pd.notna(x) else False
                    )]
                    pdf = pdf.drop(columns=["_d"], errors="ignore")
                st.dataframe(pdf.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)
                st.metric("Total parts (filtered)", money(pd.to_numeric(pdf["amount"], errors="coerce").fillna(0).sum()) if not pdf.empty else money(0))

                st.markdown("**Edit or delete a record**")
                ids = pdf["id"].tolist()
                labels = [
                    f"#{int(r['id'])} · {r['entry_date']} · {r['vehicle_name']} · {r['item']} · {money(r['amount'])}"
                    for _, r in pdf.iterrows()
                ]
                pick = st.selectbox("Select record", range(len(ids)), format_func=lambda i: labels[i], key="parts_edit_sel")
                row = pdf.iloc[pick]
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_date = st.date_input("Edit date", value=date.fromisoformat(str(row["entry_date"])[:10]), key="parts_ed")
                    e_veh = st.selectbox(
                        "Edit vehicle",
                        veh_opts,
                        index=veh_opts.index(row["vehicle_name"]) if row["vehicle_name"] in veh_opts else 0,
                        key="parts_ev",
                    )
                with ec2:
                    item_list = ["Tyre", "Battery", "Brakes", "Oil / service", "Mechanical fee", "Body / panel", "Electrical", "Other"]
                    cur_item = str(row.get("item") or "Other")
                    e_item = st.selectbox(
                        "Edit item",
                        item_list,
                        index=item_list.index(cur_item) if cur_item in item_list else item_list.index("Other"),
                        key="parts_ei",
                    )
                    e_amt = st.text_input("Edit amount (M)", value=format_amount(float(row.get("amount") or 0)), key="parts_ea")
                e_notes = st.text_input("Edit notes", value=str(row.get("notes") or ""), key="parts_en")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Save edits", type="primary", use_container_width=True, key="parts_save_edit"):
                        plate = "VARIOUS" if e_veh == "Various (all fleet)" else next(
                            (v["plate"] for v in VEHICLES if v["name"] == e_veh), ""
                        )
                        execute(
                            "UPDATE parts_workshop SET entry_date=?, vehicle_name=?, plate=?, item=?, amount=?, notes=? WHERE id=?",
                            (e_date.isoformat(), e_veh, plate, e_item, parse_amount(e_amt), e_notes, int(row["id"])),
                        )
                        st.success("Updated")
                        st.rerun()
                with b2:
                    if st.button("Delete record", use_container_width=True, key="parts_del"):
                        execute("DELETE FROM parts_workshop WHERE id=?", (int(row["id"]),))
                        st.success("Deleted")
                        st.rerun()
        except Exception as e:
            ensure_extra_tables()
            st.info("Parts table ready — save your first entry.")
            st.caption(str(e))


def _week_bounds(ref_date=None):
    """Monday–Sunday week containing ref_date."""
    d = ref_date or date.today()
    if hasattr(d, "date"):
        d = d.date()
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def page_contacts():
    st.header("Fleet Contacts")
    st.caption("Sole trader · Maxy Taxi Transport · vehicle phones")
    rows = []
    for v in VEHICLES:
        phones = " / ".join(v.get("phones") or []) or ("Office car" if v.get("role") == "office" else "—")
        rows.append({
            "Vehicle": v["name"],
            "Plate": v["plate"],
            "Type": v["type"],
            "Role": "Office" if v.get("role") == "office" else "Work",
            "Phone(s)": phones,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.info("Alphard is the office / owner car — no driver contact assigned.")


def _week_options_for_month(year, month):
    """List of (label, monday, sunday) for each Mon–Sun week overlapping the month."""
    first = date(year, month, 1)
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    # Start from Monday on or before the 1st
    m = first - timedelta(days=first.weekday())
    opts = []
    while m <= last:
        s = m + timedelta(days=6)
        if s >= first:  # overlaps month
            label = f"{m.strftime('%d %b')} – {s.strftime('%d %b %Y')}"
            opts.append((label, m, s))
        m = m + timedelta(days=7)
    return opts


def _plate_label(row):
    p = str(row.get("plate") or "").strip()
    return p if p else str(row.get("vehicle_name") or "")


def _period_expense_breakdown(df_slice, month_label=None):
    """Totals + listed expenses + gross profit for a filtered daily_records slice."""
    cash = float(df_slice["cash_collected"].sum()) if not df_slice.empty else 0.0
    credits = float(df_slice["credits"].sum()) if not df_slice.empty else 0.0
    fuel = float(df_slice["fuel_cost"].sum()) if not df_slice.empty else 0.0
    topup = float(df_slice["fuel_topup"].sum()) if not df_slice.empty else 0.0
    dcomp = float(df_slice["driver_compensation"].sum()) if not df_slice.empty else 0.0
    airtime = float(df_slice["airtime"].sum()) if not df_slice.empty else 0.0
    revenue = cash + credits
    petrol = fuel + topup

    # Fixed monthly + salaries from monthly_expenses
    fixed = 0.0
    salaries = 0.0
    try:
        if month_label and month_label != "All":
            me = query_df("SELECT * FROM monthly_expenses WHERE expense_month = ?", (month_label,))
        else:
            me = query_df("SELECT * FROM monthly_expenses")
        if me is not None and not me.empty:
            for _, r in me.iterrows():
                for k in ["rent", "wifi", "car_wash", "stationery", "miscellaneous", "maintenance"]:
                    fixed += float(r.get(k) or 0)
                salaries += float(r.get("salaries") or 0)
    except Exception:
        pass

    # Incidents
    incidents = 0.0
    try:
        idf = query_df("SELECT incident_date, amount FROM incidents")
        if idf is not None and not idf.empty:
            idf["_d"] = pd.to_datetime(idf["incident_date"], errors="coerce")
            if month_label and month_label != "All":
                idf = idf[idf["_d"].apply(
                    lambda x: next((lab for y, m, lab in FY_MONTHS if pd.notna(x) and x.year == y and x.month == m), "") == month_label
                )]
            elif not df_slice.empty:
                dmin = df_slice["record_date"].min()
                dmax = df_slice["record_date"].max()
                idf = idf[(idf["_d"] >= dmin) & (idf["_d"] <= dmax)]
            incidents = float(pd.to_numeric(idf["amount"], errors="coerce").fillna(0).sum())
    except Exception:
        pass

    # Parts
    parts = 0.0
    try:
        pdf = query_df("SELECT entry_date, amount FROM parts_workshop")
        if pdf is not None and not pdf.empty:
            pdf["_d"] = pd.to_datetime(pdf["entry_date"], errors="coerce")
            if month_label and month_label != "All":
                pdf = pdf[pdf["_d"].apply(
                    lambda x: next((lab for y, m, lab in FY_MONTHS if pd.notna(x) and x.year == y and x.month == m), "") == month_label
                )]
            elif not df_slice.empty:
                dmin = df_slice["record_date"].min()
                dmax = df_slice["record_date"].max()
                pdf = pdf[(pdf["_d"] >= dmin) & (pdf["_d"] <= dmax)]
            parts = float(pd.to_numeric(pdf["amount"], errors="coerce").fillna(0).sum())
    except Exception:
        pass

    # Asset / vehicle purchase: from Fixed "Asset amount" (vehicle_instalment) + payment log
    vehicle_purchases = 0.0
    try:
        if month_label and month_label != "All":
            me2 = query_df("SELECT vehicle_instalment FROM monthly_expenses WHERE expense_month = ?", (month_label,))
        else:
            me2 = query_df("SELECT vehicle_instalment FROM monthly_expenses")
        if me2 is not None and not me2.empty:
            vehicle_purchases += float(pd.to_numeric(me2["vehicle_instalment"], errors="coerce").fillna(0).sum())
    except Exception:
        pass
    try:
        ap = query_df("SELECT pay_date, amount FROM asset_payments")
        if ap is not None and not ap.empty:
            ap["_d"] = pd.to_datetime(ap["pay_date"], errors="coerce")
            if month_label and month_label != "All":
                ap = ap[ap["_d"].apply(
                    lambda x: next((lab for y, m, lab in FY_MONTHS if pd.notna(x) and x.year == y and x.month == m), "") == month_label
                )]
            # Avoid double-count if user also logged asset_payments AND vehicle_instalment;
            # only add payments when vehicle_instalment total is still 0
            pay_sum = float(pd.to_numeric(ap["amount"], errors="coerce").fillna(0).sum())
            if vehicle_purchases <= 0:
                vehicle_purchases += pay_sum
    except Exception:
        pass

    staff = dcomp + salaries
    expenses = petrol + airtime + staff + fixed + incidents + parts + vehicle_purchases
    gross = revenue - expenses
    return {
        "cash": cash, "credits": credits, "revenue": revenue,
        "petrol": petrol, "airtime": airtime, "staff": staff,
        "dcomp": dcomp, "salaries": salaries,
        "fixed": fixed, "incidents": incidents, "parts": parts,
        "vehicle_purchases": vehicle_purchases,
        "expenses": expenses, "gross": gross,
    }



def _plot_vehicle_bars(byc, key_prefix="chart"):
    """Stable colourful bar charts (HTML) — do not disappear on mobile scroll."""
    if byc is None or byc.empty or "Registration" not in byc.columns:
        return
    df = byc.copy()
    for col in ("Profit", "Revenue", "Expenses"):
        if col not in df.columns:
            return
    df = df.sort_values("Profit", ascending=False)
    max_p = max(float(df["Profit"].abs().max()), 1.0)
    max_r = max(float(df["Revenue"].max()), float(df["Expenses"].max()), 1.0)
    colors = ["#f5a623", "#2ecc71", "#3498db", "#e74c3c", "#9b59b6", "#1abc9c"]
    bars_p = []
    bars_m = []
    for i, (_, r) in enumerate(df.iterrows()):
        reg = str(r["Registration"])
        profit = float(r["Profit"])
        rev = float(r["Revenue"])
        exp = float(r["Expenses"])
        c = colors[i % len(colors)]
        w_p = max(4, int(abs(profit) / max_p * 100))
        bars_p.append(
            f"<div style='margin:8px 0;'>"
            f"<div style='color:#ddd;font-size:12px;margin-bottom:3px;'><b>{reg}</b> · {money(profit)}</div>"
            f"<div style='background:#222;border-radius:6px;height:18px;'>"
            f"<div style='width:{w_p}%;background:{c};height:18px;border-radius:6px;'></div></div></div>"
        )
        bars_m.append(
            f"<div style='margin:10px 0;padding:8px;border:1px solid #333;border-radius:8px;'>"
            f"<div style='color:#fff;font-weight:700;margin-bottom:6px;'>{reg}</div>"
            f"<div style='color:#2ecc71;font-size:11px;'>Revenue {money(rev)}</div>"
            f"<div style='background:#222;border-radius:4px;height:12px;margin:3px 0 6px 0;'>"
            f"<div style='width:{max(4,int(rev/max_r*100))}%;background:#2ecc71;height:12px;border-radius:4px;'></div></div>"
            f"<div style='color:#e74c3c;font-size:11px;'>Expenses {money(exp)}</div>"
            f"<div style='background:#222;border-radius:4px;height:12px;margin:3px 0 6px 0;'>"
            f"<div style='width:{max(4,int(exp/max_r*100))}%;background:#e74c3c;height:12px;border-radius:4px;'></div></div>"
            f"<div style='color:#f5a623;font-size:11px;'>Profit {money(profit)}</div>"
            f"<div style='background:#222;border-radius:4px;height:12px;margin:3px 0;'>"
            f"<div style='width:{max(4,int(abs(profit)/max_p*100))}%;background:#f5a623;height:12px;border-radius:4px;'></div></div>"
            f"</div>"
        )
    st.markdown(
        "<div style='background:#141414;border:1px solid #f5a62355;border-radius:10px;padding:12px;margin:8px 0;'>"
        + "".join(bars_p) + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='background:#141414;border:1px solid #333;border-radius:10px;padding:12px;margin:8px 0;'>"
        + "".join(bars_m) + "</div>",
        unsafe_allow_html=True,
    )



def _expense_cards_html(t):
    """Each expense in its own red-bordered box; amounts in white."""
    items = [
        ("Petrol (fuel + top-up)", t.get("petrol", 0)),
        ("Airtime", t.get("airtime", 0)),
        ("Driver compensation + salary", t.get("staff", 0)),
        ("Fixed monthly (rent, wifi, salaries excl. asset)", t.get("fixed", 0)),
        ("Incidents", t.get("incidents", 0)),
        ("Parts & workshop", t.get("parts", 0)),
        ("Vehicle / asset purchases", t.get("vehicle_purchases", 0)),
        ("Total expenses", t.get("expenses", 0)),
    ]
    cards = []
    for label, val in items:
        is_total = label == "Total expenses"
        weight = "800" if is_total else "700"
        sub = ""
        if label.startswith("Driver compensation"):
            sub = (
                f"<p style='color:#888;font-size:11px;margin:4px 0 0 0;'>"
                f"comp {money(t.get('dcomp', 0))} + salary {money(t.get('salaries', 0))}</p>"
            )
        cards.append(
            f"""
            <div style="border-left:5px solid #e74c3c; background:#141414; border-radius:10px;
                        padding:14px 16px; margin:10px 0;">
              <p style="color:#aaa;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">{label}</p>
              <p style="color:#ffffff;font-weight:{weight};font-size:22px;margin:0;">{money(val)}</p>
              {sub}
            </div>
            """
        )
    return "".join(cards)

def page_weekly_summary():
    st.header("Fleet Summary")
    st.caption("Weekly · Monthly · All · cash, credits, expenses & gross profit")

    tab_w, tab_m, tab_all = st.tabs(["Weekly (Mon–Sun)", "Monthly", "All"])

    df = prepare_records_df()

    with tab_w:
        # Choose month then week within that month
        month_labels = [label for _, _, label in FY_MONTHS]
        # Default to current FY month if possible
        today = date.today()
        default_label = next((lab for y, m, lab in FY_MONTHS if y == today.year and m == today.month), month_labels[0])
        sel_m_label = st.selectbox("Month", month_labels, index=month_labels.index(default_label) if default_label in month_labels else 0, key="ws_month")
        y, mth = next((y, m) for y, m, lab in FY_MONTHS if lab == sel_m_label)
        weeks = _week_options_for_month(y, mth)
        if not weeks:
            st.warning("No weeks in this month.")
        else:
            # Default to week containing today if in this month
            def_idx = 0
            for i, (_, mon, sun) in enumerate(weeks):
                if mon <= today <= sun:
                    def_idx = i
                    break
            wlabel = st.selectbox("Week", [w[0] for w in weeks], index=def_idx, key="ws_week")
            monday, sunday = next((mon, sun) for lab, mon, sun in weeks if lab == wlabel)
            st.write(f"**Week:** {monday.isoformat()} → {sunday.isoformat()}")

            if df.empty:
                st.info("No records yet.")
            else:
                wdf = df[(df["record_date"].dt.date >= monday) & (df["record_date"].dt.date <= sunday)].copy()
                if wdf.empty:
                    st.warning("No daily records in this week.")
                else:
                    wdf["reg"] = wdf.apply(_plate_label, axis=1)
                    cash = wdf["cash_collected"].sum()
                    credits = wdf["credits"].sum()
                    fuel = wdf["fuel_cost"].sum()
                    topup = wdf["fuel_topup"].sum()
                    dcomp = wdf["driver_compensation"].sum()
                    airtime = wdf["airtime"].sum()
                    other = wdf["other_expenses"].sum()
                    trips = int(wdf["trips"].sum())
                    expenses = fuel + topup + dcomp + airtime + other
                    revenue = cash + credits
                    net = revenue - expenses

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Cash", money(cash))
                    c2.metric("Credits / contracts", money(credits))
                    c3.metric("Total revenue", money(revenue))
                    c4.metric("Net", money(net))
                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric("Fuel", money(fuel))
                    c6.metric("Top-up", money(topup))
                    c7.metric("Driver comp", money(dcomp))
                    c8.metric("Trips", trips)

                    st.markdown("**By registration number**")
                    byv = wdf.groupby("reg").agg({
                        "cash_collected": "sum", "credits": "sum", "fuel_cost": "sum",
                        "fuel_topup": "sum", "driver_compensation": "sum", "airtime": "sum",
                        "other_expenses": "sum", "trips": "sum",
                    }).reset_index().rename(columns={"reg": "Registration"})
                    byv["Net"] = (byv["cash_collected"] + byv["credits"]
                                  - byv["fuel_cost"] - byv["fuel_topup"]
                                  - byv["driver_compensation"] - byv["airtime"] - byv["other_expenses"])
                    st.dataframe(byv, use_container_width=True, hide_index=True)

                    st.markdown("**Credits breakdown**")
                    for col, label in [
                        ("credit_alliance", "Alliance"), ("credit_lehae", "Lehae"),
                        ("credit_worldvision", "World Vision"), ("credit_waleslink", "Waleslink"),
                        ("credit_lnlvip", "LNLVIP"),
                    ]:
                        if col in wdf.columns:
                            st.write(f"- {label}: **{money(wdf[col].sum())}**")

                    wa = (
                        f"Maxy Taxi week {monday.strftime('%d %b')}–{sunday.strftime('%d %b')}: "
                        f"cash {money(cash)}, credits {money(credits)}, fuel {money(fuel)}, "
                        f"trips {trips}, net {money(net)}"
                    )
                    st.text_area("WhatsApp summary (copy)", value=wa, height=70, key="ws_wa")

                    try:
                        pdf_bytes = generate_weekly_summary_pdf(monday, sunday, wdf, byv, cash, credits, fuel, topup, dcomp, airtime, other, trips, net)
                        st.download_button(
                            "Download weekly summary PDF",
                            pdf_bytes,
                            f"maxy_weekly_{monday.isoformat()}.pdf",
                            "application/pdf",
                            use_container_width=True,
                            type="primary",
                        )
                    except Exception as e:
                        st.caption(f"PDF unavailable: {e}")

    with tab_m:
        month_labels = [label for _, _, label in FY_MONTHS]
        sel = st.selectbox("Month", month_labels, key="sum_month")
        mdf = df[df["fy_month"] == sel] if not df.empty else df
        t = _period_expense_breakdown(mdf, month_label=sel)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total cash", money(t["cash"]))
        c2.metric("Credits", money(t["credits"]))
        c3.metric("Total revenue", money(t["revenue"]))
        st.markdown(_expense_cards_html(t), unsafe_allow_html=True)
        st.markdown(f"""
        <div style="border-left:5px solid #2ecc71; background:#122016; border-radius:10px; padding:14px 16px; margin:8px 0 12px 0;">
          <p style="color:#aaa;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">Gross profit</p>
          <p style="color:#2ecc71;font-weight:800;margin:0;font-size:22px;">{money(t['gross'])}</p>
        </div>
        """, unsafe_allow_html=True)
        petrol_p = LESOTHO_PETROL_95.get(sel)
        if petrol_p:
            st.caption(f"Lesotho Petrol 95 that month: **M{petrol_p:.2f}/L**")


        # Per car breakdown + colourful bar chart
        st.subheader("Per vehicle")
        if not mdf.empty:
            mdf2 = mdf.copy()
            mdf2["reg"] = mdf2.apply(_plate_label, axis=1)
            byc = mdf2.groupby("reg").agg({
                "cash_collected": "sum", "credits": "sum",
                "fuel_cost": "sum", "fuel_topup": "sum",
                "driver_compensation": "sum", "airtime": "sum", "trips": "sum",
            }).reset_index().rename(columns={"reg": "Registration"})
            byc["Revenue"] = byc["cash_collected"] + byc["credits"]
            byc["Expenses"] = byc["fuel_cost"] + byc["fuel_topup"] + byc["driver_compensation"] + byc["airtime"]
            byc["Profit"] = byc["Revenue"] - byc["Expenses"]
            st.dataframe(byc, use_container_width=True, hide_index=True)
            st.markdown("**Colourful profit chart (this month)**")
            _plot_vehicle_bars(byc, key_prefix="fs_month")
        else:
            st.caption("No daily records for this month.")

    with tab_all:
        st.caption("Full financial year 2026–2027")
        t = _period_expense_breakdown(df if not df.empty else pd.DataFrame(), month_label="All")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total cash", money(t["cash"]))
        c2.metric("Credits", money(t["credits"]))
        c3.metric("Total revenue", money(t["revenue"]))
        st.markdown(_expense_cards_html(t), unsafe_allow_html=True)
        st.markdown(f"""
        <div style="border-left:5px solid #2ecc71; background:#122016; border-radius:10px; padding:14px 16px; margin:8px 0 12px 0;">
          <p style="color:#aaa;font-size:11px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">Gross profit</p>
          <p style="color:#2ecc71;font-weight:800;margin:0;font-size:22px;">{money(t['gross'])}</p>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Per vehicle (all months)")
        if not df.empty:
            df_all = df.copy()
            df_all["reg"] = df_all.apply(_plate_label, axis=1)
            by_all = df_all.groupby("reg").agg({
                "cash_collected": "sum", "credits": "sum",
                "fuel_cost": "sum", "fuel_topup": "sum",
                "driver_compensation": "sum", "airtime": "sum", "trips": "sum",
            }).reset_index().rename(columns={"reg": "Registration"})
            by_all["Revenue"] = by_all["cash_collected"] + by_all["credits"]
            by_all["Expenses"] = by_all["fuel_cost"] + by_all["fuel_topup"] + by_all["driver_compensation"] + by_all["airtime"]
            by_all["Profit"] = by_all["Revenue"] - by_all["Expenses"]
            st.dataframe(by_all, use_container_width=True, hide_index=True)
            st.markdown("**Colourful profit chart (all months)**")
            _plot_vehicle_bars(by_all, key_prefix="fs_all")
        else:
            st.caption("No records yet.")


def page_fuel_prices():
    st.header("Fuel Prices (Lesotho)")
    st.caption("Official Petrol 95 pump prices · Petroleum Fund")
    rows = [{"Month": m, "Petrol 95 (M/L)": p} for m, p in LESOTHO_PETROL_95.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("""
    | Month | Petrol 95 |
    |-------|-----------|
    | June 2026 | M26.20 |
    | July 2026 | M23.85 |
    | August 2026 | M24.05 |
    | September 2026 | M24.80 |
    | October 2026 | M28.60 |
    | November 2026 | M29.25 |
    """)
    st.caption("Source: Petroleum Fund / Data Matrix. Update when new gazette is published.")

    df = prepare_records_df()
    if not df.empty:
        st.subheader("Your fuel spend vs pump price")
        for label, price in LESOTHO_PETROL_95.items():
            mdf = df[df["fy_month"] == label]
            if mdf.empty:
                continue
            spend = mdf["fuel_cost"].sum() + mdf["fuel_topup"].sum()
            litres = spend / price if price else 0
            st.write(f"**{label}:** fuel+top-up {money(spend)} ≈ **{litres:,.0f} L** at M{price:.2f}/L")


def page_profit():
    st.header("Profit by Vehicle")
    st.caption("Totals by registration number")
    mode = st.radio("Period", ["Weekly (Mon–Sun)", "Month"], horizontal=True)
    df = prepare_records_df()
    if df.empty:
        st.info("No records yet.")
        return

    if mode.startswith("Weekly"):
        month_labels = [label for _, _, label in FY_MONTHS]
        today = date.today()
        default_label = next((lab for y, m, lab in FY_MONTHS if y == today.year and m == today.month), month_labels[0])
        sel_m_label = st.selectbox("Month", month_labels, index=month_labels.index(default_label) if default_label in month_labels else 0, key="profit_ws_month")
        y, mth = next((y, m) for y, m, lab in FY_MONTHS if lab == sel_m_label)
        weeks = _week_options_for_month(y, mth)
        if not weeks:
            st.warning("No weeks.")
            return
        def_idx = 0
        for i, (_, mon, sun) in enumerate(weeks):
            if mon <= today <= sun:
                def_idx = i
                break
        wlabel = st.selectbox("Week", [w[0] for w in weeks], index=def_idx, key="profit_ws_week")
        monday, sunday = next((mon, sun) for lab, mon, sun in weeks if lab == wlabel)
        st.caption(f"{monday} → {sunday}")
        fdf = df[(df["record_date"].dt.date >= monday) & (df["record_date"].dt.date <= sunday)].copy()
    else:
        labels = [label for _, _, label in FY_MONTHS]
        sel = st.selectbox("Month", labels, key="profit_month")
        fdf = df[df["fy_month"] == sel].copy()

    if fdf.empty:
        st.warning("No data for this period.")
        return

    fdf["reg"] = fdf.apply(_plate_label, axis=1)
    byv = fdf.groupby("reg").agg({
        "cash_collected": "sum", "credits": "sum", "fuel_cost": "sum",
        "fuel_topup": "sum", "driver_compensation": "sum", "airtime": "sum",
        "other_expenses": "sum", "trips": "sum",
    }).reset_index().rename(columns={"reg": "Registration"})
    byv["Revenue"] = byv["cash_collected"] + byv["credits"]
    byv["Expenses"] = (byv["fuel_cost"] + byv["fuel_topup"] + byv["driver_compensation"]
                       + byv["airtime"] + byv["other_expenses"])
    byv["Profit"] = byv["Revenue"] - byv["Expenses"]
    byv = byv.sort_values("Profit", ascending=False)
    st.dataframe(byv, use_container_width=True, hide_index=True)
    st.metric("Fleet profit (period)", money(byv["Profit"].sum()))

    st.subheader("Profit bar chart (per vehicle)")
    _plot_vehicle_bars(byv, key_prefix="profit_page")


def page_incidents():
    st.header("Incidents & Fines")
    with st.form("incident_form"):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
            veh = st.selectbox("Vehicle", [v["name"] for v in VEHICLES])
        with c2:
            cat = st.selectbox("Category", ["Fine", "Accident", "Damage", "Police", "Other"])
            amt_s = st.text_input("Amount (M)", value="", placeholder="0.00")
        notes = st.text_input("Notes")
        if st.form_submit_button("Save", type="primary"):
            plate = next((v["plate"] for v in VEHICLES if v["name"] == veh), "")
            execute(
                "INSERT INTO incidents (incident_date, vehicle_name, plate, category, amount, notes) VALUES (?,?,?,?,?,?)",
                (d.isoformat(), veh, plate, cat, parse_amount(amt_s), notes),
            )
            st.success("Saved")
            st.rerun()
    idf = query_df("SELECT incident_date, vehicle_name, category, amount, notes FROM incidents ORDER BY id DESC LIMIT 50")
    if idf.empty:
        st.info("No incidents logged.")
    else:
        st.dataframe(idf, use_container_width=True, hide_index=True)


def page_parts():
    st.header("Parts & Workshop")
    with st.form("parts_form"):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today(), key="parts_date")
            veh = st.selectbox("Vehicle", [v["name"] for v in VEHICLES], key="parts_veh")
        with c2:
            item = st.text_input("Item (tyre, battery, brakes…)")
            amt_s = st.text_input("Amount (M)", value="", placeholder="0.00", key="parts_amt")
        notes = st.text_input("Notes", key="parts_notes")
        if st.form_submit_button("Save", type="primary"):
            plate = next((v["plate"] for v in VEHICLES if v["name"] == veh), "")
            execute(
                "INSERT INTO parts_workshop (entry_date, vehicle_name, plate, item, amount, notes) VALUES (?,?,?,?,?,?)",
                (d.isoformat(), veh, plate, item, parse_amount(amt_s), notes),
            )
            st.success("Saved")
            st.rerun()
    pdf = query_df("SELECT entry_date, vehicle_name, item, amount, notes FROM parts_workshop ORDER BY id DESC LIMIT 50")
    if pdf.empty:
        st.info("No parts / workshop entries yet.")
    else:
        st.dataframe(pdf, use_container_width=True, hide_index=True)


def _night_car_for_week(monday):
    """
    One work car covers night shift Mon → Sunday morning 6am.
    Order: A945 → A765 → A943 → A940 → A238 → (repeat)
    Anchor Monday 9 Nov 2026 = A 945 BDL (until Sun 15 Nov 06:00).
    """
    order_plates = ["A 945 BDL", "A 765 BGR", "A 943 BDL", "A 940 BDL", "A 238 BGN"]
    anchor = date(2026, 11, 9)
    if hasattr(monday, "date"):
        monday = monday.date()
    week_index = (monday - anchor).days // 7
    plate = order_plates[week_index % 5]
    car = next(
        (v for v in VEHICLES if v["plate"].replace(" ", "") == plate.replace(" ", "")),
        None,
    )
    return car, plate


def page_night_duty():
    st.header("Night Duty Roster")
    st.caption("One car per week · Monday → Sunday 6am · Alphard is office only")

    # Force "right now" to the active night week (Sun before 6am still counts as that week)
    today = date.today()
    active_monday, _ = _week_bounds(today)
    car_now, plate_now = _night_car_for_week(active_monday)
    # Week Mon 9 Nov → Sun 15 Nov 6am = A 945 BDL
    phones_now = " / ".join((car_now or {}).get("phones") or []) or "—"

    st.markdown(f"""
    <div style="border:1px solid #f5a62355; border-radius:12px; padding:14px 16px; background:#1a1508; margin:8px 0 14px 0;">
      <p style="color:#f5a623; font-weight:700; margin:0 0 6px 0;">Night car right now</p>
      <p style="color:#fff; font-size:22px; font-weight:800; margin:0;">{plate_now}</p>
      <p style="color:#ccc; font-size:13px; margin:6px 0 0 0;">
        {(car_now or {}).get('name', '')} · {active_monday.strftime('%d %b')} → Sunday 6am · {phones_now}
      </p>
    </div>
    """, unsafe_allow_html=True)

    pick = st.date_input("View another week (any day)", value=active_monday, key="night_pick")
    monday, sunday = _week_bounds(pick)
    car, plate = _night_car_for_week(monday)
    phones = " / ".join((car or {}).get("phones") or []) or "—"
    st.write(f"**Selected week:** {plate} · {(car or {}).get('name', '')} · {monday} → Sunday 6am · {phones}")

    st.markdown("**Rotation order:** A 945 BDL → A 765 BGR → A 943 BDL → A 940 BDL → A 238 BGN → …")

    upcoming = []
    for i in range(0, 6):
        m = active_monday + timedelta(days=7 * i)
        c, p = _night_car_for_week(m)
        upcoming.append({
            "Week starts (Mon)": m.isoformat(),
            "Ends (Sun 6am)": (m + timedelta(days=6)).isoformat(),
            "Plate": p,
            "Vehicle": (c or {}).get("name", ""),
        })
    st.dataframe(pd.DataFrame(upcoming), use_container_width=True, hide_index=True)

    # October 2026 weeks
    st.subheader("October 2026 night cars")
    oct_rows = []
    d = date(2026, 10, 1)
    # first Monday on or before Oct 1 that starts a week overlapping October
    m0 = d - timedelta(days=d.weekday())
    if m0.month == 9:
        # include late Sep week only if it runs into Oct nights — show from first Monday in Oct
        m0 = m0 + timedelta(days=7)
    while m0.month <= 10 and m0.year == 2026:
        c, p = _night_car_for_week(m0)
        oct_rows.append({
            "Week Mon": m0.isoformat(),
            "To Sun morning": (m0 + timedelta(days=6)).isoformat(),
            "Night car": (c or {}).get("name", ""),
            "Plate": p,
        })
        m0 = m0 + timedelta(days=7)
        if m0.month > 10:
            break
    st.dataframe(pd.DataFrame(oct_rows), use_container_width=True, hide_index=True)

    # Recorded Night rows for selected week
    df = prepare_records_df()
    if not df.empty:
        wdf = df[(df["record_date"].dt.date >= monday) & (df["record_date"].dt.date <= sunday)]
        night = wdf[wdf["duty"].astype(str).str.lower() == "night"] if not wdf.empty else wdf
        st.subheader("Recorded Night entries (this week)")
        if night is not None and not night.empty:
            st.dataframe(
                night[["record_date", "vehicle_name", "plate", "driver_name", "cash_collected", "trips"]],
                use_container_width=True, hide_index=True,
            )
            # Flag mismatches
            wrong = night[night["plate"].astype(str).str.replace(" ", "") != plate.replace(" ", "")]
            if not wrong.empty:
                st.warning(
                    f"Some Night records are not on roster car **{plate}**. "
                    "Edit them under Records if they should follow the roster."
                )
        else:
            st.caption("No Night duty records for this week yet.")


def page_receipts():
    st.header("Receipts")
    st.caption("Official payment receipts · PDF ready to print or share")

    ensure_extra_tables()

    with st.expander("Create receipt", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            received_from = st.text_input("Received from *", placeholder="Client / company / passenger name", key="rc_from")
            rdate = st.date_input("Receipt date", value=date.today(), key="rc_date")
        with c2:
            pay_method = st.selectbox(
                "Payment method",
                ["Cash", "Bank transfer", "Mobile money", "Cheque", "Other"],
                key="rc_pay",
            )
            # Optional link to unpaid / any invoice
            invs = query_df("SELECT invoice_number, client_name, amount FROM invoices ORDER BY id DESC LIMIT 40")
            inv_opts = ["— None —"] + (
                [f"{r['invoice_number']} · {r['client_name']} · {money(r['amount'])}" for _, r in invs.iterrows()]
                if not invs.empty else []
            )
            related = st.selectbox("Related invoice (optional)", inv_opts, key="rc_inv")

        st.markdown("""
        <div style="background:#1a1a1a; border:1px solid #f5a62355; border-radius:10px; padding:10px 12px; margin:10px 0 6px 0;">
            <p style="color:#f5a623; font-weight:700; margin:0; letter-spacing:1px; font-size:13px;">
                DESCRIPTION &nbsp;&nbsp;|&nbsp;&nbsp; QTY &nbsp;&nbsp;|&nbsp;&nbsp; AMOUNT (M)
            </p>
        </div>
        """, unsafe_allow_html=True)

        _rc_seed = pd.DataFrame({
            "DESCRIPTION": ["", "", ""],
            "QTY": [None, None, None],
            "AMOUNT (M)": [None, None, None],
        })
        edited_rc = st.data_editor(
            _rc_seed,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="rc_line_editor",
            column_config={
                "DESCRIPTION": st.column_config.TextColumn("DESCRIPTION", width="large"),
                "QTY": st.column_config.NumberColumn("QTY", min_value=0, step=1, format="%d"),
                "AMOUNT (M)": st.column_config.NumberColumn("AMOUNT (M)", min_value=0.0, step=50.0, format="%.2f"),
            },
        )
        try:
            rc_total = float(pd.to_numeric(edited_rc["AMOUNT (M)"], errors="coerce").fillna(0).sum())
        except Exception:
            rc_total = 0.0
        st.metric("Total received", money(rc_total))
        notes = st.text_input("Notes (optional)", key="rc_notes")

        if st.button("Create receipt", type="primary", use_container_width=True):
            if not received_from.strip():
                st.error("Received from is required.")
            elif rc_total <= 0:
                st.error("Enter at least one amount in the table.")
            else:
                lines = []
                for _, r in edited_rc.iterrows():
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
                year = date.today().year
                last = query_df(
                    "SELECT receipt_number FROM receipts WHERE receipt_number LIKE ? ORDER BY id DESC LIMIT 1",
                    (f"RCT-{year}-%",),
                )
                if last.empty:
                    num = 1
                else:
                    try:
                        num = int(str(last.iloc[0]["receipt_number"]).split("-")[-1]) + 1
                    except Exception:
                        num = 1
                rct_no = f"RCT-{year}-{num:04d}"
                rel_inv = ""
                if related and related != "— None —":
                    rel_inv = related.split("·")[0].strip()
                execute(
                    """INSERT INTO receipts
                       (receipt_number, receipt_date, received_from, description, amount, payment_method, related_invoice, notes)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (rct_no, rdate.isoformat(), received_from.strip(), description, rc_total,
                     pay_method, rel_inv, notes or ""),
                )
                if "rc_line_editor" in st.session_state:
                    del st.session_state["rc_line_editor"]
                st.success(f"Receipt {rct_no} created!")
                st.rerun()

    st.subheader("All receipts")
    rdf = query_df(
        "SELECT id, receipt_number, receipt_date, received_from, amount, payment_method, related_invoice "
        "FROM receipts ORDER BY id DESC"
    )
    if rdf.empty:
        st.info("No receipts yet.")
    else:
        st.dataframe(rdf, use_container_width=True, hide_index=True)
        nums = rdf["receipt_number"].tolist()
        selected = st.selectbox("Select receipt", nums, key="rc_pdf_sel")
        rowdf = query_df("SELECT * FROM receipts WHERE receipt_number = ?", (selected,))
        if not rowdf.empty:
            rec = rowdf.iloc[0].to_dict()
            pdf = generate_receipt_pdf(rec)
            st.download_button(
                f"⬇️ Download {selected}.pdf",
                pdf.getvalue() if hasattr(pdf, "getvalue") else pdf,
                f"{selected}.pdf",
                "application/pdf",
                use_container_width=True,
                type="primary",
            )
            st.markdown("### Edit or delete receipt")
            re_from = st.text_input("Received from", value=str(rec.get("received_from") or ""), key="r_edit_from")
            re_amt = st.number_input("Amount", value=float(rec.get("amount") or 0), min_value=0.0, format="%.2f", key="r_edit_amt")
            re_pay = st.selectbox(
                "Payment method",
                ["Cash", "Bank transfer", "Mobile money", "Cheque", "Other"],
                index=max(0, ["Cash", "Bank transfer", "Mobile money", "Cheque", "Other"].index(rec.get("payment_method")) if rec.get("payment_method") in ["Cash", "Bank transfer", "Mobile money", "Cheque", "Other"] else 0),
                key="r_edit_pay",
            )
            re_desc = st.text_area("Description / lines", value=str(rec.get("description") or ""), key="r_edit_desc")
            cre1, cre2 = st.columns(2)
            with cre1:
                if st.button("Save receipt edits", type="primary", use_container_width=True, key="r_save"):
                    execute(
                        "UPDATE receipts SET received_from=?, amount=?, payment_method=?, description=? WHERE receipt_number=?",
                        (re_from, re_amt, re_pay, re_desc, selected),
                    )
                    st.success("Receipt updated")
                    st.rerun()
            with cre2:
                if st.button("Delete receipt", use_container_width=True, key="r_del"):
                    execute("DELETE FROM receipts WHERE receipt_number=?", (selected,))
                    st.success("Receipt deleted")
                    st.rerun()


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
                type="primary",
                key="dl_full_xlsx",
                on_click=_set_meta,
                args=("last_backup_date", date.today().isoformat()),
            )
        # Record backup time when user is on this page after downloading
        if st.button("Mark backup done today", use_container_width=True):
            _set_meta("last_backup_date", date.today().isoformat())
            st.success("Backup date saved — red reminder will clear for 7 days.")
            st.rerun()
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
def page_documents():
    """Single menu entry: Quotations / Invoices / Receipts."""
    st.header("Documents")
    st.caption("Quotations · Invoices · Receipts")
    t1, t2, t3 = st.tabs(["Quotations", "Invoices", "Receipts"])
    with t1:
        page_quotations()
    with t2:
        page_invoices()
    with t3:
        page_receipts()


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
        <p style="text-align:center; color:#e74c3c; font-size:12px; margin:8px 0 0 0; font-weight:700;">
        Merry Christmas
        </p>
        <p style="text-align:center; color:#c9a227; font-size:10px; margin:2px 0 0 0;">
        Season of safe journeys
        </p>
    </div>
    """, unsafe_allow_html=True)

    pages = {
        "Dashboard": page_dashboard,
        "Daily Entry": page_daily_entry,
        "Records": page_records,
        "Fleet Summary": page_weekly_summary,
        "Profit by Vehicle": page_profit,
        "Fleet": page_vehicles,
        "Contacts": page_contacts,
        "Night Duty": page_night_duty,
        "Fuel Prices": page_fuel_prices,
        "Clients": page_clients,
        "Monthly Expenses": page_monthly_expenses,
        "Documents": page_documents,
        "Backup / Export": page_export,
    }

    menu_labels = {k: k for k in pages.keys()}
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
