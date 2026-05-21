import json
import uuid
from pathlib import Path
from textwrap import dedent

def cell_id(): return uuid.uuid4().hex[:12]

def md(src, cid=None):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type":"markdown","id":cid or cell_id(),"metadata":{},"source":source}

def code(src, cid=None):
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type":"code","id":cid or cell_id(),"metadata":{},"execution_count":None,"outputs":[],"source":source}

def lesson(label, title, body):
    return code(f"# 💻 {label}  {title}\n# {'─'*77}\n{body}")

def exmd(num, title, task, steps, hint):
    sl = "\n".join(f"{i+1}. {s}" for i,s in enumerate(steps))
    return md(f"### 🎯 Exercise {num} — {title}\n\n**Task:** {task}\n\n**Steps:**\n{sl}\n\n```python\n{hint}\n```")

def exstub(num, comments):
    body = "\n".join(f"# {i+1}. {c}" for i,c in enumerate(comments))
    return code(f"# 🎯 Exercise {num} — your code here {'─'*44}\n{body}")

def exsol(num, body):
    return code(f"# ✅ Exercise {num} — Solution {'─'*52}\n{body}")

def labstep(num, title, body):
    return code(f"# 🔬 Step {num} — {title}\n# {'─'*77}\n{body}")

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "notebooks" / "geospatial_python_course" / "week_06_postgresql_data_loading.ipynb"

C = []

# ── Cell 0: Title ─────────────────────────────────────────────────────────────
C.append(md(
"""# 🌍 Week 6 — PostgreSQL Connection and Data Loading
### Geospatial Python Mastery | Module D: PostgreSQL and PostGIS

---

|  |  |
|---|---|
| **Course** | Geospatial Python Mastery |
| **Week** | 6 of 10 |
| **Theme** | PostgreSQL Connection and Data Loading |
| **Duration** | ~4 contact hours + 4 hours self-study |
| **Practice Outcome** | Assignment: Build a complete ETL loader for spatial records |
| **Next week** | PostGIS core queries — ST_Intersects, ST_Buffer, spatial indexes |

---

> 🗺️ **Why this week matters**
> Every production geospatial system stores data in a spatial database.
> PostgreSQL with the PostGIS extension is the industry standard — powering everything
> from national mapping agencies to real-time logistics platforms. This week you will
> connect Python to PostgreSQL, design schemas for spatial records, load datasets
> reliably with transaction control, and build a reusable ETL loader module.
>
> All interactive examples use **SQLite via SQLAlchemy** so they run everywhere —
> on Google Colab, Windows, macOS, and Linux — with zero setup. A single URL
> change connects the same code to a real PostgreSQL server.

---

## 📋 Table of Contents

| Section | Topic |
|---------|-------|
| [1 — Connection Fundamentals](#section-1) | DSN strings, SQLAlchemy vs psycopg2, engine creation |
| [2 — psycopg2 Direct Connection](#section-2) | connect(), cursor, execute, fetchall, RealDictCursor |
| [3 — SQLAlchemy Core](#section-3) | create_engine, text(), connection pool, URL format |
| [4 — Schema Design](#section-4) | Table planning, data types, primary keys, geometry columns |
| [5 — Creating Tables and Indexes](#section-5) | CREATE TABLE, constraints, indexes, SQLAlchemy Table |
| [6 — Inserting Data](#section-6) | INSERT, executemany, DataFrame.to_sql, UPSERT |
| [7 — Transaction Management](#section-7) | ACID, commit/rollback, context managers, savepoints |
| [8 — Querying Data](#section-8) | SELECT, parameterized queries, fetchall, read_sql |
| [9 — PostGIS Setup](#section-9) | CREATE EXTENSION, geometry types, WKT, ST_AsGeoJSON |
| [10 — ETL Module](#section-10) | spatial_etl.py, logging pipeline, error handling |
| [Mini-Lab](#mini-lab) | Build a complete city-records ETL loader |

---

## 🗺️ Symbol Guide

| Symbol | Meaning |
|--------|---------|
| 💻 | Runnable code cell |
| 🎯 | Exercise — write your own code |
| ✅ | Solution — run after attempting |
| 🔬 | Mini-Lab step |
| 📖 | Explanatory section |
| 💡 | Tip or best practice |
| ⚠️ | Common mistake or warning |
| 🐘 | PostgreSQL-specific (requires live server) |

> **Keyboard shortcuts:** `Shift+Enter` run cell · `b` insert cell below · `m` convert to Markdown · `Esc` command mode"""))

# ── Cell 1: Learning Objectives ───────────────────────────────────────────────
C.append(md(
"""## 🎯 Learning Objectives

By the end of this notebook you will be able to:

| # | Objective |
|---|-----------|
| 1 | Construct a correct **DSN connection string** for PostgreSQL and SQLite |
| 2 | Connect to a database with both **psycopg2** and **SQLAlchemy** |
| 3 | Design a **relational schema** for storing spatial records with coordinates |
| 4 | Create tables, add **constraints and indexes** from Python |
| 5 | Load records with single **INSERT**, batch **executemany**, and `DataFrame.to_sql()` |
| 6 | Manage **transactions**: commit, rollback, and context managers |
| 7 | Query data with **parameterized SQL** and load results into a pandas DataFrame |
| 8 | Explain **PostGIS** geometry types and write basic spatial INSERT/SELECT statements |
| 9 | Build a reusable **`spatial_etl.py`** module with logging and error handling |
| 10 | Run a complete **ETL pipeline**: CSV → validate → load → verify → report |

### How to use this notebook

- Run cells **top to bottom** in sequence
- **Attempt** each 🎯 exercise before looking at the ✅ solution
- Cells marked 🐘 require a live PostgreSQL server — skip or adapt to SQLite if unavailable
- The 🔬 **Mini-Lab** at the end builds a complete ETL loader you can reuse
- Tick each box in the ☑️ checklist before moving to Week 7"""))

# ── Cell 2: Environment ────────────────────────────────────────────────────────
C.append(code(
"""# 💻 Environment check and auto-install
# ─────────────────────────────────────────────────────────────────────────────
import sys
import subprocess
import importlib
import platform

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

OS_NAME = platform.system()

print("=" * 60)
print("  Geospatial Python Mastery — Week 6 Environment Check")
print("=" * 60)
print(f"  Environment : {'Google Colab' if IN_COLAB else 'Local Jupyter'}")
print(f"  Python      : {sys.version.split()[0]}")
print(f"  OS          : {OS_NAME}")
print()

REQUIRED = [
    ("sqlalchemy",   "sqlalchemy",     "1.4"),
    ("pandas",       "pandas",         "1.3"),
    ("psycopg2",     "psycopg2-binary","2.9"),
]

for import_name, pip_name, min_ver in REQUIRED:
    try:
        mod = importlib.import_module(import_name)
        ver = getattr(mod, "__version__", "ok")
        print(f"  ✅ {import_name:<20} {ver}")
    except ImportError:
        print(f"  ⬇  Installing {pip_name}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pip_name])
        print(f"  ✅ {pip_name} installed")

if OS_NAME == "Windows":
    print()
    print("  ℹ  Windows tip: if psycopg2-binary fails, try 'pip install psycopg2'")
    print("     and install PostgreSQL client libraries from postgresql.org/download")

print()
print("✅ Environment check complete — ready for Week 6!")"""))

# ── Cell 3: Imports ────────────────────────────────────────────────────────────
C.append(code(
"""# 💻 Import all libraries used this week
# ─────────────────────────────────────────────────────────────────────────────
import os
import csv
import json
import math
import logging
import sqlite3
import unittest
from pathlib import Path
from datetime import datetime

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import (
    create_engine, text, Table, Column, MetaData,
    Integer, Float, String, Boolean, DateTime
)

# psycopg2 is optional — only needed for PostgreSQL-specific cells (🐘)
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
    print(f"psycopg2 available : v{psycopg2.__version__}")
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("psycopg2 not installed — PostgreSQL-specific cells (🐘) will be skipped")
    print("Run: pip install psycopg2-binary")

print(f"SQLAlchemy         : v{sa.__version__}")
print(f"pandas             : v{pd.__version__}")
print()
print("✅ All imports successful")"""))

# ── Cell 4: Directories + DB URL ──────────────────────────────────────────────
C.append(code(
"""# 💻 Create data directories and configure the database URL
# ─────────────────────────────────────────────────────────────────────────────
from pathlib import Path

DATA_DIR = Path("data/week_06")
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR = Path("logs");  LOGS_DIR.mkdir(exist_ok=True)

# ── Database URL ─────────────────────────────────────────────────────────────
# This notebook uses SQLite so it runs EVERYWHERE with zero setup.
# To connect to a real PostgreSQL server, change this one line:
#
#   PostgreSQL:  "postgresql+psycopg2://user:password@localhost:5432/geomaster"
#   Colab/local: "sqlite:///data/week_06/geomaster_demo.db"  ← default

DB_URL = f"sqlite:///{DATA_DIR}/geomaster_demo.db"

print(f"Data directory : {DATA_DIR.resolve()}")
print(f"Logs directory : {LOGS_DIR.resolve()}")
print(f"Database URL   : {DB_URL}")
print()
print("💡 To use a real PostgreSQL server, change DB_URL above and re-run.")"""))

# ── SECTION 1 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 1 — Connection Fundamentals

Before writing a single query, you need to understand **how Python talks to a database**.

### 1.1 The database connection stack

```
Your Python code
     │
     ▼
  SQLAlchemy  ← high-level ORM / Core (abstracts the driver)
     │
     ▼
  psycopg2    ← low-level PostgreSQL driver (C extension)
     │
     ▼
  libpq       ← PostgreSQL client library
     │
     ▼
  PostgreSQL server (localhost:5432 or remote)
```

| Layer | Purpose | When to use directly |
|-------|---------|---------------------|
| **psycopg2** | Fast, direct PostgreSQL access | COPY, server cursors, pg-specific features |
| **SQLAlchemy Core** | Database-agnostic SQL expression language | Production apps, multiple DB backends |
| **SQLAlchemy ORM** | Map Python classes to tables | Large applications with complex models |

### 1.2 Connection strings (DSN)

A **Data Source Name (DSN)** encodes all connection info in one string:

```
postgresql+psycopg2://  user  :  password  @  host  :  port  /  dbname
           ┬─────────   ──┬─    ────┬─────    ──┬─    ──┬──    ─────┬──
           │              │         │            │       │           │
     driver+dialect      user    password      host    port       database
```

**SQLite** (demo mode):
```
sqlite:///relative/path/to/file.db    ← relative to cwd
sqlite:////absolute/path/to/file.db   ← absolute (4 slashes)
```

> 💡 Always store real credentials in **environment variables**, never hard-code them.
> Use `os.getenv('PGPASSWORD')` and document required vars in your README."""))

C.append(lesson("1.1", "Build connection parameters from environment variables",
"""import os

