import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"
from plotly.subplots import make_subplots

from pathlib import Path
data_dir = Path('./covid19-global-forecasting-week-1')

import os
os.listdir(data_dir)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
cleaned_data = pd.read_csv('./covid_19_clean_complete.csv', parse_dates=['Date'])

cleaned_data.rename(columns={'ObservationDate': 'date', 
                     'Province/State':'state',
                     'Country/Region':'country',
                     'Last Update':'last_updated',
                     'Confirmed': 'confirmed',
                     'Deaths':'deaths',
                     'Recovered':'recovered'
                    }, inplace=True)

# cases 
cases = ['confirmed', 'deaths', 'recovered', 'active']

# Active Case = confirmed - deaths - recovered
cleaned_data['active'] = cleaned_data['confirmed'] - cleaned_data['deaths'] - cleaned_data['recovered']

# replacing Mainland china with just China
cleaned_data['country'] = cleaned_data['country'].replace('Mainland China', 'China')

# filling missing values 
cleaned_data[['state']] = cleaned_data[['state']].fillna('')
cleaned_data[cases] = cleaned_data[cases].fillna(0)
cleaned_data.rename(columns={'Date':'date'}, inplace=True)

data = cleaned_data

print(data.head())
print(data.info())

# Check if the data is updated # 日期
print("External Data")
print(f"Earliest Entry: {data['date'].min()}")
print(f"Last Entry:     {data['date'].max()}")
print(f"Total Days:     {data['date'].max() - data['date'].min()}")

group = data.groupby('date')['date', 'confirmed', 'deaths'].sum().reset_index()

fig = px.line(group, x="date", y="confirmed", 
              title="Worldwide Confirmed Cases Over Time")
#1. Infections and Fatalities Worldwide

fig.show()

fig = px.line(group, x="date", y="deaths", title="Worldwide Deaths Over Time")

fig.show()

#2. Normalized Infection and Fatality Ratio
def p2f(x):
    """
    Convert urban percentage to float
    """
    try:
        return float(x.strip('%'))/100
    except:
        return np.nan

def age2int(x):
    """
    Convert Age to integer
    """
    try:
        return int(x)
    except:
        return np.nan

def fert2float(x):
    """
    Convert Fertility Rate to float
    """
    try:
        return float(x)
    except:
        return np.nan


countries_df = pd.read_csv("./population_by_country_2020.csv", converters={'Urban Pop %':p2f,
                                                                                                             'Fert. Rate':fert2float,
                                                                                                             'Med. Age':age2int})
countries_df.rename(columns={'Country (or dependency)': 'country',
                             'Population (2020)' : 'population',
                             'Density (P/Km²)' : 'density',
                             'Fert. Rate' : 'fertility',
                             'Med. Age' : "age",
                             'Urban Pop %' : 'urban_percentage'}, inplace=True)



countries_df['country'] = countries_df['country'].replace('United States', 'US')
countries_df = countries_df[["country", "population", "density", "fertility", "age", "urban_percentage"]]

print(countries_df.head())
data = pd.merge(data, countries_df, on='country')

cleaned_latest = data[data['date'] == max(data['date'])]
flg = cleaned_latest.groupby('country')['confirmed', 'population'].agg({'confirmed':'sum', 'population':'mean'}).reset_index()

flg['infectionRate'] = round((flg['confirmed']/flg['population'])*100, 5)
temp = flg[flg['confirmed']>100]
temp = temp.sort_values('infectionRate', ascending=False)

fig = px.bar(temp.sort_values(by="infectionRate", ascending=False)[:10][::-1],
             x = 'infectionRate', y = 'country', 
             title='% of infected people by country', text='infectionRate', height=800, orientation='h',
             color_discrete_sequence=['red']
            )
fig.show()

formated_gdf = data.groupby(['date', 'country'])['confirmed', 'population'].max()
formated_gdf = formated_gdf.reset_index()
formated_gdf['date'] = pd.to_datetime(formated_gdf['date'])
formated_gdf['date'] = formated_gdf['date'].dt.strftime('%m/%d/%Y')
formated_gdf['infectionRate'] = round((formated_gdf['confirmed']/formated_gdf['population'])*100, 8)

fig = px.scatter_geo(formated_gdf, locations="country", locationmode='country names', 
                     color="infectionRate", size='infectionRate', hover_name="country", 
                     range_color= [0, 0.2], 
                     projection="natural earth", animation_frame="date", 
                     title='COVID-19: Spread Over Time (Normalized by Country Population)', color_continuous_scale="portland")
# fig.update(layout_coloraxis_showscale=False)
fig.show()

cleaned_latest = data[data['date'] == max(data['date'])]
flg = cleaned_latest.groupby('country')['confirmed', 'deaths', 'recovered', 'active'].sum().reset_index()

flg['mortalityRate'] = round((flg['deaths']/flg['confirmed'])*100, 2)
temp = flg[flg['confirmed']>100]
temp = temp.sort_values('mortalityRate', ascending=False)

