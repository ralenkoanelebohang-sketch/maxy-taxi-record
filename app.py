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
    page_title="Maxy Taxi Records",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== PASSWORD PROTECTION ==========
# Change this password to whatever you want
APP_PASSWORD = "MaxyTaxi2026"

def check_password():
    """Returns True if the user entered the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🚕 Maxy Taxi")
    st.caption("SAFE • QUICK • RELIABLE")
    st.subheader("Business Records Login")
    st.write("Enter the password to continue.")

    password = st.text_input("Password", type="password", key="password_input")
    col1, col2 = st.columns([1, 3])
    with col1:
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
BUSINESS_PHONE = "+266 27335933 / 68335933"
BUSINESS_WHATSAPP = "+266 56432571"
BUSINESS_EMAIL = "maxytaxicab@gmail.com"
BUSINESS_TIN = ""            # Add your TIN later if needed
CURRENCY = "M"

# Monthly credit clients
CREDIT_CLIENTS = ["Alliance", "Lehae", "World Vision", "Waleslink"]

VEHICLES = [
    {"id": 1, "name": "Honda Fit 1", "plate": "A 940 BDL", "type": "Honda Fit"},
    {"id": 2, "name": "Honda Fit 2", "plate": "A 943 BDL", "type": "Honda Fit"},
    {"id": 3, "name": "Honda Fit 3", "plate": "A 945 BDL", "type": "Honda Fit"},
    {"id": 4, "name": "Honda Fit 4", "plate": "A 238 BGN", "type": "Honda Fit"},
    {"id": 5, "name": "Honda Fit 5", "plate": "A 765 BGR", "type": "Honda Fit"},
    {"id": 6, "name": "Toyota Alphard", "plate": "A 313 BCM", "type": "Alphard 7-seater"},
]

# ---------------------- DATABASE ----------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            vehicle_id INTEGER NOT NULL,
            vehicle_name TEXT,
            plate TEXT,
            cash_collected REAL DEFAULT 0,
            fuel_cost REAL DEFAULT 0,
            trips INTEGER DEFAULT 0,
            other_expenses REAL DEFAULT 0,
            expense_notes TEXT,
            credit_alliance REAL DEFAULT 0,
            credit_lehae REAL DEFAULT 0,
            credit_worldvision REAL DEFAULT 0,
            credit_waleslink REAL DEFAULT 0,
            driver_name TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add new columns if upgrading existing DB
    for col in ["credit_alliance", "credit_lehae", "credit_worldvision", "credit_waleslink"]:
        try:
            c.execute(f"ALTER TABLE daily_records ADD COLUMN {col} REAL DEFAULT 0")
        except:
            pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    c.execute("""
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_number TEXT UNIQUE,
            client_id INTEGER,
            client_name TEXT,
            quote_date TEXT,
            valid_until TEXT,
            description TEXT,
            amount REAL,
            status TEXT DEFAULT 'Draft',  -- Draft, Sent, Accepted, Rejected, Expired
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE,
            client_id INTEGER,
            client_name TEXT,
            invoice_date TEXT,
            due_date TEXT,
            description TEXT,
            amount REAL,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'Unpaid',  -- Unpaid, Partial, Paid, Overdue, Cancelled
            related_quote_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def query_df(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

# ---------------------- PDF HELPERS ----------------------
def create_pdf_buffer():
    buffer = BytesIO()
    return buffer

def generate_invoice_pdf(invoice, client=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER,
        spaceAfter=2*mm, textColor=colors.HexColor("#1a1a1a")
    )
    subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"), spaceAfter=4*mm
    )
    heading = ParagraphStyle(
        'Heading', parent=styles['Heading2'], fontSize=12, spaceBefore=4*mm, spaceAfter=2*mm
    )
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14)
    right = ParagraphStyle('Right', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10, leading=14)

    # Header with logo (Letterhead)
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=170*mm, height=35*mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 3*mm))
    else:
        # Fallback text header if logo not found
        elements.append(Paragraph(BUSINESS_NAME.upper(), title_style))
        elements.append(Paragraph(BUSINESS_TAGLINE, subtitle))
        elements.append(Paragraph(BUSINESS_LOCATION, subtitle))
        contact_lines = f"Tel: {BUSINESS_PHONE}  |  WhatsApp: {BUSINESS_WHATSAPP}"
        elements.append(Paragraph(contact_lines, subtitle))
        elements.append(Paragraph(f"Email: {BUSINESS_EMAIL}", subtitle))

    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#f5a623"), spaceAfter=4*mm))

    # Invoice title
    elements.append(Paragraph("TAX INVOICE", ParagraphStyle('InvTitle', parent=styles['Heading1'],
                                                             fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor("#c0392b"))))
    elements.append(Spacer(1, 3*mm))

    # Meta info
    meta_data = [
        [Paragraph(f"<b>Invoice No:</b> {invoice['invoice_number']}", normal),
         Paragraph(f"<b>Date:</b> {invoice['invoice_date']}", right)],
        [Paragraph(f"<b>Status:</b> {invoice['status']}", normal),
         Paragraph(f"<b>Due Date:</b> {invoice['due_date']}", right)],
    ]
    meta_table = Table(meta_data, colWidths=[95*mm, 85*mm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 4*mm))

    # Bill To
    elements.append(Paragraph("<b>BILL TO</b>", heading))
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
    elements.append(Spacer(1, 4*mm))

    # Description / Items
    elements.append(Paragraph("<b>DESCRIPTION OF SERVICES</b>", heading))
    desc = invoice.get('description') or "Transport services"
    amount = float(invoice.get('amount') or 0)
    paid = float(invoice.get('amount_paid') or 0)
    balance = amount - paid

    items_data = [
        [Paragraph("<b>Description</b>", bold), Paragraph("<b>Amount (M)</b>", bold)],
        [Paragraph(desc.replace("\n", "<br/>"), normal), Paragraph(f"{amount:,.2f}", right)],
    ]
    items_table = Table(items_data, colWidths=[130*mm, 50*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f5a623")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#fff8e7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))

    # Totals
    totals_data = [
        [Paragraph("<b>Subtotal</b>", normal), Paragraph(f"M {amount:,.2f}", right)],
        [Paragraph("<b>Amount Paid</b>", normal), Paragraph(f"M {paid:,.2f}", right)],
        [Paragraph("<b>BALANCE DUE</b>", ParagraphStyle('Bal', parent=normal, textColor=colors.HexColor("#c0392b"), fontSize=11)),
         Paragraph(f"<b>M {balance:,.2f}</b>", ParagraphStyle('BalR', parent=right, textColor=colors.HexColor("#c0392b"), fontSize=11))],
    ]
    totals_table = Table(totals_data, colWidths=[130*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor("#c0392b")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(totals_table)

    if invoice.get('notes'):
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("<b>Notes</b>", heading))
        elements.append(Paragraph(invoice['notes'], normal))

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Paragraph("Thank you for your business. Payment can be made to Maxy Taxi Transport (Postbank).",
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
    elements.append(Paragraph("This is a computer-generated document.",
                              ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_quotation_pdf(quote, client=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER,
                                 spaceAfter=2*mm, textColor=colors.HexColor("#1a1a1a"))
    subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER,
                              textColor=colors.HexColor("#555555"), spaceAfter=4*mm)
    heading = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, spaceBefore=4*mm, spaceAfter=2*mm)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14)
    right = ParagraphStyle('Right', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10)

    # Header with logo (Letterhead)
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=170*mm, height=35*mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 3*mm))
    else:
        elements.append(Paragraph(BUSINESS_NAME.upper(), title_style))
        elements.append(Paragraph(BUSINESS_TAGLINE, subtitle))
        elements.append(Paragraph(BUSINESS_LOCATION, subtitle))
        contact_lines = f"Tel: {BUSINESS_PHONE}  |  WhatsApp: {BUSINESS_WHATSAPP}"
        elements.append(Paragraph(contact_lines, subtitle))
        elements.append(Paragraph(f"Email: {BUSINESS_EMAIL}", subtitle))

    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#f5a623"), spaceAfter=4*mm))

    elements.append(Paragraph("QUOTATION", ParagraphStyle('QTitle', parent=styles['Heading1'],
                                                           fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor("#2980b9"))))
    elements.append(Spacer(1, 3*mm))

    meta_data = [
        [Paragraph(f"<b>Quote No:</b> {quote['quote_number']}", normal),
         Paragraph(f"<b>Date:</b> {quote['quote_date']}", right)],
        [Paragraph(f"<b>Status:</b> {quote['status']}", normal),
         Paragraph(f"<b>Valid Until:</b> {quote['valid_until']}", right)],
    ]
    meta_table = Table(meta_data, colWidths=[95*mm, 85*mm])
    meta_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 4*mm))

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
    elements.append(Spacer(1, 4*mm))

    elements.append(Paragraph("<b>DESCRIPTION OF SERVICES</b>", heading))
    desc = quote.get('description') or "Transport services"
    amount = float(quote.get('amount') or 0)

    items_data = [
        [Paragraph("<b>Description</b>", bold), Paragraph("<b>Amount (M)</b>", bold)],
        [Paragraph(desc.replace("\n", "<br/>"), normal), Paragraph(f"{amount:,.2f}", right)],
    ]
    items_table = Table(items_data, colWidths=[130*mm, 50*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#eaf2f8")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))

    total_data = [[Paragraph("<b>TOTAL QUOTED</b>", ParagraphStyle('T', parent=normal, fontSize=11)),
                   Paragraph(f"<b>M {amount:,.2f}</b>", ParagraphStyle('TR', parent=right, fontSize=11))]]
    total_table = Table(total_data, colWidths=[130*mm, 50*mm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#2980b9")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(total_table)

    if quote.get('notes'):
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("<b>Notes / Terms</b>", heading))
        elements.append(Paragraph(quote['notes'], normal))

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Paragraph("This quotation is valid until the date shown. Prices are in Lesotho Loti (M).",
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
    elements.append(Paragraph("Thank you for considering Maxy Taxi Transport.",
                              ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------- UI HELPERS ----------------------
def money(x):
    try:
        return f"M {float(x):,.2f}"
    except:
        return "M 0.00"

def vehicle_options():
    return {f"{v['name']} ({v['plate']})": v for v in VEHICLES}

# ---------------------- PAGES ----------------------
def page_dashboard():
    st.header("📊 Dashboard")
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Summary cards
    df = query_df("SELECT * FROM daily_records")
    if not df.empty:
        df['record_date'] = pd.to_datetime(df['record_date'])
        today_df = df[df['record_date'].dt.date == today]
        week_df = df[df['record_date'].dt.date >= week_start]
        month_df = df[df['record_date'].dt.date >= month_start]

        def total_credits(d):
            return (d.get('credit_alliance', pd.Series([0])).sum() +
                    d.get('credit_lehae', pd.Series([0])).sum() +
                    d.get('credit_worldvision', pd.Series([0])).sum() +
                    d.get('credit_waleslink', pd.Series([0])).sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Today Cash", money(today_df['cash_collected'].sum()))
        c2.metric("This Week Cash", money(week_df['cash_collected'].sum()))
        c3.metric("This Month Cash", money(month_df['cash_collected'].sum()))
        c4.metric("Month Credits", money(total_credits(month_df)))

        st.subheader("This Month by Vehicle")
        if not month_df.empty:
            by_veh = month_df.groupby('vehicle_name').agg({
                'cash_collected': 'sum',
                'fuel_cost': 'sum',
                'other_expenses': 'sum',
                'trips': 'sum',
                'credit_alliance': 'sum',
                'credit_lehae': 'sum',
                'credit_worldvision': 'sum',
                'credit_waleslink': 'sum',
            }).reset_index()
            by_veh['Total Credits'] = (by_veh['credit_alliance'] + by_veh['credit_lehae'] +
                                       by_veh['credit_worldvision'] + by_veh['credit_waleslink'])
            by_veh['Net'] = by_veh['cash_collected'] + by_veh['Total Credits'] - by_veh['fuel_cost'] - by_veh['other_expenses']
            by_veh = by_veh[['vehicle_name', 'cash_collected', 'Total Credits', 'fuel_cost', 'other_expenses', 'trips', 'Net']]
            by_veh.columns = ['Vehicle', 'Cash In', 'Credits', 'Fuel Cost', 'Other Exp', 'Trips', 'Net']
            st.dataframe(by_veh.style.format({
                'Cash In': 'M {:,.0f}', 'Credits': 'M {:,.0f}',
                'Fuel Cost': 'M {:,.0f}', 'Other Exp': 'M {:,.0f}',
                'Net': 'M {:,.0f}'
            }), use_container_width=True, hide_index=True)
        else:
            st.info("No records this month yet.")
    else:
        st.info("No daily records yet. Go to **Daily Entry** to start logging.")

    # Recent invoices
    st.subheader("Recent Invoices")
    inv_df = query_df("SELECT invoice_number, client_name, invoice_date, amount, amount_paid, status FROM invoices ORDER BY id DESC LIMIT 5")
    if not inv_df.empty:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No invoices yet.")

def page_daily_entry():
    st.header("📝 Daily Record Entry")

    with st.form("daily_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            record_date = st.date_input("Date", value=date.today())
            veh_dict = vehicle_options()
            vehicle_label = st.selectbox("Vehicle", list(veh_dict.keys()))
            vehicle = veh_dict[vehicle_label]
            driver = st.text_input("Driver name (optional)")
        with col2:
            cash = st.number_input("Cash Collected (M)", min_value=0.0, step=50.0, format="%.2f")
            trips = st.number_input("Number of trips", min_value=0, step=1)
            fuel_cost = st.number_input("Fuel cost (M)", min_value=0.0, step=10.0, format="%.2f")

        st.markdown("**Monthly Credits / Contract Payments**")
        c1, c2 = st.columns(2)
        with c1:
            credit_alliance = st.number_input("Alliance (M)", min_value=0.0, step=50.0, format="%.2f")
            credit_lehae = st.number_input("Lehae (M)", min_value=0.0, step=50.0, format="%.2f")
        with c2:
            credit_worldvision = st.number_input("World Vision (M)", min_value=0.0, step=50.0, format="%.2f")
            credit_waleslink = st.number_input("Waleslink (M)", min_value=0.0, step=50.0, format="%.2f")

        other_exp = st.number_input("Other expenses (M)", min_value=0.0, step=10.0, format="%.2f")
        exp_notes = st.text_input("Expense notes (repairs, etc.)")
        notes = st.text_area("General notes", height=80)

        submitted = st.form_submit_button("💾 Save Record", use_container_width=True, type="primary")

        if submitted:
            execute("""
                INSERT INTO daily_records 
                (record_date, vehicle_id, vehicle_name, plate, cash_collected, fuel_cost,
                 trips, other_expenses, expense_notes,
                 credit_alliance, credit_lehae, credit_worldvision, credit_waleslink,
                 driver_name, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_date.isoformat(), vehicle['id'], vehicle['name'], vehicle['plate'],
                cash, fuel_cost, trips, other_exp, exp_notes,
                credit_alliance, credit_lehae, credit_worldvision, credit_waleslink,
                driver, notes
            ))
            st.success(f"Saved for {vehicle['name']} on {record_date}")
            st.balloons()

def page_records():
    st.header("📋 All Daily Records")

    df = query_df("""
        SELECT id, record_date, vehicle_name, plate, cash_collected, fuel_cost,
               trips, other_expenses,
               credit_alliance, credit_lehae, credit_worldvision, credit_waleslink,
               driver_name, notes
        FROM daily_records ORDER BY record_date DESC, id DESC
    """)

    if df.empty:
        st.info("No records yet.")
        return

    # Filters
    c1, c2, c3 = st.columns(3)
    with c1:
        vehicles = ["All"] + sorted(df['vehicle_name'].unique().tolist())
        sel_veh = st.selectbox("Vehicle", vehicles)
    with c2:
        min_d = pd.to_datetime(df['record_date']).min().date()
        max_d = pd.to_datetime(df['record_date']).max().date()
        date_range = st.date_input("Date range", value=(min_d, max_d))
    with c3:
        st.write("")  # spacer
        if st.button("🔄 Refresh"):
            st.rerun()

    filtered = df.copy()
    if sel_veh != "All":
        filtered = filtered[filtered['vehicle_name'] == sel_veh]
    if len(date_range) == 2:
        filtered = filtered[
            (pd.to_datetime(filtered['record_date']).dt.date >= date_range[0]) &
            (pd.to_datetime(filtered['record_date']).dt.date <= date_range[1])
        ]

    st.dataframe(
        filtered.style.format({
            'cash_collected': 'M {:,.0f}',
            'fuel_cost': 'M {:,.0f}',
            'other_expenses': 'M {:,.0f}',
            'credit_alliance': 'M {:,.0f}',
            'credit_lehae': 'M {:,.0f}',
            'credit_worldvision': 'M {:,.0f}',
            'credit_waleslink': 'M {:,.0f}',
        }),
        use_container_width=True,
        hide_index=True
    )

    # Summary of filtered
    total_credits = (filtered['credit_alliance'].sum() + filtered['credit_lehae'].sum() +
                     filtered['credit_worldvision'].sum() + filtered['credit_waleslink'].sum())
    st.markdown(
        f"**Totals (filtered):** Cash **{money(filtered['cash_collected'].sum())}** | "
        f"Credits **{money(total_credits)}** | "
        f"Fuel **{money(filtered['fuel_cost'].sum())}** | "
        f"Other Exp **{money(filtered['other_expenses'].sum())}** | "
        f"Trips **{int(filtered['trips'].sum())}**"
    )

    # Export
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, "maxy_taxi_records.csv", "text/csv")

def page_vehicles():
    st.header("🚗 Fleet")
    df = query_df("""
        SELECT vehicle_name, plate,
               SUM(cash_collected) as total_cash,
               SUM(fuel_cost) as total_fuel,
               SUM(other_expenses) as total_other,
               SUM(trips) as total_trips,
               SUM(credit_alliance + credit_lehae + credit_worldvision + credit_waleslink) as total_credits
        FROM daily_records GROUP BY vehicle_name, plate
    """)

    for v in VEHICLES:
        with st.expander(f"{v['name']} — {v['plate']}", expanded=False):
            row = df[df['plate'] == v['plate']] if not df.empty else pd.DataFrame()
            if not row.empty:
                r = row.iloc[0]
                st.write(f"**Total Cash:** {money(r['total_cash'])}")
                st.write(f"**Total Credits:** {money(r['total_credits'])}")
                st.write(f"**Total Fuel Cost:** {money(r['total_fuel'])}")
                st.write(f"**Other Expenses:** {money(r['total_other'])}")
                st.write(f"**Trips:** {int(r['total_trips'])}")
                net = r['total_cash'] + r['total_credits'] - r['total_fuel'] - r['total_other']
                st.write(f"**Net (approx):** {money(net)}")
            else:
                st.caption("No records yet for this vehicle.")

def page_clients():
    st.header("👥 Clients")

    with st.expander("➕ Add New Client", expanded=False):
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
        st.info("No clients yet. Add one above.")
    else:
        st.dataframe(clients[['id', 'name', 'contact_person', 'phone', 'email', 'tin']], use_container_width=True, hide_index=True)

def page_quotations():
    st.header("📄 Quotations")

    # Create new
    with st.expander("➕ Create New Quotation", expanded=True):
        clients = query_df("SELECT id, name FROM clients ORDER BY name")
        client_options = {row['name']: row['id'] for _, row in clients.iterrows()} if not clients.empty else {}
        client_options["— Walk-in / No client —"] = None

        with st.form("quote_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.selectbox("Client", list(client_options.keys()))
                quote_date = st.date_input("Quote Date", value=date.today())
            with c2:
                valid_days = st.number_input("Valid for (days)", min_value=1, value=14)
                amount = st.number_input("Total Amount (M)", min_value=0.0, step=100.0, format="%.2f")

            description = st.text_area("Description of services *", height=100,
                                       placeholder="e.g. Daily staff transport for World Vision – 5 vehicles × 20 days...")
            notes = st.text_area("Notes / Terms", placeholder="Payment terms, inclusions, etc.")
            status = st.selectbox("Status", ["Draft", "Sent", "Accepted", "Rejected", "Expired"])

            if st.form_submit_button("Create Quotation", type="primary"):
                if not description.strip():
                    st.error("Description is required.")
                else:
                    # Generate quote number
                    year = date.today().year
                    last = query_df("SELECT quote_number FROM quotations WHERE quote_number LIKE ? ORDER BY id DESC LIMIT 1",
                                    (f"QT-{year}-%",))
                    if last.empty:
                        num = 1
                    else:
                        try:
                            num = int(last.iloc[0]['quote_number'].split("-")[-1]) + 1
                        except:
                            num = 1
                    quote_number = f"QT-{year}-{num:04d}"
                    valid_until = (quote_date + timedelta(days=int(valid_days))).isoformat()
                    cid = client_options[client_name]
                    cname = client_name if cid else None

                    execute("""
                        INSERT INTO quotations (quote_number, client_id, client_name, quote_date, valid_until,
                                                description, amount, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (quote_number, cid, cname, quote_date.isoformat(), valid_until,
                          description, amount, status, notes))
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
    st.header("🧾 Invoices")

    with st.expander("➕ Create New Invoice", expanded=True):
        clients = query_df("SELECT id, name FROM clients ORDER BY name")
        client_options = {row['name']: row['id'] for _, row in clients.iterrows()} if not clients.empty else {}
        client_options["— Cash / Walk-in —"] = None

        # Optional link to quote
        quotes = query_df("SELECT id, quote_number, client_name, amount, description FROM quotations WHERE status = 'Accepted' ORDER BY id DESC")
        quote_options = {"— None —": None}
        for _, r in quotes.iterrows():
            quote_options[f"{r['quote_number']} ({r['client_name'] or '—'} – M{r['amount']:,.0f})"] = r['id']

        with st.form("invoice_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.selectbox("Client", list(client_options.keys()))
                inv_date = st.date_input("Invoice Date", value=date.today())
                due_days = st.number_input("Due in (days)", min_value=0, value=30)
            with c2:
                related_quote = st.selectbox("Link to Quotation (optional)", list(quote_options.keys()))
                amount = st.number_input("Invoice Amount (M)", min_value=0.0, step=100.0, format="%.2f")
                amount_paid = st.number_input("Amount already paid (M)", min_value=0.0, step=50.0, format="%.2f")

            description = st.text_area("Description of services *", height=100)
            notes = st.text_area("Notes")
            status = st.selectbox("Status", ["Unpaid", "Partial", "Paid", "Overdue", "Cancelled"])

            if st.form_submit_button("Create Invoice", type="primary"):
                if not description.strip():
                    st.error("Description is required.")
                else:
                    year = date.today().year
                    last = query_df("SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
                                    (f"INV-{year}-%",))
                    if last.empty:
                        num = 1
                    else:
                        try:
                            num = int(last.iloc[0]['invoice_number'].split("-")[-1]) + 1
                        except:
                            num = 1
                    inv_number = f"INV-{year}-{num:04d}"
                    due_date = (inv_date + timedelta(days=int(due_days))).isoformat()
                    cid = client_options[client_name]
                    cname = client_name if cid else None
                    qid = quote_options[related_quote]

                    execute("""
                        INSERT INTO invoices (invoice_number, client_id, client_name, invoice_date, due_date,
                                              description, amount, amount_paid, status, related_quote_id, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (inv_number, cid, cname, inv_date.isoformat(), due_date,
                          description, amount, amount_paid, status, qid, notes))
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

def page_export():
    st.header("📤 Backup & Export")
    st.write("Download your full data regularly. On Streamlit Community Cloud the database resets if the app sleeps for long periods, so keep backups.")

    # Daily records
    df_rec = query_df("SELECT * FROM daily_records")
    if not df_rec.empty:
        st.download_button("⬇️ Daily Records (CSV)", df_rec.to_csv(index=False).encode(), "maxy_daily_records.csv")
        # Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_rec.to_excel(writer, sheet_name="Daily Records", index=False)
            query_df("SELECT * FROM clients").to_excel(writer, sheet_name="Clients", index=False)
            query_df("SELECT * FROM quotations").to_excel(writer, sheet_name="Quotations", index=False)
            query_df("SELECT * FROM invoices").to_excel(writer, sheet_name="Invoices", index=False)
        buffer.seek(0)
        st.download_button("⬇️ Full Backup (Excel)", buffer, "maxy_taxi_full_backup.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No data to export yet.")

# ---------------------- MAIN ----------------------
def main():
    init_db()

    st.sidebar.title("🚕 Maxy Taxi")
    st.sidebar.caption("Transport Records")
    st.sidebar.markdown("---")

    pages = {
        "Dashboard": page_dashboard,
        "Daily Entry": page_daily_entry,
        "Records": page_records,
        "Fleet": page_vehicles,
        "Clients": page_clients,
        "Quotations": page_quotations,
        "Invoices": page_invoices,
        "Backup / Export": page_export,
    }

    choice = st.sidebar.radio("Menu", list(pages.keys()), label_visibility="collapsed")
    st.sidebar.markdown("---")
    st.sidebar.caption("SAFE • QUICK • RELIABLE")
    st.sidebar.caption("Puma House 12 United Nations Rd")
    st.sidebar.caption("5× Honda Fit + Alphard")

    pages[choice]()

if __name__ == "__main__":
    main()