def build_db_url(driver: str = "postgresql+psycopg2") -> str:
    '''Build a PostgreSQL DSN from environment variables.

    Falls back to SQLite demo database if PG vars are not set.
    '''
    host  = os.getenv("PGHOST")
    port  = os.getenv("PGPORT",     "5432")
    db    = os.getenv("PGDATABASE")
    user  = os.getenv("PGUSER")
    pwd   = os.getenv("PGPASSWORD", "")

    if host and db and user:
        url = f"{driver}://{user}:{pwd}@{host}:{port}/{db}"
        print(f"✅ Using PostgreSQL: {driver}://{user}:***@{host}:{port}/{db}")
    else:
        url = f"sqlite:///{DATA_DIR}/geomaster_demo.db"
        print(f"ℹ  PGHOST/PGDATABASE/PGUSER not set — using SQLite demo")
        print(f"   URL: {url}")

    return url

ACTIVE_URL = build_db_url()"""))

C.append(lesson("1.2", "Create an SQLAlchemy engine and test the connection",
"""from sqlalchemy import create_engine, text

# Create engine — this does NOT open a connection yet (lazy)
engine = create_engine(ACTIVE_URL, echo=False)

# Test connectivity
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS ping")).fetchone()
        print(f"✅ Connection OK — ping returned: {result[0]}")
        # For PostgreSQL, show server version:
        if "postgresql" in ACTIVE_URL:
            ver = conn.execute(text("SELECT version()")).scalar()
            print(f"   Server: {ver[:60]}")
        else:
            ver = conn.execute(text("SELECT sqlite_version()")).scalar()
            print(f"   SQLite version: {ver}")
except Exception as e:
    print(f"❌ Connection failed: {e}")"""))

C.append(exmd(1, "Test your own connection",
    "Modify DB_URL to test a connection, check the response, and print the driver name.",
    ["Change `DB_URL` to a custom SQLite path (e.g., `sqlite:///data/week_06/test.db`)",
     "Create an engine and execute `SELECT 1`",
     "Print the dialect name from `engine.dialect.name`",
     "Handle any connection error with try/except"],
    "# engine.dialect.name   →  'sqlite' or 'postgresql'"))
C.append(exstub(1,
    ["Create a new engine with a custom DB_URL",
     "Execute SELECT 1 and capture the result",
     "Print engine.dialect.name",
     "Wrap in try/except and print a clear error message"]))
C.append(exsol(1,
"""custom_url = "sqlite:///data/week_06/test_ex1.db"
eng_test = create_engine(custom_url, echo=False)

try:
    with eng_test.connect() as conn:
        r = conn.execute(text("SELECT 1")).fetchone()
        print(f"✅ Connection OK — result: {r[0]}")
        print(f"   Dialect: {eng_test.dialect.name}")
except Exception as e:
    print(f"❌ Connection failed: {e}")"""))

# ── SECTION 2 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 2 — psycopg2 Direct Connection

**psycopg2** is the standard PostgreSQL adapter for Python. It gives direct access to
every PostgreSQL feature and is the fastest way to work with PostgreSQL from Python.

> 🐘 **This section requires a live PostgreSQL server.**
> If you only have SQLite available, read through the patterns — they will work
> once you have a server running. The SQLAlchemy approach in Section 3 is identical
> for both backends.

### 2.1 Opening a connection

```python
import psycopg2

conn = psycopg2.connect(
    host     = "localhost",
    port     = 5432,
    dbname   = "geomaster",
    user     = "geouser",
    password = os.getenv("PGPASSWORD", ""),
    connect_timeout = 5,
)
```

### 2.2 Cursor types

| Cursor | Row format | Best for |
|--------|-----------|---------|
| `conn.cursor()` | tuple | Speed, bulk operations |
| `RealDictCursor` | dict | Readable access by column name |
| `NamedTupleCursor` | namedtuple | Attribute access on rows |

### 2.3 Context manager (safe pattern)

```python
with psycopg2.connect(**params) as conn:    # auto-commit/rollback
    with conn.cursor() as cur:              # auto-close cursor
        cur.execute("SELECT * FROM locations WHERE city = %s", ("Amsterdam",))
        rows = cur.fetchall()
```

> ⚠️ **Parameterized queries always use `%s` placeholders in psycopg2**, never
> f-strings or `.format()`. f-strings risk SQL injection."""))

C.append(lesson("2.1", "psycopg2 connection patterns (simulation + real)",
r"""# Simulate the psycopg2 pattern using sqlite3 when PostgreSQL is unavailable.
# The pattern is IDENTICAL for psycopg2 — only the connect() call differs.

import sqlite3

SIM_DB = str(DATA_DIR / "sim_psycopg2.db")

def get_sim_conn():
    '''Return a sqlite3 connection that mimics psycopg2 usage patterns.'''
    conn = sqlite3.connect(SIM_DB)
    conn.row_factory = sqlite3.Row   # dict-like rows (like RealDictCursor)
    return conn

# ── Setup: create a tiny table ───────────────────────────────────────────────
with get_sim_conn() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL,
            lon  REAL    NOT NULL,
            lat  REAL    NOT NULL,
            city TEXT
        )
    """)
    conn.execute("DELETE FROM locations")   # fresh run
    conn.executemany(
        "INSERT INTO locations (name, lon, lat, city) VALUES (?, ?, ?, ?)",
        [("Centraal Station", 4.9004, 52.3791, "Amsterdam"),
         ("Rijksmuseum",      4.8852, 52.3600, "Amsterdam"),
         ("Binnenhof",        4.3136, 52.0798, "Den Haag")]
    )
    conn.commit()

# ── Query with parameterized SQL (? in sqlite3, %s in psycopg2) ──────────────
with get_sim_conn() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM locations WHERE city = ?", ("Amsterdam",))
    rows = cur.fetchall()

print("Locations in Amsterdam:")
for r in rows:
    print(f"  {dict(r)['name']:<25} lon={dict(r)['lon']:.4f}  lat={dict(r)['lat']:.4f}")"""))

C.append(lesson("2.2", "Cursor methods: fetchone, fetchmany, fetchall",
"""with get_sim_conn() as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, name, lat, lon FROM locations ORDER BY id")

    print("── fetchone() ──────────────────────────────────────────")
    first = cur.fetchone()
    print(f"  First row : {dict(first)}")

    print()
    print("── fetchmany(2) ────────────────────────────────────────")
    cur.execute("SELECT id, name, lat, lon FROM locations ORDER BY id")
    batch = cur.fetchmany(2)
    for r in batch:
        print(f"  {dict(r)}")

    print()
    print("── fetchall() ──────────────────────────────────────────")
    cur.execute("SELECT name, city FROM locations ORDER BY city, name")
    all_rows = cur.fetchall()
    print(f"  Total rows: {len(all_rows)}")
    for r in all_rows:
        d = dict(r)
        print(f"  [{d['city']}] {d['name']}")"""))

C.append(exmd(2, "Query with conditions and count",
    "Extend the locations query to filter by a bounding box and count results.",
    ["Add 2 more locations to the `locations` table (any city)",
     "Query all locations where `lon` is between 4.0 and 5.0",
     "Use `COUNT(*)` to get the number of matching rows",
     "Print each matched location name and coordinates"],
    "# INSERT INTO locations ... VALUES (?, ?, ?, ?)"))
C.append(exstub(2,
    ["Insert 2 more locations with get_sim_conn()",
     "Query WHERE lon BETWEEN ? AND ?",
     "Count matches with SELECT COUNT(*)",
     "Print each name and coords"]))
C.append(exsol(2,
"""with get_sim_conn() as conn:
    # 1. Add more locations
    conn.executemany(
        "INSERT INTO locations (name, lon, lat, city) VALUES (?, ?, ?, ?)",
        [("Euromast",    4.4670, 51.9049, "Rotterdam"),
         ("Markthal",    4.4816, 51.9225, "Rotterdam")]
    )
    conn.commit()

    # 2. Query bounding box
    cur = conn.cursor()
    cur.execute(
        "SELECT name, lon, lat FROM locations WHERE lon BETWEEN ? AND ?",
        (4.0, 5.0)
    )
    matches = cur.fetchall()

    # 3. Count
    cur.execute(
        "SELECT COUNT(*) FROM locations WHERE lon BETWEEN ? AND ?",
        (4.0, 5.0)
    )
    count = cur.fetchone()[0]

    # 4. Print
    print(f"Locations with lon 4.0–5.0 ({count} total):")
    for r in matches:
        d = dict(r)
        print(f"  {d['name']:<25} lon={d['lon']:.4f}  lat={d['lat']:.4f}")"""))

# ── SECTION 3 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 3 — SQLAlchemy Core

**SQLAlchemy** is the most-used Python SQL toolkit. Its **Core** layer provides a
Pythonic interface to SQL that works with any supported backend — SQLite, PostgreSQL,
MySQL, and more — using the same code.

### 3.1 Engine and connection lifecycle

```
create_engine(URL)      ← creates an engine (connection pool)
    │
engine.connect()        ← checks out a connection from the pool
    │
conn.execute(text(...)) ← sends SQL
    │
conn.commit()           ← or conn.rollback()
    │
connection returned to pool (auto on with-block exit)
```

### 3.2 SQLAlchemy vs raw psycopg2

| Feature | psycopg2 | SQLAlchemy Core |
|---------|---------|-----------------|
| Connection | `psycopg2.connect()` | `engine.connect()` |
| Execute SQL | `cur.execute("...", (param,))` | `conn.execute(text("..."), {"p": val})` |
| Placeholder style | `%s` | `:name` (named params) |
| Fetch rows | `cur.fetchall()` | `result.fetchall()` |
| DataFrame | manual | `pd.read_sql(sql, conn)` |
| Multi-DB support | PostgreSQL only | Any SQLAlchemy backend |

> 💡 In SQLAlchemy, **named parameters** use `:name` in SQL and `{"name": value}` in Python:
> ```python
> conn.execute(text("SELECT * FROM t WHERE city = :c"), {"c": "Amsterdam"})
> ```"""))

C.append(lesson("3.1", "Create engine, connect, and execute with SQLAlchemy",
"""from sqlalchemy import create_engine, text

engine = create_engine(DB_URL, echo=False)

# ── Create table via SQLAlchemy ───────────────────────────────────────────────
with engine.begin() as conn:   # begin() auto-commits on success, rolls back on error
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS cities (
            id      INTEGER PRIMARY KEY,
            name    TEXT    NOT NULL,
            country TEXT    NOT NULL,
            lon     REAL    NOT NULL,
            lat     REAL    NOT NULL,
            pop     INTEGER
        )
    """))
    conn.execute(text("DELETE FROM cities"))   # fresh run each time

