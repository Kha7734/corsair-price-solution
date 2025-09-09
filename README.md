# “Price Intelligent Solution Streamlit App”

## 1) Purpose

Provide a small front-end tool to upload promotion data (CSV / Excel), validate each row against business rules, let the user filter by country, review valid/invalid rows, and **confirm** to export/submit the validated promotions.

---

## 2) Success criteria (what “done” looks like)

- User can upload CSV or XLSX and see parsed rows.
- User presses **Verify** -> app runs all validations and displays a summary (valid / invalid counts + top error types).
- User can filter preview by country (single-select or multi-select).
- Table view shows valid rows (and a switch/tab to view invalid rows with error messages).
- User can download/export valid rows (and invalid rows if needed).
- **Confirm** button finalizes the selection (e.g., exports CSV and/or calls an API) and prevents accidental re-submission (shows a confirmation modal).

---

## 3) Assumptions I made (so devs know what to adjust)

- `PromtPrice` in your sample is a typo — I’ll treat it as `PromoPrice` (promotional price).
- The file includes a column for `Country` (if not, country selection filters can be applied via a separate `Country` column mapping).
- Confirm action = final submit/export of validated rows (not “approve in a backend system”) — we provide both options: download CSV and POST to a webhook/API (configurable).
- Date/time will use ISO format `YYYY-MM-DD` by default (accept common variants like `DD/MM/YYYY`), timezone = app/local server (no timezone conversion unless required).

---

## 4) Data schema (required columns & types)

| Column name | Type | Required | Notes / expected format |
| --- | --- | --- | --- |
| ProductID | string | Yes | Unique product identifier |
| ITEM_ID | string | Yes | SKU or item id |
| ActualPrice | float | Yes | Must be > 0 |
| PromoPrice | float | Yes | Must be >= 0 and normally ≤ ActualPrice |
| DiscountPercent | float | Yes/Optional | 0–100; can be provided or computed |
| StartDate | date | Yes | `YYYY-MM-DD` (accept common variants) |
| EndDate | date | Yes | `YYYY-MM-DD` |
| Country | string | Yes (for filter) | ISO country code or name |

> Add any optional columns your business needs (Currency, Channel, Comment, PromoType, Region etc.).
> 

---

## 5) Validation rules (explicit, machine-checkable)

Primary checks (run on **Verify**):

1. **Required fields** — no missing `ProductID`, `ITEM_ID`, `ActualPrice`, `PromoPrice`, `StartDate`, `EndDate`, `Country`.
2. **Numeric checks**:
    - `ActualPrice` > 0
    - `PromoPrice` >= 0
3. **Price logic**:
    - Normally `PromoPrice` ≤ `ActualPrice`. If `PromoPrice` > `ActualPrice`, flag as **ERROR: promo price higher than actual** (optionally allow override).
4. **Discount percent check**:
    - Compute `computed_discount = round((ActualPrice - PromoPrice) / ActualPrice * 100, 2)` if `ActualPrice != 0`.
    - If `DiscountPercent` is given, check `abs(DiscountPercent - computed_discount) ≤ tolerance` (default tolerance = **0.5%**). If outside tolerance → **ERROR: discount mismatch**.
    - If `DiscountPercent` missing, auto-fill with `computed_discount`.
5. **Date logic**:
    - Parse `StartDate`, `EndDate`. If parse fails → **ERROR: invalid date**.
    - `StartDate` ≤ `EndDate`. If not → **ERROR: start > end**.
    - Optional business rule: disallow promotions with `EndDate` in the past (flag as warning).
6. **Country mapping**:
    - If `Country` value not in allowed list → **ERROR: unknown country**.
7. **Duplicate / overlap checks** (optional but recommended):
    - If same `ProductID` + `Country` has overlapping `StartDate`/`EndDate`, flag as **ERROR: overlapping promotion**.
8. **Sanity thresholds** (optional):
    - `DiscountPercent` negative or > 100 → **ERROR**.

Each row that fails any check should get an **error column** listing issues (comma-separated).

---

## 6) UI / UX flow (recommended)

