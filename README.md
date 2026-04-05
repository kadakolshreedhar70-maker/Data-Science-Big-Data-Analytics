# Data-Science-Big-Data-Analysis

`Data-Science-Big-Data-Analysis` is a Python-based data engineering and analytics project that collects Google Trends signals for fashion and travel keywords, transforms the data into a small lakehouse-style layout, and serves the results through a Streamlit dashboard. The working application inside this repository is named `TrendVoyage`.

## Team Member Information

Team information below is taken from the submitted project report. GitHub usernames were not listed in the report.

| Team Member Name | Student ID / Roll No. | GitHub Username | Role / Contribution |
| --- | --- | --- | --- |
| SHREEDHAR M KADAKOL | 24bds076 | Not listed in report | Led the overall project planning, coordinated end-to-end integration, selected the initial trend keywords, helped shape the project idea, and aligned the collected data with the final dashboard requirements and report structure. |
| RAHUL PATIL | 24bds064 | Not listed in report | Worked on the Spark-friendly data pipeline, parquet-based storage design, batch processing flow, and generation of structured gold summary tables for downstream analytics. |
| SHRAWAN TIBAREWAL | 24bds075 | Not listed in report | Focused on forecasting logic, analytical interpretation of trend behavior, ranking-oriented outputs, and validation of projected trend movement in the later stages of the workflow. |
| ASMIT CHAKRABORTHY | 24bds006 | Not listed in report | Worked on the Streamlit dashboard, interface layout, chart arrangement, user flow, and integration of processed analytical outputs into the final presentation layer. |

## Repository Structure

```text
Data-Science-Big-Data-Analysis/
|-- ai_engines/
|   `-- demand_forecaster.py
|-- config/
|   `-- settings.py
|-- dashboard/
|   `-- app.py
|-- data/
|   |-- fashion_trends.csv
|   |-- travel_trends.csv
|   `-- lakehouse/
|       |-- bronze/
|       |-- silver/
|       `-- gold/
|-- data_ingestion/
|   `-- google_trends_fetcher.py
|-- spark_jobs/
|   `-- prepare_trend_marts.py
|-- utils/
|   `-- data_paths.py
|-- requirements.txt
|-- report.pdf
|-- .gitignore
`-- README.md
```

## Installation Process

### 1. Clone the repository

```powershell
git clone https://github.com/kadakolshreedhar70-maker/Data-Science-Big-Data-Analysis.git
cd Data-Science-Big-Data-Analysis
```

If the repository is created under a different GitHub account, replace the URL with the final repository URL.

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Environment requirements

- Python 3.10 or later is recommended.
- A Java runtime should be available locally because `pyspark` is used in the analytics stage.
- Internet access is required when running the Google Trends ingestion script.

## Implementation Process

The code follows a three-stage pipeline:

1. `data_ingestion/google_trends_fetcher.py`
   Fetches Google Trends data for fashion and travel keywords using `pytrends`, then saves CSV outputs and parquet datasets into the bronze and silver layers.

2. `spark_jobs/prepare_trend_marts.py`
   Reads the silver parquet datasets with PySpark, reshapes and aggregates the trend data, and writes gold-level analytics tables for downstream consumption.

3. `dashboard/app.py`
   Loads the prepared CSV and parquet datasets into a Streamlit dashboard for fashion insights, travel trend comparison, trip styling suggestions, and brand intelligence views.

Supporting modules:

- `ai_engines/demand_forecaster.py` contains the forecasting logic used by the dashboard.
- `config/settings.py` stores keyword lists and application settings.
- `utils/data_paths.py` centralizes the project data paths used by the ingestion and Spark jobs.

## Executing the Code

Run the commands below from the repository root in this order.

### 1. Fetch Google Trends data

```powershell
python data_ingestion/google_trends_fetcher.py
```

This step refreshes:

- `data/fashion_trends.csv`
- `data/travel_trends.csv`
- parquet datasets in `data/lakehouse/silver/`
- raw snapshot parquet files in `data/lakehouse/bronze/`

### 2. Build analytics-ready Spark outputs

```powershell
python spark_jobs/prepare_trend_marts.py
```

This generates the gold parquet outputs used by the dashboard in `data/lakehouse/gold/`.

### 3. Launch the Streamlit dashboard

```powershell
python -m streamlit run dashboard/app.py
```

After the app starts, open the local address shown in the terminal. The default Streamlit URL is usually:

```text
http://localhost:8501
```

## Notes

- The local `venv/` folder should not be committed; it is already excluded in `.gitignore`.
- The `data/` folder currently contains generated sample outputs that help the dashboard run immediately.
- API key placeholders remain in `config/settings.py`; update them only if your implementation later uses those services.