# ── Insert rows with named parameters ────────────────────────────────────────
cities_data = [
    {"id": 1, "name": "Amsterdam", "country": "NL", "lon": 4.9041, "lat": 52.3676, "pop": 921402},
    {"id": 2, "name": "Rotterdam", "country": "NL", "lon": 4.4777, "lat": 51.9244, "pop": 651446},
    {"id": 3, "name": "Brussels",  "country": "BE", "lon": 4.3517, "lat": 50.8503, "pop": 1208542},
    {"id": 4, "name": "Antwerp",   "country": "BE", "lon": 4.4025, "lat": 51.2194, "pop": 529247},
    {"id": 5, "name": "Utrecht",   "country": "NL", "lon": 5.1214, "lat": 52.0907, "pop": 361924},
]

with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO cities (id, name, country, lon, lat, pop) "
             "VALUES (:id, :name, :country, :lon, :lat, :pop)"),
        cities_data
    )

print(f"Inserted {len(cities_data)} cities")"""))

C.append(lesson("3.2", "Query with named params, fetchall, and scalar",
"""# ── Named-parameter query ─────────────────────────────────────────────────────
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT name, country, pop FROM cities WHERE country = :c ORDER BY pop DESC"),
        {"c": "NL"}
    ).fetchall()

print("Dutch cities by population:")
for r in rows:
    print(f"  {r.name:<12}  pop={r.pop:>8,}")

# ── Scalar (single value) ────────────────────────────────────────────────────
with engine.connect() as conn:
    total = conn.execute(
        text("SELECT SUM(pop) FROM cities WHERE country = :c"),
        {"c": "NL"}
    ).scalar()
    print(f"\nTotal NL population in dataset: {total:,}")

# ── All rows as pandas DataFrame ─────────────────────────────────────────────
with engine.connect() as conn:
    df = pd.read_sql(
        sql=text("SELECT * FROM cities ORDER BY country, name"),
        con=conn
    )
print(f"\nDataFrame shape: {df.shape}")
print(df.to_string(index=False))"""))

C.append(exmd(3, "Filter and aggregate with SQLAlchemy",
    "Query the cities table: find all cities with population above a threshold and compute average population per country.",
    ["Query cities with `pop > 600000` using a named parameter",
     "Print each matching city name and population",
     "Use `GROUP BY country` to get average population per country",
     "Print the country averages sorted descending"],
    "# text('SELECT ... WHERE pop > :threshold'), {'threshold': 600000}"))
C.append(exstub(3,
    ["Query cities WHERE pop > :threshold with named param 600000",
     "Print each matching city",
     "Use GROUP BY country, AVG(pop) query",
     "Print country averages sorted descending"]))
C.append(exsol(3,
"""# 1-2. Cities with pop > 600000
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT name, country, pop FROM cities WHERE pop > :threshold ORDER BY pop DESC"),
        {"threshold": 600000}
    ).fetchall()

print("Cities with population > 600,000:")
for r in rows:
    print(f"  {r.name:<12} ({r.country})  pop={r.pop:>9,}")

# 3-4. Average population per country
with engine.connect() as conn:
    avgs = conn.execute(
        text("SELECT country, AVG(pop) AS avg_pop, COUNT(*) AS n "
             "FROM cities GROUP BY country ORDER BY avg_pop DESC")
    ).fetchall()

print()
print("Average population by country:")
for r in avgs:
    print(f"  {r.country}  avg={r.avg_pop:>10,.0f}  ({r.n} cities)")"""))

# ── SECTION 4 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 4 — Schema Design for Geospatial Data

A good schema makes spatial queries fast and data quality reliable.

### 4.1 Anatomy of a spatial records table

```sql
CREATE TABLE locations (
    -- Identity
    id          SERIAL PRIMARY KEY,             -- auto-increment PK (PostgreSQL)
    -- or:
    id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite syntax

    -- Descriptive
    name        TEXT        NOT NULL,
    category    TEXT        NOT NULL DEFAULT 'unknown',
    source_file TEXT,

    -- Geometry (simple lon/lat, works everywhere)
    lon         DOUBLE PRECISION NOT NULL,
    lat         DOUBLE PRECISION NOT NULL,

    -- PostGIS geometry column (PostgreSQL + PostGIS only)
    -- geom        GEOMETRY(Point, 4326),

    -- Metadata
    is_valid    BOOLEAN     DEFAULT TRUE,
    loaded_at   TIMESTAMP   DEFAULT NOW()
);
```

### 4.2 Data type mapping

| Python type | SQLite | PostgreSQL | PostGIS |
|-------------|--------|-----------|---------|
| `int` | INTEGER | INTEGER / BIGINT | — |
| `float` | REAL | DOUBLE PRECISION | — |
| `str` | TEXT | TEXT / VARCHAR | — |
| `bool` | INTEGER (0/1) | BOOLEAN | — |
| `dict` | TEXT (JSON) | JSONB | — |
| `datetime` | TEXT | TIMESTAMP | — |
| Shapely geometry | TEXT (WKT) | — | GEOMETRY |

### 4.3 Choosing a primary key

| Option | Pros | Cons |
|--------|------|------|
| **SERIAL** (PostgreSQL) | Automatic, fast | Not portable to SQLite |
| **INTEGER AUTOINCREMENT** (SQLite) | Simple | SQLite only |
| **UUID** | Globally unique, portable | Slower, larger storage |
| **Natural key** (e.g., ISO code) | Human-readable | Not always unique |

> 💡 For geospatial records, always add a **spatial index** on geometry columns.
> Without one, any spatial query becomes a full-table scan."""))

C.append(lesson("4.1", "Plan and document a schema before creating it",
"""# Good practice: define your schema as a Python dict for documentation + generation

SCHEMA = {
    "table": "spatial_records",
    "description": "POI-style spatial records with coordinates and attributes",
    "columns": [
        {"name": "id",          "type": "INTEGER", "constraint": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "name",        "type": "TEXT",    "constraint": "NOT NULL"},
        {"name": "category",    "type": "TEXT",    "constraint": "NOT NULL DEFAULT 'unknown'"},
        {"name": "lon",         "type": "REAL",    "constraint": "NOT NULL"},
        {"name": "lat",         "type": "REAL",    "constraint": "NOT NULL"},
        {"name": "elevation_m", "type": "REAL",    "constraint": ""},
        {"name": "source",      "type": "TEXT",    "constraint": ""},
        {"name": "attributes",  "type": "TEXT",    "constraint": ""},  # JSON blob
        {"name": "is_valid",    "type": "INTEGER", "constraint": "DEFAULT 1"},
        {"name": "loaded_at",   "type": "TEXT",    "constraint": ""},
    ],
    "indexes": [
        {"name": "idx_category", "columns": ["category"]},
        {"name": "idx_lon_lat",  "columns": ["lon", "lat"]},
    ]
}

def schema_to_ddl(schema: dict) -> str:
    '''Generate CREATE TABLE SQL from a schema dict.'''
    cols = []
    for col in schema["columns"]:
        parts = [col["name"], col["type"]]
        if col["constraint"]:
            parts.append(col["constraint"])
        cols.append("    " + "  ".join(parts))

    ddl = f"CREATE TABLE IF NOT EXISTS {schema['table']} (\n"
    ddl += ",\n".join(cols) + "\n);"
    return ddl

ddl = schema_to_ddl(SCHEMA)
print(ddl)"""))

C.append(lesson("4.2", "Create table and indexes from the schema definition",
"""# Create the table using the generated DDL
with engine.begin() as conn:
    conn.execute(text(schema_to_ddl(SCHEMA)))
    print(f"✅ Table '{SCHEMA['table']}' created (or already exists)")

# Add indexes
idx_ddl_template = "CREATE INDEX IF NOT EXISTS {name} ON {table} ({cols})"
with engine.begin() as conn:
    for idx in SCHEMA["indexes"]:
        idx_ddl = idx_ddl_template.format(
            name  = idx["name"],
            table = SCHEMA["table"],
            cols  = ", ".join(idx["columns"])
        )
        conn.execute(text(idx_ddl))
        print(f"✅ Index '{idx['name']}' on ({', '.join(idx['columns'])})")

# Verify table exists by querying its structure (SQLite-specific pragma)
if "sqlite" in DB_URL:
    with engine.connect() as conn:
        info = conn.execute(text("PRAGMA table_info(spatial_records)")).fetchall()
        print(f"\nTable columns ({len(info)} total):")
        for col in info:
            print(f"  {col[1]:<15} {col[2]}")"""))

C.append(exmd(4, "Design a schema for transport stops",
    "Create a schema dict and DDL for a `transport_stops` table (bus/tram/metro stops).",
    ["Define a schema dict with columns: id, stop_name, stop_type (bus/tram/metro), lon, lat, line_code, is_active, loaded_at",
     "Generate the CREATE TABLE SQL using `schema_to_ddl()`",
     "Add an index on `(stop_type, line_code)`",
     "Create the table in the engine"],
    "# Use schema_to_ddl(my_schema)"))
C.append(exstub(4,
    ["Define TRANSPORT_SCHEMA dict with 8 columns",
     "Call schema_to_ddl() and print the SQL",
     "Add an index on stop_type and line_code",
     "Create table and index with engine.begin()"]))
C.append(exsol(4,
"""TRANSPORT_SCHEMA = {
    "table": "transport_stops",
    "description": "Bus, tram and metro stops",
    "columns": [
        {"name": "id",         "type": "INTEGER", "constraint": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "stop_name",  "type": "TEXT",    "constraint": "NOT NULL"},
        {"name": "stop_type",  "type": "TEXT",    "constraint": "NOT NULL"},  # bus/tram/metro
        {"name": "lon",        "type": "REAL",    "constraint": "NOT NULL"},
        {"name": "lat",        "type": "REAL",    "constraint": "NOT NULL"},
        {"name": "line_code",  "type": "TEXT",    "constraint": ""},
        {"name": "is_active",  "type": "INTEGER", "constraint": "DEFAULT 1"},
        {"name": "loaded_at",  "type": "TEXT",    "constraint": ""},
    ],
    "indexes": [
        {"name": "idx_stop_type_line", "columns": ["stop_type", "line_code"]},
    ]
}

ddl = schema_to_ddl(TRANSPORT_SCHEMA)
print(ddl)
print()

with engine.begin() as conn:
    conn.execute(text(ddl))
    for idx in TRANSPORT_SCHEMA["indexes"]:
        conn.execute(text(
            f"CREATE INDEX IF NOT EXISTS {idx['name']} "
            f"ON {TRANSPORT_SCHEMA['table']} ({', '.join(idx['columns'])})"
        ))
    print("✅ transport_stops table and index created")"""))

# ── SECTION 5 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 5 — Inserting Data

Python offers several ways to load records into a database, each with different
trade-offs between simplicity, performance, and control.

### 5.1 Insert strategies at a glance

| Method | Speed | Control | Best for |
|--------|-------|---------|---------|
| `conn.execute(text(INSERT), row)` | medium | full | Single rows, transactions |
| `conn.execute(text(INSERT), [rows])` | fast | full | Batch inserts (< 100k rows) |
| `DataFrame.to_sql()` | easy | limited | Quick data loading from pandas |
| PostgreSQL `COPY` | fastest | low | Millions of rows, CSV import |