1. **Header / title** — short explanation and allowed formats.
2. **File uploader** (`st.file_uploader`) — accepts `.csv`, `.xlsx`. Show sample expected column names and a link to a sample template.
3. On upload, **parse** and show top N rows preview (e.g., first 10) in a small table to confirm parsing.
4. **Buttons row**:
    - `Verify` (primary) — runs validations and shows progress spinner.
    - `Clear / Upload new file`
    - `Confirm` (disabled until at least one valid row exists and after Verify)
5. **Country filter** — `st.selectbox` (single) or `st.multiselect` (multi) with `['All', ...countries found in file]`.
6. **Results pane**:
    - Summary KPI row: valid_count / invalid_count / warnings.
    - Tabs or radio: `Valid` / `Invalid` / `All`.
    - Table view: `st.dataframe` (or AG Grid plugin) showing rows, plus `ValidationErrors` column. Allow sorting and filtering.
    - Row-level actions (optional): accept / reject / edit single row inline (manual override).
7. **Downloads & export**:
    - `Download Valid CSV` (st.download_button).
    - `Download Invalid CSV` (for fixing).
    - `Submit` / `Confirm` -> triggers final action (download &/or call to API).
8. **Confirmation modal** before final submit: show counts & ask “Proceed?”
9. **Result notification**: success or failure messages; export link or API response display.

---

## 7) Behavior of the Verify and Confirm buttons (explicit)

- **Verify**: does not persist anything. It only runs validations on the uploaded dataset and marks rows as valid/invalid. After Verify you can filter and inspect results.
- **Confirm**: finalizes/exports the *valid* rows. Options for implementation:
    - Download `validated_promotions.csv` locally.
    - POST valid rows to a defined webhook/API and show response.
    - Save into a DB (if backend available).
    - After confirm, optionally disable confirm or show a “Submitted” flag for that file.

---

## 8) Edge cases & error handling

- Large files: impose size limit (e.g., 10MB / 100k rows) and show friendly warning if exceeded.
- Encoding problems: detect and show “Failed to parse — check encoding” message.
- Missing Country column: allow user to map a fixed column to `Country` or set a global country value via a dropdown.
- Partial fixes: let user download invalid rows, edit in Excel, and re-upload.
- Race conditions: if multiple users can submit, add unique upload IDs and audit log.

---

## 9) Logs, auditing & security

- Save a copy of uploaded file (or hash) and the validation report for audit (if required).
- If exporting to API, require auth token (configurable).
- Do not persist files on public servers unless necessary. If persistence required, store in protected bucket with retention policy.

---

## 10) Implementation hints (libraries & functions)

- Streamlit UI: `file_uploader`, `st.button`, `st.selectbox`/`multiselect`, `st.dataframe`, `st.tabs`, `st.download_button`, `st.spinner`, `st.success`, `st.error`.
- File parsing: `pandas.read_csv(..., encoding='utf-8', engine='pyarrow' or default)`, `pandas.read_excel(..., engine='openpyxl')`.
- Date parsing: `pandas.to_datetime(..., errors='coerce', dayfirst=False)` then check for `NaT`.
- Validation: vectorized checks with pandas for performance; generate `ValidationErrors` column.
- Optional improved table: use `st_aggrid` to support row selection and inline editing.

---

## 11) Acceptance tests (QA checklist)

- Upload a valid CSV → Verify → all rows valid → Confirm → file downloads and contains same rows.
- Upload file with invalid date format → Verify → shows invalid rows with “invalid date” error.
- Upload file where `PromoPrice` > `ActualPrice` → Verify → those rows flagged.
- Discount percent mismatch beyond tolerance → flagged.
- Country filter shows only that country’s rows.
- Download invalid rows -> edit -> re-upload -> previously invalid rows update.

---

## 12) Example sample row (visual)

```
ProductID,ITEM_ID,ActualPrice,PromoPrice,DiscountPercent,StartDate,EndDate,Country
P12345,SKU-001,100.00,80.00,20.00,2025-10-01,2025-10-15,Vietnam

```

- computed_discount = (100 - 80) / 100 * 100 = 20.00 → matches DiscountPercent.