# Oikos Data Exploration

![Portada](./images/oikos-exploration.png)

## Description

**Oikos Data Exploration** is an extension of the **Oikos** project, a web application for real estate property search. This project is responsible for exploring, analyzing, and visualizing the complete dataset of properties used in the main application.

## Features

- **Interactive Dashboard**: Web interface built with Streamlit to explore data
- **Scrapers**: Scripts to obtain property data from public sources
- **Database**: Property storage in SQLite
- **Data Analysis**: Tools to clean and analyze the dataset

## Project Structure

```
oikos_data_exploration/
├── analysis/          # Data analysis scripts
│   ├── 01_analizar_dataset.py
│   └── 02_limpiar_datos.py
├── dashboard/        # Streamlit application
│   └── app.py
├── database/         # SQLite database
│   └── propiedades.db
├── images/           # Project images
│   └── oikos-exploration.png
├── scraper/          # Data scrapers
│   ├── scraper_ml.py
│   ├── scraper_ml_incremental.py
│   └── processing.py
├── src/              # Utilities and data
│   ├── db_utils.py
│   ├── crear_db.py
│   └── limpiar_db.py
└── requirements.txt
```

## Requirements

- Python 3.8+
- streamlit
- pandas
- plotly
- requests
- beautifulsoup4
- lxml

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard

```bash
streamlit run dashboard/app.py
```

This will open a web interface where you can:

- View overall dataset metrics
- Filter properties by zone, city, and price range
- Explore the complete properties table

### Run the Scrapers

```bash
# Full scraper
python scraper/scraper_ml.py

# Incremental scraper
python scraper/scraper_ml_incremental.py
```

### Data Analysis

```bash
# Analyze dataset
python analysis/01_analizar_dataset.py

# Clean data
python analysis/02_limpiar_datos.py
```

## Relationship with Oikos

This project is an **extension** of the main **Oikos** project. While Oikos is the final property search application for end users, this project:

- Provides the property dataset
- Allows analyzing and validating data quality
- Facilitates exploration and understanding of the dataset