### 5.2 Placeholder styles — avoid SQL injection!

```python
# ✅ SAFE — parameterized
conn.execute(text("INSERT INTO t VALUES (:n, :lon, :lat)"), {"n": name, "lon": x, "lat": y})

# ❌ DANGEROUS — never do this
conn.execute(text(f"INSERT INTO t VALUES ('{name}', {x}, {y})"))
```

> ⚠️ **SQL injection** is one of the most common security vulnerabilities in software.
> A user could pass `name = "'; DROP TABLE t; --"` to destroy your data.
> Parameterized queries prevent this completely."""))

C.append(lesson("5.1", "Single INSERT and batch executemany",
"""from datetime import datetime

SAMPLE_RECORDS = [
    {"name": "Vondelpark",       "category": "park",     "lon": 4.8728, "lat": 52.3580, "source": "osm"},
    {"name": "NEMO Museum",      "category": "museum",   "lon": 4.9122, "lat": 52.3738, "source": "osm"},
    {"name": "Albert Cuyp Mkt",  "category": "market",   "lon": 4.8955, "lat": 52.3540, "source": "csv"},
    {"name": "EYE Filmmuseum",   "category": "museum",   "lon": 4.9011, "lat": 52.3842, "source": "api"},
    {"name": "Erasmus Bridge",   "category": "landmark", "lon": 4.4887, "lat": 51.9097, "source": "osm"},
    {"name": "Cube Houses",      "category": "landmark", "lon": 4.4893, "lat": 51.9221, "source": "osm"},
    {"name": "Rotterdam Zoo",    "category": "park",     "lon": 4.4724, "lat": 51.9271, "source": "api"},
]

INSERT_SQL = text("""
    INSERT INTO spatial_records (name, category, lon, lat, source, loaded_at)
    VALUES (:name, :category, :lon, :lat, :source, :loaded_at)
""")

now = datetime.utcnow().isoformat()
rows_to_insert = [{**r, "loaded_at": now} for r in SAMPLE_RECORDS]

with engine.begin() as conn:
    conn.execute(INSERT_SQL, rows_to_insert)

print(f"Inserted {len(rows_to_insert)} records via batch execute")

# Confirm count
with engine.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM spatial_records")).scalar()
print(f"Total rows in spatial_records: {n}")"""))

C.append(lesson("5.2", "DataFrame.to_sql() — quick loading from pandas",
"""# Load a CSV-like structure into a DataFrame, then push to the DB
MORE_RECORDS = [
    {"name": "Keukenhof",   "category": "park",     "lon": 4.5467,  "lat": 52.2697, "source": "csv"},
    {"name": "Madurodam",   "category": "museum",   "lon": 4.2980,  "lat": 52.0944, "source": "csv"},
    {"name": "Scheveningen","category": "beach",    "lon": 4.2708,  "lat": 52.1100, "source": "csv"},
]

df_more = pd.DataFrame(MORE_RECORDS)
df_more["loaded_at"] = datetime.utcnow().isoformat()
df_more["is_valid"]  = 1
df_more["elevation_m"] = None
df_more["attributes"]  = None

print("DataFrame preview:")
print(df_more[["name", "category", "lon", "lat"]].to_string(index=False))

# to_sql with if_exists='append' — adds to existing table
# Use method='multi' for faster multi-row inserts
with engine.connect() as conn:
    df_more.to_sql(
        name       = "spatial_records",
        con        = conn,
        if_exists  = "append",
        index      = False,
        method     = "multi",
    )
    conn.commit()

print(f"\nAppended {len(df_more)} rows via DataFrame.to_sql()")

with engine.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM spatial_records")).scalar()
print(f"Total rows now: {n}")"""))

C.append(exmd(5, "Insert transport stops from a list",
    "Load 5 transport stops into the `transport_stops` table using the batch execute pattern.",
    ["Create a list of 5 stop dicts (stop_name, stop_type, lon, lat, line_code)",
     "Add `loaded_at` timestamp to each record",
     "Use `engine.begin()` + `conn.execute(text(INSERT), rows)` to insert",
     "Verify the count with a SELECT COUNT(*)"],
    "# INSERT INTO transport_stops (stop_name, stop_type, lon, lat, line_code, loaded_at)"))
C.append(exstub(5,
    ["Create list of 5 stop dicts",
     "Add loaded_at to each dict",
     "Build INSERT SQL with named params and execute with engine.begin()",
     "Verify with SELECT COUNT(*)"]))
C.append(exsol(5,
"""from datetime import datetime

stops = [
    {"stop_name": "Centraal Station",  "stop_type": "metro", "lon": 4.9004, "lat": 52.3791, "line_code": "52"},
    {"stop_name": "Leidseplein",        "stop_type": "tram",  "lon": 4.8811, "lat": 52.3625, "line_code": "2"},
    {"stop_name": "Dam Square",         "stop_type": "bus",   "lon": 4.8936, "lat": 52.3731, "line_code": "15"},
    {"stop_name": "Rembrandtplein",     "stop_type": "tram",  "lon": 4.8989, "lat": 52.3659, "line_code": "4"},
    {"stop_name": "Waterlooplein",      "stop_type": "metro", "lon": 4.9003, "lat": 52.3668, "line_code": "51"},
]

now = datetime.utcnow().isoformat()
for s in stops:
    s["loaded_at"] = now

INSERT_STOP = text(
    "INSERT INTO transport_stops (stop_name, stop_type, lon, lat, line_code, loaded_at) "
    "VALUES (:stop_name, :stop_type, :lon, :lat, :line_code, :loaded_at)"
)

with engine.begin() as conn:
    conn.execute(INSERT_STOP, stops)

with engine.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM transport_stops")).scalar()

print(f"✅ Inserted {len(stops)} stops. Total in table: {n}")"""))

# ── SECTION 6 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 6 — Transaction Management

A **transaction** is a group of SQL statements that execute as a single atomic unit.
Either ALL succeed (commit) or ALL are undone (rollback).

### 6.1 ACID properties

| Property | Meaning | Geospatial example |
|----------|---------|-------------------|
| **Atomic** | All or nothing | Load 1000 features — if one fails, none are saved |
| **Consistent** | DB stays valid | CHECK constraints always enforced |
| **Isolated** | Concurrent txns don't interfere | Two ETL jobs loading simultaneously |
| **Durable** | Committed data survives crash | Power failure after commit = data safe |

### 6.2 SQLAlchemy transaction patterns

```python
# Pattern 1: engine.begin() — auto-commit or rollback
with engine.begin() as conn:
    conn.execute(...)        # commits on exit, rolls back on exception

# Pattern 2: engine.connect() — manual control
with engine.connect() as conn:
    conn.execute(...)
    conn.commit()            # explicit commit
    # or conn.rollback()     # undo everything since last commit

# Pattern 3: nested savepoint (PostgreSQL supports this natively)
with engine.begin() as conn:
    conn.execute(insert_A)
    sp = conn.begin_nested()   # savepoint
    try:
        conn.execute(insert_B)
        sp.commit()
    except:
        sp.rollback()          # undo only insert_B
    conn.execute(insert_C)     # still runs
```"""))

C.append(lesson("6.1", "Demonstrate commit and rollback behaviour",
"""# Show that rollback undoes inserts
print("=== Commit example ===")
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
             "VALUES (:n, :c, :lon, :lat, :ts)"),
        {"n": "Test Commit", "c": "test", "lon": 5.0, "lat": 52.0, "ts": datetime.utcnow().isoformat()}
    )
    # engine.begin() auto-commits here

with engine.connect() as conn:
    row = conn.execute(text("SELECT name FROM spatial_records WHERE name='Test Commit'")).fetchone()
print(f"  After commit  — found: {row[0] if row else 'NOT FOUND'}")

print()
print("=== Rollback example ===")
try:
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                 "VALUES (:n, :c, :lon, :lat, :ts)"),
            {"n": "Test Rollback", "c": "test", "lon": 5.0, "lat": 52.0, "ts": datetime.utcnow().isoformat()}
        )
        # Force a failure
        conn.execute(text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                          "VALUES (NULL, 'x', 0, 0, 'x')"))   # NULL violates NOT NULL
except Exception as e:
    print(f"  Exception caught: {type(e).__name__}")

with engine.connect() as conn:
    row = conn.execute(text("SELECT name FROM spatial_records WHERE name='Test Rollback'")).fetchone()
print(f"  After rollback — found: {row[0] if row else 'NOT FOUND (correctly rolled back)'}")"""))

C.append(lesson("6.2", "Partial rollback with savepoints (nested transactions)",
"""# Savepoints let you roll back part of a transaction while keeping the rest.
# SQLite supports savepoints; PostgreSQL does too.

print("=== Savepoint demo ===")

with engine.begin() as conn:
    # Insert A — this will be kept
    conn.execute(
        text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
             "VALUES (:n, :c, :lon, :lat, :ts)"),
        {"n": "SavepointA", "c": "test", "lon": 4.9, "lat": 52.3, "ts": datetime.utcnow().isoformat()}
    )

    # Savepoint before risky insert
    sp = conn.begin_nested()
    try:
        conn.execute(
            text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                 "VALUES (:n, :c, :lon, :lat, :ts)"),
            {"n": "SavepointB_bad", "c": "test", "lon": 999, "lat": 999, "ts": datetime.utcnow().isoformat()}
        )
        # Simulate a business-rule rejection
        raise ValueError("lon=999 is out of valid range!")
        sp.commit()
    except Exception as e:
        sp.rollback()   # only undo SavepointB_bad
        print(f"  Savepoint rolled back: {e}")

    # Insert C after savepoint recovery — still in the same outer transaction
    conn.execute(
        text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
             "VALUES (:n, :c, :lon, :lat, :ts)"),
        {"n": "SavepointC", "c": "test", "lon": 4.88, "lat": 52.35, "ts": datetime.utcnow().isoformat()}
    )

# Verify which rows are present
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT name FROM spatial_records WHERE name LIKE 'Savepoint%' ORDER BY name")
    ).fetchall()

print("Rows saved after savepoint demo:")
for r in rows:
    print(f"  ✅ {r[0]}")"""))

C.append(exmd(6, "Transaction with validation gate",
    "Insert a batch of records but reject the entire batch if any record fails a coordinate check.",
    ["Create a list of 4 records — include 1 with an invalid lat (> 90)",
     "Validate all records BEFORE inserting (fail fast)",
     "If validation passes, insert with `engine.begin()`",
     "If validation fails, print which record failed and skip the batch"],
    "# Validate: -180 <= lon <= 180 and -90 <= lat <= 90"))
C.append(exstub(6,
    ["Create a list with 4 records including 1 with lat > 90",
     "Loop through records validating lon/lat ranges",
     "If invalid found, print the offending record and abort",
     "Otherwise insert all records with engine.begin()"]))
