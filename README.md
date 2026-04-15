
**Project Title: PhonePe Pulse Data Visualization & Exploration (2026)**

**The Problem:** PhonePe Pulse contains massive amounts of JSON data that are difficult to interpret in raw form.

**The Solution:** An end-to-end data pipeline that extracts, cleans, and stores data in MySQL, visualized through a Streamlit dashboard to provide actionable insights into India's digital economy.

## Project Structure

├── app.py                  # Main Streamlit app
├── SQL/                   # SQL queries
├── data/                  # Raw/processed data            
└── README.md

**Data Flow:**
-Extract: Python scripts clone the Pulse GitHub and parse nested JSON.
-Transform: Pandas handles data cleaning, handling missing values, and state-name normalization.
-Load: Cleaned data is pushed to a MySQL relational database for optimized querying.
-Visualize: Streamlit fetches data via SQL and renders interactive Plotly charts.

**Home Dashboard**
-State-wise choropleth map
-Metrics: Transactions, Users, App Opens

**Key Features & Analysis Pillars:** 
-Transaction Dynamics: Mapping the "Beat of Progress" across 36 states/UTs using charts.
-Device Dominance: Identifying hardware trends (Xiaomi vs. Apple) and their correlation with user engagement.
-Insurance Penetration: Analyzing the growth of digital insurance adoption in Tier-2 and Tier-3 cities.
-User Engagement: Measuring "App Adoption Efficiency" by calculating the ratio of app opens to registered users.
-Market Expansion (Growth Intelligence): * High-Value Targeting: Filtering states with >₹1 Billion in transaction value to identify mature markets.

**Technical Skills Demonstrated:** 
-Languages: Python (Pandas, Plotly, Streamlit).
-Database: MySQL (Complex joins, aggregations, and performance indexing).
-Geospatial Analysis: Mapping India’s financial landscape using GeoJSON and Choropleth visualization.

**Live Insights:**
-While Maharashtra leads in transaction volume, Karnataka shows the highest average ticket size per user.
-Insurance adoption is growing 3x faster in Northern districts compared to the national average.

**Installation:**
-Clone the repo: git clone https://github.com/your-username/phonepe-pulse-analysis.git
-Install dependencies: pip install -r requirements.txt
-Setup MySQL database : Import dataset, Update DB credentials in app.py
-Run the app : python3 -m streamlit run app.py

**Challenges:**
-Data cleaning
-Optimizing SQL queries
-Handling large datasets in visualizations