fig = px.bar(temp.sort_values(by="mortalityRate", ascending=False)[:10][::-1],
             x = 'mortalityRate', y = 'country', 
             title='Deaths per 100 Confirmed Cases', text='mortalityRate', height=800, orientation='h',
             color_discrete_sequence=['darkred']
            )
fig.show()

formated_gdf = data.groupby(['date', 'country'])['confirmed', 'deaths'].max()
formated_gdf = formated_gdf.reset_index()
formated_gdf['date'] = pd.to_datetime(formated_gdf['date'])
formated_gdf['date'] = formated_gdf['date'].dt.strftime('%m/%d/%Y')
formated_gdf['mortalityRate'] = round((formated_gdf['deaths']/formated_gdf['confirmed'])*100, 2)

fig = px.scatter_geo(formated_gdf.fillna(0), locations="country", locationmode='country names', 
                     color="mortalityRate", size='mortalityRate', hover_name="country", 
                     range_color= [0, 10], 
                     projection="natural earth", animation_frame="date", 
                     title='COVID-19: Mortality Rate in % by country', color_continuous_scale="portland")
# fig.update(layout_coloraxis_showscale=False)
fig.show()

#3. ICU Beds per Country
icu_df = pd.read_csv("./API_SH.MED.BEDS.ZS_DS2_en_csv_v2_887506.csv")
icu_df['Country Name'] = icu_df['Country Name'].replace('United States', 'US')
icu_df['Country Name'] = icu_df['Country Name'].replace('Russian Federation', 'Russia')
icu_df['Country Name'] = icu_df['Country Name'].replace('Iran, Islamic Rep.', 'Iran')
icu_df['Country Name'] = icu_df['Country Name'].replace('Egypt, Arab Rep.', 'Egypt')
icu_df['Country Name'] = icu_df['Country Name'].replace('Venezuela, RB', 'Venezuela')
data['country'] = data['country'].replace('Czechia', 'Czech Republic')

# We wish to have the most recent values, thus we need to go through every year and extract the most recent one, if it exists.
icu_cleaned = pd.DataFrame()
icu_cleaned["country"] = icu_df["Country Name"]
icu_cleaned["icu"] = np.nan

for year in range(1960, 2020):
    year_df = icu_df[str(year)].dropna()
    icu_cleaned["icu"].loc[year_df.index] = year_df.values

data = pd.merge(data, icu_cleaned, on='country')

data['state'] = data['state'].fillna('')
temp = data[[col for col in data.columns if col != 'state']]

latest = temp[temp['date'] == max(temp['date'])].reset_index()
latest_grouped = latest.groupby('country')['icu'].mean().reset_index()


fig = px.bar(latest_grouped.sort_values('icu', ascending=False)[:10][::-1], 
             x='icu', y='country',
             title='Ratio of ICU Beds per 1000 People', text='icu', orientation='h',color_discrete_sequence=['green'] )
fig.show()

#4. Temperature Data
df_temperature = pd.read_csv("./temperature_dataframe.csv")
df_temperature['country'] = df_temperature['country'].replace('USA', 'US')
df_temperature['country'] = df_temperature['country'].replace('UK', 'United Kingdom')
df_temperature = df_temperature[["country", "province", "date", "humidity", "sunHour", "tempC", "windspeedKmph"]].reset_index()
df_temperature.rename(columns={'province': 'state'}, inplace=True)
df_temperature["date"] = pd.to_datetime(df_temperature['date'])
df_temperature['state'] = df_temperature['state'].fillna('')


df_temperature.info()
# Check if the temperature data is updated
print("External Data")
print(f"Earliest Entry: {df_temperature['date'].min()}")
print(f"Last Entry:     {df_temperature['date'].max()}")
print(f"Total Days:     {df_temperature['date'].max() - data['date'].min()}")
data = data.merge(df_temperature, on=['country','date', 'state'], how='inner')
data.head()

#Regression Model
print("====Regression Model====")
train_data = data
print(train_data.shape)
train_data.head()

threshold = 0.
train_data['infectionRate'] = round((train_data['confirmed']/train_data['population'])*100, 5)
train_data = train_data[train_data['infectionRate'] > threshold]
print(train_data.shape)

train_data = train_data.drop([
                     "country", 
                     "active", 
                     "recovered", 
                     "infectionRate",
                     "state",
                     "Lat",
                     "Long",
                     "date",
                     "index"
                    ], axis= 1).dropna()

y = train_data[["confirmed", "deaths"]]
X = train_data.drop(["confirmed", "deaths"],axis=1)

print(X.head())
print(X.shape, y.shape)

y_infections = y[["confirmed"]]
y_deaths = y[["deaths"]]

X_Infections = X[["population", "density", "fertility", "urban_percentage", 
                  "humidity", "sunHour", "tempC", "windspeedKmph"]]
X_Deaths = X[["population", "density", "age", "icu", "urban_percentage"]]

print(X_Infections.head())
print(X_Infections.shape, y_infections.shape)