C.append(exsol(6,
"""batch = [
    {"name": "Good A",   "category": "test", "lon":  4.90, "lat": 52.37},
    {"name": "Good B",   "category": "test", "lon":  4.48, "lat": 51.92},
    {"name": "BAD LON",  "category": "test", "lon": 999.0, "lat": 52.00},  # invalid!
    {"name": "Good D",   "category": "test", "lon":  5.12, "lat": 52.09},
]

def validate_record(r):
    if not (-180 <= r["lon"] <= 180):
        return f"lon={r['lon']} out of range [-180, 180]"
    if not (-90  <= r["lat"] <=  90):
        return f"lat={r['lat']} out of range [-90, 90]"
    return None

errors = [(r["name"], validate_record(r)) for r in batch if validate_record(r)]

if errors:
    print(f"❌ Batch rejected — {len(errors)} validation error(s):")
    for name, msg in errors:
        print(f"   {name}: {msg}")
    print("   No rows inserted.")
else:
    now = datetime.utcnow().isoformat()
    rows = [{**r, "loaded_at": now} for r in batch]
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                 "VALUES (:name, :category, :lon, :lat, :loaded_at)"),
            rows
        )
    print(f"✅ {len(batch)} records inserted successfully")"""))

# ── SECTION 7 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 7 — Querying Data

Effective data retrieval is just as important as loading. This section covers
patterns for safe, efficient SQL SELECT queries from Python.

### 7.1 Query result objects

SQLAlchemy `execute()` returns a `CursorResult`. Key methods:

| Method | Returns | When to use |
|--------|---------|-------------|
| `.fetchone()` | single `Row` or `None` | Lookup by ID |
| `.fetchall()` | `list[Row]` | Small result sets |
| `.fetchmany(n)` | `list[Row]` | Page-at-a-time processing |
| `.scalar()` | single value | `COUNT(*)`, `MAX()` |
| `.mappings().all()` | `list[dict]` | Dict access by column name |

### 7.2 Row access patterns

```python
row = conn.execute(text("SELECT name, lon FROM cities WHERE id=:id"), {"id": 1}).fetchone()
row[0]          # positional: "Amsterdam"
row.name        # attribute:  "Amsterdam"
dict(row)       # dict:       {"name": "Amsterdam", "lon": 4.9041}
row._mapping    # MappingProxyType — read-only dict
```"""))

C.append(lesson("7.1", "SELECT with WHERE, ORDER BY, LIMIT, and row access",
"""with engine.connect() as conn:

    # --- All records in a category, sorted ---
    rows = conn.execute(
        text("SELECT name, lon, lat FROM spatial_records "
             "WHERE category = :cat ORDER BY name LIMIT :lim"),
        {"cat": "museum", "lim": 10}
    ).fetchall()

    print(f"Museums (up to 10):")
    for r in rows:
        print(f"  {r.name:<25}  lon={r.lon:.4f}  lat={r.lat:.4f}")

    # --- Aggregate queries ---
    print()
    agg = conn.execute(text("""
        SELECT
            category,
            COUNT(*)     AS n,
            MIN(lon)     AS min_lon,
            MAX(lon)     AS max_lon,
            AVG(lat)     AS avg_lat
        FROM spatial_records
        WHERE is_valid = 1
        GROUP BY category
        ORDER BY n DESC
    """)).fetchall()

    print(f"{'Category':<12} {'Count':>5}  {'min_lon':>8}  {'max_lon':>8}  {'avg_lat':>8}")
    print("-" * 52)
    for r in agg:
        print(f"{r.category:<12} {r.n:>5}  {r.min_lon:>8.4f}  {r.max_lon:>8.4f}  {r.avg_lat:>8.4f}")"""))

C.append(lesson("7.2", "Load query results into a pandas DataFrame",
"""with engine.connect() as conn:

    # read_sql accepts text() objects and returns a DataFrame directly
    df = pd.read_sql(
        sql = text("""
            SELECT name, category, lon, lat, source
            FROM spatial_records
            WHERE is_valid = 1
              AND category != 'test'
            ORDER BY category, name
        """),
        con = conn,
    )

print(f"Loaded {len(df)} rows into DataFrame")
print(f"Columns: {list(df.columns)}")
print()

# Summary stats
print("Records per category:")
print(df.groupby("category").size().sort_values(ascending=False).to_string())
print()

# Bounding box from the data
print(f"Longitude range : {df['lon'].min():.4f} → {df['lon'].max():.4f}")
print(f"Latitude range  : {df['lat'].min():.4f} → {df['lat'].max():.4f}")
print()

# Export DataFrame to CSV
csv_out = DATA_DIR / "spatial_records_export.csv"
df.to_csv(csv_out, index=False)
print(f"Exported to: {csv_out}")"""))

C.append(exmd(7, "Parameterized bounding-box query",
    "Query all spatial_records within a geographic bounding box using named parameters.",
    ["Define min_lon, max_lon, min_lat, max_lat to cover the Netherlands (roughly 3.4–7.2°E, 50.8–53.6°N)",
     "Run a WHERE clause with all four parameters",
     "Load results into a DataFrame with pd.read_sql()",
     "Print the count and a summary of categories found"],
    "# WHERE lon BETWEEN :min_lon AND :max_lon AND lat BETWEEN :min_lat AND :max_lat"))
C.append(exstub(7,
    ["Define bbox parameters for the Netherlands",
     "Write parameterized SELECT with all four bounds",
     "Load into DataFrame with pd.read_sql()",
     "Print count and value_counts() of categories"]))
C.append(exsol(7,
"""bbox = {"min_lon": 3.4, "max_lon": 7.2, "min_lat": 50.8, "max_lat": 53.6}

with engine.connect() as conn:
    df_nl = pd.read_sql(
        sql = text(
            "SELECT name, category, lon, lat FROM spatial_records "
            "WHERE lon BETWEEN :min_lon AND :max_lon "
            "  AND lat BETWEEN :min_lat AND :max_lat "
            "  AND category != 'test' "
            "ORDER BY name"
        ),
        con    = conn,
        params = bbox,
    )

print(f"Records within Netherlands bounding box: {len(df_nl)}")
print()
print("Categories found:")
print(df_nl["category"].value_counts().to_string())
print()
print(df_nl[["name","category","lon","lat"]].to_string(index=False))"""))

# ── SECTION 8 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## �� Section 8 — PostGIS Setup and Geometry Types

**PostGIS** extends PostgreSQL with native geometry storage and hundreds of spatial
functions. It is the reference implementation for spatial SQL.

> 🐘 **This section describes PostgreSQL + PostGIS patterns.** Code cells that
> require a live server are clearly marked. The SQL shown here is exact
> production code — run it when you have a PostgreSQL server available.

### 8.1 Enabling PostGIS

```sql
-- Run once as a database superuser:
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify installation:
SELECT PostGIS_Version();
-- → "3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1"
```

### 8.2 Geometry vs Geography

| Type | Storage | Distance unit | Accuracy | Use when |
|------|---------|--------------|---------|---------|
| **geometry** | Cartesian (flat) | map units (m for UTM) | Exact in local CRS | Analysis within a region |
| **geography** | Spheroidal (globe) | metres | Accurate globally | Distance across continents |

### 8.3 Creating a PostGIS table

```sql
CREATE TABLE poi_postgis (
    id       SERIAL PRIMARY KEY,
    name     TEXT   NOT NULL,
    category TEXT,
    -- WGS84 point geometry, SRID 4326
    geom     GEOMETRY(Point, 4326)
);

-- ALWAYS add a spatial index:
CREATE INDEX ON poi_postgis USING GIST (geom);
```

### 8.4 Inserting geometry

```sql
-- From WKT (Well-Known Text):
INSERT INTO poi_postgis (name, category, geom)
VALUES (
    'Rijksmuseum',
    'museum',
    ST_GeomFromText('POINT(4.8852 52.3600)', 4326)
);

-- From lon/lat directly:
INSERT INTO poi_postgis (name, category, geom)
VALUES ('Vondelpark', 'park', ST_SetSRID(ST_MakePoint(4.8728, 52.3580), 4326));
```

### 8.5 Reading geometry back

```sql
-- As WKT:
SELECT name, ST_AsText(geom) FROM poi_postgis;

-- As GeoJSON (ready for mapping):
SELECT name, ST_AsGeoJSON(geom)::json FROM poi_postgis;

-- X and Y coordinates:
SELECT name, ST_X(geom) AS lon, ST_Y(geom) AS lat FROM poi_postgis;
```"""))

C.append(lesson("8.1", "Simulate PostGIS WKT patterns with SQLite (portable demo)",
r"""# We store WKT strings in SQLite to demonstrate the PostGIS INSERT/SELECT pattern.
# On PostgreSQL + PostGIS, replace the WKT column with a GEOMETRY column
# and use ST_GeomFromText() / ST_AsText().

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS poi_wkt (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            category TEXT,
            wkt      TEXT    NOT NULL,    -- stores WKT; replace with GEOMETRY on PostGIS
            srid     INTEGER DEFAULT 4326
        )
    """))
    conn.execute(text("DELETE FROM poi_wkt"))

pois = [
    {"name": "Rijksmuseum",  "category": "museum",   "lon": 4.8852,  "lat": 52.3600},
    {"name": "Vondelpark",   "category": "park",     "lon": 4.8728,  "lat": 52.3580},
    {"name": "NEMO Science", "category": "museum",   "lon": 4.9122,  "lat": 52.3738},
    {"name": "Artis Zoo",    "category": "park",     "lon": 4.9163,  "lat": 52.3665},
]

for p in pois:
    p["wkt"] = f"POINT({p['lon']} {p['lat']})"

with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO poi_wkt (name, category, wkt) VALUES (:name, :category, :wkt)"),
        pois
    )

# Read back — parse WKT to extract lon/lat
with engine.connect() as conn:
    rows = conn.execute(text("SELECT name, category, wkt FROM poi_wkt ORDER BY name")).fetchall()

print(f"POI table ({len(rows)} rows):")
print(f"{'Name':<20} {'Category':<10} {'WKT'}")
print("-" * 55)
for r in rows:
    print(f"{r.name:<20} {r.category:<10} {r.wkt}")

print()
print("Equivalent PostGIS INSERT (copy-paste ready for PostgreSQL):")
print("  INSERT INTO poi_postgis (name, category, geom)")
print("  VALUES ('Rijksmuseum', 'museum', ST_GeomFromText('POINT(4.8852 52.3600)', 4326));")"""))

C.append(lesson("8.2", "PostGIS reference SQL patterns (read-only — requires live server)",
"""# 🐘 The SQL in this cell requires PostgreSQL + PostGIS.
# It is shown as print() output so the notebook runs everywhere.

