# Q3 — Unix Shell Script

A shell script that processes S&P 500 company data from a CSV file, extracting company names, headquarters locations, and founding years, sorted chronologically.

## Overview

This script downloads or reads a CSV file containing S&P 500 company information and extracts three key fields:
- Company name (Security)
- Headquarters location
- Founded year

The output is sorted by founding year (oldest first) and formatted as tab-separated values.

## Features

- **Flexible input**: Accepts both URLs and local file paths
- **Automatic download**: Downloads CSV from URL if provided
- **Year extraction**: Intelligently extracts 4-digit years from various date formats
- **Data validation**: Filters out entries without valid founding years
- **Sorted output**: Results sorted chronologically by founding year
- **Clean formatting**: Tab-separated output for easy parsing

## Requirements

- **Bash**: Unix shell (Git Bash or WSL on Windows)
- **Python 3**: For CSV parsing
- **curl**: For downloading files from URLs (usually pre-installed)

## Usage

### With URL (recommended):

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
```

### With local file:

```bash
./extract_companies.sh constituents.csv
```

### Make script executable (first time):

```bash
chmod +x extract_companies.sh
```

## Output Format

The script outputs tab-separated values with three columns:

```
Company Name    Headquarters Location    Founded Year
```

Example output:

```
Colgate-Palmolive    New York, New York    1806
JPMorgan Chase    New York, New York    1823
Procter & Gamble    Cincinnati, Ohio    1837
Pfizer    New York, New York    1849
Wells Fargo    San Francisco, California    1852
...
```

## Implementation Details

### Script Flow

1. **Input validation**: Checks if a file path or URL is provided
2. **Download handling**: If URL is provided, downloads to temporary file
3. **CSV parsing**: Uses Python's CSV module for robust parsing
4. **Year extraction**: Regex pattern `\b(1[6-9]\d{2}|20\d{2})\b` matches years 1600-2099
5. **Sorting**: Sorts by founding year (oldest first)
6. **Cleanup**: Removes temporary files if downloaded

### Year Extraction Logic

The script handles various date formats:
- `1837` → extracts 1837
- `Founded in 1849` → extracts 1849
- `1852-01-01` → extracts 1852
- `Est. 1900` → extracts 1900

Only entries with valid 4-digit years (1600-2099) are included in the output.

### Error Handling

- Exits with error if no input file/URL is provided
- Uses `set -euo pipefail` for strict error handling
- Cleans up temporary files even if script fails

## Data Source

The script is designed to work with the S&P 500 companies dataset:

**Public Dataset URL**:
```
https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv
```

**Expected CSV columns**:
- `Security`: Company name
- `Headquarters Location`: City and state
- `Founded`: Founding year or date

## Example Usage

### Basic usage:

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
```

### Save to file:

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv" > companies_sorted.txt
```

### Count results:

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv" | wc -l
```

### Find oldest companies:

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv" | head -10
```

### Find newest companies:

```bash
./extract_companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv" | tail -10
```

## Notes

- The script uses an embedded Python script for CSV parsing to ensure cross-platform compatibility
- Temporary files are automatically cleaned up after processing
- The script is safe to run multiple times
- Tab-separated output makes it easy to import into spreadsheets or databases
- Companies without valid founding years are excluded from the output

## Troubleshooting

### Permission denied:
```bash
chmod +x extract_companies.sh
```

### Python not found:
Ensure Python 3 is installed and available as `python3`

### curl not found:
Install curl or download the CSV manually and use local file path

### No output:
Check that the CSV file has the expected column names: `Security`, `Headquarters Location`, and `Founded`
