import pandas as pd # 匯入套件pandas，並簡稱它為pd
data = pd.read_csv('https://drive.google.com/uc?id=1DwWDG0zvAIRjh3rzD_llnCUHEV7nxf3Y',encoding='big5') # 讀取csv資料表

data.head() # 查看前五筆資料

data.shape # 查看欄、列數

data.columns # 查看欄名稱

# 將不用的資料整欄刪除
data_cleaned = data.drop(columns=['unit'])
data_cleaned = data.drop(columns=['o3_8hr'])
data_cleaned = data.drop(columns=['co_8hr'])

# 查看遺失資料筆數
missing_data_cleaned = data_cleaned.isnull().sum()
print(missing_data_cleaned)
data_cleaned.shape

# 將本為數字格式的資料轉為數字(原本為文字)
numeric_columns = ['aqi','so2', 'co', 'o3', 'pm10', 'pm2.5', 'no2', 'nox', 'no', 'pm2.5_avg', 'pm10_avg', 'so2_avg','longitude','latitude']
for col in numeric_columns:
  data_cleaned[col] = pd.to_numeric(data[col], errors='coerce')
  data_cleaned[col].fillna(data_cleaned[col].mean(), inplace=True)

# 將缺失非數字資料的整筆資料刪除
data_cleaned = data_cleaned.dropna(subset=['county', 'aqi', 'datacreationdate', 'longitude', 'latitude','windspeed'])
data_cleaned['windspeed'] = pd.to_numeric(data['windspeed'], errors='coerce')

# 重新檢視遺失資料筆數
missing_data_cleaned = data_cleaned.isnull().sum()
print(missing_data_cleaned)

# 加入月份資料(由datacreationdate中讀取月份資料放入新的一欄)
data_cleaned['month'] = pd.to_datetime(data_cleaned['datacreationdate'],errors='coerce').dt.month

# 加入小時資料(由datacreationdate中讀取小時資料放入新的一欄)
data_cleaned['hour'] = pd.to_datetime(data_cleaned['datacreationdate'],errors='coerce').dt.hour

# 加入各月份平均
monthly_county_avg = data_cleaned.groupby(['county', 'month'])[numeric_columns].mean().reset_index()

# 加入各測站平均
monthly_site_avg = data_cleaned.groupby(['county','sitename', 'month'])[numeric_columns].mean().reset_index()

# 加入每小時平均
hourly_county_avg = data_cleaned.groupby(['county', "hour"])[numeric_columns].mean().reset_index()

# 加入每小時測站平均
hourly_site_avg = data_cleaned.groupby(['sitename', "hour"])[numeric_columns].mean().reset_index()
monthly_county_avg, monthly_site_avg, hourly_county_avg

import plotly.express as px
import plotly.graph_objects as go

# 縣市空氣品質比較（箱形圖）
fig_box = px.box(monthly_county_avg, x='county', y='aqi', title='台灣各縣市各月平均空氣品質指標(AQI)比較箱型圖', labels={'county': '縣市', 'aqi': 'AQI'},width=1600*0.95,height=900*0.95)

# 調整圖名位置、字體大小
fig_box.update_layout(xaxis_tickangle=90,title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(size=18))
fig_box.show()

# 月份空氣品質變化（折線圖）
fig_line = px.line(monthly_county_avg, x='month', y='aqi',color = 'county', title='台灣各縣市各月平均空氣品質指標(AQI)變化折線圖', labels={'month': '月份', 'aqi': 'AQI'},width=1600,height=900)

# 調整圖名位置、字體大小
fig_line.update_layout(xaxis_tickangle=90,title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(size=18))

fig_line.show()

# 各地每月AQI值(地圖散佈動畫圖)
fig_mapbox = px.scatter_mapbox(monthly_site_avg,lon='longitude',lat='latitude',range_color=(20,85),color='aqi',title='各地每月AQI值地圖散佈動畫圖',animation_frame='month',labels={'pm2.5': 'PM2.5 濃度', 'pm10': 'PM10 濃度'},width = 1600,height = 900,hover_data={
    'sitename':True,
    'latitude':True,
    'longitude':True
})

# 調整圖名位置、字體大小
fig_mapbox.update_layout(
    title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    font=dict(size=18))

# 以MapBox網站Token取用世界地圖後依照經緯度繪出散佈點、調整縮放與點大小
fig_mapbox.update_layout(mapbox = {'accesstoken':'pk.eyJ1IjoieWtldmluYyIsImEiOiJjbHhqNXl3Z3QxeTFrMmpvdmllazJuaDUwIn0.XGT2IUF3HpQiEycf-IFifA','zoom':6.5})
fig_mapbox.update_traces(marker=dict(size=15))
fig_mapbox

# 風速對空氣品質指標 (AQI) 之影響(散佈圖)
fig_wind_speed = px.scatter(data_cleaned.sort_values(by=["windspeed"]), x='windspeed', y='aqi', color='county', title='風速對空氣品質指標 (AQI) 之影響散佈圖', labels={'windspeed': '風速', 'aqi': '空氣品質指標 (AQI)'},width = 1600,height = 900,hover_data={
    'sitename':True
})

# 調整圖名位置、字體大小
fig_wind_speed.update_layout(
    title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    font=dict(size=18))

fig_wind_speed.show()

# 月份空氣品質變化（折線圖）
fig_line = px.line(hourly_county_avg, x='hour', y='aqi',color = 'county', title='台灣各縣市各測站每小時平均空氣品質指標(AQI)變化折線圖', labels={'hour': '時', 'aqi': 'AQI'},width=1600,height=900)

# 調整圖名位置、字體大小
fig_line.update_layout(xaxis_tickangle=90,title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(size=18))

fig_line.show()

# 每小時AQI值(地圖散佈動畫圖)並調整浮動資料窗格顯示資料
fig_mapbox = px.scatter_mapbox(hourly_site_avg,lon='longitude',lat='latitude',range_color=(20,80),color='aqi',title='每小時AQI值地圖散佈動畫圖',animation_frame='hour',labels={'pm2.5': 'PM2.5 濃度', 'pm10': 'PM10 濃度'},width = 1600,height = 900,hover_data={
    'sitename':True,
    'latitude':True,
    'longitude':True
})

# 調整圖名位置、字體大小
fig_mapbox.update_layout(
    title={
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    font=dict(size=18))

# 以MapBox網站Token取用世界地圖後依照經緯度繪出散佈點、調整縮放與點大小
fig_mapbox.update_layout(mapbox = {'accesstoken':'pk.eyJ1IjoieWtldmluYyIsImEiOiJjbHhqNXl3Z3QxeTFrMmpvdmllazJuaDUwIn0.XGT2IUF3HpQiEycf-IFifA','zoom':6.5})
fig_mapbox.update_traces(marker=dict(size=15))
fig_mapbox