POSTGIS_PATTERNS = {
    "enable_extension": """
-- Enable PostGIS (run once as superuser):
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_Version();
""",
    "create_table": """
-- Create a spatial table with a geometry column:
CREATE TABLE poi_postgis (
    id       SERIAL PRIMARY KEY,
    name     TEXT   NOT NULL,
    category TEXT,
    geom     GEOMETRY(Point, 4326)   -- WGS84 point
);
CREATE INDEX ON poi_postgis USING GIST (geom);
""",
    "insert_wkt": """
-- Insert from WKT:
INSERT INTO poi_postgis (name, category, geom)
VALUES ('Rijksmuseum', 'museum',
        ST_GeomFromText('POINT(4.8852 52.3600)', 4326));
""",
    "insert_makepoint": """
-- Insert with ST_MakePoint (lon, lat order):
INSERT INTO poi_postgis (name, category, geom)
SELECT name, category,
       ST_SetSRID(ST_MakePoint(lon, lat), 4326)
FROM   staging_csv;               -- bulk load from staging table
""",
    "select_geojson": """
-- Export as GeoJSON FeatureCollection-ready JSON:
SELECT
    name,
    category,
    ST_AsGeoJSON(geom)::json AS geometry
FROM poi_postgis
WHERE category = 'museum';
""",
    "spatial_distance": """
-- Distance between two points (metres, using geography cast):
SELECT
    a.name, b.name,
    ST_Distance(a.geom::geography, b.geom::geography) AS dist_m
FROM poi_postgis a, poi_postgis b
WHERE a.id < b.id
ORDER BY dist_m;
""",
}

for key, sql in POSTGIS_PATTERNS.items():
    print(f"=== {key.upper()} ===")
    print(sql)"""))

C.append(exmd(8, "Build a WKT insert helper",
    "Write a function that takes a list of POI dicts (name, category, lon, lat) and inserts them into `poi_wkt` as WKT strings.",
    ["Write `insert_pois(pois: list[dict], engine) -> int` that builds WKT and batch-inserts",
     "Include a `is_valid_coord(lon, lat)` guard — skip invalid records",
     "Return the number of successfully inserted rows",
     "Test with 3 valid and 1 invalid record"],
    "# f'POINT({lon} {lat})'  ← WKT point string"))
C.append(exstub(8,
    ["Write is_valid_coord(lon, lat) returning bool",
     "Write insert_pois(pois, engine) that filters and inserts",
     "Build WKT string for each valid record",
     "Return count of inserted rows and call with test data"]))
C.append(exsol(8,
"""def is_valid_coord(lon: float, lat: float) -> bool:
    return -180 <= lon <= 180 and -90 <= lat <= 90

def insert_pois(pois: list, engine) -> int:
    valid = []
    for p in pois:
        if is_valid_coord(p["lon"], p["lat"]):
            valid.append({**p, "wkt": f"POINT({p['lon']} {p['lat']})"})
        else:
            print(f"  ⚠️  Skipped invalid: {p['name']} (lon={p['lon']}, lat={p['lat']})")

    if valid:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO poi_wkt (name, category, wkt) "
                     "VALUES (:name, :category, :wkt)"),
                valid
            )
    return len(valid)

test_pois = [
    {"name": "Keukenhof Gardens", "category": "park",    "lon":  4.5467, "lat": 52.2697},
    {"name": "Leiden Observatory","category": "museum",  "lon":  4.4570, "lat": 52.1565},
    {"name": "Bad Coord",         "category": "test",    "lon": 999.0,   "lat":  0.0},
    {"name": "Gouda Kaasmarkt",   "category": "market",  "lon":  4.7116, "lat": 52.0116},
]

n = insert_pois(test_pois, engine)
print(f"\n✅ Inserted {n} POIs (1 skipped)")

with engine.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM poi_wkt")).scalar()
print(f"Total rows in poi_wkt: {total}")"""))

# ── SECTION 9 ─────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 9 — Error Handling and Connection Management

Production ETL pipelines need robust error handling so a single bad record
doesn't silently corrupt the whole dataset.

### 9.1 Database exceptions hierarchy

```
Exception
└── SQLAlchemyError
    ├── OperationalError    ← connection refused, timeout, server restart
    ├── IntegrityError      ← NOT NULL, UNIQUE, FK violation
    ├── ProgrammingError    ← bad SQL syntax, missing table
    └── DataError           ← value out of range, bad type
```

For psycopg2 directly:
```
psycopg2.Error
├── psycopg2.OperationalError
├── psycopg2.IntegrityError
└── psycopg2.ProgrammingError
```

### 9.2 Connection pooling

SQLAlchemy manages a **connection pool** automatically:

```python
engine = create_engine(
    DB_URL,
    pool_size       = 5,    # keep 5 connections alive
    max_overflow    = 10,   # allow up to 10 extra during spikes
    pool_timeout    = 30,   # wait max 30s for a free connection
    pool_recycle    = 1800, # recycle connections older than 30 min
)
```

> 💡 For long-running ETL jobs, set `pool_pre_ping=True` to test connections
> before using them — prevents "server closed the connection" errors."""))

C.append(lesson("9.1", "Catch and classify database exceptions",
"""from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

def safe_insert(engine, name, category, lon, lat):
    '''Insert one record with detailed error reporting.'''
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                     "VALUES (:n, :c, :lon, :lat, :ts)"),
                {"n": name, "c": category, "lon": lon, "lat": lat,
                 "ts": datetime.utcnow().isoformat()}
            )
        return True, None

    except IntegrityError as e:
        return False, f"IntegrityError (NOT NULL / UNIQUE): {e.orig}"
    except OperationalError as e:
        return False, f"OperationalError (connection / table missing): {e.orig}"
    except ProgrammingError as e:
        return False, f"ProgrammingError (bad SQL): {e.orig}"
    except Exception as e:
        return False, f"Unexpected error: {type(e).__name__}: {e}"

test_cases = [
    ("Valid Record",  "landmark", 4.85, 52.35),   # should succeed
    (None,            "landmark", 4.85, 52.35),   # NULL name → IntegrityError
    ("Valid B",       "landmark", 4.86, 52.36),   # should succeed
]

for args in test_cases:
    ok, err = safe_insert(engine, *args)
    status = "✅" if ok else "❌"
    label  = args[0] if args[0] else "(NULL name)"
    print(f"  {status} {label:<20}  {err or 'inserted OK'}")"""))

C.append(lesson("9.2", "Retry logic for transient errors",
"""import time

def insert_with_retry(engine, records: list, max_retries: int = 3, delay: float = 1.0) -> dict:
    '''Insert records with retry on OperationalError (transient connection issues).

    Returns a dict with 'inserted', 'failed', and 'errors'.
    '''
    result = {"inserted": 0, "failed": 0, "errors": []}

    for attempt in range(1, max_retries + 1):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
                         "VALUES (:name, :category, :lon, :lat, :loaded_at)"),
                    records
                )
            result["inserted"] = len(records)
            return result

        except OperationalError as e:
            if attempt < max_retries:
                print(f"  ⚠️  Attempt {attempt} failed (OperationalError). "
                      f"Retrying in {delay}s…")
                time.sleep(delay)
            else:
                result["failed"]  = len(records)
                result["errors"].append(str(e))
                return result

        except Exception as e:
            result["failed"]  = len(records)
            result["errors"].append(f"{type(e).__name__}: {e}")
            return result

    return result

retry_records = [
    {"name": "Retry A", "category": "test", "lon": 4.9, "lat": 52.3,
     "loaded_at": datetime.utcnow().isoformat()},
    {"name": "Retry B", "category": "test", "lon": 4.8, "lat": 52.2,
     "loaded_at": datetime.utcnow().isoformat()},
]

r = insert_with_retry(engine, retry_records)
print(f"Result: inserted={r['inserted']}, failed={r['failed']}, errors={r['errors']}")"""))

C.append(exmd(9, "Error-safe batch loader with per-row fallback",
    "Write a loader that tries to insert a batch, and if that fails, falls back to row-by-row insertion so valid records are saved.",
    ["Write `batch_or_rowwise(engine, records) -> dict` returning `{inserted, failed, errors}`",
     "First try batch insert with `engine.begin()`",
     "On failure, fall back to inserting one row at a time, collecting errors per row",
     "Test with a mixed batch (3 valid + 1 with NULL name)"],
    "# Try batch → on IntegrityError → loop individual inserts"))
C.append(exstub(9,
    ["Write batch_or_rowwise(engine, records) function",
     "Try batch insert first — return on success",
     "On exception, loop row-by-row and collect errors",
     "Return dict with inserted/failed/errors counts"]))
C.append(exsol(9,
"""def batch_or_rowwise(engine, records: list) -> dict:
    result = {"inserted": 0, "failed": 0, "errors": []}

    INSERT = text(
        "INSERT INTO spatial_records (name, category, lon, lat, loaded_at) "
        "VALUES (:name, :category, :lon, :lat, :loaded_at)"
    )

    try:
        with engine.begin() as conn:
            conn.execute(INSERT, records)
        result["inserted"] = len(records)
    except Exception as batch_err:
        print(f"  Batch failed ({type(batch_err).__name__}) — falling back to row-by-row")
        for r in records:
            try:
                with engine.begin() as conn:
                    conn.execute(INSERT, r)
                result["inserted"] += 1
            except Exception as row_err:
                result["failed"] += 1
                result["errors"].append({"record": r.get("name", "?"), "error": str(row_err)[:80]})

    return result

mixed_batch = [
    {"name": "Good X",  "category": "test", "lon": 4.9, "lat": 52.3, "loaded_at": datetime.utcnow().isoformat()},
    {"name": "Good Y",  "category": "test", "lon": 4.8, "lat": 52.2, "loaded_at": datetime.utcnow().isoformat()},
    {"name": None,      "category": "test", "lon": 4.7, "lat": 52.1, "loaded_at": datetime.utcnow().isoformat()},  # NULL!
    {"name": "Good Z",  "category": "test", "lon": 4.6, "lat": 52.0, "loaded_at": datetime.utcnow().isoformat()},
]

res = batch_or_rowwise(engine, mixed_batch)
print(f"\nResult: inserted={res['inserted']}, failed={res['failed']}")
for err in res["errors"]:
    print(f"  ❌ {err['record']}: {err['error']}")"""))

# ── SECTION 10 ────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 📖 Section 10 — Building the ETL Module

A well-structured ETL module makes your data loading **reproducible, testable,
and production-ready**. This section builds `spatial_etl.py` — a reusable
module you can drop into any geospatial project.

### 10.1 ETL module responsibilities

```
spatial_etl.py
├── validate_record(r)      → True / raises ValidationError
├── transform_record(r)     → clean, typed dict
├── load_records(records, engine) → LoadResult
├── verify_load(table, n_expected, engine) → bool
└── run_etl(csv_path, engine) → report dict
```

### 10.2 Module design principles

