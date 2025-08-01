import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from prophet.plot import plot_plotly

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Scottish Births Dashboard",
    page_icon="👶",
    layout="wide"
)

# -----------------------
# CUSTOM CSS
# -----------------------
st.markdown("""
<style>
    .main-heading {
        font-size: 40px;
        font-weight: bold;
        color: #1F4E79;
        margin-bottom: 5px;
    }
    .sub-heading {
        font-size: 16px;
        color: #777;
        margin-bottom: 25px;
    }
    .kpi {
        font-size: 22px;
        font-weight: 600;
    }
    .kpi-label {
        font-size: 14px;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
st.markdown('<div class="main-heading">👶 Scottish Births Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-heading">Explore trends in birth statistics by region, month, and age group — now with forecasting!</div>', unsafe_allow_html=True)

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_excel("monthly region data.xlsx")
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(str)
    return df

df = load_data()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🎛️ Filters")

year_range = st.sidebar.slider(
    "Year Range",
    int(df['year'].min()), int(df['year'].max()),
    (int(df['year'].min()), int(df['year'].max()))
)

month_order = list(calendar.month_name)[1:]
months = st.sidebar.multiselect("Months", month_order, default=month_order)

regions = st.sidebar.multiselect("Regions", sorted(df['region'].unique()), default=sorted(df['region'].unique()))

age_cols = ['<20', '20-29', '30-39', '40+']
selected_ages = st.sidebar.multiselect("Age Groups", age_cols, default=age_cols)

# Forecast controls
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Forecast Settings")
enable_forecast = st.sidebar.checkbox("Enable Birth Forecasting", value=False)
forecast_months = st.sidebar.slider("Forecast Months Ahead", 3, 36, 12)

# -----------------------
# FILTER DATA
# -----------------------
filtered_df = df[(df['year'].between(year_range[0], year_range[1])) &
                 (df['month'].isin(months)) &
                 (df['region'].isin(regions))]

# -----------------------
# KPIs
# -----------------------
total_births = filtered_df['birth_count'].sum()
avg_births = filtered_df.groupby('region')['birth_count'].mean().mean()
top_region = filtered_df.groupby('region')['birth_count'].sum().idxmax()
dominant_age = filtered_df[selected_ages].sum().idxmax()

st.markdown("### 🔢 Key Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Births", value=f"{total_births:,}")
with kpi2:
    st.metric(label="Avg Births/Region", value=f"{int(avg_births):,}")
with kpi3:
    st.metric(label="Top Region", value=top_region)
with kpi4:
    st.metric(label="Dominant Age Group", value=dominant_age)

st.markdown("---")

# -----------------------
# OVERVIEW GRAPHS
# -----------------------
st.subheader("📊 Overview Trends")
col1, col2 = st.columns(2)

with col1:
    yearly = filtered_df.groupby('year')['birth_count'].sum().reset_index()
    fig_yearly = px.line(yearly, x='year', y='birth_count', markers=True,
                         title="Yearly Birth Trend",
                         template="simple_white", color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_yearly, use_container_width=True)

with col2:
    monthly_avg = filtered_df.groupby('month')['birth_count'].mean().reindex(month_order).reset_index()
    fig_monthly = px.bar(monthly_avg, x='month', y='birth_count', text_auto='.2s',
                         title="Average Births per Month",
                         color='birth_count', color_continuous_scale='Blues')
    st.plotly_chart(fig_monthly, use_container_width=True)

# -----------------------
# DISTRIBUTION
# -----------------------
st.subheader("🧬 Birth Distribution Insights")
col3, col4 = st.columns(2)

with col3:
    age_dist = filtered_df[selected_ages].sum().reset_index()
    age_dist.columns = ['Age Group', 'Births']
    fig_age_pie = px.pie(age_dist, names='Age Group', values='Births', hole=0.45,
                         title="By Age Group", color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_age_pie, use_container_width=True)

with col4:
    region_share = filtered_df.groupby('region')['birth_count'].sum().reset_index()
    fig_region_pie = px.pie(region_share, names='region', values='birth_count', hole=0.45,
                            title="By Region", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_region_pie, use_container_width=True)

# -----------------------
# DETAILED TRENDS
# -----------------------
st.subheader("📈 Detailed Trends")

# Age group area chart
age_trend = filtered_df.groupby('year')[selected_ages].sum().reset_index()
fig_age_trend = px.area(age_trend, x='year', y=selected_ages,
                        title="Age Group Birth Trends Over Time",
                        template="simple_white")
st.plotly_chart(fig_age_trend, use_container_width=True)

# Region line chart
region_trend = filtered_df.groupby(['year', 'region'])['birth_count'].sum().reset_index()
fig_region_trend = px.line(region_trend, x='year', y='birth_count', color='region',
                           title="Yearly Births by Region", template="plotly_white")
st.plotly_chart(fig_region_trend, use_container_width=True)

# -----------------------
# HEATMAP
# -----------------------
st.subheader("🔥 Monthly Births by Region Heatmap")

heat_df = filtered_df.groupby(['region', 'month'])['birth_count'].mean().unstack().reindex(columns=month_order)
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(heat_df, cmap="YlOrRd", annot=True, fmt=".0f", linewidths=.5, ax=ax)
st.pyplot(fig)

# -----------------------
# PROPHET FORECAST
# -----------------------
if enable_forecast:
    st.subheader("🔮 Forecast: Future Birth Trends with Prophet")

    prophet_df = filtered_df.groupby(['year', 'month'])['birth_count'].sum().reset_index()
    prophet_df['month'] = prophet_df['month'].apply(lambda x: list(calendar.month_name).index(x))
    prophet_df['ds'] = pd.to_datetime(dict(year=prophet_df['year'], month=prophet_df['month'], day=1))
    prophet_df = prophet_df[['ds', 'birth_count']]
    prophet_df.columns = ['ds', 'y']

    model = Prophet(yearly_seasonality=True)
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=forecast_months, freq='MS')
    forecast = model.predict(future)

    fig_forecast = plot_plotly(model, forecast)
    fig_forecast.update_layout(title="📅 Forecasted Monthly Births", xaxis_title="Date", yaxis_title="Births")
    st.plotly_chart(fig_forecast, use_container_width=True)

    forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_months)
    forecast_display.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound']
    forecast_display['Date'] = forecast_display['Date'].dt.strftime('%b %Y')
    st.markdown("##### 📋 Forecast Summary Table")
    st.dataframe(forecast_display.set_index('Date').style.format("{:.0f}"))
