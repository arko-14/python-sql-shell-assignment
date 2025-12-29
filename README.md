# Assignment

This repository contains solutions to a three-part technical assignment.
Each question is implemented independently and documented in its own folder.

The root README provides a brief overview and points to the detailed
documentation for each part.

---

## Repository Layout

```
ASSIGNMENT/
│
├── scraper/     → Q1: Python Web Scraping
├── sql/         → Q2: SQL Queries (Rfam Database)
├── shell/       → Q3: Unix Shell Script
│
└── README.md    (this file)
```

---

## Contents

### Q1 — Python Web Scraping
**Location:** `scraper/`

- Scrapes product data from *mdcomputers.in*
- Accepts a search term as input
- Handles pagination
- Extracts product name, URL, and pricing

➡ Full implementation details, design choices, and run instructions are documented in:
[scraper/README.md](scraper/README.md)

---

### Q2 — SQL Queries (Rfam Database)
**Location:** `sql/`

- Uses the public Rfam MySQL database
- Answers:
  - Count of *Acacia* plant types
  - Wheat species with the longest DNA sequence
  - Paginated query over RNA families with large DNA sequences

➡ SQL queries and observed outputs are documented in:
[sql/README.md](sql/README.md)

---

### Q3 — Unix Shell Script
**Location:** `shell/`

- Processes a public CSV dataset of S&P 500 companies
- Extracts company name, headquarters location, and founding year
- Outputs results sorted by founding year

➡ Usage instructions and implementation notes are documented in:
[shell/README.md](shell/README.md)

---

## Requirements

- Python 3.9+
- MySQL / MariaDB client
- Git Bash or WSL (for running shell scripts on Windows)

---

## Notes

- All data sources used are public and read-only
- Generated and temporary files are excluded via `.gitignore`
- Each question can be evaluated independently

---

## Status

✔ All questions implemented  
✔ Outputs verified  
✔ Code documented per section  
✔ Ready for review