| Principle | Implementation |
|-----------|---------------|
| **Single responsibility** | Each function does one thing |
| **Fail loudly** | Raise custom exceptions, never silently ignore errors |
| **Log everything** | Use Python `logging` with timestamps and counts |
| **Return structured results** | Return dicts/dataclasses, not just print() |
| **Testable** | Pure functions where possible; no hidden state |"""))

# Build the ETL module cell using %%writefile (no triple-quote conflict)
etl_module_lines = [
    "%%writefile spatial_etl.py\n",
    '"""Spatial ETL module for loading geospatial records into a database."""\n',
    "from __future__ import annotations\n",
    "import csv, json, logging\n",
    "from dataclasses import dataclass, field\n",
    "from datetime import datetime\n",
    "from pathlib import Path\n",
    "from sqlalchemy import create_engine, text\n",
    "from sqlalchemy.exc import SQLAlchemyError\n",
    "\n",
    "logger = logging.getLogger(__name__)\n",
    "\n",
    "\n",
    "class ValidationError(ValueError):\n",
    "    pass\n",
    "\n",
    "\n",
    "@dataclass\n",
    "class LoadResult:\n",
    "    table:    str\n",
    "    inserted: int = 0\n",
    "    rejected: int = 0\n",
    "    errors:   list = field(default_factory=list)\n",
    "    started:  str  = field(default_factory=lambda: datetime.utcnow().isoformat())\n",
    "    finished: str  = ''\n",
    "\n",
    "    def summary(self) -> str:\n",
    "        return (f'Table={self.table}  inserted={self.inserted}  '\n",
    "                f'rejected={self.rejected}  errors={len(self.errors)}')\n",
    "\n",
    "\n",
    "def validate_record(r: dict) -> dict:\n",
    "    name = (r.get('name') or '').strip()\n",
    "    if not name:\n",
    "        raise ValidationError(\"'name' is required and cannot be blank\")\n",
    "    try:\n",
    "        lon = float(r['lon'])\n",
    "        lat = float(r['lat'])\n",
    "    except (KeyError, TypeError, ValueError) as exc:\n",
    "        raise ValidationError(f'lon/lat must be numeric: {exc}') from exc\n",
    "    if not (-180 <= lon <= 180):\n",
    "        raise ValidationError(f'lon={lon} outside [-180, 180]')\n",
    "    if not (-90 <= lat <= 90):\n",
    "        raise ValidationError(f'lat={lat} outside [-90, 90]')\n",
    "    return {'name': name, 'category': (r.get('category') or 'unknown').strip().lower(),\n",
    "            'lon': lon, 'lat': lat, 'source': (r.get('source') or '').strip(),\n",
    "            'is_valid': 1, 'loaded_at': datetime.utcnow().isoformat()}\n",
    "\n",
    "\n",
    "def load_records(records: list, engine, table: str = 'spatial_records') -> LoadResult:\n",
    "    result = LoadResult(table=table)\n",
    "    valid_rows = []\n",
    "    for r in records:\n",
    "        try:\n",
    "            valid_rows.append(validate_record(r))\n",
    "        except ValidationError as e:\n",
    "            result.rejected += 1\n",
    "            result.errors.append({'record': r.get('name', '?'), 'error': str(e)})\n",
    "            logger.warning('Rejected record %r: %s', r.get('name', '?'), e)\n",
    "    if not valid_rows:\n",
    "        result.finished = datetime.utcnow().isoformat()\n",
    "        return result\n",
    "    INSERT = text(f'INSERT INTO {table} (name, category, lon, lat, source, is_valid, loaded_at) '\n",
    "                  'VALUES (:name, :category, :lon, :lat, :source, :is_valid, :loaded_at)')\n",
    "    try:\n",
    "        with engine.begin() as conn:\n",
    "            conn.execute(INSERT, valid_rows)\n",
    "        result.inserted = len(valid_rows)\n",
    "        logger.info('Batch-inserted %d rows into %r', result.inserted, table)\n",
    "    except SQLAlchemyError as e:\n",
    "        logger.error('Batch insert failed: %s -- falling back to row-by-row', e)\n",
    "        for row in valid_rows:\n",
    "            try:\n",
    "                with engine.begin() as conn:\n",
    "                    conn.execute(INSERT, row)\n",
    "                result.inserted += 1\n",
    "            except SQLAlchemyError as row_err:\n",
    "                result.rejected += 1\n",
    "                result.errors.append({'record': row['name'], 'error': str(row_err)[:120]})\n",
    "    result.finished = datetime.utcnow().isoformat()\n",
    "    return result\n",
    "\n",
    "\n",
    "def verify_load(table: str, n_expected: int, engine) -> bool:\n",
    "    with engine.connect() as conn:\n",
    "        n = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()\n",
    "    ok = n >= n_expected\n",
    "    logger.info('verify_load: %s has %d rows (expected >= %d) -> %s', table, n, n_expected, ok)\n",
    "    return ok\n",
    "\n",
    "\n",
    "def run_etl(csv_path, engine, table: str = 'spatial_records') -> dict:\n",
    "    csv_path = Path(csv_path)\n",
    "    logger.info('ETL started: %s -> %s', csv_path.name, table)\n",
    "    with open(csv_path, encoding='utf-8', newline='') as fh:\n",
    "        records = list(csv.DictReader(fh))\n",
    "    logger.info('Read %d raw records from %s', len(records), csv_path.name)\n",
    "    result   = load_records(records, engine, table)\n",
    "    verified = verify_load(table, result.inserted, engine)\n",
    "    report   = {'source': csv_path.name, 'table': table, 'raw': len(records),\n",
    "                'inserted': result.inserted, 'rejected': result.rejected,\n",
    "                'verified': verified, 'errors': result.errors,\n",
    "                'started': result.started, 'finished': result.finished}\n",
    "    logger.info('ETL finished: %s', result.summary())\n",
    "    return report\n",
]

C.append({
    "cell_type": "code",
    "id": cell_id(),
    "metadata": {},
    "execution_count": None,
    "outputs": [],
    "source": etl_module_lines,
})


C.append(lesson("10.2", "Import and use the spatial_etl module",
"""# Configure logging so we can see what the module does
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt = "%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "week6_etl.log", mode="w", encoding="utf-8"),
    ]
)

import importlib, sys

# Reload fresh (handles repeated notebook runs)
if "spatial_etl" in sys.modules:
    importlib.reload(sys.modules["spatial_etl"])
else:
    import spatial_etl

# ── Quick function-level tests ────────────────────────────────────────────────
print("=== validate_record ===")
try:
    r = spatial_etl.validate_record({"name": "Test", "lon": "4.9", "lat": "52.3"})
    print(f"  Valid:   {r['name']}, lon={r['lon']}, lat={r['lat']}")
except spatial_etl.ValidationError as e:
    print(f"  ❌ {e}")

try:
    spatial_etl.validate_record({"name": "", "lon": "0", "lat": "0"})
except spatial_etl.ValidationError as e:
    print(f"  Caught expected error: {e}")

print()
print("=== load_records ===")
test_records = [
    {"name": "Module Test A", "category": "test", "lon": "4.88", "lat": "52.34"},
    {"name": "Module Test B", "category": "test", "lon": "4.90", "lat": "52.37"},
    {"name": "Bad Record",    "category": "test", "lon": "999",  "lat": "0"},
]

result = spatial_etl.load_records(test_records, engine)
print(f"  {result.summary()}")

print()
print("=== verify_load ===")
ok = spatial_etl.verify_load("spatial_records", 1, engine)
print(f"  verify_load → {ok}")"""))

C.append(exmd(10, "Add a unit test for validate_record",
    "Write a `unittest.TestCase` for `spatial_etl.validate_record` covering valid input, blank name, and out-of-range coordinates.",
    ["Write `TestValidateRecord(unittest.TestCase)` with at least 4 test methods",
     "Test a fully valid record returns the expected dict",
     "Test blank name raises `ValidationError`",
     "Test lon > 180 raises `ValidationError`",
     "Test lat < -90 raises `ValidationError`"],
    "# self.assertRaises(spatial_etl.ValidationError, spatial_etl.validate_record, bad_record)"))
C.append(exstub(10,
    ["Import unittest and spatial_etl",
     "Write TestValidateRecord(unittest.TestCase) class",
     "Add test_valid, test_blank_name, test_bad_lon, test_bad_lat methods",
     "Run with unittest.main(argv=[''], exit=False)"]))
C.append(exsol(10,
"""import unittest
import importlib
import spatial_etl
importlib.reload(spatial_etl)

class TestValidateRecord(unittest.TestCase):

    def test_valid_record(self):
        r = spatial_etl.validate_record({"name": "Park", "lon": "4.9", "lat": "52.3", "category": "park"})
        self.assertEqual(r["name"], "Park")
        self.assertAlmostEqual(r["lon"], 4.9)
        self.assertAlmostEqual(r["lat"], 52.3)
        self.assertEqual(r["category"], "park")

    def test_blank_name(self):
        with self.assertRaises(spatial_etl.ValidationError):
            spatial_etl.validate_record({"name": "  ", "lon": "0", "lat": "0"})

    def test_missing_name(self):
        with self.assertRaises(spatial_etl.ValidationError):
            spatial_etl.validate_record({"lon": "0", "lat": "0"})

    def test_lon_out_of_range(self):
        with self.assertRaises(spatial_etl.ValidationError):
            spatial_etl.validate_record({"name": "X", "lon": "181", "lat": "0"})

    def test_lat_out_of_range(self):
        with self.assertRaises(spatial_etl.ValidationError):
            spatial_etl.validate_record({"name": "X", "lon": "0", "lat": "-91"})

    def test_non_numeric_coords(self):
        with self.assertRaises(spatial_etl.ValidationError):
            spatial_etl.validate_record({"name": "X", "lon": "abc", "lat": "52"})

suite = unittest.TestLoader().loadTestsFromTestCase(TestValidateRecord)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
print(f"\nPassed: {result.testsRun - len(result.failures) - len(result.errors)} / {result.testsRun}")"""))

# ── MINI-LAB ──────────────────────────────────────────────────────────────────
C.append(md(
"""---
## 🔬 Mini-Lab — City Records ETL Loader

**Scenario:** You receive a CSV file of European city records from a field team.
Some records have coordinate errors, missing fields, or wrong data types.
Your job is to build a complete ETL pipeline that:

1. Creates a clean target table in the database
2. Reads the raw CSV
3. Validates and transforms each record
4. Loads valid records with transaction control
5. Verifies the load count
6. Writes a structured loading report to JSON

**Tools used:** `pathlib`, `csv`, `sqlalchemy`, `spatial_etl`, `logging`, `json`

---

Work through Steps 1–6 below. Each step builds on the previous."""))

C.append(labstep(1, "Create the raw CSV input file",
"""# Simulate the CSV that arrives from the field team
RAW_CSV = DATA_DIR / "cities_raw.csv"

