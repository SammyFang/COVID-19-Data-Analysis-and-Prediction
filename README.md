# COVID-19-Data-Analysis-and-Prediction

A comprehensive data analysis and forecasting project for COVID-19 using machine learning and data visualization techniques.

## Overview

This project explores COVID-19 data, focusing on confirmed cases, deaths, and recoveries across different countries. It applies data preprocessing, visualization, and predictive modeling to analyze infection trends and predict future cases.

## Features

- **Data Collection & Processing**: Aggregates and cleans COVID-19 datasets.
- **Data Visualization**: Generates interactive plots and charts using Matplotlib, Seaborn, and Plotly.
- **Machine Learning Predictions**: Implements Random Forest for forecasting infections and fatalities.
- **Geospatial Analysis**: Uses Plotly to visualize infection and mortality rates over time.

## Dataset Sources

- **COVID-19 Case Data**: `covid_19_clean_complete.csv`
- **Population Data**: `population_by_country_2020.csv`
- **ICU Bed Availability**: `API_SH.MED.BEDS.ZS_DS2_en_csv_v2_887506.csv`
- **Temperature Data**: `temperature_dataframe.csv`
- **Submission File**: `submission.csv`
- **Test Data**: `test.csv`

## Installation

### **Prerequisites**
- **Python 3.9+**
- Required Libraries:
  ```sh
  pip install numpy pandas matplotlib seaborn plotly scikit-learn
  Data Processing
## Data Processing  
The dataset is processed by:  
- Cleaning missing values.  
- Normalizing infection rates per country.  
- Merging with population and healthcare capacity data.  

## Exploratory Data Analysis (EDA)  

### Confirmed Cases Over Time  
```python
import plotly.express as px

fig = px.line(group, x="date", y="confirmed", title="Worldwide Confirmed Cases Over Time")
fig.show()
```
# Results

## Predicted Confirmed Cases
The trained model effectively forecasts COVID-19 cases based on historical data and external factors such as temperature and population density.

## Mortality Rate Analysis
Countries with lower ICU bed availability exhibited higher fatality rates.

## Correlation Findings
Urban population density and median age strongly correlate with infection rates.

## Future Enhancements
- **Real-Time Data Integration**: Automate data retrieval from APIs.  
- **Advanced Deep Learning Models**: Implement LSTMs for time-series forecasting.  
- **Web Dashboard**: Develop an interactive dashboard for live data visualization.  