print(X_Deaths.head())
print(X_Deaths.shape, y_deaths.shape)

cm = train_data.corr()
plt.figure(figsize=(20,10))
sns.heatmap(cm, annot=True)
plt.show()

#Train and Evaluate Model (Random Forest)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_inf_scaled = scaler.fit_transform(X_Infections)
X_dth_scaled = scaler.fit_transform(X_Deaths)
from sklearn.model_selection import train_test_split as tts
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_log_error, make_scorer
def rmsle(y_true, y_pred):
    return np.sqrt(mean_squared_log_error(y_true, y_pred))

rmsle_scorer = make_scorer(rmsle)
X_inf_train, X_inf_val, y_inf_train, y_inf_val = tts(X_inf_scaled, y_infections, test_size= 0.2, random_state=42, shuffle=True)
X_dth_train, X_dth_val, y_dth_train, y_dth_val = tts(X_dth_scaled, y_deaths, test_size= 0.2, random_state=42, shuffle=True)
model_infected = DecisionTreeRegressor(random_state=42, criterion="mae")
scores = cross_val_score(model_infected, 
                      X_inf_train,
                      y_inf_train["confirmed"],
                      cv=5, scoring=rmsle_scorer)

print("Cross Validation of Confirmed Cases: Mean = {}, std = {}".format(scores.mean(), scores.std()))
model_infected.fit(X_inf_train, y_inf_train["confirmed"])

result_infected = rmsle(y_inf_val["confirmed"], model_infected.predict(X_inf_val))
print("Validation Infected set RMSLE: {}".format(result_infected))
model_deaths = DecisionTreeRegressor(random_state=42, criterion="mae")
scores = cross_val_score(model_deaths, 
                      X_dth_train,
                      y_dth_train["deaths"],
                      cv=5, scoring=rmsle_scorer)
print("Cross Validation of Fatal Cases: Mean = {}, std = {}".format(scores.mean(), scores.std()))
model_deaths.fit(X_dth_train, y_dth_train["deaths"])
result_deaths = rmsle(y_dth_val["deaths"], model_deaths.predict(X_dth_val))
print("Validation Death set RMSLE: {}".format(result_deaths))
# Final Evalutation
print("Final Validation score: {}".format(np.mean([result_infected, result_deaths])))

#Extract Features for Infections

# model_infected = model_infected.fit(X_scaled, y["confirmed"])
# model_deaths = model_deaths.fit(X_scaled, y["deaths"])
model_infected = model_infected.fit(X_inf_scaled, y_infections["confirmed"])
model_deaths = model_deaths.fit(X_dth_scaled, y_deaths["deaths"])

def show_feature_importance(forest, X):
    """
    Creates a sorted list of the feature importance of a decision tree algorithm.
    Furthermore it plots it.
    params:
        forest: Decision Tree algorithm
    """
    importances = forest.feature_importances_
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(X.shape[1]):
        print("{}, Feature: {}, Importance: {}".format(f + 1, X.columns[indices[f]], importances[indices[f]]))

    # Plot the feature importances of the forest
    plt.figure(figsize=(20,10))
    plt.title("Feature importances")
    plt.bar(range(X.shape[1]), importances[indices], color="b", align="center")
    plt.xticks(range(X.shape[1]),  X.columns[indices], rotation='vertical')
    plt.xlim([-1, X.shape[1]])
    plt.show()
show_feature_importance(model_deaths, X_Deaths)
#show_feature_importance(model_infected, X_Infections)
plt.show()
test_df = pd.read_csv("./covid19-global-forecasting-week-1/test.csv")
test_df.rename(columns={'Date': 'date', 
                     'Province/State':'state',
                     'Country/Region':'country',
                    }, inplace=True)
test_df["date"] = pd.to_datetime(test_df['date'])
test_df['state'] = test_df['state'].fillna('')
print(test_df.info())
test_df = test_df.merge(df_temperature, on=['country','date', 'state'], how='left')
test_df = test_df.merge(countries_df, on=['country'], how='left')
test_df = test_df.merge(icu_cleaned, on=['country'], how='left')
test_df.shape
X_test = test_df.set_index("ForecastId").drop(["Lat", "Long", "date", "state", "country", "index"], axis=1).fillna(0)
X_test_inf = X_test[["population", "density", "fertility", "urban_percentage", 
                  "humidity", "sunHour", "tempC", "windspeedKmph"]]
X_test_dth = X_test[["population", "density", "age", "icu", "urban_percentage"]]

y_pred_confirmed = model_infected.predict(X_test_inf)
y_pred_deaths = model_deaths.predict(X_test_dth)

submission = pd.DataFrame()
submission["ForecastId"] = test_df["ForecastId"]
submission = submission.set_index(['ForecastId'])
submission["ConfirmedCases"] = y_pred_confirmed.astype(int)
submission["Fatalities"] = y_pred_deaths.astype(int)
submission.to_csv("submission.csv")
print(submission.tail())
