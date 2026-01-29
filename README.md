# 🏗️ Resilience Supply Chain Hub (v5.0)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Fast--Analytics-yellow.svg)](https://duckdb.org/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-AI--Insights-purple.svg)](https://ai.google.dev/)

**Resilience Supply Chain Hub** is an advanced analytical platform that transforms raw logistics data into strategic narratives. Built with a modern data stack, it monitors performance, identifies bottlenecks, and correlates sales with global market indicators like Brent Oil prices.

## 🌟 Strategic Features
* **Storytelling Narrative:** Organized in 3 strategic levels (Overview → Diagnosis → Action Plan).
* **Medallion Architecture:** Structured ETL pipeline with **Bronze**, **Silver**, and **Gold** layers ensuring data integrity.
* **AI-Powered Brain:** Integrated with **Google Gemini Pro** to generate automated strategic consulting based on filtered data.
* **High Performance:** Powered by **DuckDB** for sub-second analytical processing of Parquet files.
* **Market Correlation:** Automated ingestion of Brent Oil prices via Yahoo Finance API.

## 🛠️ Tech Stack
* **Data Engine:** DuckDB + Parquet (Columnar storage)
* **Frontend:** Streamlit + Plotly (Interactive visualizations)
* **AI/LLM:** Google Generative AI (Gemini Pro)
* **Orchestration:** Python-based main pipeline

## 📁 Project Structure
```text
resilience_supply_chain/
├── data/
│   ├── bronze/     # Raw CSVs & API Downloads
│   ├── silver/     # Cleaned Data (Parquet)
│   └── gold/       # Star Schema Model (Fact & Dimensions)
├── main.py         # Pipeline Orchestrator (Run this first!)
├── dashboard.py    # Streamlit Interface
├── silver_layer.py # Cleaning Logic
├── gold_layer.py   # Dimensional Modeling
└── requirements.txt

## 🚀 Getting Started

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/andrewnav/resilience_supply_chain.git](https://github.com/andrewnav/resilience_supply_chain.git)
   cd resilience_supply_chain


**Create a .env file in the root directory:**

GEMINI_API_KEY=sua_chave_gemini
NGROK_AUTH_TOKEN=seu_token_ngrok

O projeto é dividido em um pipeline de dados (ETL) e uma interface de visualização (Dashboard).

### Run the Full Pipeline
This command triggers the API data fetch, cleaning, and Star Schema creation:
```bash
    python main.py
```

**📊 Data Pipeline (Medallion)**
The project implements a Star Schema in the Gold layer, optimizing the dashboard to answer complex questions such as: "How do Brent Oil price fluctuations impact shipping costs for Electronics in South America?"

Developed by **Andrew Navarro**
Connecting Data Engineering with Business Strategy.