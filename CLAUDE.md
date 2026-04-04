# CLAUDE.md — SP500 Trade Signals

Guidance for AI assistants working in this repository.

## Project Overview

An S&P 500 trade signal dashboard built with Streamlit. It fetches live SPY price data via Yahoo Finance, computes RSI and MACD technical indicators, generates LONG/SHORT signals, and renders interactive Plotly charts in a web UI.

## Repository Structure

```
sp500-trade-signals/
├── main.py              # Primary Streamlit entry point (Streamlit Cloud)
├── signals.py           # Data fetching and indicator logic (shared module)
├── requirements.txt     # Python dependencies (no version pins)
├── README.md
└── dashboard/
    └── app.py           # Legacy entry point; nearly identical to main.py
                         # Uses sys.path manipulation to import signals.py
```

**The canonical entry point is `main.py`.** `dashboard/app.py` is a legacy file kept for backwards compatibility — it adds the repo root to `sys.path` so it can also import `signals.py`.

## Running the App

```bash
pip install -r requirements.txt
streamlit run main.py
# or
streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501` by default.

## Key Module: `signals.py`

Contains a single public function:

```python
@st.cache_data(ttl=3600)
def get_spy_data(period="2y") -> pd.DataFrame
```

- Fetches SPY OHLCV history from Yahoo Finance using `yfinance`
- Computes RSI via `ta.momentum.RSIIndicator`
- Computes MACD, MACD signal line, and MACD histogram via `ta.trend.MACD`
- Generates a `Signal` column: `'LONG'` when RSI < 30, `'SHORT'` when RSI > 70, `''` otherwise
- Results are cached for 3600 seconds to avoid redundant API calls
- Returns a `pd.DataFrame` indexed by date with columns: `Close`, `RSI`, `Signal`, `MACD`, `MACD_Signal`, `MACD_Diff`

## Signal Logic

| Condition | Signal |
|-----------|--------|
| RSI < 30  | `LONG` (oversold — buy) |
| RSI > 70  | `SHORT` (overbought — sell) |
| Otherwise | `''` (no signal) |

MACD is displayed for context but does **not** currently influence signal generation.

## Dashboard Layout (`main.py`)

1. **Sidebar** — time period selector (`1mo`, `3mo`, `6mo`, `1y`, `2y`; default `2y`)
2. **Metric row** — LONG count, SHORT count, last signal (type + date), current RSI
3. **Price chart** — SPY close with green triangle-up (LONG) and red triangle-down (SHORT) markers
4. **RSI chart** — RSI oscillator with dashed overbought (70) and oversold (30) reference lines
5. **MACD chart** — MACD line, signal line, and color-coded histogram (green ≥ 0, red < 0)
6. **Recent signals table** — last 10 signal rows showing Date, Close, RSI, MACD, Signal

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `yfinance` | Yahoo Finance data fetching |
| `pandas` | DataFrame manipulation |
| `numpy` | Numerical support |
| `ta` | Technical analysis indicators (RSI, MACD) |
| `plotly` | Interactive charts |

No versions are pinned in `requirements.txt`. If adding new dependencies, append to that file.

## Development Conventions

- **No test suite exists.** There is no `pytest` setup, no test files, and no CI/CD pipeline. Validate changes by running the dashboard manually.
- **No linter or formatter is configured.** Follow PEP 8 style. Keep lines under 100 characters.
- **No type annotations are used** in the existing code; do not add them unless asked.
- **Caching is critical.** `get_spy_data` is decorated with `@st.cache_data(ttl=3600)`. Any function that fetches external data should use this decorator to avoid hammering the Yahoo Finance API.
- **Data flows in one direction:** `signals.py` produces the DataFrame → `main.py` consumes it. Keep these responsibilities separate.
- **Do not duplicate logic** between `main.py` and `dashboard/app.py`. If changing signal or chart logic, `main.py` is the source of truth.

## Common Tasks

### Add a new technical indicator
1. Compute it inside `get_spy_data` in `signals.py` and add it as a new DataFrame column.
2. Render it in `main.py` as a new Plotly figure using `st.plotly_chart`.

### Change signal thresholds
Edit the lambda in `signals.py:14`:
```python
hist['Signal'] = hist['RSI'].apply(lambda r: 'LONG' if r < 30 else 'SHORT' if r > 70 else '')
```

### Add a new time period option
Add the yfinance-compatible period string to the `options` list in `main.py:13` (and the matching line in `dashboard/app.py` if keeping it in sync).

### Clear the data cache
Streamlit caches are keyed on function arguments. Restarting the server clears the cache, or call `st.cache_data.clear()` programmatically.

## Git Workflow

- The `main` branch is the stable branch.
- Feature branches follow the pattern `claude/<description>-<id>` for AI-assisted work.
- Commit messages should be concise and imperative (e.g., `Add Bollinger Band indicator`).
- There are no pre-commit hooks or CI checks — push directly once manually verified.

## Known Issues / Technical Debt

- `requirements.txt` has no version pins — dependency updates may break the app.
- `dashboard/app.py` is nearly identical to `main.py`; consider removing it once Streamlit Cloud is confirmed to use `main.py`.
- No `.gitignore` — consider adding one to exclude `__pycache__/`, `.streamlit/`, and virtual environment directories.
- No error handling for network failures when fetching SPY data from Yahoo Finance.
