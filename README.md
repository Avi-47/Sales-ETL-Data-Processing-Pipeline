# 🛒 Sales ETL Pipeline

A production-style **ETL (Extract → Transform → Load)** pipeline built with **Python**, **Pandas**, **SQLite**, and **SQL** — designed to process raw sales CSV data, clean and validate it, load it into a relational database, and generate beautiful analytical reports with charts.

---

## 📌 Project Highlights

- ✅ **Extract** raw sales data from CSV files
- ✅ **Transform** — clean dirty data, validate fields, enrich with calculated columns
- ✅ **Load** into a **SQLite** database using raw **SQL**
- ✅ **Reject** invalid records with reasons logged separately
- ✅ **Generate** SQL-powered analytics reports (revenue by region, category, trends)
- ✅ **HTML Report** with 4 charts — bar, line, pie graphs
- ✅ **ETL Audit Log** — tracks every pipeline run with stats
- ✅ **Unit Tested** with `unittest`
- ✅ **Structured logging** to file and console
- ✅ **Flask REST API** — expose sales data as JSON endpoints
- ✅ **Docker** support — run anywhere with one command

---

## 🗂️ Project Structure
```
sales-etl/
│
├── data/
│   ├── sales_data.csv          # Raw input CSV
│   └── rejected_records.csv    # Auto-generated: failed validation records
│
├── etl/
│   ├── __init__.py
│   ├── extractor.py            # Step 1: Read CSV → DataFrame
│   ├── transformer.py          # Step 2: Clean, validate, enrich
│   ├── loader.py               # Step 3: Load into SQLite via SQL
│   ├── reporter.py             # Step 4: SQL queries → TXT report
│   ├── html_reporter.py        # Step 5: Beautiful HTML report + charts
│   └── logger_setup.py         # Logging configuration
│
├── reports/                    # Auto-generated reports (HTML, TXT, CSV, PNG charts)
├── logs/                       # Auto-generated ETL run logs
├── tests/
│   └── test_transformer.py     # 16 unit tests
│
├── app.py                      # Flask REST API
├── Dockerfile                  # Docker support
├── main.py                     # 🚀 Pipeline entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Tool           | Purpose                            |
|----------------|------------------------------------|
| Python 3.11+   | Core language                      |
| Pandas         | Data extraction & transformation   |
| SQLite         | Lightweight relational database    |
| SQL            | Table creation, inserts, queries   |
| Matplotlib     | Auto-generated charts & graphs     |
| Flask          | REST API layer                     |
| Docker         | Containerization                   |
| unittest       | Unit testing (16 tests)            |
| Logging        | Run tracking & debugging           |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/vivekrai89/sales-etl.git
cd sales-etl
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the ETL Pipeline
```bash
python main.py
```

### 4. Open the HTML Report
After running, open `reports/sales_report_XXXXXX.html` in your browser to see the full dashboard with charts!

---

## 🔄 ETL Flow
```
[CSV File]
    │
    ▼
[ EXTRACT ]   ──► Read all rows as raw strings
    │
    ▼
[ TRANSFORM ] ──► Clean, validate, enrich data
    │
    ▼
[ LOAD ]      ──► Insert into SQLite database
    │
    ▼
[ REPORT ]    ──► TXT report + HTML dashboard + 4 charts
```

---

## 🌐 Flask REST API
```bash
python app.py
```

| Endpoint | Method | Description |
|---|---|---|
| `/api/sales` | GET | All sales records as JSON |
| `/api/sales/summary` | GET | Total revenue, orders, units |
| `/api/sales/category` | GET | Revenue breakdown by category |
| `/api/sales/region` | GET | Revenue breakdown by region |
| `/api/sales/top-products` | GET | Top 5 best-selling products |
| `/api/run-etl` | POST | Trigger ETL pipeline via API |

---

## 🐳 Docker
```bash
docker build -t sales-etl .
docker run sales-etl
```

---

## 🧪 Running Tests
```bash
python -m unittest tests/test_transformer.py -v
```

---

## 🗄️ Database Schema

### `sales` table
| Column           | Type    | Description                     |
|------------------|---------|---------------------------------|
| order_id         | INTEGER | Unique order identifier         |
| customer_name    | TEXT    | Customer full name              |
| product_name     | TEXT    | Product name                    |
| category         | TEXT    | Product category                |
| quantity         | INTEGER | Units ordered                   |
| unit_price       | REAL    | Price per unit                  |
| discount_percent | REAL    | Discount applied                |
| gross_amount     | REAL    | quantity × unit_price           |
| discount_amount  | REAL    | Discount value                  |
| net_amount       | REAL    | Final revenue after discount    |
| region           | TEXT    | Sales region                    |
| order_date       | TEXT    | Date of order                   |
| status           | TEXT    | COMPLETED / PENDING / CANCELLED |

---

## 🙋‍♂️ Author

**Vivek Rai** — Java & Python Full Stack Developer  
📍 Bengaluru, India  
🔗 [GitHub](https://github.com/vivekrai89) | [Portfolio](https://portfolio-vivekrai.vercel.app/)

---

## 📄 License

MIT License
```

---
