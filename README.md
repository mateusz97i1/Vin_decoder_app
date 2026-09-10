# VIN Decoder 🚗

A web application that decodes Vehicle Identification Numbers (VINs) for **US-market vehicles** and generates detailed AI-powered reports about the car's brand and engine.

## 📋 Overview

VIN Decoder lets a user enter a vehicle's VIN, automatically decode the basic data (brand, engine, horsepower) via an external API, and then generate a rich text report using the GPT API, including:

- an overview of the vehicle's brand and model,
- engine and performance characteristics,
- the most common issues/faults reported for that configuration,
- a general description of the vehicle.

The finished report is stored in the database and made available to the user for download as a **PDF**.

> ⚠️ The app supports **US-market vehicles only**.

## ✨ Features

- 🔍 VIN decoding (brand, engine, horsepower) via an external API
- 🤖 AI-generated reports (GPT API) based on the decoded data
- 🛠️ A section covering the most common faults for a given brand/engine
- 📄 Report export to PDF (rendered from an HTML template, with report content converted from Markdown using `markdown2`)
- ☁️ Reports and PDF files stored in Supabase (Storage + download URL)
- 🔐 Google login (django-allauth)
- ⚡ Data caching (Redis) to reduce the number of calls to external APIs
- 🗄️ PostgreSQL as the main relational database
- 🎨 Lightweight frontend: HTML, plain JS, HTMX for forms, GSAP for animations
- ✅ Core functionality covered with pytest
- 📧 Newsletter subscription (email sign-up)
- 🧵 Background task queue (Celery) for PDF generation and welcome emails

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Django |
| Frontend | HTML, vanilla JS, HTMX, GSAP |
| Database | PostgreSQL (Supabase) |
| File storage | Supabase Storage |
| Cache | Redis |
| Task queue | Celery |
| Auth | django-allauth (Google login) |
| AI / report generation | OpenAI GPT API |
| VIN decoding | External VIN API (brand, engine, horsepower) |
| Reports | PDF generation from an HTML template, Markdown parsing via `markdown2` |
| Testing | pytest (core features) |

## 🔄 How it works

1. The user logs in with Google (django-allauth).
2. The user submits a VIN for a US vehicle via an HTMX-powered form.
3. The app queries an external VIN API, which returns the brand, engine, and horsepower.
4. The result is cached in Redis to avoid repeated lookups for the same VIN.
5. The decoded data is sent to the GPT API, which generates a description of the brand/engine and a list of common faults.
6. The generated report is saved to PostgreSQL (Supabase). A Celery background task then converts the GPT-generated Markdown content into HTML (via `markdown2`), renders it into an HTML template, and produces the final PDF.
7. The PDF file is uploaded to Supabase Storage, and the user receives a download link.

## 🎨 Frontend

The frontend is intentionally lightweight:

- **HTML** for page structure/templates (Django templates)
- **Plain JavaScript** for small interactive bits
- **HTMX** for form submissions and partial page updates without full reloads
- **GSAP** for UI animations and transitions

## 📧 Newsletter

Users can subscribe to a newsletter by submitting their email address. Subscriptions are stored in the database, and a welcome email is sent out via a **Celery** background task.

## 🧵 Background Tasks (Celery)

Celery is used to queue and process time-consuming or non-blocking tasks in the background, so the user doesn't have to wait on the request/response cycle:

- generating the PDF report
- sending the newsletter welcome email

Redis is used as the Celery broker.

## ✅ Testing

Core application logic (VIN decoding flow, caching, report generation/storage) is covered with **pytest**.

```bash
pytest
```

## ⚙️ Requirements

- Python 3.x
- PostgreSQL (database provided by Supabase)
- Redis
- Celery worker running (for background tasks)
- A Supabase account (database + storage)
- OpenAI API key (GPT)
- API key/access for the external VIN decoding service
- Google OAuth credentials configured (django-allauth)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/your-user/vin_decoder.git
cd vin_decoder

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start the dev server
python manage.py runserver
```

## 🔑 Configuration (environment variables)

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True

# PostgreSQL / Supabase
DATABASE_URL=postgres://user:password@host:port/dbname

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-or-anon-key
SUPABASE_STORAGE_BUCKET=reports

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI GPT
OPENAI_API_KEY=your-openai-api-key

# VIN decoding API
VIN_API_URL=https://api.example.com/decode
VIN_API_KEY=your-vin-api-key

# Google OAuth (django-allauth)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 📖 Usage

1. Log in with Google.
2. Enter a VIN for a US-market vehicle.
3. Wait for the AI-generated report to be created.
4. Download the finished PDF report from the Supabase-hosted link.

## 📸 Screenshots

**Home page**
![Home page](screenshots/home.PNG)

**Navigation menu**
![Navigation menu](screenshots/burger.PNG)

**VIN decoded — build sheet**
![VIN decoded](screenshots/vin_decoded.PNG)

**Generated report (web view)**
![Web report](screenshots/web_raport.PNG)

**Download PDF prompt**
![Download PDF](screenshots/donwload_pdf.PNG)

**PDF generation in progress**
![Pending PDF generation](screenshots/pending_downlaod.PNG)

**Final PDF report**
![PDF report](screenshots/actual_pdf.PNG)

**Newsletter sign-up**
![Newsletter](screenshots/newsletter.PNG)

## 🗂️ PDF Report Structure

- Vehicle brand and model
- Engine data and horsepower
- Vehicle description
- Most common faults and maintenance issues

## 📌 Limitations

- Only US-market vehicles are supported.
- Report quality and accuracy depend on the data returned by the VIN decoding API and the GPT model's output.

## 📄 License

This project is licensed under the [MIT License](LICENSE) (or another license of your choice — update as needed).
