import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import matplotlib.pyplot as plt
import seaborn as sns
import pmdarima as pm

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Scottish Births Dashboard", page_icon="👶", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
st.markdown('<div class="main-heading">👶 Scottish Births Analytics </div>', unsafe_allow_html=True)
st.markdown('<div class="sub-heading">Explore trends in birth statistics by region, month, and age group — with forecasting</div>', unsafe_allow_html=True)

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
# SIDEBAR FILTERS
# -----------------------
st.sidebar.title("🎛️ Filters")

year_range = st.sidebar.slider("Year Range", int(df['year'].min()), int(df['year'].max()),
                               (int(df['year'].min()), int(df['year'].max())))

month_order = list(calendar.month_name)[1:]
months = st.sidebar.multiselect("Months", month_order, default=month_order)

regions = st.sidebar.multiselect("Regions", sorted(df['region'].unique()), default=sorted(df['region'].unique()))

age_cols = ['<20', '20-29', '30-39', '40+']
selected_ages = st.sidebar.multiselect("Age Groups", age_cols, default=age_cols)

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
kpi1.metric("Total Births", f"{total_births:,}")
kpi2.metric("Avg Births/Region", f"{int(avg_births):,}")
kpi3.metric("Top Region", top_region)
kpi4.metric("Dominant Age Group", dominant_age)

st.markdown("---")

# -----------------------
# SECTION 1: OVERVIEW CHARTS
# -----------------------
st.subheader("📊 Overview Trends")
col1, col2 = st.columns(2)

with col1:
    yearly = filtered_df.groupby('year')['birth_count'].sum().reset_index()
    fig_yearly = px.line(yearly, x='year', y='birth_count', markers=True,
                         title="Yearly Birth Trend", template="simple_white", color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_yearly, use_container_width=True)

with col2:
    monthly_avg = filtered_df.groupby('month')['birth_count'].mean().reindex(month_order).reset_index()
    fig_monthly = px.bar(monthly_avg, x='month', y='birth_count', text_auto='.2s',
                         title="Average Births per Month",
                         color='birth_count', color_continuous_scale='Blues')
    st.plotly_chart(fig_monthly, use_container_width=True)

# -----------------------
# SECTION 2: DISTRIBUTIONS
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
# SECTION 3: TRENDS
# -----------------------
st.subheader("📈 Detailed Trends")

# Age trend over time
age_trend = filtered_df.groupby('year')[selected_ages].sum().reset_index()
fig_age_trend = px.area(age_trend, x='year', y=selected_ages,
                        title="Age Group Birth Trends Over Time",
                        template="simple_white")
st.plotly_chart(fig_age_trend, use_container_width=True)

# Region trend line
region_trend = filtered_df.groupby(['year', 'region'])['birth_count'].sum().reset_index()
fig_region_trend = px.line(region_trend, x='year', y='birth_count', color='region',
                           title="Yearly Births by Region", template="plotly_white")
st.plotly_chart(fig_region_trend, use_container_width=True)

# -----------------------
# SECTION 4: HEATMAP
# -----------------------
st.subheader("🔥 Monthly Births by Region Heatmap")

heat_df = filtered_df.groupby(['region', 'month'])['birth_count'].mean().unstack().reindex(columns=month_order)
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(heat_df, cmap="YlOrRd", annot=True, fmt=".0f", linewidths=.5, ax=ax)
st.pyplot(fig)

# -----------------------
# SECTION 5: FORECASTING (SARIMA)
# -----------------------
st.markdown("---")
st.subheader("🔮 Forecasting Future Births")

with st.expander("📈 Run Forecasting with SARIMA"):
    forecast_region = st.selectbox("Select Region for Forecast", sorted(df['region'].unique()))
    forecast_months = st.slider("Forecast Months", 6, 36, 12)

    region_df = df[df['region'] == forecast_region]
    ts_df = region_df.groupby(['year', 'month'])['birth_count'].sum().reset_index()

    # Convert to datetime and reindex by month
    ts_df['date'] = pd.to_datetime(ts_df['year'].astype(str) + '-' + ts_df['month'], format='%Y-%B')
    ts_df = ts_df.sort_values('date').set_index('date').resample('MS').sum()
    ts_df['birth_count'] = ts_df['birth_count'].fillna(0)  # Fill NaNs

    ts = ts_df['birth_count']

    with st.spinner("Training SARIMA model..."):
        model = pm.auto_arima(ts, seasonal=True, m=12, stepwise=True, suppress_warnings=True)

    forecast_values = model.predict(n_periods=forecast_months)
    forecast_index = pd.date_range(ts.index[-1] + pd.offsets.MonthBegin(1), periods=forecast_months, freq='MS')
    forecast_series = pd.Series(forecast_values, index=forecast_index)

    full_series = pd.concat([ts, forecast_series])
    fig_forecast = px.line(full_series.reset_index(), x='index', y=0,
                           title=f"{forecast_region}: Historical + Forecasted Births",
                           labels={'index': 'Date', '0': 'Birth Count'},
                           template="plotly_white")
    fig_forecast.add_scatter(x=forecast_series.index, y=forecast_series,
                             mode='lines', name='Forecast', line=dict(dash='dot'))
    st.plotly_chart(fig_forecast, use_container_width=True)
