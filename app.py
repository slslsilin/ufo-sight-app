import streamlit as st
import pandas as pd
import plotly.express as px

# 配置页面
st.set_page_config(page_title="UFO地理分析", layout="wide")
st.title("UFO目击地理分布分析 🛸")

# 从GitHub读取数据
@st.cache_data
def load_data():
    csv_url = "https://raw.githubusercontent.com/slslsilin/ufo-sight-app/main/ufo_sighting_data.csv"
    df = pd.read_csv(csv_url)
    
    # 数据清洗
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]
    df["city"] = df["city"].astype(str).str.lower()
    df["area_type"] = df["city"].apply(
        lambda x: "rural" if "country" in x else 
                 "suburban" if "rural" in x else 
                 "urban"
    )
    return df

df = load_data()

# =========================================================================
# 问题1：目击最多的国家/地区
# =========================================================================
st.header("The most witnessed countries")
country_counts = df["country"].value_counts().reset_index()
country_counts.columns = ["Country", "Witeness times"]

# 双列布局
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Ranking")
    st.dataframe(country_counts, height=400)

with col2:
    st.subheader(" ")
    fig = px.bar(country_counts.head(20), 
                 x="Country", y="Witeness times",
                 color="Witeness times", 
                 labels={"Country": "Country", "Witeness times": "Witeness times"},
                 height=400)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 问题2：地理热点分析
# =========================================================================
st.header("Geographic hotspot distribution")

# 交互式地图
st.subheader("目击地点热力图")
st.map(df[["latitude", "longitude"]], zoom=1)

# 按州/省的目击密度
st.subheader("州/省级热点排名")
state_counts = df["state/province"].value_counts().reset_index()
state_counts.columns = ["State", "Witeness times"]
fig = px.bar(state_counts, 
             x="Witeness times", y="State", 
             orientation="h",
             labels={"State": "Region", "Witeness time": "Witeness time"},
             height=600)
st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 城乡分类逻辑（基于城市名称关键词）
# =========================================================================
def classify_urban_rural(city_name):
    """根据城市名称中的关键词分类"""
    city_name = str(city_name).lower()
    if "country" in city_name:
        return "农村"
    elif "rural" in city_name:
        return "郊区"
    else:
        return "城市"

# 应用分类
df["地区类型"] = df["city"].apply(classify_urban_rural)

# =========================================================================
# 城乡分布可视化
# =========================================================================
# =========================================================================
# Creative Visual 1: Animated Time Series Globe
# =========================================================================
st.header("🌍 Temporal Distribution Globe")
st.write("Animated sightings over time with classification")

# Create time-based aggregation
time_df = df.groupby([pd.to_datetime(df["date_time"]).dt.year, "area_type"]).size().reset_index(name="counts")
time_df.columns = ["year", "area_type", "sightings"]

# Generate 3D animated globe
fig_globe = px.scatter_geo(
    df,
    lat="latitude",
    lon="longitude",
    color="area_type",
    hover_name="city",
    animation_frame=pd.to_datetime(df["date_time"]).dt.year,
    color_discrete_map={
        "urban": "#636EFA",
        "suburban": "#EF553B",
        "rural": "#00CC96"
    },
    projection="orthographic",
    template="plotly_dark",
    height=600
)
fig_globe.update_layout(showlegend=False)
st.plotly_chart(fig_globe, use_container_width=True)

# =========================================================================
# Creative Visual 2: 3D Classification Cube
# =========================================================================
st.header("🧊 Spatial Classification Matrix")
col1, col2 = st.columns([2, 1])

with col1:
    # 3D Scatter Plot
    fig_3d = px.scatter_3d(
        df.sample(1000),  # Sampling for performance
        x="longitude",
        y="latitude",
        z=pd.to_datetime(df["date_time"]).dt.year,
        color="area_type",
        symbol="area_type",
        opacity=0.7,
        labels={"z": "Year"},
        color_discrete_map={
            "urban": "#2E91E5",
            "suburban": "#E15F99",
            "rural": "#1CA71C"
        },
        template="seaborn"
    )
    fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig_3d, use_container_width=True)

with col2:
    # Contextual Word Cloud
    st.subheader("Top Location Lexicon")
    text = " ".join(df["city"].dropna().astype(str))
    wordcloud = WordCloud(
        width=400,
        height=300,
        background_color="white",
        colormap="twilight"
    ).generate(text)
    
    plt.figure(figsize=(8, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)
 
# =========================================================================
# 添加筛选器
# =========================================================================
st.sidebar.header("筛选选项")
selected_countries = st.sidebar.multiselect("选择国家", df["country"].unique())
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
