# Q2 — SQL Queries (Rfam Database)

SQL queries against the public Rfam MySQL database to extract biological data about plant species and RNA families.

## Overview

This section contains SQL queries that answer three specific questions using the Rfam public database:
1. Count distinct Acacia plant types
2. Find wheat species with the longest DNA sequence
3. List RNA families with large DNA sequences (paginated)

## Database Connection

The queries use the public Rfam MySQL database:

```bash
mysql --user=rfamro --host=mysql-rfam-public.ebi.ac.uk --port=4497 --database=Rfam
```

Connection details:
- **Host**: mysql-rfam-public.ebi.ac.uk
- **Port**: 4497
- **User**: rfamro (read-only)
- **Database**: Rfam
- **Password**: (none required)

## Queries and Results

### Query 1: Count of Acacia Plant Types

**Question**: How many distinct types of Acacia plants are in the database?

**SQL Query**:
```sql
SELECT COUNT(DISTINCT ncbi_id) AS acacia_types
FROM taxonomy
WHERE species LIKE 'Acacia %';
```

**Result**:
```
+--------------+
| acacia_types |
+--------------+
|          326 |
+--------------+
1 row in set (0.182 sec)
```

**Answer**: There are **326 distinct Acacia plant types** in the Rfam database.

---

### Query 2: Wheat Species with Longest DNA Sequence

**Question**: Which wheat species has the longest DNA sequence?

**SQL Query**:
```sql
SELECT 
    t.species AS wheat_type,
    r.rfamseq_acc,
    r.length
FROM rfamseq r
JOIN taxonomy t ON r.ncbi_id = t.ncbi_id
WHERE t.species LIKE '%wheat%'
ORDER BY r.length DESC
LIMIT 1;
```

**Result**:
```
+------------------------------+-------------+-----------+
| wheat_type                   | rfamseq_acc | length    |
+------------------------------+-------------+-----------+
| Triticum durum (durum wheat) | LT934116.1  | 836514780 |
+------------------------------+-------------+-----------+
```

**Answer**: **Triticum durum (durum wheat)** has the longest DNA sequence with **836,514,780 base pairs** (accession: LT934116.1).

---

### Query 3: RNA Families with Large DNA Sequences (Paginated)

**Question**: List RNA families that have DNA sequences longer than 800 million base pairs, showing 15 results per page.

**SQL Query** (Page 1):
```sql
SELECT 
    f.rfam_acc,
    f.rfam_id AS family_name,
    MAX(r.length) AS max_seq_length
FROM family f
JOIN full_region fr ON f.rfam_acc = fr.rfam_acc
JOIN rfamseq r ON fr.rfamseq_acc = r.rfamseq_acc
GROUP BY f.rfam_acc, f.rfam_id
HAVING max_seq_length > 800000000
ORDER BY max_seq_length DESC
LIMIT 15 OFFSET 0;
```

**Result** (First 15 rows):
```
+----------+--------------+----------------+
| rfam_acc | family_name  | max_seq_length |
+----------+--------------+----------------+
| RF01848  | ACEA_U3      |      836514780 |
| RF01856  | Protozoa_SRP |      836514780 |
| RF01911  | MIR2118      |      836514780 |
| RF03160  | twister-P1   |      836514780 |
| RF03209  | MIR9657      |      836514780 |
| RF03674  | MIR5387      |      836514780 |
| RF03685  | MIR9677      |      836514780 |
| RF03896  | MIR2275      |      836514780 |
| RF03926  | MIR1435      |      836514780 |
| RF04110  | MIR5084      |      836514780 |
| RF04251  | MIR5070      |      836514780 |
| RF00145  | snoZ105      |      830829764 |
| RF00134  | snoZ196      |      801256715 |
| RF00160  | snoZ159      |      801256715 |
| RF00202  | snoR66       |      801256715 |
+----------+--------------+----------------+
```

**Pagination**: To get the next page, change `OFFSET 0` to `OFFSET 15`, then `OFFSET 30`, etc.

---

## Database Schema

Key tables used:
- **taxonomy**: Contains species information (ncbi_id, species name)
- **rfamseq**: Contains DNA sequence data (rfamseq_acc, length, ncbi_id)
- **family**: Contains RNA family information (rfam_acc, rfam_id)
- **full_region**: Links families to sequences (rfam_acc, rfamseq_acc)

## Notes

- All queries are read-only and safe to execute
- The Rfam database is publicly accessible and requires no authentication
- Query execution times may vary based on network latency and database load
- The longest sequences are typically from plant genomes (wheat, barley, etc.)
- Many RNA families share the same maximum sequence length because they're found in the same long genome sequences

## Running the Queries

1. Connect to the database:
```bash
mysql --user=rfamro --host=mysql-rfam-public.ebi.ac.uk --port=4497 --database=Rfam
```

2. Copy and paste any query from above

3. Or run from a file:
```bash
mysql --user=rfamro --host=mysql-rfam-public.ebi.ac.uk --port=4497 --database=Rfam < queries.sql
```