raw_rows = [
    "name,country,city_type,lon,lat,population",
    "Amsterdam,NL,capital,4.9041,52.3676,921402",
    "Rotterdam,NL,port,4.4777,51.9244,651446",
    "The Hague,NL,government,4.2952,52.0705,545000",
    "Utrecht,NL,university,5.1214,52.0907,361924",
    "Eindhoven,NL,technology,5.4697,51.4416,235691",
    "Brussels,BE,capital,4.3517,50.8503,1208542",
    "Antwerp,BE,port,4.4025,51.2194,529247",
    "Ghent,BE,university,3.7174,51.0543,262219",
    ",BE,unknown,3.5,50.5,0",           # missing name
    "BadLon,DE,test,999.0,52.0,1000",   # invalid lon
    "Munich,DE,state,11.5820,48.1351,1488202",
    "Frankfurt,DE,finance,8.6821,50.1109,764104",
    "Cologne,DE,culture,6.9578,50.9333,1084394",
    "Hamburg,DE,port,9.9937,53.5511,1841179",
    "Berlin,DE,capital,13.4050,52.5200,3669491",
]

RAW_CSV.write_text("\n".join(raw_rows), encoding="utf-8")
print(f"Written: {RAW_CSV}  ({len(raw_rows)-1} data rows + header)")
print()
print("Preview (first 5 rows):")
for line in raw_rows[:6]:
    print(f"  {line}")"""))

C.append(labstep(2, "Create a fresh target table for the lab",
"""LAB_TABLE = "lab_cities"

create_sql = text(f"""
    CREATE TABLE IF NOT EXISTS {LAB_TABLE} (
        id          INTEGER  PRIMARY KEY AUTOINCREMENT,
        name        TEXT     NOT NULL,
        category    TEXT     NOT NULL DEFAULT 'city',
        lon         REAL     NOT NULL,
        lat         REAL     NOT NULL,
        source      TEXT,
        is_valid    INTEGER  DEFAULT 1,
        loaded_at   TEXT
    )
""")

with engine.begin() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {LAB_TABLE}"))
    conn.execute(create_sql)
    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_lab_lon_lat ON {LAB_TABLE} (lon, lat)"))

print(f"✅ Table '{LAB_TABLE}' created with spatial index")"""))

C.append(labstep(3, "Read and inspect the raw CSV",
"""import csv

with open(RAW_CSV, encoding="utf-8", newline="") as fh:
    reader = csv.DictReader(fh)
    raw_records = list(reader)

print(f"Raw records read : {len(raw_records)}")
print(f"Columns          : {list(raw_records[0].keys())}")
print()
print(f"{'name':<20} {'country':<5} {'lon':>8} {'lat':>8} {'pop':>10}")
print("-" * 58)
for r in raw_records:
    print(f"{r.get('name','(blank)'):<20} {r.get('country',''):<5} "
          f"{r.get('lon','?'):>8} {r.get('lat','?'):>8} "
          f"{r.get('population','?'):>10}")"""))

C.append(labstep(4, "Transform and validate records using spatial_etl",
"""importlib.reload(spatial_etl)

valid_rows   = []
invalid_rows = []

for r in raw_records:
    # Map CSV columns → spatial_etl expected fields
    mapped = {
        "name":     r.get("name", ""),
        "category": r.get("city_type", "city"),
        "lon":      r.get("lon", ""),
        "lat":      r.get("lat", ""),
        "source":   f"{r.get('country','')}:csv",
    }
    try:
        valid_rows.append(spatial_etl.validate_record(mapped))
    except spatial_etl.ValidationError as e:
        invalid_rows.append({"raw": r, "reason": str(e)})

print(f"Validation results:")
print(f"  ✅ Valid   : {len(valid_rows)}")
print(f"  ❌ Invalid : {len(invalid_rows)}")
print()
print("Rejected records:")
for inv in invalid_rows:
    print(f"  name='{inv['raw'].get('name','')}'  reason={inv['reason']}")"""))

C.append(labstep(5, "Load valid records with transaction control and verify",
"""# Load into the lab table
result = spatial_etl.load_records(valid_rows, engine, table=LAB_TABLE)
print(f"Load result: {result.summary()}")

# Verify
ok = spatial_etl.verify_load(LAB_TABLE, result.inserted, engine)
print(f"Verification : {'✅ PASSED' if ok else '❌ FAILED'}")

# Show what's in the table
with engine.connect() as conn:
    df_lab = pd.read_sql(
        text(f"SELECT name, category, lon, lat, source FROM {LAB_TABLE} ORDER BY source, name"),
        conn
    )

print(f"\nLoaded records ({len(df_lab)} rows):")
print(df_lab.to_string(index=False))"""))

C.append(labstep(6, "Write a structured load report to JSON",
"""from datetime import datetime

report = {
    "etl_run": {
        "timestamp":    datetime.utcnow().isoformat() + "Z",
        "source_file":  str(RAW_CSV),
        "target_table": LAB_TABLE,
    },
    "counts": {
        "raw_records":    len(raw_records),
        "valid":          result.inserted,
        "invalid":        result.rejected + len(invalid_rows),
    },
    "verification": {
        "passed":         ok,
        "rows_in_table":  result.inserted,
    },
    "errors": [
        {"record": inv["raw"].get("name",""), "reason": inv["reason"]}
        for inv in invalid_rows
    ],
}

REPORT_PATH = DATA_DIR / "etl_report.json"
REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("ETL Report:")
print(json.dumps(report, indent=2))
print()
print(f"✅ Report saved to: {REPORT_PATH}")"""))

# ── Extension ─────────────────────────────────────────────────────────────────
C.append(md(
"""### 🎯 Mini-Lab Extension Exercises

Work through these before Week 7 to consolidate your skills.

---

**Extension A — UPSERT (insert or update)**
Modify `spatial_etl.load_records()` to use `INSERT OR REPLACE` (SQLite) or
`INSERT … ON CONFLICT DO UPDATE` (PostgreSQL) so re-running the ETL updates
existing records instead of duplicating them.

---

**Extension B — Add population column**
Extend the lab to preserve the `population` field from the raw CSV.
Add a `population INTEGER` column to the table, include it in validation,
and display a bar-chart of population by country using pandas/matplotlib.

---

**Extension C — Connect to a real PostgreSQL server**
If you have access to a PostgreSQL server (local install or cloud):
1. Change `DB_URL` to `postgresql+psycopg2://user:pwd@host:5432/dbname`
2. Run `CREATE EXTENSION IF NOT EXISTS postgis;`
3. Change the `lon`/`lat` columns to a `GEOMETRY(Point, 4326)` column
4. Use `ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)` in your INSERT statements
5. Read back using `ST_X(geom)` and `ST_Y(geom)`"""))

# ── SUMMARY ───────────────────────────────────────────────────────────────────
C.append(md(
"""---
## ✅ Week 6 Summary

| Topic | Key concepts mastered |
|-------|-----------------------|
| **Connection strings** | DSN format, SQLite vs PostgreSQL URLs, env-var credentials |
| **psycopg2** | `connect()`, `cursor()`, `execute()`, `%s` placeholders, `RealDictCursor` |
| **SQLAlchemy Core** | `create_engine()`, `engine.begin()`, `text()`, named parameters |
| **Schema design** | Column types, constraints, indexes, geometry column planning |
| **Table creation** | `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX`, `PRAGMA table_info` |
| **Batch INSERT** | `executemany`, `DataFrame.to_sql()`, `if_exists='append'` |
| **Transactions** | ACID, `engine.begin()` auto-commit, `rollback()`, savepoints |
| **Querying** | `fetchall()`, `fetchone()`, `scalar()`, `pd.read_sql()` |
| **PostGIS** | `CREATE EXTENSION postgis`, `GEOMETRY(Point, 4326)`, `ST_GeomFromText` |
| **ETL module** | `spatial_etl.py` — validate, load, verify, report with logging |

---

### ☑️ Self-assessment checklist

Before moving to Week 7, confirm you can do each of these **without looking at notes**:

- [ ] Write a correct SQLAlchemy connection URL for both SQLite and PostgreSQL
- [ ] Create an engine, open a connection, and execute a SELECT with named parameters
- [ ] Design a schema for a spatial records table with appropriate data types
- [ ] Create a table and spatial index in Python using `engine.begin()`
- [ ] Insert a batch of records using `conn.execute(text(INSERT), list_of_dicts)`
- [ ] Load a CSV into a DataFrame and push it to a table with `DataFrame.to_sql()`
- [ ] Explain the difference between `engine.begin()` (auto-commit) and `engine.connect()`
- [ ] Catch `IntegrityError` and `OperationalError` separately and handle each
- [ ] Describe the difference between `GEOMETRY` and `GEOGRAPHY` in PostGIS
- [ ] Run a complete ETL pipeline using `spatial_etl.run_etl(csv_path, engine)`

---

## 📚 Week 7 Preview — PostGIS Core Queries

Next week we write spatial SQL that answers real urban-planning questions:

| Topic | What you will learn |
|-------|---------------------|
| **Spatial types** | `GEOMETRY`, `GEOGRAPHY`, WKT, WKB, GeoJSON in SQL |
| **ST_Intersects** | Find all features that overlap a polygon |
| **ST_Within** | Point-in-polygon checks at database scale |
| **ST_Buffer** | Generate buffer zones around features |
| **ST_DWithin** | Find features within N metres of a point |
| **ST_Transform** | Reproject geometries between SRID in SQL |
| **Spatial indexes** | GIST index creation, EXPLAIN ANALYZE, query plans |
| **Lab** | Answer urban planning questions using PostGIS |

**Assignment due Week 7:**
Using this week's `spatial_etl.py` as a starting point, extend it to:
1. Accept a `geometry_wkt` field in input records
2. Build `ST_GeomFromText(:wkt, 4326)` INSERT statements
3. Verify loaded geometries with `ST_IsValid(geom)`
Full instructions provided at the start of Week 7.

---

## 📖 Further Reading

| Resource | Why |
|----------|-----|
| [SQLAlchemy Core docs](https://docs.sqlalchemy.org/en/20/core/) | Authoritative reference for all Core patterns |
| [psycopg2 docs](https://www.psycopg.org/docs/) | Official psycopg2 API and connection parameters |
| [PostgreSQL CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html) | Full syntax for constraints, types, defaults |
| [PostGIS intro](https://postgis.net/documentation/getting_started/) | Getting started with PostGIS spatial types |
| [Real Python — Python & PostgreSQL](https://realpython.com/python-postgresql/) | Worked psycopg2 examples with explanations |
| [Use The Index, Luke](https://use-the-index-luke.com/) | Deep guide to database indexing strategy |
| [Natural Earth Data](https://www.naturalearthdata.com/) | Free country/city datasets for practice |

---

*Geospatial Python Mastery — Week 6 of 10*
*For educational use. Please keep feedback to help improve future iterations.*"""))

# ── Write notebook ─────────────────────────────────────────────────────────────
metadata = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11.0",
    },
}

notebook = {
    "cells":     C,
    "metadata":  metadata,
    "nbformat":  4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

md_cells   = sum(1 for c in C if c["cell_type"] == "markdown")
code_cells = sum(1 for c in C if c["cell_type"] == "code")
size_kb    = OUT.stat().st_size / 1024

print(f"Written : {OUT}")
print(f"Cells   : {len(C)}  (markdown: {md_cells}, code: {code_cells})")
print(f"Size    : {size_kb:.1f} KB")
