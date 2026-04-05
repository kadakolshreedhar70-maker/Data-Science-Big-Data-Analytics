# Data-Science-Big-Data-Analytics

`Data-Science-Big-Data-Analytics` is a Python-based data engineering and analytics project that collects Google Trends signals for fashion and travel keywords, transforms the data into a small lakehouse-style layout, and serves the results through a Streamlit dashboard. The working application inside this repository is named `TrendVoyage`.

## Team Member Information

Replace the sample rows below with your actual team details before publishing or submitting the repository.

| Team Member Name | Student ID / Roll No. | GitHub Username | Role / Contribution |
| --- | --- | --- | --- |
| Member 1 | Add here | Add here | Project coordination and integration |
| Member 2 | Add here | Add here | Data ingestion and preprocessing |
| Member 3 | Add here | Add here | Spark analytics and forecasting |
| Member 4 | Add here | Add here | Dashboard development and documentation |

## Repository Structure

```text
Data-Science-Big-Data-Analytics/
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
git clone https://github.com/kadakolshreedhar70-maker/Data-Science-Big-Data-Analytics.git
cd Data-Science-Big-Data-Analytics
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
