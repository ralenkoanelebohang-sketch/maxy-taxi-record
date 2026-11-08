# Maxy Taxi Transport – Business Records App

Mobile-friendly web app for daily cash / fuel / trips records, weekly & monthly summaries, professional **Quotations** and **Invoices** (PDF).

Works great on Android – open in Chrome and **Add to Home screen** so it feels like a real app.

---

## Features

- **Dashboard** – Today / This Week / This Month cash, expenses, and per-vehicle performance
- **Daily Entry** – Quick form for each vehicle (cash, fuel litres + cost, trips, km, other expenses, driver, notes)
- **Records** – Filterable history + CSV download
- **Fleet** – Overview of all 6 vehicles
- **Clients** – Store client details (World Vision etc.)
- **Quotations** – Create numbered quotes → download professional PDF
- **Invoices** – Create invoices, track payments, download tax-ready PDF
- **Backup** – Full Excel export of everything

### Your Vehicles (pre-loaded)
1. Honda Fit 1 – A 940 BDL  
2. Honda Fit 2 – A 943 BDL  
3. Honda Fit 3 – A 945 BDL  
4. Honda Fit 4 – A 238 BGN  
5. Honda Fit 5 – A 765 BGR  
6. Toyota Alphard – A 313 BCM  

---

## How to put it online (FREE)

### Option A – Streamlit Community Cloud (recommended)

1. Create a free GitHub account (if you don’t have one): https://github.com
2. Create a **new repository** called `maxy-taxi-app` (public is fine)
3. Upload these files into the repository:
   - `app.py`
   - `requirements.txt`
   - `README.md`
4. Go to https://share.streamlit.io and sign in with GitHub
5. Click **Create app**
6. Select your `maxy-taxi-app` repository
7. Main file path: `app.py`
8. Click **Deploy**

You will get a link like:  
`https://maxy-taxi-app-xxxxx.streamlit.app`

Open that link on your phone → Chrome menu → **Add to Home screen**.

### Option B – Run on your computer first (for testing)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local link it gives you.

---

## Important notes about data

On the free Streamlit Community Cloud:
- The database lives with the app.
- If the app sleeps for a long time (no one visits), data can be lost.
- **Solution**: Use the **Backup / Export** page regularly and download the Excel file.
- Keep the Excel file safe (Google Drive / phone storage).

Later we can connect it to Google Sheets so data never disappears.

---

## Customising your business details

Open `app.py` and edit these lines near the top:

```python
BUSINESS_NAME = "Maxy Taxi Transport"
BUSINESS_TAGLINE = "Reliable Transport Services"
BUSINESS_LOCATION = "Maseru, Lesotho"
BUSINESS_PHONE = "Your phone number"
BUSINESS_EMAIL = "your@email.com"
BUSINESS_TIN = "Your TIN number"
```

Then re-upload / re-deploy.

---

## Next improvements (tell me if you want them)

- Google Sheets as permanent storage (data never lost)
- Automatic weekly/monthly PDF reports
- More detailed expense categories
- Driver login (if you have drivers entering data)
- Logo on the PDFs

---

Built for Maxy Taxi Transport • Maseru, Lesotho
