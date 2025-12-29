-- Rfam Database Queries
-- Connection: mysql --user=rfamro --host=mysql-rfam-public.ebi.ac.uk --port=4497 --database=Rfam

-- Query 1: Count distinct Acacia plant types
SELECT COUNT(DISTINCT ncbi_id) AS acacia_types
FROM taxonomy
WHERE species LIKE 'Acacia %';

-- Query 2: Wheat species with longest DNA sequence
SELECT 
    t.species AS wheat_type,
    r.rfamseq_acc,
    r.length
FROM rfamseq r
JOIN taxonomy t ON r.ncbi_id = t.ncbi_id
WHERE t.species LIKE '%wheat%'
ORDER BY r.length DESC
LIMIT 1;

-- Query 3: RNA families with large DNA sequences (paginated, 15 per page)
-- Page 1 (OFFSET 0)
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

-- For next pages, change OFFSET to 15, 30, 45, etc.
